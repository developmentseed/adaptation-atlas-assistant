from langgraph.prebuilt.chat_agent_executor import AgentStatePydantic
from langchain_core.documents import Document
from typing import Optional
from pydantic import Field
from typing import Literal
from pydantic import BaseModel


class Base64Plot(BaseModel):
    type: Literal["image/png"] = "image/png"
    data: str


class AgentState(AgentStatePydantic):
    dataset: Optional[Document] = Field(
        default=None,
        description="The dataset to use for the current task",
    )

    plot: Optional[Base64Plot] = Field(
        default=None, description="Base64 string representing a plot"
    )
