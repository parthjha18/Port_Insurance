from __future__ import annotations

import json
import logging
import re
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.core import pdf_parser
from backend.models.schemas import PolicyBenefits, UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = 50


def _regex_to_benefits(raw: dict) -> PolicyBenefits:
    """Convert regex-extracted string fields → typed PolicyBenefits. Zero latency."""

    def to_float(v: str | None) -> float | None:
        if v is None:
            return None
        try:
            return float(v.replace(",", "").replace("%", "").strip())
        except ValueError:
            return None

    def years_from_str(v: str | None) -> int | None:
        if v is None:
            return None
        m = re.search(r"(\d+)\s*(year|years)", v, re.IGNORECASE)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d+)\s*(month|months)", v, re.IGNORECASE)
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
    Upload a health insurance PDF — returns in < 2 seconds, zero API calls.

    What happens here (all local, no network):
      1. Save the file to disk
      2. Extract text with pdfplumber
      3. Run regex extractor → instant structured fields
      4. Chunk the text and save chunks to a .chunks.json sidecar

    What does NOT happen here:
      - No OpenRouter embedding call (moved to compare/chat on first use)

    The /analyze/compare endpoint embeds on first access (lazy).
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
        regex_fields = pdf_parser.extract_structured_fields(text)
        benefits = _regex_to_benefits(regex_fields)
        chunks = pdf_parser.chunk_text(text)

        # Persist chunks so RAG pipeline can embed lazily on first compare/chat
        chunks_path = UPLOAD_DIR / f"{collection_id}.chunks.json"
        chunks_path.write_text(json.dumps(chunks), encoding="utf-8")

    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        logger.exception("Processing failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")

    logger.info(
        "Uploaded %s — %d pages, %d chunks saved to disk (embedding deferred). insurer=%s",
        file.filename, page_count, len(chunks), benefits.insurer_name,
    )

    return UploadResponse(
        collection_id=collection_id,
        filename=file.filename,
        pages_extracted=page_count,
        chunks_indexed=len(chunks),
        message="Policy uploaded and indexed successfully.",
        benefits=benefits,
    )
