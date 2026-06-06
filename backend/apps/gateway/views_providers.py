import json

import httpx
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pricing.models import ModelPricing
from .models import Provider
from .models_routing import ModelRouting
from .serializers import ProviderCreateSerializer, ProviderSerializer


def success_response(data=None, message="success"):
    return Response({"code": 0, "message": message, "data": data})


class ProviderListCreateView(generics.ListCreateAPIView):
    serializer_class = ProviderCreateSerializer

    def get_queryset(self):
        return Provider.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProviderCreateSerializer
        return ProviderSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = ProviderSerializer(qs, many=True)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.save(user=request.user)
        return success_response(data=ProviderSerializer(provider).data, message="供应商添加成功")


class ProviderDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProviderCreateSerializer

    def get_queryset(self):
        return Provider.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProviderCreateSerializer
        return ProviderSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=ProviderSerializer(instance).data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="已删除")


class ProviderDetectView(APIView):
    """POST /api/providers/{id}/detect/ — auto-detect provider capabilities."""

    def post(self, request, pk):
        try:
            provider = Provider.objects.get(id=pk, user=request.user)
        except Provider.DoesNotExist:
            return Response(
                {"code": 1, "message": "供应商不存在", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        base_url = provider.base_url.rstrip("/")
        api_key = provider.api_key

        headers = {"Authorization": f"Bearer {api_key}"}
        detect_result = {
            "api_ok": False,
            "models": [],
            "has_usage": False,
            "pricing": [],
        }

        # Step 1: Try to list models
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(f"{base_url}/models", headers=headers)
                if resp.status_code == 200:
                    detect_result["api_ok"] = True
                    data = resp.json()
                    models_list = data.get("data", data.get("models", []))
                    for m in models_list:
                        model_id = m.get("id") or m.get("name", "")
                        if model_id:
                            detect_result["models"].append(model_id)
        except Exception:
            pass

        # Step 2: Test a small request to check if usage is reported
        test_model = detect_result["models"][0] if detect_result["models"] else None
        if test_model:
            try:
                with httpx.Client(timeout=30.0) as client:
                    test_body = {
                        "model": test_model,
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 1,
                    }
                    resp = client.post(
                        f"{base_url}/chat/completions",
                        json=test_body,
                        headers={**headers, "Content-Type": "application/json"},
                    )
                    if resp.status_code == 200:
                        resp_json = resp.json()
                        usage = resp_json.get("usage", {})
                        if usage.get("prompt_tokens") is not None:
                            detect_result["has_usage"] = True

                        # Match pricing
                        for model_id in detect_result["models"]:
                            pricing_match = ModelPricing.objects.filter(
                                model_keyword__icontains=model_id,
                                is_builtin=True,
                            ).first()
                            if pricing_match:
                                detect_result["pricing"].append({
                                    "model": model_id,
                                    "input_price": str(pricing_match.input_price),
                                    "output_price": str(pricing_match.output_price),
                                    "status": "matched",
                                })
                            else:
                                detect_result["pricing"].append({
                                    "model": model_id,
                                    "input_price": None,
                                    "output_price": None,
                                    "status": "manual",
                                })
            except Exception:
                pass

        # Save detection result
        provider.detect_result = detect_result
        provider.save(update_fields=["detect_result"])

        # Auto-create routing entries for detected models
        routing_created = 0
        for model_id in detect_result["models"]:
            _, created = ModelRouting.objects.get_or_create(
                user=request.user,
                model_name=model_id,
                defaults={"provider": provider, "is_active": True},
            )
            if created:
                routing_created += 1

        detect_result["routing_created"] = routing_created

        return success_response(data=detect_result, message="检测完成")


class StandaloneDetectView(APIView):
    """POST /api/detect/ — detect API capabilities with base_url + api_key directly.

    Auto-creates provider + routing entries for discovered models.
    """

    def post(self, request):
        base_url = request.data.get("base_url", "").strip()
        api_key = request.data.get("api_key", "").strip()
        name = request.data.get("name", "").strip()

        if not base_url or not api_key:
            return Response(
                {"code": 1, "message": "请填写 API 地址和 Key", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        base_url = base_url.rstrip("/")
        headers = {"Authorization": f"Bearer {api_key}"}

        api_connected = False
        models_found = []
        token_mode = "estimated"
        matched_prices = []

        # Step 1: Try to list models
        test_urls = [f"{base_url}/models", f"{base_url}/v1/models"]
        for test_url in test_urls:
            try:
                with httpx.Client(timeout=15.0) as client:
                    resp = client.get(test_url, headers=headers)
                    if resp.status_code == 200:
                        api_connected = True
                        data = resp.json()
                        models_list = data.get("data", data.get("models", []))
                        for m in models_list:
                            model_id = m.get("id") or m.get("name", "")
                            if model_id:
                                models_found.append(model_id)
                        break
            except Exception:
                continue

        # Step 2: Test a small request to check if usage is reported
        test_model = models_found[0] if models_found else None
        if test_model:
            try:
                with httpx.Client(timeout=30.0) as client:
                    test_body = {
                        "model": test_model,
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 1,
                    }
                    resp = client.post(
                        f"{base_url}/chat/completions",
                        json=test_body,
                        headers={**headers, "Content-Type": "application/json"},
                    )
                    if resp.status_code != 200:
                        # Try with /v1 prefix
                        base_url_alt = base_url
                        if "/v1" not in base_url:
                            base_url_alt = f"{base_url}/v1"
                        resp = client.post(
                            f"{base_url_alt}/chat/completions",
                            json=test_body,
                            headers={**headers, "Content-Type": "application/json"},
                        )
                    if resp.status_code == 200:
                        resp_json = resp.json()
                        usage = resp_json.get("usage", {})
                        if usage.get("prompt_tokens") is not None:
                            token_mode = "provider"
            except Exception:
                pass

        # Step 3: Match pricing
        for model_id in models_found:
            pricing_match = ModelPricing.objects.filter(
                model_keyword__icontains=model_id,
                is_builtin=True,
            ).first()
            if pricing_match:
                matched_prices.append({
                    "model": model_id,
                    "input_price": float(pricing_match.input_price),
                    "output_price": float(pricing_match.output_price),
                    "status": "matched",
                })
            else:
                matched_prices.append({
                    "model": model_id,
                    "input_price": None,
                    "output_price": None,
                    "status": "manual",
                })

        # Step 4: Auto-create provider + routing
        provider_created = False
        routing_created = 0
        provider_id = None
        provider_name = name

        if api_connected and models_found:
            # Determine provider name
            if not provider_name:
                if "xiaomi" in base_url.lower() or "mimo" in base_url.lower():
                    provider_name = "小米"
                elif "modelscope" in base_url.lower():
                    provider_name = "ModelScope"
                elif "deepseek" in base_url.lower():
                    provider_name = "DeepSeek"
                elif "openai" in base_url.lower():
                    provider_name = "OpenAI"
                else:
                    provider_name = f"Provider-{base_url.split('/')[2][:20]}"

            # Determine model prefix
            model_prefix = ""
            if models_found:
                first = models_found[0]
                if "/" in first:
                    model_prefix = first.rsplit("/", 1)[0] + "/"
                elif "-" in first:
                    model_prefix = first.split("-")[0] + "-"

            # Check if provider already exists
            existing = Provider.objects.filter(
                user=request.user, base_url__icontains=base_url.split("//")[1].split("/")[0]
            ).first()

            if not existing:
                provider = Provider(
                    user=request.user,
                    name=provider_name,
                    base_url=base_url,
                    model_prefix=model_prefix,
                    status="active",
                )
                provider.set_api_key(api_key)
                provider.save()
                provider_created = True
                provider_id = provider.id
            else:
                provider = existing
                provider_id = provider.id
                provider_name = provider.name

            # Create routing entries
            for model_id in models_found:
                _, created = ModelRouting.objects.get_or_create(
                    user=request.user,
                    model_name=model_id,
                    defaults={"provider": provider, "is_active": True},
                )
                if created:
                    routing_created += 1

        result_data = {
            "api_connected": api_connected,
            "models_found": models_found,
            "token_mode": token_mode,
            "matched_prices": matched_prices,
            "provider_created": provider_created,
            "routing_created": routing_created,
            "provider_id": provider_id,
            "provider_name": provider_name,
        }

        return success_response(data=result_data, message="检测完成")
