from django.urls import path

from . import views_report

urlpatterns = [
    path("", views_report.SDKReportView.as_view(), name="sdk-report"),
]
