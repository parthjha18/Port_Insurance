from __future__ import annotations

import re
from pathlib import Path

import pdfplumber


def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF file, page by page."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())

    return "\n\n".join(pages)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks using a sliding window over word tokens.
    Overlap ensures context is not lost at chunk boundaries.
    """
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start += chunk_size - overlap

    return chunks


def extract_structured_fields(text: str) -> dict:
    """
    Use regex heuristics to pull out key insurance fields from raw policy text.
    Returns a dict of field -> value (string). LLM will refine these later.
    """
    fields: dict[str, str | None] = {
        "policy_number": None,
        "insurer_name": None,
        "sum_insured": None,
        "annual_premium": None,
        "waiting_period": None,
        "pre_existing_waiting": None,
        "no_claim_bonus": None,
        "co_pay": None,
        "room_rent_cap": None,
        "policy_start_date": None,
        "policy_end_date": None,
        "insured_name": None,
    }

    # Policy number
    m = re.search(r"policy\s*(no|number|#)[.:\s]*([A-Z0-9/-]{5,20})", text, re.IGNORECASE)
    if m:
        fields["policy_number"] = m.group(2).strip()

    # Sum insured — allow arbitrary text between "sum insured" and the amount
    m = re.search(
        r"sum\s*insured[^.]{0,40}?(?:rs\.?|inr)\.?\s*([\d,]+(?:\.\d{1,2})?)\s*(?:lakh|lac|lakhs)?",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["sum_insured"] = m.group(1).replace(",", "").strip()

    # Annual premium
    m = re.search(
        r"(?:annual\s*)?premium[:\s]*(?:rs\.?|inr)?\s*([\d,]+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["annual_premium"] = m.group(1).replace(",", "").strip()

    # Waiting period (initial)
    m = re.search(
        r"(?:initial\s*)?waiting\s*period[:\s]*(\d+)\s*(day|days|month|months|year|years)",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["waiting_period"] = f"{m.group(1)} {m.group(2)}"

    # Pre-existing disease waiting period
    m = re.search(
        r"pre[\s-]*existing[^.]*waiting[^.]*?(\d+)\s*(year|years|month|months)",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["pre_existing_waiting"] = f"{m.group(1)} {m.group(2)}"

    # No claim bonus
    m = re.search(
        r"no[\s-]*claim[\s-]*bonus[:\s]*(\d+)\s*%?",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["no_claim_bonus"] = f"{m.group(1)}%"

    # Co-pay
    m = re.search(
        r"co[\s-]*pay(?:ment)?[:\s]*(\d+)\s*%?",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["co_pay"] = f"{m.group(1)}%"

    # Room rent cap
    m = re.search(
        r"room\s*rent[^.]*?(?:rs\.?|inr)?\s*([\d,]+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["room_rent_cap"] = m.group(1).replace(",", "").strip()

    # Insurer name — look for common Indian insurers
    insurers = [
        "Star Health",
        "HDFC ERGO",
        "ICICI Lombard",
        "Bajaj Allianz",
        "New India Assurance",
        "United India",
        "National Insurance",
        "Oriental Insurance",
        "Niva Bupa",
        "Care Health",
        "Aditya Birla Health",
        "Tata AIG",
        "Reliance Health",
        "SBI Health",
        "ManipalCigna",
        "Prudential",
        "Max Bupa",
    ]
    for insurer in insurers:
        if re.search(re.escape(insurer), text, re.IGNORECASE):
            fields["insurer_name"] = insurer
            break

    # Policy dates
    date_pattern = r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})"
    m = re.search(
        rf"(?:commencement|start|inception|from)\s*date[:\s]*{date_pattern}",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["policy_start_date"] = m.group(1)

    m = re.search(
        rf"(?:expiry|end|to|until|renewal)\s*date[:\s]*{date_pattern}",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["policy_end_date"] = m.group(1)

    return fields


def get_page_count(pdf_path: str) -> int:
    """Return the number of pages in a PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        return len(pdf.pages)
