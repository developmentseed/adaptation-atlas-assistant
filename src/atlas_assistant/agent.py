import datetime

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from .settings import Settings
from .state import AgentState
from .tools.choose_dataset import choose_dataset

SYSTEM_PROMPT = """
You help users leverage the Adaptation Atlas data to answer their questions.

You have access to the following tools:
- select_dataset: to pick a dataset from the Adaptation Atlas
- create_chart: to make a plot about the dataset
"""


async def create_graph(settings: Settings) -> CompiledStateGraph:
    tools = [
        choose_dataset,
    ]

    checkpointer = InMemorySaver()
    return create_react_agent(
        settings.get_chat_model(),
        tools,
        prompt=(
            SYSTEM_PROMPT
            + f"\nToday is {datetime.datetime.now(datetime.UTC):%Y-%m-%d}."
        ),
        state_schema=AgentState,
        checkpointer=checkpointer,
    )
