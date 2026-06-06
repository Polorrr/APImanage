from django.urls import path
from . import views_settings

urlpatterns = [
    path("", views_settings.UserSettingsView.as_view(), name="user-settings"),
]
