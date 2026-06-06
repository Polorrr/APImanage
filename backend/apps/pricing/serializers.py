from rest_framework import serializers

from .models import ModelPricing


class ModelPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelPricing
        fields = (
            "id", "model_keyword", "provider_name", "input_price",
            "input_price_cached", "output_price", "currency", "is_builtin", "user", "created_at",
        )
        read_only_fields = ("id", "is_builtin", "created_at")


class ModelPricingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelPricing
        fields = ("model_keyword", "provider_name", "input_price", "input_price_cached", "output_price", "currency")
