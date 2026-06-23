from __future__ import annotations

import hashlib
import json
import os
import random
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATASET_PATH = os.environ.get(
    "LINKEDIN_DATASET_PATH",
    "10k_data_li_india.txt/10k_data_li_india.txt",
)

# Map raw occupation keywords to insurance-relevant categories
OCCUPATION_CATEGORIES: dict[str, list[str]] = {
    "IT Professional": [
        "software", "engineer", "developer", "programmer", "analyst", "data",
        "sde", "swe", "architect", "devops", "cloud", "it ", "technology",
    ],
    "Banking & Finance": [
        "bank", "finance", "financial", "accountant", "ca ", "chartered",
        "investment", "equity", "credit", "loan", "insurance", "actuar",
    ],
    "Healthcare": [
        "doctor", "physician", "nurse", "medical", "hospital", "pharma",
        "clinical", "health", "dentist", "surgeon", "therapist",
    ],
    "Sales & Marketing": [
        "sales", "marketing", "business development", "bd ", "crm",
        "relationship manager", "account manager", "brand",
    ],
    "Self-Employed / Business": [
        "founder", "co-founder", "owner", "entrepreneur", "proprietor",
        "director", "ceo", "coo", "cto", "managing director",
    ],
    "Government & Public Sector": [
        "government", "ias", "ips", "upsc", "civil service", "public sector",
        "municipal", "railways", "defence", "army", "navy", "air force",
    ],
    "Education": [
        "teacher", "professor", "faculty", "lecturer", "principal",
        "education", "school", "college", "university",
    ],
    "Operations & Logistics": [
        "operations", "supply chain", "logistics", "warehouse", "procurement",
        "manager", "executive",
    ],
}

# Insurance advice tailored by occupation category
INSURANCE_PROFILES: dict[str, str] = {
    "IT Professional": (
        "Typically covered under employer group policy. Primary porting need arises on job change "
        "or when employer policy is inadequate. Prioritise: high sum insured, restoration benefit, "
        "OPD coverage if WFH. Consider top-up plans."
    ),
    "Banking & Finance": (
        "Often has employer group cover. High-stress occupation increases health risk. "
        "Prioritise: cardiac/critical illness cover, mental health benefits, higher room rent limit."
    ),
    "Healthcare": (
        "Needs individual policy independent of employer. Risk of occupational exposure. "
        "Prioritise: comprehensive hospitalization, professional indemnity linkage, no co-pay."
    ),
    "Sales & Marketing": (
        "Frequent travel increases accident risk. Likely needs individual policy. "
        "Prioritise: personal accident add-on, pan-India network hospitals, cashless facility."
    ),
    "Self-Employed / Business": (
        "No employer cover. Critical to have robust individual or family floater. "
        "Prioritise: high sum insured, maternity if applicable, restoration benefit, low co-pay."
    ),
    "Government & Public Sector": (
        "May have CGHS or ECHS cover. Porting need for supplementary private cover. "
        "Prioritise: top-up plans, OPD riders, dental and vision add-ons."
    ),
    "Education": (
        "Typically modest income; cost sensitivity high. "
        "Prioritise: affordable premium, good NCB, family floater plan, pre-existing disease cover."
    ),
    "Operations & Logistics": (
        "Physical work increases injury risk. "
        "Prioritise: accident cover, cashless hospitalization, wide network."
    ),
}


def _categorize_occupation(occupation: str) -> str:
    occ_lower = (occupation or "").lower()
    for category, keywords in OCCUPATION_CATEGORIES.items():
        if any(kw in occ_lower for kw in keywords):
            return category
    return "Operations & Logistics"


def _make_demo_scenario(full_name: str, occupation: str, city: str, category: str) -> str:
    insurers = [
        ("Star Health", "HDFC ERGO"),
        ("ICICI Lombard", "Bajaj Allianz"),
        ("Niva Bupa", "Care Health"),
        ("New India Assurance", "Aditya Birla Health"),
    ]
    old_insurer, new_insurer = random.choice(insurers)
    years = random.choice([2, 3, 4, 5])
    return (
        f"{full_name}, a {occupation} based in {city}, has been insured with {old_insurer} "
        f"for {years} years and is considering porting to {new_insurer}. "
        f"What waiting period credits will carry over and is this cost-effective?"
    )


def _stable_id(profile: dict) -> str:
    """Generate a stable ID from the profile's public identifier."""
    raw = profile.get("public_identifier", profile.get("full_name", "unknown"))
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _parse_profile(line: str) -> dict | None:
    """Parse a single JSONL line into a usable profile dict."""
    try:
        p = json.loads(line)
    except json.JSONDecodeError:
        return None

    full_name = p.get("full_name", "").strip()
    occupation = p.get("occupation", "").strip()
    city = (p.get("city") or "India").strip()
    state = (p.get("state") or "").strip()
    country = p.get("country_full_name", "india").lower()

    if country != "india" or not full_name or not occupation:
        return None

    return {
        "id": _stable_id(p),
        "full_name": full_name,
        "occupation": occupation,
        "city": city,
        "state": state,
    }


def load_personas(limit: int = 5, seed: int = 42) -> list[dict]:
    """
    Read the LinkedIn JSONL dataset and return `limit` diverse demo personas.
    Tries to return one persona per occupation category for variety.
    """
    dataset_path = Path(DATASET_PATH)
    if not dataset_path.exists():
        return _fallback_personas()

    random.seed(seed)
    seen_categories: set[str] = set()
    personas: list[dict] = []

    try:
        with open(dataset_path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if len(personas) >= limit and len(seen_categories) >= limit:
                    break
                line = line.strip()
                if not line:
                    continue

                profile = _parse_profile(line)
                if not profile:
                    continue

                category = _categorize_occupation(profile["occupation"])
                if category in seen_categories and len(personas) >= limit:
                    continue

                scenario = _make_demo_scenario(
                    profile["full_name"],
                    profile["occupation"],
                    profile["city"],
                    category,
                )
                personas.append(
                    {
                        "id": profile["id"],
                        "full_name": profile["full_name"],
                        "occupation": profile["occupation"],
                        "city": profile["city"],
                        "state": profile["state"],
                        "occupation_category": category,
                        "insurance_profile": INSURANCE_PROFILES.get(category, ""),
                        "demo_scenario": scenario,
                    }
                )
                seen_categories.add(category)

    except Exception:
        return _fallback_personas()

    if not personas:
        return _fallback_personas()

    return personas[:limit]


def get_persona_by_id(persona_id: str) -> dict | None:
    """Return a single persona matching the given ID."""
    for persona in load_personas(limit=50):
        if persona["id"] == persona_id:
            return persona
    return None


def get_persona_context(persona_id: str) -> str:
    """
    Return a short natural-language description of the persona for LLM injection.
    """
    persona = get_persona_by_id(persona_id)
    if not persona:
        return ""
    return (
        f"{persona['full_name']}, {persona['occupation']} from {persona['city']}, {persona['state']}. "
        f"Category: {persona['occupation_category']}. "
        f"Insurance considerations: {persona['insurance_profile']}"
    )


def _fallback_personas() -> list[dict]:
    """Hardcoded fallback personas when the dataset is unavailable."""
    return [
        {
            "id": "fallback-001",
            "full_name": "Priya Sharma",
            "occupation": "Software Engineer at Infosys",
            "city": "Bengaluru",
            "state": "Karnataka",
            "occupation_category": "IT Professional",
            "insurance_profile": INSURANCE_PROFILES["IT Professional"],
            "demo_scenario": (
                "Priya Sharma, a Software Engineer based in Bengaluru, has been insured with "
                "Star Health for 3 years and is considering porting to HDFC ERGO after switching jobs. "
                "What waiting period credits will carry over and is this cost-effective?"
            ),
        },
        {
            "id": "fallback-002",
            "full_name": "Rajesh Kumar",
            "occupation": "Founder at TechStart Ventures",
            "city": "Mumbai",
            "state": "Maharashtra",
            "occupation_category": "Self-Employed / Business",
            "insurance_profile": INSURANCE_PROFILES["Self-Employed / Business"],
            "demo_scenario": (
                "Rajesh Kumar, Founder of a Mumbai-based startup, needs to port from his previous "
                "employer's group policy to an individual Star Health policy. "
                "What benefits will he retain and what's the cost difference?"
            ),
        },
        {
            "id": "fallback-003",
            "full_name": "Anjali Mehta",
            "occupation": "Branch Manager at HDFC Bank",
            "city": "Delhi",
            "state": "Delhi",
            "occupation_category": "Banking & Finance",
            "insurance_profile": INSURANCE_PROFILES["Banking & Finance"],
            "demo_scenario": (
                "Anjali Mehta, Branch Manager at HDFC Bank in Delhi, has 4 years with ICICI Lombard "
                "and wants to switch to Bajaj Allianz for better cardiac coverage. "
                "Will her pre-existing disease waiting period reset?"
            ),
        },
        {
            "id": "fallback-004",
            "full_name": "Dr. Suresh Nair",
            "occupation": "General Physician at Apollo Hospitals",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "occupation_category": "Healthcare",
            "insurance_profile": INSURANCE_PROFILES["Healthcare"],
            "demo_scenario": (
                "Dr. Suresh Nair, a physician in Chennai with Niva Bupa for 2 years, "
                "wants to port to Care Health for better OPD coverage. "
                "What's the risk of porting after only 2 years?"
            ),
        },
        {
            "id": "fallback-005",
            "full_name": "Meena Verma",
            "occupation": "School Teacher at DAV Public School",
            "city": "Jaipur",
            "state": "Rajasthan",
            "occupation_category": "Education",
            "insurance_profile": INSURANCE_PROFILES["Education"],
            "demo_scenario": (
                "Meena Verma, a school teacher in Jaipur with New India Assurance for 5 years, "
                "wants to port to Aditya Birla Health for a family floater with maternity benefits. "
                "How much NCB can she carry over?"
            ),
        },
    ]
