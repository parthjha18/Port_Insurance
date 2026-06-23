from __future__ import annotations

import logging
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.core import pdf_parser, rag_pipeline
from backend.models.schemas import UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = 50


@router.post("", response_model=UploadResponse)
async def upload_policy(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a health insurance policy PDF.
    Saves the file, extracts text, chunks it, and embeds chunks into ChromaDB.
    Returns a collection_id used by /analyze and /chat.
    This step is fast (~5-10s). The AI extraction happens via /analyze separately.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB} MB.",
        )

    collection_id = str(uuid.uuid4())
    dest_path = UPLOAD_DIR / f"{collection_id}_{file.filename}"

    async with aiofiles.open(dest_path, "wb") as f:
        await f.write(content)

    try:
        text = pdf_parser.extract_text(str(dest_path))
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        logger.exception("PDF text extraction failed for %s", file.filename)
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {exc}")

    if not text.strip():
        dest_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail="No text found in PDF. It may be a scanned/image-based document.",
        )

    try:
        page_count = pdf_parser.get_page_count(str(dest_path))
        chunks = pdf_parser.chunk_text(text)
        chunks_indexed = rag_pipeline.ingest_document(collection_id, chunks)
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        logger.exception("Embedding/indexing failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=f"Indexing failed: {exc}")

    logger.info("Uploaded %s — %d pages, %d chunks", file.filename, page_count, chunks_indexed)

    return UploadResponse(
        collection_id=collection_id,
        filename=file.filename,
        pages_extracted=page_count,
        chunks_indexed=chunks_indexed,
        message="Policy uploaded and indexed. Call /analyze to extract benefits.",
    )
