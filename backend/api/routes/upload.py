from __future__ import annotations

import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.core import pdf_parser, rag_pipeline
from backend.models.schemas import UploadResponse

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}
MAX_FILE_SIZE_MB = 50


@router.post("", response_model=UploadResponse)
async def upload_policy(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a health insurance policy PDF.
    Extracts text, chunks it, embeds it into ChromaDB, and returns a collection_id
    that is used in subsequent /analyze and /chat calls.
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
    safe_name = f"{collection_id}_{file.filename}"
    dest_path = UPLOAD_DIR / safe_name

    async with aiofiles.open(dest_path, "wb") as f:
        await f.write(content)

    try:
        text = pdf_parser.extract_text(str(dest_path))
        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from the PDF. It may be scanned/image-based.",
            )

        chunks = pdf_parser.chunk_text(text)
        page_count = pdf_parser.get_page_count(str(dest_path))
        chunks_indexed = rag_pipeline.ingest_document(collection_id, chunks)

    except HTTPException:
        raise
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(exc)}")

    return UploadResponse(
        collection_id=collection_id,
        filename=file.filename,
        pages_extracted=page_count,
        chunks_indexed=chunks_indexed,
        message="Policy uploaded and indexed successfully.",
    )
