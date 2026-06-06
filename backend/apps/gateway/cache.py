"""Response caching for gateway requests."""
import hashlib
import json
import logging
import time

from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache TTL in seconds
CACHE_TTL = 300  # 5 minutes


def get_cache_key(request_body: dict) -> str:
    """Generate a cache key from request body.

    Only caches when:
    - temperature is 0 or not set (deterministic)
    - stream is False or not set
    """
    model = request_body.get("model", "")
    messages = request_body.get("messages", [])
    temperature = request_body.get("temperature", 0)
    stream = request_body.get("stream", False)

    # Don't cache streaming or high-temperature requests
    if stream or (temperature and temperature > 0):
        return None

    # Create hash from model + messages
    content = json.dumps({"model": model, "messages": messages}, sort_keys=True)
    return f"gw_cache:{hashlib.md5(content.encode()).hexdigest()}"


def get_cached_response(cache_key: str):
    """Get cached response if exists."""
    if not cache_key:
        return None
    return cache.get(cache_key)


def cache_response(cache_key: str, response_json: dict, ttl: int = CACHE_TTL):
    """Cache a response."""
    if not cache_key:
        return
    try:
        cache.set(cache_key, response_json, timeout=ttl)
    except Exception as e:
        logger.debug(f"Cache set failed: {e}")


def is_cache_disabled(request_headers) -> bool:
    """Check if caching is disabled via header."""
    return request_headers.get("HTTP_X_NO_CACHE", "").lower() in ("true", "1")
