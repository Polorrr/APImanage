"""User settings API endpoints."""
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserSettings
from .serializers_settings import UserSettingsSerializer


class UserSettingsView(APIView):
    """Get or update user settings."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        settings, _ = UserSettings.objects.get_or_create(user=request.user)
        return Response({"code": 0, "data": UserSettingsSerializer(settings).data, "message": "ok"})

    def patch(self, request):
        settings, _ = UserSettings.objects.get_or_create(user=request.user)
        serializer = UserSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 0, "data": serializer.data, "message": "ok"})
