from django.urls import path

from . import views

urlpatterns = [
    path("", views.ModelPricingListCreateView.as_view(), name="pricing-list-create"),
    path("<int:pk>/", views.ModelPricingDetailUpdateDeleteView.as_view(), name="pricing-detail"),
    path("builtin/", views.BuiltinPricingListView.as_view(), name="pricing-builtin"),
]
