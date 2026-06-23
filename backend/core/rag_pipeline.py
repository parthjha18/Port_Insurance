from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.core import embedder, vector_store

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("backend/uploads")


def _chunks_path(collection_id: str) -> Path:
    return UPLOAD_DIR / f"{collection_id}.chunks.json"


def ensure_ingested(collection_id: str) -> None:
    """
    Ensure the collection exists in ChromaDB.

    If not yet embedded (upload only saved chunks to disk), embed now.
    This is called lazily on the first compare/chat request, so the user
    never waits for embedding during upload.
    """
    if vector_store.collection_exists(collection_id):
        return

    path = _chunks_path(collection_id)
    if not path.exists():
        raise FileNotFoundError(
            f"No chunks found for collection {collection_id}. "
            "The document may not have been uploaded correctly."
        )

    logger.info("Lazy-embedding collection %s …", collection_id)
    chunks: list[str] = json.loads(path.read_text(encoding="utf-8"))
    ingest_document(collection_id, chunks)
    logger.info("Embedding complete for collection %s (%d chunks)", collection_id, len(chunks))


def ingest_document(collection_id: str, chunks: list[str]) -> int:
    """
    Embed all chunks and store them in ChromaDB.
    Returns the number of chunks indexed.
    """
    vector_store.create_collection(collection_id)
    embeddings = embedder.embed_texts(chunks)
    vector_store.upsert_chunks(collection_id, chunks, embeddings)
    return len(chunks)


def retrieve_context(collection_id: str, query: str, top_k: int = 5) -> list[str]:
    """
    Retrieve the most relevant chunks for a query from the given collection.
    Ensures the collection is embedded first (lazy).
    """
    ensure_ingested(collection_id)
    query_embedding = embedder.embed_query(query)
    return vector_store.retrieve(collection_id, query_embedding, top_k=top_k)


def answer_query(query: str, collection_id: str, persona_context: str = "") -> dict:
    """
    Full RAG answer: retrieve context → build prompt → call LLM → return answer + sources.
    """
    from backend.core import llm_client, benefit_extractor

    chunks = retrieve_context(collection_id, query)
    context = "\n\n".join(chunks)
    prompt = benefit_extractor.build_chat_prompt(query, context, persona_context)
    answer = llm_client.complete(prompt)

    return {
        "answer": answer,
        "sources": chunks,
    }


def extract_benefits(collection_id: str) -> dict:
    """
    Extract structured policy benefits using RAG + LLM.
    Embedding is done lazily here if not already in ChromaDB.
    """
    from backend.core import llm_client, benefit_extractor

    query = (
        "Extract all key insurance policy details: insurer name, policy number, "
        "sum insured, premium, waiting periods, pre-existing disease coverage, "
        "no claim bonus, co-pay, room rent cap, maternity benefit, restoration benefit."
    )
    chunks = retrieve_context(collection_id, query, top_k=8)
    context = "\n\n".join(chunks)
    prompt = benefit_extractor.build_extraction_prompt(context)
    raw = llm_client.complete_structured(prompt)
    return raw


def compare_policies(
    old_collection_id: str,
    new_collection_id: str,
    persona_context: str = "",
) -> dict:
    """
    Compare benefits from two policy collections and return a porting recommendation.
    Both collections are embedded lazily if needed.
    """
    old_benefits = extract_benefits(old_collection_id)
    new_benefits = extract_benefits(new_collection_id)

    from backend.core import llm_client, benefit_extractor

    prompt = benefit_extractor.build_comparison_prompt(
        old_benefits, new_benefits, persona_context
    )
    comparison = llm_client.complete_structured(prompt)
    return {
        "old_policy": old_benefits,
        "new_policy": new_benefits,
        "comparison": comparison,
    }
