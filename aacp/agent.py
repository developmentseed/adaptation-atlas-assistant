import datetime

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from aacp.state import AgentState
from aacp.models import mistral_large as llm
from aacp.tools.select_dataset import select_dataset
from aacp.tools.create_chart import create_chart


SYSTEM_PROMPT = """
You help picking datasets from the Adaptation Atlas. 
And then make a plot about the dataset. Always run the create chart tool.
"""


async def create_graph():
    tools = [
        select_dataset,
        create_chart,
    ]

    checkpointer = InMemorySaver()
    return create_react_agent(
        llm,
        tools,
        prompt=(
            SYSTEM_PROMPT
            + "\nToday is {date:%Y-%m-%d}.".format(
                date=datetime.datetime.now(datetime.timezone.utc)
            )
        ),
        state_schema=AgentState,
        checkpointer=checkpointer,
    )
