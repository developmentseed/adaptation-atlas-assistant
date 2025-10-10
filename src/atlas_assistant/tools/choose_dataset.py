from pathlib import Path
from typing import Annotated

from langchain_chroma import Chroma
from langchain_core.messages.tool import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langchain_mistralai import MistralAIEmbeddings
from langgraph.types import Command

from ..models import Dataset
from ..settings import Settings, get_settings


@tool
def choose_dataset(
    query: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command[None]:
    """Choose a single Adaptation Atlas dataset based on the input query.

    Args:
        query: The input query

    Returns:
        The STAC Item describing the dataset, or None if no datasets were found.
    """
    settings = get_settings()
    datasets = query_datasets(query, settings)
    if datasets:
        dataset = datasets[0]
        return Command(
            update={
                "dataset": dataset,
                "messages": [
                    ToolMessage(
                        content="Choosing dataset: " + dataset.title,
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )
    else:
        return Command(
            update={
                "dataset": None,
                "messages": [
                    ToolMessage(
                        content="No dataset found",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )


def query_datasets(query: str, settings: Settings) -> list[Dataset]:
    """Find all datasets that match the query"""
    if not Path(settings.database_path).exists():
        raise Exception(f"Database does not exist at path {settings.database_path}.")
    if not settings.mistral_api_key:
        raise Exception("Cannot create mistral AI embeddings object without an API key")
    embedder = MistralAIEmbeddings(
        model="mistral-embed", api_key=settings.mistral_api_key
    )
    vectorstore = Chroma(
        persist_directory=settings.database_path, embedding_function=embedder
    )
    results = vectorstore.similarity_search_with_score(query, k=3)
    return [
        Dataset.from_document_and_score(document, score)
        for (document, score) in results
    ]
