from django.urls import path

from . import views

urlpatterns = [
    path("overview/", views.StatsOverviewView.as_view(), name="stats-overview"),
    path("daily/", views.StatsDailyView.as_view(), name="stats-daily"),
    path("by-model/", views.StatsByModelView.as_view(), name="stats-by-model"),
    path("by-agent/", views.StatsByAgentView.as_view(), name="stats-by-agent"),
    path("by-provider/", views.StatsByProviderView.as_view(), name="stats-by-provider"),
    path("calls/", views.CallLogsView.as_view(), name="stats-calls"),
]
