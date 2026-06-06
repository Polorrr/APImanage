"""Data retention cleanup task."""
import logging
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


def cleanup_old_logs():
    """Clean up old call logs based on user settings."""
    from apps.alerts.models import UserSettings
    from apps.gateway.models import LLMCallLog

    # Get all user settings
    settings_list = UserSettings.objects.select_related('user').all()

    if not settings_list.exists():
        logger.info("No user settings found")
        return

    total_deleted = 0

    for setting in settings_list:
        cutoff_date = timezone.now() - timedelta(days=setting.log_retention_days)

        deleted_count, _ = LLMCallLog.objects.filter(
            user=setting.user,
            created_at__lt=cutoff_date,
        ).delete()

        total_deleted += deleted_count
        logger.info(f"Deleted {deleted_count} logs for user {setting.user_id} (retention: {setting.log_retention_days} days)")

    logger.info(f"Total deleted: {total_deleted}")
    return total_deleted
