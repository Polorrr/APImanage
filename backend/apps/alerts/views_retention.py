"""Data retention policy API endpoints."""
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import DataRetentionPolicy


class RetentionPolicyListView(generics.ListCreateAPIView):
    """List and create data retention policies."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        from .serializers import DataRetentionPolicySerializer
        return DataRetentionPolicySerializer

    def get_queryset(self):
        return DataRetentionPolicy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RetentionPolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete data retention policies."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        from .serializers import DataRetentionPolicySerializer
        return DataRetentionPolicySerializer

    def get_queryset(self):
        return DataRetentionPolicy.objects.filter(user=self.request.user)
