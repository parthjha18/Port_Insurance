# Structured benefit extraction prompts — implemented in feat/llm-client


def build_extraction_prompt(context: str) -> str:
    raise NotImplementedError("Implemented in feat/llm-client branch")


def build_comparison_prompt(old_benefits: dict, new_benefits: dict, persona_context: str = "") -> str:
    raise NotImplementedError("Implemented in feat/llm-client branch")


def build_chat_prompt(query: str, context: str, persona_context: str = "") -> str:
    raise NotImplementedError("Implemented in feat/llm-client branch")
