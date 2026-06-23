from __future__ import annotations

import json

IRDAI_CONTEXT = """
Under IRDAI (Insurance Regulatory and Development Authority of India) Health Insurance Regulations:
- Portability requests must be filed at least 45 days before policy renewal.
- Waiting period credits (initial + pre-existing disease) earned with the old insurer are transferable.
- No-Claim Bonus (NCB) portability is at the discretion of the new insurer.
- The new insurer cannot offer lower sum insured or fewer benefits than the old policy at portability.
- Pre-existing diseases are defined as conditions diagnosed/treated within 48 months before policy inception.
"""


def build_extraction_prompt(context: str) -> str:
    """
    Build a structured extraction prompt that asks GPT-4o mini to return
    a JSON object with all key policy fields.
    """
    return f"""You are analyzing an Indian health insurance policy document.
Extract the following fields from the policy text and return them as a single JSON object.
Return null for any field not clearly mentioned in the text. Do NOT guess or hallucinate values.

Fields to extract:
- insurer_name: string (name of the insurance company)
- policy_number: string
- sum_insured: number (in rupees, e.g. 500000 for 5 lakh)
- annual_premium: number (in rupees)
- waiting_period_years: number (initial waiting period in years, typically 30 days = 0.08)
- pre_existing_waiting_years: number (pre-existing disease waiting period, typically 2-4 years)
- pre_existing_covered: boolean (true if pre-existing diseases are covered after waiting period)
- no_claim_bonus_pct: number (NCB percentage per claim-free year)
- co_pay_pct: number (co-payment percentage, 0 if none)
- room_rent_cap: string (e.g. "1% of sum insured per day" or "Rs. 5000/day" or "No limit")
- maternity_covered: boolean
- restoration_benefit: boolean (true if sum insured is restored after full utilization)
- day_care_procedures: boolean
- ayush_treatment: boolean (Ayurveda, Yoga, Naturopathy, Unani, Siddha, Homeopathy)
- ambulance_cover: string (amount or description)
- family_floater: boolean (true if it is a family floater plan)
- policy_tenure_years: number
- claim_history_notes: string (any claims mentioned in the document)

Policy Document Context:
{context}

Return only valid JSON. Example:
{{"insurer_name": "Star Health", "sum_insured": 500000, "annual_premium": 12000, ...}}"""


def build_comparison_prompt(
    old_benefits: dict,
    new_benefits: dict,
    persona_context: str = "",
) -> str:
    """
    Build a prompt that compares old and new policy benefits and returns
    a structured porting recommendation.
    """
    old_json = json.dumps(old_benefits, indent=2)
    new_json = json.dumps(new_benefits, indent=2)

    persona_section = f"\nUser Profile: {persona_context}\n" if persona_context else ""

    return f"""You are an IRDAI-certified health insurance portability advisor in India.
{IRDAI_CONTEXT}
{persona_section}
Compare the following two health insurance policies and provide a portability recommendation.

OLD POLICY (current insurer):
{old_json}

NEW POLICY (target insurer):
{new_json}

Return a JSON object with:
- diffs: array of objects, each with:
  - field: string (benefit name)
  - old_value: string
  - new_value: string
  - change_type: "improved" | "degraded" | "unchanged" | "unknown"
  - notes: string (IRDAI-specific advice for this field)
- premium_delta: number (new_premium - old_premium, negative means cheaper)
- coverage_delta: number (new_sum_insured - old_sum_insured)
- waiting_period_risk: string (explanation of waiting period continuity)
- recommendation: string (2-3 sentence plain-English advice)
- cost_effective: boolean (true if porting is financially advisable)
- key_warnings: array of strings (important caveats the user must know)

Return only valid JSON."""


def build_chat_prompt(query: str, context: str, persona_context: str = "") -> str:
    """
    Build a conversational prompt grounded in retrieved policy chunks.
    """
    persona_section = f"User Profile: {persona_context}\n" if persona_context else ""

    return f"""You are an expert health insurance portability advisor for India.
{IRDAI_CONTEXT}
{persona_section}
Answer the user's question based ONLY on the policy document excerpts provided below.
If the answer is not in the provided context, say so clearly. Do not hallucinate policy terms.
Be concise, use plain English, and cite specific clauses when relevant.

Policy Document Excerpts:
{context}

User Question: {query}

Answer:"""


def build_system_prompt(persona_context: str = "") -> str:
    """
    Build the system-level prompt for multi-turn chat sessions.
    """
    persona_section = f"\nUser Profile Context: {persona_context}" if persona_context else ""
    return f"""You are an AI-powered health insurance portability advisor for India.
You help users understand their existing health insurance policy, compare it with potential new policies,
and make informed portability decisions under IRDAI guidelines.
{IRDAI_CONTEXT}
{persona_section}
Rules:
- Only answer based on the policy documents provided by the user.
- Always cite the specific benefit or clause when making claims.
- Flag any waiting period resets or coverage gaps the user might face.
- Be empathetic and use simple language — the user may not know insurance jargon.
- When unsure, say "Based on the document..." or "This is not clearly stated in your policy..."."""
