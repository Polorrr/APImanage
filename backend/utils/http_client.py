"""HTTP client utility — thin wrapper around httpx for LLM API proxying."""
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Default timeout for LLM requests (longer for large responses)
DEFAULT_TIMEOUT = 120.0

# Default timeout for quick requests (model listing, health checks)
QUICK_TIMEOUT = 15.0


def make_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    json_body: dict | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> httpx.Response:
    """
    Make an HTTP request to an external API.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Target URL
        headers: Request headers
        json_body: JSON body for POST/PUT
        timeout: Request timeout in seconds

    Returns:
        httpx.Response object

    Raises:
        httpx.HTTPError: On request failure
    """
    with httpx.Client(timeout=timeout) as client:
        return client.request(
            method,
            url,
            headers=headers,
            json=json_body,
        )


def post_json(
    url: str,
    json_body: dict,
    headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """
    Post JSON to a URL and return the parsed response.

    Returns:
        Parsed JSON response as dict

    Raises:
        httpx.HTTPError: On request failure
        ValueError: If response is not valid JSON
    """
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)

    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=json_body, headers=default_headers)
        resp.raise_for_status()
        return resp.json()
