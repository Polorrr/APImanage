from django.conf import settings
from django.db import models


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
