import json
import logging

from django.http import StreamingHttpResponse, JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import ApiKey, LLMCallLog, Provider
from .services import proxy_chat_completion, proxy_embedding
from .cache import get_cache_key, get_cached_response, cache_response, is_cache_disabled
from .monitoring import record_request

logger = logging.getLogger(__name__)


def success_response(data=None, message="success"):
    return JsonResponse({"code": 0, "message": message, "data": data})


def error_response(code=1, message="error", status=400):
    return JsonResponse({"code": code, "message": message, "data": None}, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class GatewayChatView(View):
    """Proxy POST /api/gateway/v1/chat/completions"""

    def post(self, request):
        user_id = getattr(request, "api_user_id", None)
        api_key_id = getattr(request, "api_key_id", None)
        if not user_id:
            return error_response(code=401, message="未授权", status=401)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response(message="无效的 JSON 请求体", status=400)

        agent_id = request.headers.get("X-Agent-Id") or getattr(request, "api_key_agent_id", "")
        provider_name = request.headers.get("X-Provider")
        model = body.get("model", "")

        # Check response cache
        cache_key = get_cache_key(body)
        if cache_key and not is_cache_disabled(request.META):
            cached = get_cached_response(cache_key)
            if cached:
                resp = JsonResponse(cached)
                resp["X-Cache"] = "HIT"
                return resp

        # Smart routing with health check
        from .health import get_healthy_provider
        provider, max_tokens_limit = get_healthy_provider(user_id, model, provider_name)

        if not provider:
            return error_response(message="未找到可用的供应商，请先添加供应商", status=404)

        # Clamp max_tokens to model limit
        clamped = False
        if max_tokens_limit > 0:
            req_max_tokens = body.get("max_tokens")
            if req_max_tokens and req_max_tokens > max_tokens_limit:
                body["max_tokens"] = max_tokens_limit
                clamped = True

        try:
            result = proxy_chat_completion(
                user_id=user_id,
                api_key_id=api_key_id,
                provider=provider,
                request_body=body,
                agent_id=agent_id,
            )

            if isinstance(result, tuple) and len(result) == 4:
                resp_json, status_code, latency_ms, is_stream = result
                if is_stream:
                    return result  # StreamingHttpResponse
                # Cache successful non-streaming responses
                if status_code == 200 and cache_key:
                    cache_response(cache_key, resp_json)
                # Record metrics
                if provider:
                    record_request(provider.id, status_code)
                response = JsonResponse(resp_json, status=status_code)
                response["X-Cache"] = "MISS"
                if clamped:
                    response["X-Max-Tokens-Clamped"] = f"true (limit: {max_tokens_limit})"
                return response
            else:
                # Streaming httpx.Response
                resp, latency_ms = result
                return StreamingHttpResponse(
                    resp.iter_bytes(),
                    content_type=resp.headers.get("content-type", "text/event-stream"),
                    status=resp.status_code,
                )

        except Exception as e:
            logger.exception("Gateway proxy error")
            return error_response(message=f"代理请求失败: {e}", status=502)


@method_decorator(csrf_exempt, name='dispatch')
class GatewayEmbeddingView(View):
    """Proxy POST /api/gateway/v1/embeddings"""

    def post(self, request):
        user_id = getattr(request, "api_user_id", None)
        api_key_id = getattr(request, "api_key_id", None)
        if not user_id:
            return error_response(code=401, message="未授权", status=401)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response(message="无效的 JSON 请求体", status=400)

        agent_id = request.headers.get("X-Agent-Id")
        provider_name = request.headers.get("X-Provider")

        provider = Provider.objects.filter(user_id=user_id, status="active").first()
        if provider_name:
            provider = Provider.objects.filter(
                user_id=user_id, name=provider_name, status="active"
            ).first()

        if not provider:
            return error_response(message="未找到可用的供应商", status=404)

        try:
            resp_json, status_code, latency_ms, _ = proxy_embedding(
                user_id=user_id,
                api_key_id=api_key_id,
                provider=provider,
                request_body=body,
                agent_id=agent_id,
            )
            return JsonResponse(resp_json, status=status_code)
        except Exception as e:
            logger.exception("Gateway embedding proxy error")
            return error_response(message=f"代理请求失败: {e}", status=502)


@method_decorator(csrf_exempt, name='dispatch')
class GatewayModelsView(View):
    """GET /api/gateway/v1/models — list all models from all providers."""

    def get(self, request):
        user_id = getattr(request, "api_user_id", None)
        if not user_id:
            return error_response(code=401, message="未授权", status=401)

        allowed_models = getattr(request, "api_key_allowed_models", [])

        import httpx

        all_models = []
        providers = Provider.objects.filter(user_id=user_id, status="active")

        for provider in providers:
            try:
                url = f"{provider.base_url.rstrip('/')}/models"
                headers = {"Authorization": f"Bearer {provider.api_key}"}
                with httpx.Client(timeout=15.0) as client:
                    resp = client.get(url, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        models_list = data.get("data", data.get("models", []))
                        for m in models_list:
                            model_id = m.get("id") or m.get("name", "")
                            if model_id:
                                all_models.append({
                                    "id": model_id,
                                    "object": m.get("object", "model"),
                                    "owned_by": provider.name,
                                    "created": m.get("created", 0),
                                })
            except Exception as e:
                logger.warning(f"Failed to fetch models from {provider.name}: {e}")

        # Also add models from routing table
        from .models_routing import ModelRouting
        routing_models = ModelRouting.objects.filter(
            user_id=user_id, is_active=True
        ).select_related("provider")

        existing_ids = {m["id"] for m in all_models}
        for r in routing_models:
            if r.model_name not in existing_ids:
                all_models.append({
                    "id": r.model_name,
                    "object": "model",
                    "owned_by": r.provider.name,
                    "created": 0,
                })

        # Filter by allowed_models if set
        if allowed_models:
            all_models = [m for m in all_models if m["id"] in allowed_models]

        return JsonResponse({
            "object": "list",
            "data": all_models,
        })
