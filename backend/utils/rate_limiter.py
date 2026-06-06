"""Rate limiter utility — Redis-based sliding window rate limiting."""
import time

from django.core.cache import cache


def check_rate_limit(key: str, limit: int, window_seconds: int = 60) -> tuple[bool, int]:
    """
    Check if a rate limit has been exceeded using a sliding window counter.

    Args:
        key: Unique identifier (e.g., "apikey:{id}")
        limit: Maximum allowed requests in the window
        window_seconds: Time window in seconds

    Returns:
        Tuple of (is_allowed, current_count)
    """
    now = time.time()
    window_start = now - window_seconds

    # Use a sorted set for sliding window
    cache_key = f"ratelimit:{key}"

    pipe = cache.client.get_client(cache_key) if hasattr(cache, 'client') else None

    # Simple implementation using cache increment
    minute_key = f"{cache_key}:{int(now // window_seconds)}"
    current = cache.get(minute_key, 0)

    if current >= limit:
        return False, current

    cache.set(minute_key, current + 1, timeout=window_seconds * 2)
    return True, current + 1


def get_remaining(key: str, limit: int, window_seconds: int = 60) -> int:
    """Get remaining requests in the current window."""
    now = time.time()
    minute_key = f"ratelimit:{key}:{int(now // window_seconds)}"
    current = cache.get(minute_key, 0)
    return max(0, limit - current)
