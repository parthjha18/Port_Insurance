from __future__ import annotations

import os
import uuid

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "./chroma_db")

_chroma_client: chromadb.PersistentClient | None = None


def _get_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
    return _chroma_client


def create_collection(collection_id: str) -> None:
    """Create (or reset) a ChromaDB collection for a policy document."""
    client = _get_client()
    # get_or_create is idempotent; delete+create gives a clean slate for re-uploads
    try:
        client.delete_collection(collection_id)
    except Exception:
        pass
    client.create_collection(name=collection_id, metadata={"hnsw:space": "cosine"})


def upsert_chunks(
    collection_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    """Insert text chunks with their embeddings into the ChromaDB collection."""
    if not chunks:
        return

    client = _get_client()
    collection = client.get_collection(collection_id)

    ids = [str(uuid.uuid4()) for _ in chunks]
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
    )


def retrieve(
    collection_id: str,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[str]:
    """
    Retrieve the top-k most similar text chunks for a query embedding.
    Returns list of document strings.
    """
    client = _get_client()
    collection = client.get_collection(collection_id)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents"],
    )

    docs = results.get("documents", [[]])[0]
    return docs


def delete_collection(collection_id: str) -> None:
    """Delete a collection and all its embeddings."""
    client = _get_client()
    try:
        client.delete_collection(collection_id)
    except Exception:
        pass


def collection_exists(collection_id: str) -> bool:
    """Check whether a collection with this ID exists."""
    client = _get_client()
    try:
        client.get_collection(collection_id)
        return True
    except Exception:
        return False


def get_chunk_count(collection_id: str) -> int:
    """Return the number of chunks stored in a collection."""
    client = _get_client()
    try:
        return client.get_collection(collection_id).count()
    except Exception:
        return 0
