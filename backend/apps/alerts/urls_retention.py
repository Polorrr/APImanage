from django.urls import path
from . import views_retention

urlpatterns = [
    path("", views_retention.RetentionPolicyListView.as_view(), name="retention-list"),
    path("<int:pk>/", views_retention.RetentionPolicyDetailView.as_view(), name="retention-detail"),
]
