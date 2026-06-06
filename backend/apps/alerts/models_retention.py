from django.conf import settings
from django.db import models


class DataRetentionPolicy(models.Model):
    """Data retention policy for automatic cleanup."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="retention_policies",
    )
    name = models.CharField(max_length=100, help_text="策略名称")
    retention_days = models.IntegerField(
        default=30,
        help_text="保留天数（超过此天数的日志将被自动删除）",
    )
    is_active = models.BooleanField(default=True, help_text="是否启用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "data_retention_policy"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.retention_days}天"
