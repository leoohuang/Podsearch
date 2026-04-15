# src/indexing.py
import chromadb
from src.config import CHROMA_DIR

def get_collection(name="podcast"):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )