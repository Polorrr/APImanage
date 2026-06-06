from django.conf import settings
from django.db import models


class BudgetRule(models.Model):
    """Budget alert rule."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budget_rules",
    )
    name = models.CharField(max_length=100, help_text="规则名称")
    rule_type = models.CharField(
        max_length=20,
        choices=[("daily", "每日"), ("monthly", "每月"), ("total", "累计")],
        help_text="规则类型",
    )
    api_key = models.ForeignKey(
        "gateway.ApiKey",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="budget_rules",
        help_text="关联的 API Key，为空表示用户级规则",
    )
    threshold_yuan = models.DecimalField(max_digits=10, decimal_places=2, help_text="告警阈值（元）")
    auto_disable = models.BooleanField(default=False, help_text="超预算后自动禁用 Key")
    alert_channel = models.CharField(
        max_length=20,
        choices=[("webhook", "Webhook"), ("email", "Email")],
        help_text="告警渠道",
    )
    webhook_url = models.CharField(max_length=500, null=True, blank=True, help_text="Webhook URL")
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "budget_rules"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.rule_type}: ¥{self.threshold_yuan})"


class AlertLog(models.Model):
    """Alert trigger log."""

    id = models.BigAutoField(primary_key=True)
    rule = models.ForeignKey(
        BudgetRule,
        on_delete=models.CASCADE,
        related_name="alert_logs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alert_logs",
    )
    trigger_cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="触发时的费用")
    threshold = models.DecimalField(max_digits=10, decimal_places=2)
    channel = models.CharField(max_length=20)
    send_status = models.CharField(
        max_length=20,
        default="sent",
        choices=[("sent", "已发送"), ("failed", "发送失败")],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alert_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alert for {self.rule.name}: ¥{self.trigger_cost} > ¥{self.threshold}"


class AlertNotification(models.Model):
    """In-app notification for budget alerts."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(
        max_length=20,
        default="warning",
        choices=[("info", "信息"), ("warning", "警告"), ("error", "错误")],
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alert_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.level}] {self.title}"


class UserSettings(models.Model):
    """User settings."""

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings",
    )
    log_retention_days = models.IntegerField(
        default=30,
        help_text="调用日志保留天数（超过此天数的日志将被自动删除）",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_settings"

    def __str__(self):
        return f"Settings for {self.user.email}"
