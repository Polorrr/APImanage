from rest_framework import serializers

from .models import UserSettings


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ["log_retention_days", "updated_at"]
        read_only_fields = ["updated_at"]
