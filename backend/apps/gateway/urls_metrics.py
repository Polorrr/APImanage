from django.urls import path
from . import views_metrics

urlpatterns = [
    path("", views_metrics.GatewayMetricsView.as_view(), name="gateway-metrics"),
]
