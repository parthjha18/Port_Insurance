"""Smoke tests for the PDF parser module."""
from __future__ import annotations

import os
import pytest

from backend.core.pdf_parser import chunk_text, extract_structured_fields


def test_chunk_text_basic():
    text = " ".join([f"word{i}" for i in range(100)])
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    # Each chunk should have at most chunk_size words
    for chunk in chunks:
        assert len(chunk.split()) <= 20


def test_chunk_text_overlap():
    text = " ".join([f"w{i}" for i in range(30)])
    chunks = chunk_text(text, chunk_size=10, overlap=3)
    # The last word of chunk N should appear in chunk N+1 (overlap)
    last_word = chunks[0].split()[-1]
    assert last_word in chunks[1]


def test_chunk_text_empty():
    assert chunk_text("") == []


def test_chunk_text_small():
    text = "hello world"
    chunks = chunk_text(text, chunk_size=500)
    assert chunks == ["hello world"]


def test_extract_structured_fields_sum_insured():
    sample = "The Sum Insured under this policy is Rs. 5,00,000 for the insured."
    fields = extract_structured_fields(sample)
    assert fields["sum_insured"] == "500000"


def test_extract_structured_fields_no_claim_bonus():
    sample = "No Claim Bonus: 10% for every claim-free year up to 50%."
    fields = extract_structured_fields(sample)
    assert fields["no_claim_bonus"] == "10%"


def test_extract_structured_fields_insurer_star_health():
    sample = "This policy is issued by Star Health and Allied Insurance Co. Ltd."
    fields = extract_structured_fields(sample)
    assert fields["insurer_name"] == "Star Health"


def test_extract_structured_fields_no_match_returns_none():
    fields = extract_structured_fields("This is a random document with no insurance terms.")
    # All fields should be None since no patterns match
    assert all(v is None for v in fields.values())


# Integration test: only runs if actual PDF exists in data/
PDF_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "health_insurance_policy_and_portability_kit.pdf"
)


@pytest.mark.skipif(not os.path.exists(PDF_PATH), reason="PDF not present locally")
def test_extract_text_real_pdf():
    from backend.core.pdf_parser import extract_text, get_page_count

    text = extract_text(PDF_PATH)
    assert isinstance(text, str)
    assert len(text) > 100

    pages = get_page_count(PDF_PATH)
    assert pages > 0
    print(f"Extracted {len(text)} chars from {pages} pages")
