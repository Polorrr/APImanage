"""Monitoring API endpoints."""
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .monitoring import get_all_metrics, check_and_alert


def success_response(data=None, message="success"):
    return JsonResponse({"code": 0, "message": message, "data": data})


@method_decorator(csrf_exempt, name='dispatch')
class GatewayMetricsView(View):
    """GET /api/gateway/metrics/ — get error rates and alerts."""

    def get(self, request):
        metrics = get_all_metrics()
        alerts = check_and_alert()
        return success_response(data={
            "metrics": metrics,
            "alerts": alerts,
        })
