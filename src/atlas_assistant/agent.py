import datetime

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from .models import mistral_large as llm
from .state import AgentState
from .tools.create_chart import create_chart
from .tools.select_dataset import select_dataset

SYSTEM_PROMPT = """
You help users leverage the Adaptation Atlas data to answer their questions.

You have access to the following tools:
- select_dataset: to pick a dataset from the Adaptation Atlas
- create_chart: to make a plot about the dataset
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
