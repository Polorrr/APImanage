from rest_framework import serializers
from .models_routing import ModelRouting


class ModelRoutingSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.name", read_only=True)

    class Meta:
        model = ModelRouting
        fields = ("id", "model_name", "provider", "provider_name", "priority", "max_tokens", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class ModelRoutingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelRouting
        fields = ("model_name", "provider", "priority", "max_tokens", "is_active")
