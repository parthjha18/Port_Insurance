from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.core.persona_loader import get_persona_by_id, load_personas
from backend.models.schemas import Persona, PersonaListResponse

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/demo", response_model=PersonaListResponse)
async def get_demo_personas(
    limit: int = Query(default=5, ge=1, le=20, description="Number of personas to return"),
) -> PersonaListResponse:
    """
    Returns a set of realistic Indian professional personas derived from the
    LinkedIn India dataset. Used by the frontend demo mode.
    Each persona includes an occupation category and a pre-built insurance porting scenario.
    """
    personas_raw = load_personas(limit=limit)
    personas = [Persona(**p) for p in personas_raw]
    return PersonaListResponse(personas=personas, total=len(personas))


@router.get("/{persona_id}", response_model=Persona)
async def get_persona(persona_id: str) -> Persona:
    """
    Retrieve a specific persona by ID.
    """
    raw = get_persona_by_id(persona_id)
    if not raw:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found.")
    return Persona(**raw)
