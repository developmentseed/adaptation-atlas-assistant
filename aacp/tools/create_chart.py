"""
https://github.com/e2b-dev/e2b-cookbook/blob/main/examples/codestral-code-interpreter-python/codestral_code_interpreter.ipynb
"""
from langgraph.prebuilt import InjectedState
from aacp.settings import get_settings
import os
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

settings = get_settings()

# Set E2B API key as environment variable
os.environ["E2B_API_KEY"] = settings.e2b_api_key

client = Mistral(api_key=settings.mistral_api_key)

SYSTEM_PROMPT = "Calculate how many r's are in the word 'strawberry'"
SYSTEM_PROMPT_ORIG = """You're a python data scientist that is analyzing datasets.

You will write SQL code to extract and simplify data from a larger dataset.

The SQL code will be executed using duckdb database.

The dataset is in a parquet file in S3. here is the info about the dataset

{dataset_info}

Here is the parquet_metadata of the parquet file:

{data_sample}

Instructions:
- Return ONLY executable sql code without any markdown formatting or explanations.
- Always use the S3 path to read the parquet file in the sql code you write.
- Use csv mode for the output
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
    sql_to_extract_metadata = f"""SELECT * FROM parquet_metadata('{s3_path}')"""
    result = conn.execute(sql_to_extract_metadata)

    column_names = [desc[0] for desc in result.description]
    data_rows = result.fetchall()
    data_sample = [column_names] + list(data_rows)

    response = client.chat.complete(
        model="codestral-latest",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_ORIG.format(
                    dataset_info=json.dumps(state.dataset.metadata),
                    data_sample=data_sample,
                ),
            },
            {"role": "user", "content": plot_query},
        ],
    )
    code = extract_code_from_response(response.choices[0].message.content)

    print("DUCKDB CODE: \n", code)

    # Execute DuckDB query on S3 parquet file
    conn = duckdb.connect()
    result = conn.execute(code).fetchall()
    conn.close()

    return Command(
        update={
            # "plot": results[0][0],
            "messages": [
                ToolMessage(
                    content=(f"Code: {code}"),
                    tool_call_id=tool_call_id,
                )
            ],
        },
    )
