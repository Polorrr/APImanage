"""Pricing detection service — send probe requests to upstream APIs."""
import httpx


def detect_pricing(base_url: str, api_key: str, model: str) -> dict:
    """
    Send a minimal chat request to detect if the upstream returns usage data
    and attempt to match pricing from the built-in table.
    """
    result = {
        "model": model,
        "has_usage": False,
        "input_tokens": None,
        "output_tokens": None,
        "latency_ms": 0,
    }

    import time

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    body = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
    }

    try:
        start = time.monotonic()
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                json=body,
                headers=headers,
            )
            result["latency_ms"] = int((time.monotonic() - start) * 1000)

            if resp.status_code == 200:
                data = resp.json()
                usage = data.get("usage", {})
                if usage.get("prompt_tokens") is not None:
                    result["has_usage"] = True
                    result["input_tokens"] = usage["prompt_tokens"]
                    result["output_tokens"] = usage.get("completion_tokens", 0)
    except Exception:
        pass

    return result
