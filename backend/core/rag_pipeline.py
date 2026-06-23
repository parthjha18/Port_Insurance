# RAG orchestration — implemented in feat/rag-pipeline


def answer_query(query: str, collection_id: str, persona_context: str = "") -> dict:
    raise NotImplementedError("Implemented in feat/rag-pipeline branch")


def extract_benefits(collection_id: str) -> dict:
    raise NotImplementedError("Implemented in feat/llm-client branch")


def compare_policies(old_collection_id: str, new_collection_id: str, persona_context: str = "") -> dict:
    raise NotImplementedError("Implemented in feat/llm-client branch")
