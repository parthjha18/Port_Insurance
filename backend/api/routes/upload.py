from __future__ import annotations

import logging
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.core import pdf_parser, rag_pipeline
from backend.models.schemas import PolicyBenefits, UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = 50


def _regex_to_benefits(raw: dict) -> PolicyBenefits:
    """
    Convert regex-extracted string fields into a typed PolicyBenefits object.
    No LLM involved — this is instant.
    """

    def to_float(v: str | None) -> float | None:
        if v is None:
            return None
        try:
            return float(v.replace(",", "").replace("%", "").strip())
        except ValueError:
            return None

    def years_from_str(v: str | None) -> int | None:
        """Convert '3 years' or '36 months' → int years."""
        if v is None:
            return None
        v_lower = v.lower()
        import re
        m = re.search(r"(\d+)\s*(year|years)", v_lower)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d+)\s*(month|months)", v_lower)
        if m:
            return max(1, round(int(m.group(1)) / 12))
        return None

    return PolicyBenefits(
        insurer_name=raw.get("insurer_name"),
        policy_number=raw.get("policy_number"),
        sum_insured=to_float(raw.get("sum_insured")),
        annual_premium=to_float(raw.get("annual_premium")),
        waiting_period_years=years_from_str(raw.get("waiting_period")),
        no_claim_bonus_pct=to_float(raw.get("no_claim_bonus")),
        co_pay_pct=to_float(raw.get("co_pay")),
        room_rent_cap=raw.get("room_rent_cap"),
    )


@router.post("", response_model=UploadResponse)
async def upload_policy(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a health insurance policy PDF.

    Fast path (~5-10s):
      1. Save the file
      2. Extract text with pdfplumber
      3. Run regex extractor → instant structured fields (no LLM)
      4. Chunk text and embed into ChromaDB

    The benefits returned here come from regex (instant preview).
    The /analyze/compare endpoint runs the full LLM extraction + comparison.
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
        # Regex extraction — zero latency, no API call
        regex_fields = pdf_parser.extract_structured_fields(text)
        benefits = _regex_to_benefits(regex_fields)
        # Embedding — fast (~3-5s for small PDFs)
        chunks = pdf_parser.chunk_text(text)
        chunks_indexed = rag_pipeline.ingest_document(collection_id, chunks)
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        logger.exception("Processing failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")

    logger.info(
        "Uploaded %s — %d pages, %d chunks, insurer=%s",
        file.filename, page_count, chunks_indexed, benefits.insurer_name,
    )

    return UploadResponse(
        collection_id=collection_id,
        filename=file.filename,
        pages_extracted=page_count,
        chunks_indexed=chunks_indexed,
        message="Policy uploaded and indexed successfully.",
        benefits=benefits,
    )
