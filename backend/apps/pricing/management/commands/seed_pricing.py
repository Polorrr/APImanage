"""Seed built-in pricing data for common LLM models."""
from django.core.management.base import BaseCommand
from apps.pricing.models import ModelPricing


BUILTIN_PRICING = [
    # === 小米 MiMo ===
    {"model_keyword": "mimo-v2.5-pro", "input_price": 3.00, "input_price_cached": 0.025, "output_price": 6.00},
    {"model_keyword": "mimo-v2.5", "input_price": 1.00, "input_price_cached": 0.02, "output_price": 2.00},
    {"model_keyword": "mimo-v2-pro", "input_price": 7.00, "input_price_cached": 1.40, "output_price": 21.00},
    {"model_keyword": "mimo-v2-omni", "input_price": 2.80, "input_price_cached": 0.56, "output_price": 14.00},
    {"model_keyword": "mimo-v2-flash", "input_price": 0.70, "input_price_cached": 0.07, "output_price": 2.10},

    # === DeepSeek ===
    {"model_keyword": "deepseek-chat", "input_price": 1.00, "input_price_cached": 0.10, "output_price": 2.00},
    {"model_keyword": "deepseek-coder", "input_price": 1.00, "input_price_cached": 0.10, "output_price": 2.00},
    {"model_keyword": "deepseek-reasoner", "input_price": 4.00, "input_price_cached": 1.00, "output_price": 16.00},
    {"model_keyword": "deepseek-v3", "input_price": 1.00, "input_price_cached": 0.10, "output_price": 2.00},

    # === 智谱 AI (GLM) ===
    {"model_keyword": "glm-4-flash", "input_price": 0.10, "input_price_cached": 0, "output_price": 0.10},
    {"model_keyword": "glm-4-air", "input_price": 1.00, "input_price_cached": 0, "output_price": 1.00},
    {"model_keyword": "glm-4-airx", "input_price": 10.00, "input_price_cached": 0, "output_price": 10.00},
    {"model_keyword": "glm-4-long", "input_price": 1.00, "input_price_cached": 0, "output_price": 1.00},
    {"model_keyword": "glm-4", "input_price": 100.00, "input_price_cached": 0, "output_price": 100.00},
    {"model_keyword": "glm-4-plus", "input_price": 50.00, "input_price_cached": 0, "output_price": 50.00},
    {"model_keyword": "glm-5", "input_price": 50.00, "input_price_cached": 0, "output_price": 50.00},

    # === 阿里通义千问 (Qwen) ===
    {"model_keyword": "qwen-turbo", "input_price": 0.30, "input_price_cached": 0.15, "output_price": 0.60},
    {"model_keyword": "qwen-plus", "input_price": 0.80, "input_price_cached": 0.40, "output_price": 2.00},
    {"model_keyword": "qwen-max", "input_price": 2.00, "input_price_cached": 1.00, "output_price": 6.00},
    {"model_keyword": "qwen-max-longcontext", "input_price": 0.50, "input_price_cached": 0, "output_price": 2.00},
    {"model_keyword": "qwen2.5-72b-instruct", "input_price": 4.00, "input_price_cached": 0, "output_price": 12.00},
    {"model_keyword": "qwen2.5-32b-instruct", "input_price": 2.00, "input_price_cached": 0, "output_price": 6.00},
    {"model_keyword": "qwen2.5-14b-instruct", "input_price": 1.00, "input_price_cached": 0, "output_price": 3.00},
    {"model_keyword": "qwen2.5-7b-instruct", "input_price": 0.50, "input_price_cached": 0, "output_price": 1.50},

    # === 百度文心 (ERNIE) ===
    {"model_keyword": "ernie-speed-8k", "input_price": 0.40, "input_price_cached": 0, "output_price": 0.80},
    {"model_keyword": "ernie-4.0-8k", "input_price": 60.00, "input_price_cached": 0, "output_price": 60.00},
    {"model_keyword": "ernie-4.0-turbo-8k", "input_price": 20.00, "input_price_cached": 0, "output_price": 60.00},
    {"model_keyword": "ernie-3.5-8k", "input_price": 0.80, "input_price_cached": 0, "output_price": 2.00},

    # === 月之暗面 Kimi (Moonshot) ===
    {"model_keyword": "moonshot-v1-8k", "input_price": 12.00, "input_price_cached": 0, "output_price": 12.00},
    {"model_keyword": "moonshot-v1-32k", "input_price": 24.00, "input_price_cached": 0, "output_price": 24.00},
    {"model_keyword": "moonshot-v1-128k", "input_price": 60.00, "input_price_cached": 0, "output_price": 60.00},

    # === MiniMax ===
    {"model_keyword": "abab6.5-chat", "input_price": 1.00, "input_price_cached": 0, "output_price": 1.00},
    {"model_keyword": "abab6.5s-chat", "input_price": 0.10, "input_price_cached": 0, "output_price": 0.10},
    {"model_keyword": "abab5.5-chat", "input_price": 5.00, "input_price_cached": 0, "output_price": 5.00},

    # === 零一万物 (01.AI Yi) ===
    {"model_keyword": "yi-lightning", "input_price": 0.99, "input_price_cached": 0, "output_price": 0.99},
    {"model_keyword": "yi-large", "input_price": 20.00, "input_price_cached": 0, "output_price": 20.00},
    {"model_keyword": "yi-medium", "input_price": 2.50, "input_price_cached": 0, "output_price": 2.50},

    # === OpenAI ===
    {"model_keyword": "gpt-4o", "input_price": 18.00, "input_price_cached": 4.50, "output_price": 36.00},
    {"model_keyword": "gpt-4o-mini", "input_price": 1.08, "input_price_cached": 0.27, "output_price": 4.32},
    {"model_keyword": "gpt-4-turbo", "input_price": 72.00, "input_price_cached": 0, "output_price": 216.00},
    {"model_keyword": "gpt-3.5-turbo", "input_price": 3.60, "input_price_cached": 0, "output_price": 10.80},
    {"model_keyword": "o1", "input_price": 108.00, "input_price_cached": 27.00, "output_price": 432.00},
    {"model_keyword": "o1-mini", "input_price": 21.60, "input_price_cached": 5.40, "output_price": 86.40},

    # === Anthropic Claude ===
    {"model_keyword": "claude-3.5-sonnet", "input_price": 21.60, "input_price_cached": 2.16, "output_price": 108.00},
    {"model_keyword": "claude-3-opus", "input_price": 108.00, "input_price_cached": 10.80, "output_price": 540.00},
    {"model_keyword": "claude-3-haiku", "input_price": 1.80, "input_price_cached": 0.18, "output_price": 7.20},
]


class Command(BaseCommand):
    help = "Seed built-in pricing data for common LLM models"

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for item in BUILTIN_PRICING:
            obj, was_created = ModelPricing.objects.update_or_create(
                model_keyword=item["model_keyword"],
                is_builtin=True,
                defaults={
                    "input_price": item["input_price"],
                    "input_price_cached": item.get("input_price_cached", 0),
                    "output_price": item["output_price"],
                    "currency": "CNY",
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"完成: 新增 {created} 个, 更新 {updated} 个, 共 {len(BUILTIN_PRICING)} 个内置价格"
            )
        )
