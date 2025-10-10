from __future__ import annotations

from langchain_core.documents import Document
from pydantic import BaseModel


class Dataset(BaseModel):
    """A STAC item, but only with the fields we care about."""

    id: str
    title: str
    description: str
    score: float
    assets: dict[str, Asset]

    @classmethod
    def from_document_and_score(cls, document: Document, score: float) -> Dataset:
        # TODO the document should just be a STAC item
        metadata = document.metadata
        asset = Asset(href=metadata["s3"])
        return cls(
            id=metadata["name"],
            title=metadata["info"],
            description=metadata["note"],
            assets={"data": asset},
            score=score,
        )


class Asset(BaseModel):
    """A simplified STAC asset."""

    href: str
