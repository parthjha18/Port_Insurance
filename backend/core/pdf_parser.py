# PDF text extraction and chunking — implemented in feat/pdf-parser


def extract_text(pdf_path: str) -> str:
    raise NotImplementedError("Implemented in feat/pdf-parser branch")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    raise NotImplementedError("Implemented in feat/pdf-parser branch")


def extract_structured_fields(text: str) -> dict:
    raise NotImplementedError("Implemented in feat/pdf-parser branch")
