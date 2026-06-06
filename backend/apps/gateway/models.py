import hashlib
import secrets

from django.conf import settings
from django.db import models

from utils.encryption import encrypt, decrypt


class ApiKey(models.Model):
    """API key for gateway authentication."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(max_length=100, help_text="Key 名称，如'生产环境'")
    key_prefix = models.CharField(max_length=16, help_text="前缀，用于快速查找")
    key_hash = models.CharField(max_length=128, help_text="SHA256 hash")
    key_plain = models.CharField(max_length=128, default='', help_text="完整 Key（内部平台用）")
    permissions = models.JSONField(default=dict, help_text='{"read": true, "write": true}')
    rate_limit_rpm = models.IntegerField(default=60, help_text="每分钟请求数限制")
    is_active = models.BooleanField(default=True)
    # Agent & Scope fields
    agent_id = models.CharField(max_length=100, default='', blank=True, help_text="Agent 标识，如 customer-service")
    agent_name = models.CharField(max_length=100, default='', blank=True, help_text="Agent 显示名，如 客服 Bot")
    allowed_models = models.JSONField(default=list, blank=True, help_text="可用模型列表，空=不限制")
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="月度预算（元），0=不限制")
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "api_keys"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"

    @staticmethod
    def generate_key():
        """Generate a new API key and return (plain_key, prefix, hash)."""
        raw_key = "sk-" + secrets.token_hex(32)
        prefix = raw_key[:16]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return raw_key, prefix, key_hash

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.key_prefix or not self.key_hash:
            raw_key, prefix, key_hash = self.generate_key()
            self.key_prefix = prefix
            self.key_hash = key_hash
        super().save(*args, **kwargs)


class Provider(models.Model):
    """LLM provider / relay station configuration."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="providers",
    )
    name = models.CharField(max_length=100, help_text="供应商名称")
    base_url = models.CharField(max_length=500, help_text="API 基础地址")
    api_key_enc = models.TextField(help_text="加密存储的 API Key")
    model_prefix = models.CharField(max_length=200, default="", blank=True, help_text="模型前缀，逗号分隔。如 mimo-,deepseek-。用于自动路由")
    status = models.CharField(
        max_length=20,
        default="active",
        choices=[("active", "active"), ("disabled", "disabled"), ("error", "error")],
    )
    health_status = models.CharField(max_length=20, default="unknown", help_text="健康状态: healthy/unhealthy/unknown")
    last_health_check = models.DateTimeField(null=True, blank=True)
    detect_result = models.JSONField(null=True, blank=True, help_text="自动检测结果")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "providers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def api_key(self):
        """Decrypt and return the API key."""
        return decrypt(self.api_key_enc)

    def set_api_key(self, raw_key: str):
        """Encrypt and store the API key."""
        self.api_key_enc = encrypt(raw_key)

    def save(self, *args, **kwargs):
        # Auto-encrypt if the key looks like plaintext (not encrypted)
        if self.api_key_enc and not self.api_key_enc.startswith('gAAAAA'):
            # Looks like plaintext, encrypt it
            self.api_key_enc = encrypt(self.api_key_enc)
        super().save(*args, **kwargs)


class LLMCallLog(models.Model):
    """LLM call log — the core data table, highest volume."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="call_logs",
    )
    api_key = models.ForeignKey(
        ApiKey,
        on_delete=models.CASCADE,
        related_name="call_logs",
        null=True,
        blank=True,
    )
    provider = models.ForeignKey(
        Provider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="call_logs",
    )
    agent_id = models.CharField(max_length=100, null=True, blank=True, help_text="来自请求头 X-Agent-Id")
    model = models.CharField(max_length=100)

    # Token data
    input_tokens_reported = models.IntegerField(null=True, blank=True, help_text="上游返回的 input tokens")
    output_tokens_reported = models.IntegerField(null=True, blank=True, help_text="上游返回的 output tokens")
    input_tokens_estimated = models.IntegerField(null=True, blank=True, help_text="本地估算的 input tokens")
    output_tokens_estimated = models.IntegerField(null=True, blank=True, help_text="本地估算的 output tokens")
    data_source = models.CharField(max_length=20, help_text="provider / estimated / mixed")

    # Cost
    cost_yuan = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    # Performance
    latency_ms = models.IntegerField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    is_error = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "llm_call_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"], name="idx_user_time"),
            models.Index(fields=["agent_id", "created_at"], name="idx_agent_time"),
            models.Index(fields=["model"], name="idx_model"),
            models.Index(fields=["created_at"], name="idx_created_at"),
        ]

    def __str__(self):
        return f"{self.model} @ {self.created_at}"
