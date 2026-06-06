"""测试 SDK 完整流程"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sdk"))

# 读取真实的 API Key
key_file = os.path.join(os.path.dirname(__file__), "sdk_key.txt")
if os.path.exists(key_file):
    with open(key_file) as f:
        SDK_KEY = f.read().strip()
else:
    print("请先创建 SDK Key")
    sys.exit(1)

from aimanage import AIMonitor

monitor = AIMonitor(
    api_key=SDK_KEY,
    endpoint="http://localhost:8000",
    project="test-project",
)

print("=== AImanage SDK 测试 ===")
print(f"SDK Key: {SDK_KEY[:10]}...{SDK_KEY[-6:]}")
print()

# 调用小米 API
print("1. 直接调用小米 MiMo API（不走代理）...")
try:
    import openai

    client = openai.OpenAI(
        api_key="tp-chmnl96odrgkep3f42xfrrloiuojxqrp0i1ygm7dxat488xj",
        base_url="https://token-plan-cn.xiaomimimo.com/v1",
    )

    for i in range(3):
        resp = client.chat.completions.create(
            model="mimo-v2.5-pro",
            messages=[{"role": "user", "content": f"测试第{i+1}次：用一句话介绍Python"}],
            max_tokens=30,
        )
        usage = resp.usage
        print(f"   第{i+1}次: tokens in={usage.prompt_tokens}, out={usage.completion_tokens}")

except Exception as e:
    print(f"   API 调用失败: {e}")
    # 用模拟数据
    for i in range(3):
        monitor._add_record({
            "model": "mimo-v2.5-pro",
            "input_tokens": 250 + i,
            "output_tokens": 30 + i,
            "latency_ms": 2000 + i * 100,
            "is_error": False,
            "error_message": None,
        })

print()
print("2. 上报数据到平台...")
monitor.flush()

import time
time.sleep(3)

print()
print("3. 验证平台数据...")
try:
    import requests
    base = "http://localhost:8000/api"
    r = requests.post(f"{base}/auth/login/", json={"email": "admin@aimanage.com", "password": "admin123456"})
    token = r.json()["data"]["access"]
    h = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{base}/stats/calls/", headers=h, timeout=5)
    data = r.json()["data"]
    print(f"   调用日志总数: {data['count']} 条")
    print()
    print("   最新记录:")
    for log in data["results"][:5]:
        src = "SDK" if log["data_source"] == "sdk" else "代理"
        print(f"   - [{src}] {log['model']}: in={log['input_tokens_reported']}, out={log['output_tokens_reported']}, cost=¥{log['cost_yuan']}")

    r = requests.get(f"{base}/stats/overview/", headers=h, timeout=5)
    overview = r.json()["data"]
    print()
    print(f"   总消耗: ¥{overview['total_cost']}")
    print(f"   总调用: {overview['total_calls']} 次")

except Exception as e:
    print(f"   验证失败: {e}")

print()
print("=== 测试完成 ===")
print("打开 http://localhost:3000 查看 Dashboard！")
