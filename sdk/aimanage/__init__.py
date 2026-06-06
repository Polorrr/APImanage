"""aimanage — AI 成本管理 SDK

用法：
    from aimanage import AIMonitor

    monitor = AIMonitor(
        api_key="sk-xxx",
        endpoint="http://localhost:8000",
    )

    # 之后正常用 openai，自动上报
    import openai
    client = openai.OpenAI(api_key="tp-xxx", base_url="https://xxx/v1")
    resp = client.chat.completions.create(model="mimo-v2.5-pro", messages=[...])
"""

from .monitor import AIMonitor

__version__ = "0.1.0"
__all__ = ["AIMonitor"]
