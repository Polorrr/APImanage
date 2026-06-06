from django.urls import path
from . import views_health

urlpatterns = [
    path("", views_health.ProviderHealthView.as_view(), name="provider-health-all"),
    path("<int:pk>/", views_health.ProviderHealthView.as_view(), name="provider-health-single"),
]
