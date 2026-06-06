"""Gateway monitoring — error rate tracking and alerts."""
import logging
import time

from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# Monitoring keys
METRIC_KEY_PREFIX = "gw_metric:"
ERROR_RATE_THRESHOLD = 0.5  # 50% error rate triggers alert


def record_request(provider_id: int, status_code: int):
    """Record a gateway request for monitoring."""
    minute = int(time.time() // 60)
    key = f"{METRIC_KEY_PREFIX}{provider_id}:{minute}"

    data = cache.get(key) or {"total": 0, "errors": 0}
    data["total"] += 1
    if status_code >= 400:
        data["errors"] += 1
    cache.set(key, data, timeout=300)  # Keep for 5 minutes


def get_error_rate(provider_id: int, window_minutes: int = 5) -> dict:
    """Get error rate for a provider over the last N minutes."""
    current_minute = int(time.time() // 60)
    total = 0
    errors = 0

    for i in range(window_minutes):
        minute = current_minute - i
        key = f"{METRIC_KEY_PREFIX}{provider_id}:{minute}"
        data = cache.get(key)
        if data:
            total += data["total"]
            errors += data["errors"]

    rate = errors / total if total > 0 else 0
    return {
        "total": total,
        "errors": errors,
        "rate": round(rate, 2),
        "healthy": rate < ERROR_RATE_THRESHOLD,
    }


def check_and_alert():
    """Check all providers error rates and send alerts if needed."""
    from apps.gateway.models import Provider

    alerts = []
    for p in Provider.objects.filter(status="active"):
        metrics = get_error_rate(p.id)
        if not metrics["healthy"] and metrics["total"] >= 5:
            alert = {
                "provider": p.name,
                "error_rate": f"{metrics['rate']:.0%}",
                "total_requests": metrics["total"],
                "errors": metrics["errors"],
            }
            alerts.append(alert)
            logger.warning(f"Gateway alert: {p.name} error rate {metrics['rate']:.0%}")

    return alerts


def get_all_metrics() -> dict:
    """Get metrics for all active providers."""
    from apps.gateway.models import Provider

    result = {}
    for p in Provider.objects.filter(status="active"):
        result[p.name] = get_error_rate(p.id)
    return result
