# OpenRouter LLM client — implemented in feat/llm-client


def complete(prompt: str, system: str = "") -> str:
    raise NotImplementedError("Implemented in feat/llm-client branch")


def complete_structured(prompt: str, system: str = "", response_schema: dict = None) -> dict:
    raise NotImplementedError("Implemented in feat/llm-client branch")


def stream(prompt: str, system: str = ""):
    raise NotImplementedError("Implemented in feat/llm-client branch")
