from google import genai
from google.genai import types
import dotenv
from langgraph.prebuilt import InjectedState
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.tools import tool
from typing import Annotated

from langchain_core.messages import ToolMessage
from langgraph.types import Command
import json

from aacp.state import AgentState

dotenv.load_dotenv()

client = genai.Client()


@tool("create_chart_tool")
async def create_chart(
    chart_query: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[AgentState, InjectedState] = None,
) -> Command:
    """Create a plot from the list of available datasets.

    Updates the `plot` state with the details of the best matching plot if found,
    """
    print(f"Creating plot for query: {chart_query}")

    json_string = json.dumps(state.dataset.metadata)

    prompt = f"""
    Here is my dataset in json format. It contains a link to a parquet file in S3.
    Use the content of the to create a plot.
    
    {json_string}
    
    Please analyze this data and make a recharts compatible data dictionary.
    Generate and run code for the analysis.

    Return the chart with a heading and a caption.

    Make the plot answering as good as possible to the user query instructions:

    {chart_query}
    """

    print(prompt)

    config = types.GenerateContentConfig(
        # response_schema=gemini_schema,
        tools=[types.Tool(code_execution=types.ToolCodeExecution)]
    )
    print(config)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        if part.executable_code is not None:
            print(part.executable_code.code)
        if part.code_execution_result is not None:
            print(part.code_execution_result.output)

    return Command(
        update={
            # "plot": results[0][0],
            "messages": [
                ToolMessage(
                    content=part.text,
                    tool_call_id=tool_call_id,
                )
            ],
        },
    )
