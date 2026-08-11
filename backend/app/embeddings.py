"""Embeddings with Gemini primary + deterministic local fallback.

Why fallback: lets ingestion, retrieval and evals run without an API key
(local dev / CI). With GEMINI_API_KEY set, real `text-embedding-004`
(768-dim) vectors are used and stored in pgvector.
"""

import hashlib
import random

from .config import settings
from .models import EMBEDDING_DIM

_model_configured = False


def _ensure_gemini():
    global _model_configured
    if _model_configured:
        return True
    if not settings.gemini_api_key:
        return False
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        _model_configured = True
        return True
    except Exception as e:
        print(f"[embeddings] Gemini configure failed, using fallback: {e}")
        return False


def _fallback_vector(text: str) -> list[float]:
    """Deterministic pseudo-embedding: same text -> same vector."""
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    vec = [rng.gauss(0, 1) for _ in range(EMBEDDING_DIM)]
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if _ensure_gemini():
        try:
            import google.generativeai as genai

            result = genai.embed_content(
                model="models/text-embedding-004",
                content=texts,
                task_type="retrieval_document",
            )
            vectors = result["embedding"]
            # Single-text call returns one vector; batch returns list of vectors.
            if vectors and isinstance(vectors[0], float):
                return [list(vectors)]
            return [list(v) for v in vectors]
        except Exception as e:
            print(f"[embeddings] Gemini failed, fallback used: {e}")
    return [_fallback_vector(t) for t in texts]


def embed_query(text: str) -> list[float]:
    if _ensure_gemini():
        try:
            import google.generativeai as genai

            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_query",
            )
            return list(result["embedding"])
        except Exception as e:
            print(f"[embeddings] Gemini query embed failed, fallback: {e}")
    return _fallback_vector(text)
