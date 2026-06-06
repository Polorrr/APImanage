"""Statistics aggregation service."""
from datetime import timedelta

from django.db.models import Avg, Count, F, Q, Sum
from django.utils import timezone

from apps.gateway.models import LLMCallLog


def get_overview(user_id: int, days: int = 30, agent_id: str = None) -> dict:
    """Get overview stats: total cost, total calls, avg latency, active keys."""
    from apps.gateway.models import ApiKey

    since = timezone.now() - timedelta(days=days)
    logs = LLMCallLog.objects.filter(user_id=user_id, created_at__gte=since)
    if agent_id:
        logs = logs.filter(agent_id=agent_id)

    agg = logs.aggregate(
        total_cost=Sum("cost_yuan"),
        total_calls=Count("id"),
        avg_latency=Avg("latency_ms"),
    )

    active_keys = ApiKey.objects.filter(
        user_id=user_id, is_active=True
    ).count()

    return {
        "total_cost": float(agg["total_cost"] or 0),
        "total_calls": agg["total_calls"],
        "avg_latency": int(agg["avg_latency"] or 0),
        "active_keys": active_keys,
        "cost_change": 0,
        "calls_change": 0,
        "latency_change": 0,
    }


def get_daily_trend(user_id: int, days: int = 30, agent_id: str = None) -> list[dict]:
    """Get daily cost trend for the last N days."""
    from django.db.models import DateField
    from django.db.models.functions import Cast

    since = timezone.now() - timedelta(days=days)
    qs = LLMCallLog.objects.filter(user_id=user_id, created_at__gte=since)
    if agent_id:
        qs = qs.filter(agent_id=agent_id)
    qs = (
        qs.annotate(date=Cast("created_at", DateField()))
        .values("date")
        .annotate(
            total_cost=Sum("cost_yuan"),
            total_calls=Count("id"),
            avg_latency=Avg("latency_ms"),
        )
        .order_by("date")
    )

    return [
        {
            "date": item["date"].strftime("%Y-%m-%d") if item["date"] else "",
            "cost": float(item["total_cost"] or 0),
            "calls": item["total_calls"],
            "avg_latency": int(item["avg_latency"] or 0),
        }
        for item in qs
    ]


def get_by_model(user_id: int, days: int = 30, agent_id: str = None) -> list[dict]:
    """Get cost breakdown by model."""
    since = timezone.now() - timedelta(days=days)
    qs = LLMCallLog.objects.filter(user_id=user_id, created_at__gte=since)
    if agent_id:
        qs = qs.filter(agent_id=agent_id)
    qs = (
        qs.values("model")
        .annotate(
            total_cost=Sum("cost_yuan"),
            total_calls=Count("id"),
            total_input_tokens=Sum("input_tokens_reported"),
            total_output_tokens=Sum("output_tokens_reported"),
        )
        .order_by("-total_cost")
    )

    results = list(qs)
    total_cost_all = sum(float(i["total_cost"] or 0) for i in results) or 1
    return [
        {
            "model": item["model"],
            "cost": float(item["total_cost"] or 0),
            "calls": item["total_calls"],
            "percentage": round(float(item["total_cost"] or 0) / total_cost_all * 100, 1),
        }
        for item in results
    ]


def get_by_agent(user_id: int, days: int = 30) -> list[dict]:
    """Get cost breakdown by agent_id."""
    since = timezone.now() - timedelta(days=days)
    qs = (
        LLMCallLog.objects.filter(
            user_id=user_id,
            created_at__gte=since,
            agent_id__isnull=False,
        )
        .exclude(agent_id="")
        .values("agent_id")
        .annotate(
            total_cost=Sum("cost_yuan"),
            total_calls=Count("id"),
        )
        .order_by("-total_cost")
    )

    return [
        {
            "agent_id": item["agent_id"],
            "cost": float(item["total_cost"] or 0),
            "calls": item["total_calls"],
        }
        for item in qs
    ]


def get_by_provider(user_id: int, days: int = 30) -> list[dict]:
    """Get cost breakdown by provider."""
    from apps.gateway.models import Provider

    since = timezone.now() - timedelta(days=days)
    qs = (
        LLMCallLog.objects.filter(user_id=user_id, created_at__gte=since, provider__isnull=False)
        .values(provider_name=F("provider__name"))
        .annotate(
            total_cost=Sum("cost_yuan"),
            total_calls=Count("id"),
        )
        .order_by("-total_cost")
    )

    return [
        {
            "provider": item["provider_name"],
            "total_cost": float(item["total_cost"] or 0),
            "total_calls": item["total_calls"],
        }
        for item in qs
    ]


def get_call_logs(
    user_id: int,
    model: str = None,
    agent_id: str = None,
    status_code: int = None,
    start_date: str = None,
    end_date: str = None,
):
    """Get call logs with filters."""
    qs = LLMCallLog.objects.filter(user_id=user_id)

    if model:
        qs = qs.filter(model__icontains=model)
    if agent_id:
        qs = qs.filter(agent_id=agent_id)
    if status_code:
        qs = qs.filter(status_code=status_code)
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    return qs.select_related("provider")
