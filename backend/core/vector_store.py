# ChromaDB vector store — implemented in feat/rag-pipeline


def create_collection(collection_id: str) -> None:
    raise NotImplementedError("Implemented in feat/rag-pipeline branch")


def upsert_chunks(collection_id: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    raise NotImplementedError("Implemented in feat/rag-pipeline branch")


def retrieve(collection_id: str, query_embedding: list[float], top_k: int = 5) -> list[str]:
    raise NotImplementedError("Implemented in feat/rag-pipeline branch")


def delete_collection(collection_id: str) -> None:
    raise NotImplementedError("Implemented in feat/rag-pipeline branch")
