"""Embeddings with Gemini primary + deterministic local fallback.

Why fallback: lets ingestion, retrieval and evals run without an API key
(local dev / CI). With GEMINI_API_KEY set, real `text-embedding-004`
(768-dim) vectors are used and stored in pgvector.
"""

import hashlib
import random

from . import cache
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


def _raw_embed(texts: list[str], task_type: str) -> list[list[float]] | None:
    """Real Gemini call. None when unconfigured/failed (caller uses fallback)."""
    if not _ensure_gemini():
        return None
    try:
        import google.generativeai as genai

        result = genai.embed_content(
            model="models/text-embedding-004",
            content=texts,
            task_type=task_type,
        )
        vectors = result["embedding"]
        if vectors and isinstance(vectors[0], float):
            return [list(vectors)]
        return [list(v) for v in vectors]
    except Exception as e:
        print(f"[embeddings] Gemini failed, fallback used: {e}")
        return None


def _cached_vectors(texts: list[str], task_type: str) -> list[list[float]]:
    """Redis-cached embeddings: cache hit avoids a paid embedding call."""
    out: list[list[float]] = []
    missing: list[int] = []
    for i, t in enumerate(texts):
        key = f"emb:v1:{cache.sha_key(task_type, t)}"
        hit = cache.cache_get_json(key)
        if isinstance(hit, list) and len(hit) == EMBEDDING_DIM:
            out.append(hit)
        else:
            out.append([])  # placeholder
            missing.append(i)
    if missing:
        fresh = _raw_embed([texts[i] for i in missing], task_type)
        for pos, i in enumerate(missing):
            vec = fresh[pos] if fresh else _fallback_vector(texts[i])
            out[i] = vec
            # Cache only real API vectors under a key; fallback is free
            # to recompute, but caching it is harmless and faster.
            try:
                cache.cache_set_json(
                    f"emb:v1:{cache.sha_key(task_type, texts[i])}",
                    vec,
                    settings.embedding_cache_ttl_s,
                )
            except Exception:
                pass
    return out


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return _cached_vectors(texts, "retrieval_document")


def embed_query(text: str) -> list[float]:
    return _cached_vectors([text], "retrieval_query")[0]
