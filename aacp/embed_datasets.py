"""
https://onewri.sharepoint.com/:x:/s/LandandCarbonWatch/ESllWse7dmFAnobmcA4IMXABbyDYhta0p81qnPH3-XUsBw
"""

from pathlib import Path

from langchain_mistralai import MistralAIEmbeddings
import dotenv
import json
from langchain_chroma import Chroma

datasets = json.load(open("aacp/data/datasets.json"))

dotenv.load_dotenv()

embedder = MistralAIEmbeddings(model="mistral-embed")

data_dir = Path("aacp/data").absolute()

docs = []
metadatas = []
for ds in datasets:
    docs.append(f"Name: {ds['name']}, Info: {ds['info']}, Note: {ds['note']}")
    metadatas.append(ds)


Chroma.from_texts(
    texts=docs,
    embedding=embedder,
    metadatas=metadatas,
    persist_directory=str(data_dir / "aa-docs-mistral-index"),
)
