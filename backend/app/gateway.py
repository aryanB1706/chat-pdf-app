"""Model gateway: primary LLM with fallback to secondary on errors/timeouts.

Returns (text, model_used, fallback_used, latency_ms) so every request can
be logged per the "token/latency logging" requirement. Raises when no API
key is configured — callers use their extractive fallback in that case.
"""

import re
import time

from .config import settings


def _call_gemini(model_name: str, prompt: str) -> str:
    import google.generativeai as genai

    if not getattr(_call_gemini, "_configured", False):
        genai.configure(api_key=settings.gemini_api_key)
        _call_gemini._configured = True  # type: ignore[attr-defined]
    model = genai.GenerativeModel(model_name)
    resp = model.generate_content(
        prompt, request_options={"timeout": settings.llm_timeout_s}
    )
    return resp.text.strip()


def generate(prompt: str) -> tuple[str, str, bool, float]:
    """Try primary, fall back to secondary. Returns (text, model, fallback, ms)."""
    if not settings.gemini_api_key:
        raise RuntimeError("no GEMINI_API_KEY configured")

    start = time.perf_counter()
    try:
        text = _call_gemini(settings.primary_llm_model, prompt)
        ms = (time.perf_counter() - start) * 1000
        return text, settings.primary_llm_model, False, ms
    except Exception as primary_err:
        print(f"[gateway] primary {settings.primary_llm_model} failed: {primary_err}")

    start2 = time.perf_counter()
    text = _call_gemini(settings.secondary_llm_model, prompt)
    ms = (time.perf_counter() - start + time.perf_counter() - start2) * 1000
    return text, settings.secondary_llm_model, True, ms


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token) for cost logging."""
    return max(len(text) // 4, 1)


def generate_json(prompt: str):
    """Gateway generate + strict JSON parse (strips markdown fences)."""
    import json as _json

    text, model_used, fallback_used, ms = generate(prompt)
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return _json.loads(cleaned), model_used, fallback_used, ms


def generate_vision(prompt: str, image_bytes: bytes, mime: str = "image/png") -> tuple[str, str, bool, float]:
    """Vision call with primary→secondary fallback. Returns like generate()."""
    import time as _time

    if not settings.gemini_api_key:
        raise RuntimeError("no GEMINI_API_KEY configured")

    def _call(model_name: str) -> str:
        import google.generativeai as genai

        if not getattr(_call, "_configured", False):
            genai.configure(api_key=settings.gemini_api_key)
            _call._configured = True  # type: ignore[attr-defined]
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(
            [{"mime_type": mime, "data": image_bytes}, prompt],
            request_options={"timeout": settings.llm_timeout_s},
        )
        return resp.text.strip()

    start = _time.perf_counter()
    try:
        text = _call(settings.primary_llm_model)
        return text, settings.primary_llm_model, False, (_time.perf_counter() - start) * 1000
    except Exception as primary_err:
        print(f"[gateway] vision primary failed: {primary_err}")
    text = _call(settings.secondary_llm_model)
    return text, settings.secondary_llm_model, True, (_time.perf_counter() - start) * 1000
