from django.conf import settings
from django.db import models


class ModelPricing(models.Model):
    """Model pricing table — price per 1K tokens (CNY)."""

    id = models.BigAutoField(primary_key=True)
    model_keyword = models.CharField(max_length=100, db_index=True, help_text="模型名关键词")
    provider_name = models.CharField(max_length=100, null=True, blank=True, help_text="供应商名，NULL 表示通用")
    input_price = models.DecimalField(max_digits=10, decimal_places=6, help_text="输入价格-未命中缓存（元/千token）")
    input_price_cached = models.DecimalField(max_digits=10, decimal_places=6, default=0, help_text="输入价格-命中缓存（元/千token）")
    output_price = models.DecimalField(max_digits=10, decimal_places=6, help_text="输出价格（元/千token）")
    currency = models.CharField(max_length=3, default="CNY")
    is_builtin = models.BooleanField(default=False, help_text="是否内置价格")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="custom_pricing",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "model_pricing"
        ordering = ["model_keyword"]

    def __str__(self):
        return f"{self.model_keyword}: ¥{self.input_price}/¥{self.output_price} per 1K"

    @classmethod
    def find_for_model(cls, model_name: str, user_id: int = None):
        """Find the best matching pricing for a model name.

        Priority:
        1. User-specific pricing (exact match)
        2. User-specific pricing (keyword match)
        3. Built-in pricing (exact match)
        4. Built-in pricing (keyword match)
        """
        # Try user-specific exact match
        if user_id:
            match = cls.objects.filter(
                model_keyword=model_name, user_id=user_id
            ).first()
            if match:
                return match

        # Try user-specific keyword match
        if user_id:
            for p in cls.objects.filter(user_id=user_id).order_by("-model_keyword"):
                if p.model_keyword.lower() in model_name.lower():
                    return p

        # Try built-in exact match
        match = cls.objects.filter(
            model_keyword=model_name, is_builtin=True
        ).first()
        if match:
            return match

        # Try built-in keyword match
        for p in cls.objects.filter(is_builtin=True).order_by("-model_keyword"):
            if p.model_keyword.lower() in model_name.lower():
                return p

        return None
