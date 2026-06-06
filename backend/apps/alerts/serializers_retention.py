from rest_framework import serializers

from .models import DataRetentionPolicy


class DataRetentionPolicySerializer(serializers.ModelSerializer):
    """Serializer for data retention policies."""

    class Meta:
        model = DataRetentionPolicy
        fields = ["id", "name", "retention_days", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
