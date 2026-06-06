"""Celery tasks for budget alert checking."""
import logging
from datetime import timedelta

import httpx
from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.gateway.models import ApiKey, LLMCallLog

logger = logging.getLogger(__name__)


@shared_task
def check_budget_rules():
    """Periodic task — check all active budget rules and fire alerts."""
    from apps.alerts.models import AlertLog, BudgetRule

    now = timezone.now()
    active_rules = BudgetRule.objects.filter(is_active=True).select_related("api_key")

    for rule in active_rules:
        # Determine the time window
        if rule.rule_type == "daily":
            since = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
        elif rule.rule_type == "monthly":
            since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # total
            since = timezone.datetime.min.replace(tzinfo=timezone.get_current_timezone())

        # Calculate cost based on scope (per-key or user-level)
        cost_filter = {
            "user_id": rule.user_id,
            "created_at__gte": since,
            "cost_yuan__isnull": False,
        }

        # If rule is linked to a specific API key, filter by that key
        if rule.api_key_id:
            cost_filter["api_key_id"] = rule.api_key_id

        total = LLMCallLog.objects.filter(**cost_filter).aggregate(
            total=Sum("cost_yuan")
        )["total"] or 0

        # Check threshold
        if total > rule.threshold_yuan:
            # Avoid re-triggering within 1 hour for the same rule
            if rule.last_triggered and (now - rule.last_triggered) < timedelta(hours=1):
                continue

            # Send alert
            send_status = _send_alert(rule, total, now)

            # Log the alert
            AlertLog.objects.create(
                rule=rule,
                user_id=rule.user_id,
                trigger_cost=total,
                threshold=rule.threshold_yuan,
                channel=rule.alert_channel,
                send_status=send_status,
            )

            rule.last_triggered = now
            rule.save(update_fields=["last_triggered"])

            # Auto-disable API key if configured
            if rule.auto_disable and rule.api_key_id:
                key = rule.api_key
                if key.is_active:
                    key.is_active = False
                    key.save(update_fields=["is_active"])
                    logger.warning(
                        f"Auto-disabled API key '{key.name}' (id={key.id}) "
                        f"due to budget rule '{rule.name}': ¥{total} > ¥{rule.threshold_yuan}"
                    )


def _send_alert(rule, current_cost, now) -> str:
    """Send alert via webhook. Returns 'sent' or 'failed'."""
    if rule.alert_channel == "webhook" and rule.webhook_url:
        return _send_webhook(rule, current_cost, now)
    elif rule.alert_channel == "email":
        # TODO: implement email sending
        logger.info(f"Email alert would be sent to user {rule.user_id}: {rule.name}")
        return "sent"
    return "failed"


def _send_webhook(rule, current_cost, now) -> str:
    """Send a webhook notification (compatible with WeCom/DingTalk)."""
    scope = f"Key: {rule.api_key.name}" if rule.api_key_id else "全部 Key"
    message = {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                f"**LLM 成本告警**\n"
                f"> 规则名称: {rule.name}\n"
                f"> 规则类型: {rule.rule_type}\n"
                f"> 作用范围: {scope}\n"
                f"> 告警阈值: ¥{rule.threshold_yuan}\n"
                f"> 当前费用: ¥{current_cost}\n"
                f"> 触发时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            ),
        },
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(rule.webhook_url, json=message)
            if resp.status_code == 200:
                return "sent"
            logger.warning(f"Webhook returned {resp.status_code}: {resp.text}")
            return "failed"
    except Exception as e:
        logger.exception(f"Failed to send webhook: {e}")
        return "failed"


def check_key_budget_sync(api_key_id: int, user_id: int):
    """Synchronous check for API key budget — called from gateway middleware.

    Returns (is_over_budget, current_cost, threshold) tuple.
    """
    from apps.alerts.models import AlertLog, BudgetRule

    now = timezone.now()

    # Find active rules for this key
    rules = BudgetRule.objects.filter(
        user_id=user_id,
        api_key_id=api_key_id,
        is_active=True,
    )

    for rule in rules:
        # Determine time window
        if rule.rule_type == "daily":
            since = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
        elif rule.rule_type == "monthly":
            since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            since = timezone.datetime.min.replace(tzinfo=timezone.get_current_timezone())

        total = LLMCallLog.objects.filter(
            api_key_id=api_key_id,
            created_at__gte=since,
            cost_yuan__isnull=False,
        ).aggregate(total=Sum("cost_yuan"))["total"] or 0

        if total > rule.threshold_yuan:
            return True, float(total), float(rule.threshold_yuan)

    return False, 0, 0
