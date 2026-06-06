"""Health check API endpoints."""
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .health import check_provider_health, check_all_providers
from .models import Provider


def success_response(data=None, message="success"):
    return JsonResponse({"code": 0, "message": message, "data": data})


@method_decorator(csrf_exempt, name='dispatch')
class ProviderHealthView(View):
    """GET /api/providers/health/ — check all providers health.
       POST /api/providers/{id}/health/ — check single provider."""

    def get(self, request):
        user_id = getattr(request, 'api_user_id', None)
        if not user_id:
            # Try JWT
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                raw_key = auth_header[7:]
                if raw_key.count('.') == 2:
                    try:
                        from rest_framework_simplejwt.tokens import AccessToken
                        token = AccessToken(raw_key)
                        user_id = token['user_id']
                    except Exception:
                        pass
        if not user_id:
            return JsonResponse({"code": 1, "message": "未授权"}, status=401)
        results = check_all_providers(user_id)
        return success_response(data=results, message="健康检查完成")

    def post(self, request, pk=None):
        if pk:
            try:
                provider = Provider.objects.get(id=pk)
                result = check_provider_health(provider)
                return success_response(data={provider.name: result})
            except Provider.DoesNotExist:
                return JsonResponse({"code": 1, "message": "供应商不存在"}, status=404)
        results = check_all_providers()
        return success_response(data=results)
