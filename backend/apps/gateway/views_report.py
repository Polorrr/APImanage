"""SDK report endpoint — receives batched usage data from aimanage SDK."""
import json
import logging
from decimal import Decimal

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.gateway.models import ApiKey, LLMCallLog, Provider
from apps.pricing.models import ModelPricing

logger = logging.getLogger(__name__)


def success_response(data=None, message="success"):
    return JsonResponse({"code": 0, "message": message, "data": data})


def error_response(code=1, message="error", status=400):
    return JsonResponse({"code": code, "message": message, "data": None}, status=status)


def match_price(model_name: str) -> tuple:
    """Match model to pricing. Returns (input_price, output_price) or (None, None)."""
    pricing = ModelPricing.objects.filter(
        model_keyword__icontains=model_name, is_builtin=True
    ).first()
    if pricing:
        return float(pricing.input_price), float(pricing.output_price)

    # Try user custom pricing
    pricing = ModelPricing.objects.filter(
        model_keyword__icontains=model_name, is_builtin=False
    ).first()
    if pricing:
        return float(pricing.input_price), float(pricing.output_price)

    return None, None


def calculate_cost(input_tokens, output_tokens, input_price, output_price):
    """Calculate cost in yuan."""
    if input_price is None or output_price is None:
        return None
    cost = (input_tokens or 0) * input_price / 1000 + (output_tokens or 0) * output_price / 1000
    return round(cost, 6)


@method_decorator(csrf_exempt, name='dispatch')
class SDKReportView(View):
    """POST /api/v1/report/ — receive batched usage data from SDK."""

    def post(self, request):
        # Extract API key from Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return error_response(code=401, message="缺少 API Key", status=401)

        raw_key = auth_header[7:]
        key_hash = ApiKey.hash_key(raw_key)

        try:
            api_key = ApiKey.objects.select_related("user").get(key_hash=key_hash, is_active=True)
        except ApiKey.DoesNotExist:
            return error_response(code=401, message="无效的 API Key", status=401)

        # Parse request body
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response(message="无效的 JSON", status=400)

        records = body.get("records", [])
        if not records:
            return error_response(message="records 为空", status=400)

        project = body.get("project", "")
        accepted = 0

        for record in records:
            model = record.get("model", "unknown")
            input_tokens = record.get("input_tokens")
            output_tokens = record.get("output_tokens")

            # Match pricing
            input_price, output_price = match_price(model)
            cost = calculate_cost(input_tokens, output_tokens, input_price, output_price)

            # Find default provider (if any)
            provider = Provider.objects.filter(user=api_key.user, status="active").first()

            try:
                LLMCallLog.objects.create(
                    user=api_key.user,
                    api_key=api_key,
                    provider=provider,
                    agent_id=record.get("agent_id") or project or None,
                    model=model,
                    input_tokens_reported=input_tokens,
                    output_tokens_reported=output_tokens,
                    data_source="sdk",
                    cost_yuan=cost,
                    latency_ms=record.get("latency_ms"),
                    status_code=record.get("status_code"),
                    is_error=record.get("is_error", False),
                    error_message=record.get("error_message"),
                )
                accepted += 1
            except Exception as e:
                logger.warning(f"Failed to save record: {e}")

        return success_response(
            data={"accepted": accepted, "total": len(records)},
            message=f"已接收 {accepted}/{len(records)} 条记录"
        )
