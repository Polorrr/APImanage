from django.urls import path

from . import views_keys

urlpatterns = [
    path("", views_keys.ApiKeyListCreateView.as_view(), name="apikey-list-create"),
    path("<int:pk>/", views_keys.ApiKeyDetailUpdateDeleteView.as_view(), name="apikey-detail"),
]