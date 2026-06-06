from django.urls import path
from . import views_routing

urlpatterns = [
    path("", views_routing.ModelRoutingListCreateView.as_view(), name="routing-list-create"),
    path("<int:pk>/", views_routing.ModelRoutingDetailView.as_view(), name="routing-detail"),
]
