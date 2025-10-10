from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic
from pydantic import Field

from .models import Dataset


class AgentState(AgentStatePydantic):
    dataset: Dataset | None = Field(
        default=None,
        description="The dataset to use for the current task",
    )
