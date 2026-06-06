from django.conf import settings
from django.db import models


class ModelRouting(models.Model):
    """Model-to-provider routing table with priority.

    Maps model names to specific providers for smart gateway routing.
    Multiple providers can be mapped to the same model name with different priorities.
    Priority 1 = highest, will be tried first.
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="model_routings",
    )
    model_name = models.CharField(max_length=200, db_index=True, help_text="完整模型名，如 mimo-v2.5-pro")
    provider = models.ForeignKey(
        "gateway.Provider",
        on_delete=models.CASCADE,
        related_name="model_routings",
    )
    priority = models.IntegerField(default=1, help_text="优先级，1=最高。同名模型按优先级排序")
    max_tokens = models.IntegerField(default=0, help_text="模型最大 token 数，0=不限制")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "model_routing"
        ordering = ["model_name", "priority"]

    def __str__(self):
        return f"{self.model_name} → {self.provider.name} (P{self.priority})"

    @classmethod
    def find_provider(cls, user_id: int, model_name: str):
        """Find the best provider for a given model name.

        Returns (provider, max_tokens) tuple.
        Priority:
        1. Exact match in routing table (by priority)
        2. Prefix match (longest prefix wins)
        3. Fallback to any active provider
        """
        # 1. Exact match (ordered by priority)
        routings = cls.objects.filter(
            user_id=user_id, model_name=model_name, is_active=True
        ).select_related("provider").order_by("priority")

        for r in routings:
            if r.provider.status == "active" and r.provider.health_status != "unhealthy":
                return r.provider, r.max_tokens

        # If exact match exists but all unhealthy, try any exact match
        if routings.exists():
            r = routings.first()
            return r.provider, r.max_tokens

        # 2. Prefix match (longest first)
        all_routings = cls.objects.filter(
            user_id=user_id, is_active=True
        ).select_related("provider").order_by("-model_name", "priority")

        best_match = None
        best_max_tokens = 0
        best_length = 0

        for r in all_routings:
            if r.provider.status != "active":
                continue
            if model_name.startswith(r.model_name) and len(r.model_name) > best_length:
                best_match = r.provider
                best_max_tokens = r.max_tokens
                best_length = len(r.model_name)
            elif r.model_name in model_name and len(r.model_name) > best_length:
                best_match = r.provider
                best_max_tokens = r.max_tokens
                best_length = len(r.model_name)

        if best_match:
            return best_match, best_max_tokens

        # 3. Fallback: use model_prefix on providers
        from apps.gateway.models import Provider
        providers = Provider.objects.filter(user_id=user_id, status="active")
        for p in providers:
            if p.model_prefix:
                prefixes = [x.strip() for x in p.model_prefix.split(",") if x.strip()]
                for prefix in prefixes:
                    if model_name.startswith(prefix) or prefix in model_name:
                        return p, 0

        # 4. Last resort: first active provider
        provider = Provider.objects.filter(user_id=user_id, status="active").first()
        return provider, 0
