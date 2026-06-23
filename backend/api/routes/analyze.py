from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

from pathlib import Path

from backend.core import rag_pipeline
from backend.models.schemas import (
    AnalyzeRequest,
    CompareRequest,
    PolicyBenefits,
    PortingComparison,
    BenefitDiff,
)

router = APIRouter(prefix="/analyze", tags=["analyze"])

UPLOAD_DIR = Path("backend/uploads")


def _require_collection(collection_id: str) -> None:
    """Check that the document was uploaded (chunks file exists on disk)."""
    chunks_file = UPLOAD_DIR / f"{collection_id}.chunks.json"
    if not chunks_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_id}' not found. Upload a PDF first.",
        )


@router.post("", response_model=PolicyBenefits)
async def analyze_policy(request: AnalyzeRequest) -> PolicyBenefits:
    """
    Extract structured policy benefits (sum insured, waiting periods, NCB, etc.)
    from a previously uploaded policy document.
    """
    _require_collection(request.collection_id)

    try:
        raw = rag_pipeline.extract_benefits(request.collection_id)
    except Exception as exc:
        logger.exception("Benefit extraction failed for collection %s", request.collection_id)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(exc)}")

    try:
        return PolicyBenefits(**raw)
    except Exception:
        return PolicyBenefits(**{k: v for k, v in raw.items() if k in PolicyBenefits.model_fields})


@router.post("/compare", response_model=PortingComparison)
async def compare_policies(request: CompareRequest) -> PortingComparison:
    """
    Compare two uploaded policy documents side by side.
    Returns benefit diffs, premium delta, and a porting recommendation.
    """
    _require_collection(request.old_collection_id)
    _require_collection(request.new_collection_id)

    persona_context = ""
    if request.persona_id:
        try:
            from backend.core.persona_loader import get_persona_context
            persona_context = get_persona_context(request.persona_id)
        except Exception:
            pass

    try:
        result = rag_pipeline.compare_policies(
            request.old_collection_id,
            request.new_collection_id,
            persona_context=persona_context,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(exc)}")

    old_benefits = PolicyBenefits(**{
        k: v for k, v in result["old_policy"].items() if k in PolicyBenefits.model_fields
    })
    new_benefits = PolicyBenefits(**{
        k: v for k, v in result["new_policy"].items() if k in PolicyBenefits.model_fields
    })

    comparison = result.get("comparison", {})
    raw_diffs = comparison.get("diffs", [])
    diffs = [
        BenefitDiff(
            field=d.get("field", ""),
            old_value=str(d.get("old_value", "")),
            new_value=str(d.get("new_value", "")),
            change_type=d.get("change_type", "unknown"),
            notes=d.get("notes"),
        )
        for d in raw_diffs
        if isinstance(d, dict)
    ]

    return PortingComparison(
        old_policy=old_benefits,
        new_policy=new_benefits,
        diffs=diffs,
        premium_delta=comparison.get("premium_delta"),
        coverage_delta=comparison.get("coverage_delta"),
        recommendation=comparison.get("recommendation", ""),
        cost_effective=bool(comparison.get("cost_effective", False)),
        waiting_period_risk=comparison.get("waiting_period_risk", ""),
    )
