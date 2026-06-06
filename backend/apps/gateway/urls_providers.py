from django.urls import path

from . import views_providers

urlpatterns = [
    path("", views_providers.ProviderListCreateView.as_view(), name="provider-list-create"),
    path("<int:pk>/", views_providers.ProviderDetailUpdateDeleteView.as_view(), name="provider-detail"),
    path("<int:pk>/detect/", views_providers.ProviderDetectView.as_view(), name="provider-detect"),
]
