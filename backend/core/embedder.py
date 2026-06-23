from __future__ import annotations

import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        if not api_key:
            raise EnvironmentError("OPENROUTER_API_KEY is not set in environment.")
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small")

# OpenRouter caps embeddings at 2048 tokens per text; chunk at ~1500 chars to stay safe
_MAX_CHARS_PER_CHUNK = 6000


def _safe_text(text: str) -> str:
    """Truncate text to fit within the embedding model token limit."""
    return text[:_MAX_CHARS_PER_CHUNK]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of text strings using text-embedding-3-small via OpenRouter.
    Returns a list of float vectors, one per input text.
    """
    if not texts:
        return []

    client = _get_client()
    safe_texts = [_safe_text(t) for t in texts]

    # OpenRouter supports batch embedding up to 100 items
    batch_size = 100
    all_embeddings: list[list[float]] = []

    for i in range(0, len(safe_texts), batch_size):
        batch = safe_texts[i : i + batch_size]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        # response.data is sorted by index
        batch_vectors = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
        all_embeddings.extend(batch_vectors)

    return all_embeddings


def embed_query(query: str) -> list[float]:
    """
    Embed a single query string. Used for similarity search at inference time.
    """
    result = embed_texts([query])
    return result[0]
