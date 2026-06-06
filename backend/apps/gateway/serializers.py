from rest_framework import serializers

from .models import ApiKey, LLMCallLog, Provider


class ApiKeyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ("name", "permissions", "rate_limit_rpm", "expires_at", "agent_id", "agent_name", "allowed_models", "monthly_budget")

    def create(self, validated_data):
        raw_key, prefix, key_hash = ApiKey.generate_key()
        validated_data["key_prefix"] = prefix
        validated_data["key_hash"] = key_hash
        validated_data["key_plain"] = raw_key
        api_key = ApiKey(**validated_data)
        api_key.save()
        api_key._raw_key = raw_key  # Only returned on creation
        return api_key


class ApiKeyListSerializer(serializers.ModelSerializer):
    key = serializers.CharField(source='key_plain', read_only=True)

    class Meta:
        model = ApiKey
        fields = (
            "id", "name", "key", "key_prefix", "permissions", "rate_limit_rpm",
            "is_active", "agent_id", "agent_name", "allowed_models", "monthly_budget",
            "last_used_at", "expires_at", "created_at",
        )
        read_only_fields = fields


class ApiKeyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ("name", "permissions", "rate_limit_rpm", "is_active", "agent_id", "agent_name", "allowed_models", "monthly_budget")


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ("id", "name", "base_url", "model_prefix", "status", "health_status", "last_health_check", "detect_result", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at", "detect_result", "health_status", "last_health_check")


class ProviderCreateSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True, source='api_key_enc')

    class Meta:
        model = Provider
        fields = ("name", "base_url", "api_key", "model_prefix")


class LLMCallLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMCallLog
        fields = (
            "id", "agent_id", "model", "input_tokens_reported",
            "output_tokens_reported", "input_tokens_estimated",
            "output_tokens_estimated", "data_source", "cost_yuan",
            "latency_ms", "status_code", "is_error", "error_message",
            "created_at",
        )
        read_only_fields = fields
