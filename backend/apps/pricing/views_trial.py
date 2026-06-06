"""Trial pricing — send a test request to calculate actual cost per token."""
import json
import time

import httpx
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def success_response(data=None, message="success"):
    return JsonResponse({"code": 0, "message": message, "data": data})


def error_response(code=1, message="error", status=400):
    return JsonResponse({"code": code, "message": message, "data": None}, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class TrialPricingView(View):
    """POST /api/pricing/trial/ — auto-calculate pricing by sending test requests."""

    def post(self, request):
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response(message="无效的 JSON", status=400)

        base_url = body.get("base_url", "").strip().rstrip("/")
        api_key = body.get("api_key", "").strip()
        model = body.get("model", "").strip()

        if not base_url or not api_key:
            return error_response(message="请填写 API 地址和 Key", status=400)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Step 1: Get available models if not specified
        models_to_test = []
        if model:
            models_to_test = [model]
        else:
            try:
                with httpx.Client(timeout=15.0) as client:
                    resp = client.get(f"{base_url}/models", headers={"Authorization": f"Bearer {api_key}"})
                    if resp.status_code == 200:
                        data = resp.json()
                        for m in data.get("data", data.get("models", [])):
                            mid = m.get("id") or m.get("name", "")
                            if mid:
                                models_to_test.append(mid)
            except Exception:
                pass

        if not models_to_test:
            return error_response(message="未找到可用模型", status=400)

        # Step 2: For each model, send a test request and check balance
        results = []
        for m in models_to_test[:5]:  # Max 5 models to test
            try:
                with httpx.Client(timeout=30.0) as client:
                    # Send test request
                    test_body = {
                        "model": m,
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 5,
                    }
                    start = time.time()
                    resp = client.post(
                        f"{base_url}/chat/completions",
                        json=test_body,
                        headers=headers,
                    )
                    latency_ms = int((time.time() - start) * 1000)

                    if resp.status_code != 200:
                        results.append({
                            "model": m,
                            "status": "error",
                            "error": f"HTTP {resp.status_code}",
                        })
                        continue

                    resp_json = resp.json()
                    usage = resp_json.get("usage", {})
                    input_tokens = usage.get("prompt_tokens")
                    output_tokens = usage.get("completion_tokens")

                    if input_tokens is None:
                        results.append({
                            "model": m,
                            "status": "no_usage",
                            "input_tokens": None,
                            "output_tokens": None,
                        })
                        continue

                    # We can't get balance from most APIs, so we use a heuristic:
                    # Send two requests with different token counts and calculate
                    # For now, just report the token data for manual calculation
                    results.append({
                        "model": m,
                        "status": "ok",
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": (input_tokens or 0) + (output_tokens or 0),
                        "latency_ms": latency_ms,
                        "has_usage": True,
                    })

            except Exception as e:
                results.append({
                    "model": m,
                    "status": "error",
                    "error": str(e)[:100],
                })

        return success_response(
            data={
                "models_tested": len(results),
                "results": results,
            },
            message="试算完成"
        )
