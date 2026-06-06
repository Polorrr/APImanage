# AImanage SDK

AI 成本管理 SDK — 自动追踪 LLM 调用的 token 和费用。

## 安装

```bash
pip install aimanage
```

## 使用

```python
from aimanage import AIMonitor

# 初始化监控（只需一次）
monitor = AIMonitor(
    api_key="sk-你的平台Key",
    endpoint="http://your-platform.com",
    project="my-project",  # 可选
)

# 之后正常用 openai，自动监控
import openai

client = openai.OpenAI(
    api_key="tp-xxx",
    base_url="https://your-relay.com/v1"
)

response = client.chat.completions.create(
    model="mimo-v2.5-pro",
    messages=[{"role": "user", "content": "你好"}]
)

# 数据会自动上报到 AImanage 平台
```

## 特性

- **零侵入** — 不改用户的 API 调用链路
- **零延迟** — 异步上报，不影响响应速度
- **批量上报** — 攒够 10 条或每 30 秒自动上报
- **失败静默** — 上报失败不影响用户代码
- **自动拦截** — 猴子补丁 openai SDK，用户无感

## 许可证

MIT
