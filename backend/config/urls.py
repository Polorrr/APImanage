from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.gateway.views_providers import StandaloneDetectView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth endpoints
    path("api/auth/", include("apps.users.urls")),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Business endpoints
    path("api/gateway/", include("apps.gateway.urls")),
    path("api/gateway/metrics/", include("apps.gateway.urls_metrics")),
    path("api/keys/", include("apps.gateway.urls_keys")),
    path("api/routing/", include("apps.gateway.urls_routing")),
    path("api/providers/", include("apps.gateway.urls_providers")),
    path("api/providers/health/", include("apps.gateway.urls_health")),
    path("api/pricing/", include("apps.pricing.urls")),
    path("api/pricing/trial/", include("apps.pricing.urls_trial")),
    path("api/stats/", include("apps.stats.urls")),
    path("api/alerts/", include("apps.alerts.urls")),
    path("api/alerts/notifications/", include("apps.alerts.urls_notification")),
    path("api/settings/", include("apps.alerts.urls_settings")),
    # SDK report endpoint
    path("api/v1/report/", include("apps.gateway.urls_report")),
    # Standalone detect endpoint
    path("api/detect/", StandaloneDetectView.as_view(), name="standalone-detect"),
]
