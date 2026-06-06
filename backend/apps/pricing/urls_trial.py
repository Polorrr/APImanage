from django.urls import path

from . import views_trial

urlpatterns = [
    path("", views_trial.TrialPricingView.as_view(), name="pricing-trial"),
]
