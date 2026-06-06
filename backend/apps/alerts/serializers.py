from rest_framework import serializers

from .models import AlertLog, BudgetRule


class BudgetRuleSerializer(serializers.ModelSerializer):
    api_key_name = serializers.CharField(source="api_key.name", read_only=True, default=None)

    class Meta:
        model = BudgetRule
        fields = (
            "id", "name", "rule_type", "api_key", "api_key_name", "threshold_yuan",
            "auto_disable", "alert_channel", "webhook_url", "is_active",
            "last_triggered", "created_at",
        )
        read_only_fields = ("id", "last_triggered", "created_at")


class BudgetRuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetRule
        fields = ("name", "rule_type", "api_key", "threshold_yuan", "auto_disable", "alert_channel", "webhook_url")


class AlertLogSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source="rule.name", read_only=True)

    class Meta:
        model = AlertLog
        fields = (
            "id", "rule", "rule_name", "trigger_cost", "threshold",
            "channel", "send_status", "created_at",
        )
        read_only_fields = fields
