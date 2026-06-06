from django.urls import path

from . import views

urlpatterns = [
    path("rules/", views.BudgetRuleListCreateView.as_view(), name="alert-rules-list-create"),
    path("rules/<int:pk>/", views.BudgetRuleDetailView.as_view(), name="alert-rules-detail"),
    path("logs/", views.AlertLogListView.as_view(), name="alert-logs"),
]
