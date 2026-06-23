from __future__ import annotations

from backend.core import embedder, vector_store


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
    """
    query_embedding = embedder.embed_query(query)
    return vector_store.retrieve(collection_id, query_embedding, top_k=top_k)


def answer_query(query: str, collection_id: str, persona_context: str = "") -> dict:
    """
    Full RAG answer: retrieve context, build prompt, call LLM, return answer + sources.
    LLM call is implemented in feat/llm-client; this wires the retrieval side.
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
