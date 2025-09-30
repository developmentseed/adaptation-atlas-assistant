from langchain_core.tools.base import InjectedToolCallId
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings
from pathlib import Path
from typing import Annotated
import logging

from langchain_core.messages import ToolMessage
from langgraph.types import Command

logger = logging.getLogger(__name__)


async def load_datasets_vector_embeddings() -> Chroma:
    # Initialize ChromaDB with existing database
    db_path = Path("aacp/data/aa-docs-mistral-index")
    if not Path(db_path).exists():
        raise RuntimeError(f"Database does not exist at path {db_path}.")
    embedder = MistralAIEmbeddings(model="mistral-embed")
    vectorstore = Chroma(persist_directory=str(db_path), embedding_function=embedder)
    return vectorstore


@tool("select_dataset_tool")
async def select_dataset(
    dataset_query: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Select a dataset from the list of available datasets.

    dataset_query: "The query to select a dataset"

    Updates the `dataset` state with the details of the best matching dataset if found,
    """
    logger.info(f"Finding dataset for query: {dataset_query}")
    vectorstore = await load_datasets_vector_embeddings()

    results = vectorstore.similarity_search_with_score(dataset_query, k=3)

    return Command(
        update={
            "dataset": results[0][0],
            "messages": [
                ToolMessage(
                    content=("Returning dataset: " + results[0][0].page_content),
                    tool_call_id=tool_call_id,
                )
            ],
        },
    )
