"""Redis helpers: safe get/set with graceful degradation.

Every helper returns a fallback value when Redis is unreachable so the API
keeps serving (degraded) instead of 500ing — same pattern as /health.
"""

import hashlib
import json

from .config import settings

try:
    import redis
except ImportError:  # local dev without deps; Docker image always has it
    redis = None  # type: ignore[assignment]

_client = None


def get_client():
    global _client
    if _client is not None:
        return _client
    if redis is None:
        return None
    try:
        _client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        _client.ping()
        return _client
    except Exception as e:
        print(f"[cache] redis unavailable: {e}")
        return None


def sha_key(*parts: str) -> str:
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return h


def cache_get(key: str) -> str | None:
    client = get_client()
    if not client:
        return None
    try:
        val = client.get(key)
        return val.decode("utf-8") if isinstance(val, bytes) else val
    except Exception:
        return None


def cache_set(key: str, value: str, ttl_s: int) -> None:
    client = get_client()
    if not client:
        return
    try:
        client.setex(key, ttl_s, value)
    except Exception as e:
        print(f"[cache] set failed: {e}")


def cache_get_json(key: str) -> dict | list | None:
    raw = cache_get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def cache_set_json(key: str, obj: dict | list, ttl_s: int) -> None:
    cache_set(key, json.dumps(obj), ttl_s)
