"""API Key verification, rate limiting, and model scope middleware for the gateway."""
import json
import logging
import time

from django.core.cache import cache
from django.db import models
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .models import ApiKey

logger = logging.getLogger(__name__)


def error_response(code=1, message="error", status=400):
    return JsonResponse({"code": code, "message": message, "data": None}, status=status)


def _check_budget(api_key_id: int, user_id: int) -> tuple:
    """Check if API key has exceeded its budget.

    Returns (is_over_budget, current_cost, threshold) tuple.
    Checks both key-level and user-level rules for all rule types.
    """
    try:
        from datetime import timedelta
        from django.db.models import Sum
        from django.utils import timezone
        from apps.alerts.models import BudgetRule
        from apps.gateway.models import LLMCallLog

        now = timezone.now()

        # Check all active rules (key-level and user-level)
        rules = BudgetRule.objects.filter(
            user_id=user_id,
            is_active=True,
        ).filter(
            # Either key-specific rules or user-level rules
            models.Q(api_key_id=api_key_id) | models.Q(api_key__isnull=True)
        )

        for rule in rules:
            # Determine time window
            if rule.rule_type == "daily":
                since = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif rule.rule_type == "monthly":
                since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:  # total
                since = timezone.datetime.min.replace(tzinfo=timezone.get_current_timezone())

            # Calculate cost based on scope
            cost_filter = {
                "user_id": user_id,
                "created_at__gte": since,
                "cost_yuan__isnull": False,
            }
            if rule.api_key_id:
                cost_filter["api_key_id"] = api_key_id

            total = LLMCallLog.objects.filter(**cost_filter).aggregate(
                total=Sum("cost_yuan")
            )["total"] or 0

            logger.info(
                "[BudgetCheck] key_id=%s user_id=%s rule=%s(%s) since=%s total=%s threshold=%s exceeded=%s",
                api_key_id, user_id, rule.id, rule.rule_type, since,
                total, rule.threshold_yuan, total > rule.threshold_yuan,
            )

            if total > rule.threshold_yuan:
                # Create in-app notification
                scope = f"Key {rule.api_key.name}" if rule.api_key_id else "全部 Key"
                _create_notification(
                    user_id=user_id,
                    title=f"预算超限: {rule.name}",
                    message=f"[{scope}] 当前消耗 ¥{float(total):.2f}，已超过阈值 ¥{float(rule.threshold_yuan):.2f}",
                    level="error",
                )
                # Record alert log
                _record_alert_log(user_id, rule, float(total))
                # Auto-disable if configured
                if rule.auto_disable and rule.api_key_id:
                    from apps.gateway.models import ApiKey
                    ApiKey.objects.filter(id=api_key_id, is_active=True).update(is_active=False)
                return True, float(total), float(rule.threshold_yuan)

        return False, 0, 0
    except Exception as e:
        logger.exception("[BudgetCheck] Error checking budget for key_id=%s user_id=%s: %s", api_key_id, user_id, e)
        return False, 0, 0


def _create_notification(user_id: int, title: str, message: str, level: str = "warning"):
    """Create an in-app notification. Deduplicates within 1 hour."""
    from django.core.cache import cache
    from apps.alerts.models import AlertNotification

    cache_key = f"notif:{user_id}:{title}"
    if cache.get(cache_key):
        return  # Already notified within the cache window

    AlertNotification.objects.create(
        user_id=user_id,
        title=title,
        message=message,
        level=level,
    )
    cache.set(cache_key, True, timeout=3600)  # 1 hour dedup


def _log_blocked_request(user_id: int, api_key_id: int, agent_id: str, request, current_cost: float, threshold: float):
    """Log a blocked request to LLMCallLog with status=403."""
    import json as _json
    from apps.gateway.models import LLMCallLog

    # Extract model from request body
    model = "unknown"
    try:
        body = _json.loads(request.body)
        model = body.get("model", "unknown")
    except Exception:
        pass

    LLMCallLog.objects.create(
        user_id=user_id,
        api_key_id=api_key_id,
        agent_id=agent_id or "",
        model=model,
        input_tokens_reported=0,
        output_tokens_reported=0,
        data_source="blocked",
        cost_yuan=0,
        latency_ms=0,
        status_code=403,
        is_error=True,
        error_message=f"预算超限: 当前 ¥{current_cost:.2f} > 阈值 ¥{threshold:.2f}",
    )


def _record_alert_log(user_id: int, rule, current_cost: float):
    """Record an alert trigger in AlertLog."""
    from django.core.cache import cache
    from apps.alerts.models import AlertLog

    cache_key = f"alert_log:{user_id}:{rule.id}"
    if cache.get(cache_key):
        return  # Already logged within the cache window

    AlertLog.objects.create(
        rule=rule,
        user_id=user_id,
        trigger_cost=current_cost,
        threshold=rule.threshold_yuan,
        channel=rule.alert_channel,
        send_status="sent",
    )
    cache.set(cache_key, True, timeout=3600)  # 1 hour dedup


class ApiKeyAuthMiddleware(MiddlewareMixin):
    """Validates the API key and checks model scope for gateway routes."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only apply to gateway paths
        if not request.path.startswith("/api/gateway/"):
            return None

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return error_response(code=401, message="缺少 API Key", status=401)

        raw_key = auth_header[7:]

        # Try JWT token first (for testing via frontend)
        if raw_key.count('.') == 2:
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                token = AccessToken(raw_key)
                user_id = token['user_id']
                request.api_user_id = user_id
                request.api_key_id = None
                request.api_key_allowed_models = []  # JWT = no restriction
                request.api_key_agent_id = ''
                request.api_key_agent_name = ''

                # Budget check for JWT requests (user-level rules only)
                if request.path != "/api/gateway/v1/models":
                    try:
                        budget_exceeded, current_cost, threshold = _check_budget(
                            api_key_id=0, user_id=user_id  # api_key_id=0 means no key-specific rules
                        )
                        if budget_exceeded:
                            return error_response(
                                code=403,
                                message=f"预算已超限: 当前 ¥{current_cost:.2f} > 阈值 ¥{threshold:.2f}。请提升预算或联系管理员。",
                                status=403,
                            )
                    except Exception as e:
                        logger.exception("[BudgetCheck] Error in JWT budget check: %s", e)

                return None
            except Exception:
                return error_response(code=401, message="无效的 JWT Token", status=401)

        # Platform API Key
        key_hash = ApiKey.hash_key(raw_key)

        # Try cache first
        cache_key = f"apikey:{key_hash}"
        key_data = cache.get(cache_key)

        if key_data is None:
            try:
                api_key = ApiKey.objects.select_related("user").get(
                    key_hash=key_hash, is_active=True
                )
                key_data = {
                    "id": api_key.id,
                    "user_id": api_key.user_id,
                    "rate_limit_rpm": api_key.rate_limit_rpm,
                    "permissions": api_key.permissions,
                    "allowed_models": api_key.allowed_models or [],
                    "agent_id": api_key.agent_id or '',
                    "agent_name": api_key.agent_name or '',
                }
                cache.set(cache_key, key_data, timeout=300)
            except ApiKey.DoesNotExist:
                return error_response(code=401, message="无效的 API Key", status=401)

        # Check expiration and active status
        try:
            api_key = ApiKey.objects.get(id=key_data["id"])
            if not api_key.is_active:
                cache.delete(cache_key)
                return error_response(code=401, message="API Key 已被禁用", status=401)
            if api_key.expires_at and api_key.expires_at < __import__("django.utils.timezone", fromlist=["now"]).now():
                cache.delete(cache_key)
                return error_response(code=401, message="API Key 已过期", status=401)
        except ApiKey.DoesNotExist:
            cache.delete(cache_key)
            return error_response(code=401, message="API Key 不存在", status=401)

        # Rate limiting (sliding window per minute)
        rate_key = f"rate:{key_data['id']}:{int(time.time() // 60)}"
        current_count = cache.get(rate_key, 0)
        if current_count >= key_data["rate_limit_rpm"]:
            return error_response(
                code=429,
                message=f"请求过于频繁，限制 {key_data['rate_limit_rpm']} 次/分钟",
                status=429,
            )
        cache.set(rate_key, current_count + 1, timeout=120)

        # Model scope check (for chat/embeddings endpoints)
        allowed_models = key_data.get("allowed_models", [])
        if allowed_models and request.path != "/api/gateway/v1/models":
            # Extract model from request body
            try:
                body = json.loads(request.body)
                model = body.get("model", "")
                if model and model not in allowed_models:
                    return error_response(
                        code=403,
                        message=f"该 Agent 无权使用模型「{model}」，可用模型: {', '.join(allowed_models[:5])}{'...' if len(allowed_models) > 5 else ''}",
                        status=403,
                    )
            except (json.JSONDecodeError, Exception):
                pass  # Let the view handle bad JSON

        # Budget check (synchronous, no Celery needed)
        if request.path != "/api/gateway/v1/models":
            budget_exceeded, current_cost, threshold = _check_budget(
                key_data["id"], key_data["user_id"]
            )
            if budget_exceeded:
                # Log the blocked request
                _log_blocked_request(
                    user_id=key_data["user_id"],
                    api_key_id=key_data["id"],
                    agent_id=key_data.get("agent_id", ""),
                    request=request,
                    current_cost=current_cost,
                    threshold=threshold,
                )
                return error_response(
                    code=403,
                    message=f"API Key 预算已超限: 当前 ¥{current_cost:.2f} > 阈值 ¥{threshold:.2f}。请提升预算或联系管理员。",
                    status=403,
                )

        # Attach to request
        request.api_key_id = key_data["id"]
        request.api_user_id = key_data["user_id"]
        request.api_key_allowed_models = allowed_models
        request.api_key_agent_id = key_data.get("agent_id", "")
        request.api_key_agent_name = key_data.get("agent_name", "")

        # Update last_used_at (throttled to avoid hammering DB)
        last_used_key = f"last_used:{key_data['id']}"
        if not cache.get(last_used_key):
            ApiKey.objects.filter(id=key_data["id"]).update(
                last_used_at=__import__("django.utils.timezone", fromlist=["now"]).now()
            )
            cache.set(last_used_key, True, timeout=60)

        return None
