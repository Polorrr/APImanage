"""Gateway service — proxy requests to upstream LLM APIs and record logs."""
import asyncio
import json
import logging
import time

import httpx
from django.utils import timezone

from apps.pricing.models import ModelPricing
from utils.cost_calculator import calculate_cost
from utils.token_counter import estimate_tokens

logger = logging.getLogger(__name__)


def get_provider_for_request(user_id: int, model: str, provider_name: str | None = None):
    """Find the appropriate provider for a given model/request."""
    from apps.gateway.models import Provider

    qs = Provider.objects.filter(user_id=user_id, status="active")
    if provider_name:
        qs = qs.filter(name=provider_name)
    return qs.first()


def proxy_chat_completion(
    user_id: int,
    api_key_id: int,
    provider,
    request_body: dict,
    agent_id: str | None = None,
):
    """
    Forward a chat completion request to the upstream provider.
    Returns (response_json, status_code, latency_ms, is_stream).
    """
    model = request_body.get("model", "unknown")
    is_stream = request_body.get("stream", False)

    # Ensure stream is explicitly set (some providers like ModelScope need this)
    if "stream" not in request_body:
        request_body["stream"] = False

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {provider.api_key}",
    }

    url = f"{provider.base_url.rstrip('/')}/chat/completions"
    start_time = time.monotonic()

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, json=request_body, headers=headers)
            latency_ms = int((time.monotonic() - start_time) * 1000)

            if is_stream:
                # For streaming, we return the raw response for streaming back
                return resp, latency_ms

            resp_json = resp.json()
            status_code = resp.status_code

            # Handle null/empty response
            if resp_json is None:
                resp_json = {"choices": [], "usage": {}}
            if not isinstance(resp_json, dict):
                resp_json = {"choices": [], "usage": {}}

            # Handle empty choices (some providers return null)
            if resp_json.get("choices") is None:
                resp_json["choices"] = []

            # Extract token usage
            usage = resp_json.get("usage") or {}
            if not isinstance(usage, dict):
                usage = {}
            input_tokens_reported = usage.get("prompt_tokens")
            output_tokens_reported = usage.get("completion_tokens")

            # Extract cached tokens
            prompt_details = usage.get("prompt_tokens_details") or {}
            if not isinstance(prompt_details, dict):
                prompt_details = {}
            cached_tokens = prompt_details.get("cached_tokens", 0) or 0
            uncached_tokens = (input_tokens_reported or 0) - cached_tokens

            # If no usage reported, estimate locally
            data_source = "provider"
            input_tokens_estimated = None
            output_tokens_estimated = None

            if input_tokens_reported is None:
                data_source = "estimated"
                input_tokens_estimated = estimate_tokens(
                    model, json.dumps(request_body.get("messages", []))
                )
                output_tokens_estimated = 0
                choices = resp_json.get("choices", [])
                if choices:
                    output_text = choices[0].get("message", {}).get("content", "")
                    output_tokens_estimated = estimate_tokens(model, output_text)

            # Calculate cost (with cache hit/miss pricing)
            cost_yuan = None
            input_for_cost = input_tokens_reported or input_tokens_estimated or 0
            output_for_cost = output_tokens_reported or output_tokens_estimated or 0

            pricing = ModelPricing.find_for_model(model, user_id)
            if pricing:
                cached_price = float(getattr(pricing, 'input_price_cached', 0) or 0)
                uncached_price = float(pricing.input_price)
                output_price = float(pricing.output_price)

                if cached_tokens > 0 and cached_price > 0:
                    # Split pricing: cached + uncached + output
                    cost_yuan = round(
                        cached_tokens * cached_price / 1000
                        + uncached_tokens * uncached_price / 1000
                        + output_for_cost * output_price / 1000,
                        6
                    )
                else:
                    cost_yuan = calculate_cost(
                        input_for_cost, output_for_cost,
                        uncached_price, output_price,
                    )

            # Record the call log asynchronously
            _record_log_async(
                user_id=user_id,
                api_key_id=api_key_id,
                provider_id=provider.id,
                agent_id=agent_id,
                model=model,
                input_tokens_reported=input_tokens_reported,
                output_tokens_reported=output_tokens_reported,
                input_tokens_estimated=input_tokens_estimated,
                output_tokens_estimated=output_tokens_estimated,
                data_source=data_source,
                cost_yuan=cost_yuan,
                latency_ms=latency_ms,
                status_code=status_code,
                is_error=status_code >= 400,
                error_message=resp.text if status_code >= 400 else None,
            )

            return resp_json, status_code, latency_ms, False

    except httpx.TimeoutException:
        latency_ms = int((time.monotonic() - start_time) * 1000)
        _record_log_async(
            user_id=user_id,
            api_key_id=api_key_id,
            provider_id=provider.id if provider else None,
            agent_id=agent_id,
            model=model,
            data_source="estimated",
            latency_ms=latency_ms,
            status_code=504,
            is_error=True,
            error_message="请求上游超时",
        )
        raise
    except Exception as e:
        latency_ms = int((time.monotonic() - start_time) * 1000)
        _record_log_async(
            user_id=user_id,
            api_key_id=api_key_id,
            provider_id=provider.id if provider else None,
            agent_id=agent_id,
            model=model,
            data_source="estimated",
            latency_ms=latency_ms,
            status_code=500,
            is_error=True,
            error_message=str(e),
        )
        raise


def proxy_embedding(
    user_id: int,
    api_key_id: int,
    provider,
    request_body: dict,
    agent_id: str | None = None,
):
    """Forward an embedding request to the upstream provider."""
    model = request_body.get("model", "unknown")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {provider.api_key}",
    }

    url = f"{provider.base_url.rstrip('/')}/embeddings"
    start_time = time.monotonic()

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=request_body, headers=headers)
            latency_ms = int((time.monotonic() - start_time) * 1000)
            resp_json = resp.json()
            status_code = resp.status_code

            usage = resp_json.get("usage", {})
            input_tokens_reported = usage.get("prompt_tokens")

            data_source = "provider"
            input_tokens_estimated = None
            if input_tokens_reported is None:
                data_source = "estimated"
                input_tokens_estimated = estimate_tokens(
                    model, json.dumps(request_body.get("input", ""))
                )

            cost_yuan = None
            input_for_cost = input_tokens_reported or input_tokens_estimated or 0

            pricing = ModelPricing.find_for_model(model, user_id)
            if pricing:
                cost_yuan = calculate_cost(
                    input_for_cost, 0,
                    float(pricing.input_price), float(pricing.output_price),
                )

            _record_log_async(
                user_id=user_id,
                api_key_id=api_key_id,
                provider_id=provider.id,
                agent_id=agent_id,
                model=model,
                input_tokens_reported=input_tokens_reported,
                input_tokens_estimated=input_tokens_estimated,
                data_source=data_source,
                cost_yuan=cost_yuan,
                latency_ms=latency_ms,
                status_code=status_code,
                is_error=status_code >= 400,
            )

            return resp_json, status_code, latency_ms, False
    except Exception as e:
        latency_ms = int((time.monotonic() - start_time) * 1000)
        _record_log_async(
            user_id=user_id,
            api_key_id=api_key_id,
            provider_id=provider.id if provider else None,
            agent_id=agent_id,
            model=model,
            data_source="estimated",
            latency_ms=latency_ms,
            status_code=500,
            is_error=True,
            error_message=str(e),
        )
        raise


def _record_log_async(**kwargs):
    """Write call log to DB. Uses sync call for simplicity; can be replaced with Celery task."""
    from apps.gateway.models import LLMCallLog

    try:
        LLMCallLog.objects.create(**kwargs)
    except Exception:
        logger.exception("Failed to record LLM call log")
