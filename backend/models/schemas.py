from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    collection_id: str
    filename: str
    pages_extracted: int
    chunks_indexed: int
    message: str


class PolicyBenefits(BaseModel):
    insurer_name: Optional[str] = None
    policy_number: Optional[str] = None
    sum_insured: Optional[float] = None
    annual_premium: Optional[float] = None
    waiting_period_years: Optional[int] = None
    pre_existing_covered: Optional[bool] = None
    no_claim_bonus_pct: Optional[float] = None
    co_pay_pct: Optional[float] = None
    room_rent_cap: Optional[str] = None
    maternity_covered: Optional[bool] = None
    restoration_benefit: Optional[bool] = None
    day_care_procedures: Optional[bool] = None
    ayush_treatment: Optional[bool] = None
    ambulance_cover: Optional[str] = None
    policy_tenure_years: Optional[int] = None
    family_floater: Optional[bool] = None
    claim_history_notes: Optional[str] = None


class BenefitDiff(BaseModel):
    field: str
    old_value: Optional[str]
    new_value: Optional[str]
    change_type: str = Field(description="improved | degraded | unchanged | unknown")
    notes: Optional[str] = None


class PortingComparison(BaseModel):
    old_policy: PolicyBenefits
    new_policy: PolicyBenefits
    diffs: list[BenefitDiff]
    premium_delta: Optional[float] = None
    coverage_delta: Optional[float] = None
    recommendation: str
    cost_effective: bool
    waiting_period_risk: str


class ChatMessage(BaseModel):
    role: str = Field(description="user | assistant | system")
    content: str


class ChatRequest(BaseModel):
    collection_id: str
    messages: list[ChatMessage]
    persona_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)


class Persona(BaseModel):
    id: str
    full_name: str
    occupation: str
    city: str
    state: str
    occupation_category: str
    insurance_profile: str
    demo_scenario: str


class PersonaListResponse(BaseModel):
    personas: list[Persona]
    total: int


class AnalyzeRequest(BaseModel):
    collection_id: str


class CompareRequest(BaseModel):
    old_collection_id: str
    new_collection_id: str
    persona_id: Optional[str] = None
