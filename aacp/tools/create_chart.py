"""
https://github.com/e2b-dev/e2b-cookbook/blob/main/examples/codestral-code-interpreter-python/codestral_code_interpreter.ipynb
"""

from langgraph.prebuilt import InjectedState
from aacp.settings import get_settings
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.tools import tool
from typing import Annotated
import duckdb
from aacp.state import AgentState
from langchain_core.messages import ToolMessage
from langgraph.types import Command
import re
from mistralai import Mistral
import json
import pandas as pd

settings = get_settings()

client = Mistral(api_key=settings.mistral_api_key)

SYSTEM_PROMPT = "Calculate how many r's are in the word 'strawberry'"
SYSTEM_PROMPT_ORIG = """You're a python data scientist that is analyzing datasets.

You will write SQL code to extract and simplify data from a larger dataset.

The SQL code will be executed using duckdb database.

The dataset is in a parquet file in S3. here is the info about the dataset

{dataset_info}

Here is a csv of the head of the dataset:

```csv
{data_sample}
```

Instructions:
- Return ONLY executable sql code without any markdown formatting or explanations.
- Always use the S3 path to read the parquet file in the sql code you write.
"""


def extract_code_from_response(content: str) -> str:
    """Extract Python code from LLM response."""
    # Try to find markdown code blocks first
    code_pattern = r"```(?:python|sql)?\n(.*?)```"
    matches = re.findall(code_pattern, content, re.DOTALL)

    if matches:
        return matches[0].strip()

    # If no code blocks, return cleaned content
    return content.strip()


@tool("create_chart_tool")
async def create_chart(
    plot_query: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[AgentState, InjectedState] = None,
) -> Command:
    """Create a plot from the list of available datasets.

    Updates the `plot` state with the details of the best matching plot if found,
    """
    print(f"Creating plot for query: {plot_query}")
    if not state.dataset:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="No dataset selected", tool_call_id=tool_call_id
                    )
                ]
            }
        )
    s3_path = state.dataset.metadata["s3"]
    conn = duckdb.connect()
    sql_to_extract_metadata = f"""SELECT * FROM '{s3_path}' LIMIT 5"""
    result = conn.execute(sql_to_extract_metadata)

    column_names = [desc[0] for desc in result.description]
    data_rows = result.fetchall()
    data_sample = pd.DataFrame(data_rows, columns=column_names)
    conn.close()

    response = client.chat.complete(
        model="codestral-latest",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_ORIG.format(
                    dataset_info=json.dumps(state.dataset.metadata),
                    data_sample=data_sample.to_string(index=False),
                ),
            },
            {"role": "user", "content": plot_query},
        ],
    )
    code = extract_code_from_response(response.choices[0].message.content)

    print("DUCKDB CODE: \n", code)

    conn = duckdb.connect()
    result = conn.execute(code)

    column_names = [desc[0] for desc in result.description]
    data_rows = result.fetchall()
    chart_data = pd.DataFrame(data_rows, columns=column_names)
    conn.close()

    return Command(
        update={
            "chart_data": chart_data.to_dict(),
            "messages": [
                ToolMessage(
                    content=(
                        f"Retrieved data for chart: {chart_data.head().to_string(index=False)}"
                    ),
                    tool_call_id=tool_call_id,
                )
            ],
        },
    )
