"""Core monitor — patches openai SDK and collects usage data."""
import time
import logging
from datetime import datetime, timezone

logger = logging.getLogger("aimanage")


class AIMonitor:
    """AI 成本管理监控器

    初始化后自动拦截 openai SDK 的调用，收集 token 用量并异步上报。

    用法：
        monitor = AIMonitor(api_key="sk-xxx", endpoint="http://localhost:8000")
        # 之后正常用 openai 即可
    """

    def __init__(self, api_key: str, endpoint: str, project: str = ""):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.project = project
        self._buffer = []
        self._last_flush = time.time()
        self._flush_interval = 30  # 秒
        self._batch_size = 10
        self._patched = False
        self._patch()

    def _patch(self):
        """Patch openai SDK to intercept calls."""
        if self._patched:
            return

        try:
            import openai
        except ImportError:
            logger.warning("aimanage: openai package not found, SDK monitoring disabled")
            return

        monitor = self

        # Patch chat.completions.create
        original_create = openai.resources.chat.completions.Completions.create

        def patched_create(self_resource, *args, **kwargs):
            start_time = time.time()
            model = kwargs.get("model", "unknown")

            # Call original method
            response = original_create(self_resource, *args, **kwargs)

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Extract usage
            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "prompt_tokens", None) if usage else None
            output_tokens = getattr(usage, "completion_tokens", None) if usage else None

            # Build record
            record = {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "is_error": False,
                "error_message": None,
            }

            monitor._add_record(record)
            return response

        # Patch streaming version
        original_stream_create = openai.resources.chat.completions.Completions.create

        # Apply patch
        openai.resources.chat.completions.Completions.create = patched_create
        self._patched = True
        logger.info("aimanage: openai SDK patched successfully")

    def _add_record(self, record: dict):
        """Add a record to buffer, flush if needed."""
        self._buffer.append(record)

        # Flush if buffer is full or interval elapsed
        now = time.time()
        if len(self._buffer) >= self._batch_size or (now - self._last_flush) >= self._flush_interval:
            self.flush()

    def flush(self):
        """Send buffered records to the platform."""
        if not self._buffer:
            return

        records = self._buffer.copy()
        self._buffer.clear()
        self._last_flush = time.time()

        # Send in background thread
        import threading
        threading.Thread(
            target=self._send_batch,
            args=(records,),
            daemon=True,
        ).start()

    def _send_batch(self, records: list):
        """Send a batch of records to the platform."""
        try:
            import requests
            resp = requests.post(
                f"{self.endpoint}/api/v1/report/",
                json={
                    "api_key": self.api_key,
                    "project": self.project,
                    "records": records,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                logger.debug(f"aimanage: reported {data.get('data', {}).get('accepted', 0)} records")
            else:
                logger.warning(f"aimanage: report failed with status {resp.status_code}")
        except Exception as e:
            # Silent fail — never affect user's code
            logger.debug(f"aimanage: report error: {e}")

    def __del__(self):
        """Flush remaining records on cleanup."""
        try:
            self.flush()
        except Exception:
            pass
