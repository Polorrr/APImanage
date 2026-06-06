"""Provider health check service."""
import logging
from datetime import timedelta

import httpx
from django.utils import timezone

logger = logging.getLogger(__name__)


def check_provider_health(provider) -> dict:
    """Check if a provider's API is reachable and responding.

    Returns:
        dict with keys: status, latency_ms, error
    """
    result = {"status": "unknown", "latency_ms": None, "error": None}

    base_url = provider.base_url.rstrip("/")
    headers = {"Authorization": f"Bearer {provider.api_key}"}

    try:
        with httpx.Client(timeout=15.0) as client:
            import time
            start = time.monotonic()

            # Try /models endpoint (standard OpenAI format)
            # Try with and without /v1 prefix
            test_urls = [f"{base_url}/models", f"{base_url}/v1/models"]
            for test_url in test_urls:
                try:
                    resp = client.get(test_url, headers=headers)
                    latency_ms = int((time.monotonic() - start) * 1000)
                    result["latency_ms"] = latency_ms

                    if resp.status_code in (200, 401, 403):
                        result["status"] = "healthy"
                        return result
                except Exception:
                    continue

            result["status"] = "unhealthy"
            result["error"] = f"所有检测端点不可达"

    except Exception as e:
        result["status"] = "unhealthy"
        result["error"] = str(e)[:200]

    return result


def get_healthy_provider(user_id: int, model: str = "", provider_name: str = ""):
    """Find a healthy provider for the given user/model.

    Returns (provider, max_tokens) tuple or (None, 0).
    """
    from apps.gateway.models import Provider
    from apps.gateway.models_routing import ModelRouting

    # 1. If provider name specified, try that first
    if provider_name:
        provider = Provider.objects.filter(
            user_id=user_id, name=provider_name, status="active"
        ).first()
        if provider:
            return provider, 0

    # 2. Smart routing: find provider by model name
    if model:
        result = ModelRouting.find_provider(user_id, model)
        if result and result[0]:
            provider, max_tokens = result
            # Check if this provider is healthy
            if provider.health_status != "unhealthy":
                return provider, max_tokens
            # If unhealthy, try other providers for same model
            other_routings = ModelRouting.objects.filter(
                user_id=user_id, model_name=model, is_active=True
            ).select_related("provider").order_by("priority")
            for r in other_routings:
                if r.provider.id != provider.id and r.provider.status == "active" and r.provider.health_status != "unhealthy":
                    return r.provider, r.max_tokens
            # All unhealthy, return the best one anyway
            return provider, max_tokens

    # 3. Fallback: first active provider
    provider = Provider.objects.filter(user_id=user_id, status="active").first()
    return provider, 0


def check_all_providers(user_id: int) -> list:
    """Check health of all providers for a user."""
    from apps.gateway.models import Provider

    providers = Provider.objects.filter(user_id=user_id)
    results = []

    for provider in providers:
        if provider.status != "active":
            continue

        health = check_provider_health(provider)

        # Update provider health status
        provider.health_status = health["status"]
        provider.last_health_check = timezone.now()
        provider.save(update_fields=[
            "health_status", "last_health_check"
        ])

        results.append({
            "provider_id": provider.id,
            "name": provider.name,
            "status": health["status"],
            "latency_ms": health["latency_ms"],
            "error": health["error"],
        })

    return results
