#!/usr/bin/env python
"""Seed built-in model pricing data into the database.

Usage:
    python scripts/seed_pricing.py

Run from the backend/ directory:
    cd backend && python scripts/seed_pricing.py
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.pricing.models import ModelPricing


BUILTIN_PRICING = [
    # OpenAI
    {"keyword": "gpt-4o",            "input": 18.0,  "output": 72.0},
    {"keyword": "gpt-4o-mini",       "input": 1.08,  "output": 4.32},
    {"keyword": "gpt-4-turbo",       "input": 72.0,  "output": 216.0},
    {"keyword": "gpt-3.5-turbo",     "input": 3.6,   "output": 10.8},
    {"keyword": "o1",                "input": 108.0, "output": 432.0},
    {"keyword": "o3-mini",           "input": 7.92,  "output": 31.68},

    # Anthropic
    {"keyword": "claude-3-5-sonnet", "input": 21.6,  "output": 108.0},
    {"keyword": "claude-3-opus",     "input": 108.0, "output": 540.0},
    {"keyword": "claude-3-haiku",    "input": 1.8,   "output": 9.0},

    # DeepSeek
    {"keyword": "deepseek-chat",     "input": 1.0,   "output": 2.0},
    {"keyword": "deepseek-reasoner", "input": 4.0,   "output": 16.0},
    {"keyword": "deepseek-coder",    "input": 1.0,   "output": 2.0},

    # 通义千问
    {"keyword": "qwen-max",          "input": 20.0,  "output": 60.0},
    {"keyword": "qwen-plus",         "input": 0.8,   "output": 2.0},
    {"keyword": "qwen-turbo",        "input": 0.3,   "output": 0.6},
    {"keyword": "qwen-long",         "input": 0.5,   "output": 2.0},

    # 智谱
    {"keyword": "glm-4",             "input": 100.0, "output": 100.0},
    {"keyword": "glm-4-flash",       "input": 1.0,   "output": 1.0},
    {"keyword": "glm-3-turbo",       "input": 1.0,   "output": 1.0},

    # 百度文心
    {"keyword": "ernie-4.0",         "input": 120.0, "output": 120.0},
    {"keyword": "ernie-3.5",         "input": 8.0,   "output": 8.0},
    {"keyword": "ernie-speed",       "input": 0.0,   "output": 0.0},

    # MiniMax
    {"keyword": "abab6.5-chat",      "input": 10.0,  "output": 30.0},
    {"keyword": "abab5.5-chat",      "input": 10.0,  "output": 30.0},

    # 零一万物
    {"keyword": "yi-large",          "input": 6.0,   "output": 6.0},
    {"keyword": "yi-medium",         "input": 1.0,   "output": 1.0},

    # Moonshot
    {"keyword": "moonshot-v1-128k",  "input": 60.0,  "output": 60.0},
    {"keyword": "moonshot-v1-32k",   "input": 48.0,  "output": 48.0},
    {"keyword": "moonshot-v1-8k",    "input": 12.0,  "output": 12.0},

    # Google
    {"keyword": "gemini-2.0-flash",  "input": 0.72,  "output": 2.88},
    {"keyword": "gemini-1.5-pro",    "input": 25.2,  "output": 75.6},
]

# All prices are in CNY per 1K tokens


def seed():
    """Seed built-in pricing data. Skips duplicates."""
    created_count = 0
    skipped_count = 0

    for item in BUILTIN_PRICING:
        _, created = ModelPricing.objects.update_or_create(
            model_keyword=item["keyword"],
            is_builtin=True,
            defaults={
                "input_price": item["input"],
                "output_price": item["output"],
                "currency": "CNY",
                "is_builtin": True,
            },
        )
        if created:
            created_count += 1
            print(f"  Created: {item['keyword']} — ¥{item['input']}/¥{item['output']}")
        else:
            skipped_count += 1
            print(f"  Exists:  {item['keyword']}")

    print(f"\nDone: {created_count} created, {skipped_count} skipped (already exist)")


if __name__ == "__main__":
    print("Seeding built-in model pricing data...\n")
    seed()
