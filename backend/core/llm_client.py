from __future__ import annotations

import json
import os
from typing import Generator

from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-4o-mini")

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        if not api_key:
            raise EnvironmentError("OPENROUTER_API_KEY is not set in environment.")
        _client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/parthjha18/Port_Insurance",
                "X-Title": "Insurance Port Assistant",
            },
        )
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def complete(prompt: str, system: str = "") -> str:
    """
    Single-turn completion via GPT-4o mini on OpenRouter.
    Returns the assistant's text response.
    """
    client = _get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=2048,
    )
    return response.choices[0].message.content or ""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def complete_structured(prompt: str, system: str = "", response_schema: dict | None = None) -> dict:
    """
    Completion that expects a JSON response from the model.
    Uses response_format=json_object to ensure parseable output.
    Falls back to text extraction on JSON parse failure.
    """
    client = _get_client()
    messages = []

    base_system = (
        "You are an Indian health insurance portability expert. "
        "Always respond with valid JSON only. No explanations outside the JSON object."
    )
    combined_system = f"{base_system}\n\n{system}" if system else base_system

    messages.append({"role": "system", "content": combined_system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.0,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON substring
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
        return {"raw_response": raw}


def stream(prompt: str, system: str = "") -> Generator[str, None, None]:
    """
    Streaming completion — yields text chunks as they arrive.
    Used by the /chat endpoint for real-time responses.
    """
    client = _get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    with client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=2048,
        stream=True,
    ) as response_stream:
        for chunk in response_stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


def multi_turn_complete(messages: list[dict], system: str = "") -> str:
    """
    Multi-turn chat completion. Accepts a list of {role, content} dicts.
    """
    client = _get_client()
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=full_messages,
        temperature=0.1,
        max_tokens=2048,
    )
    return response.choices[0].message.content or ""
