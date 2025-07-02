"""Wrapper utilities for performing HTTP API calls."""

from typing import Any, Dict
try:
    import httpx  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    httpx = None  # type: ignore


def fetch_json(url: str, *, method: str = "GET", **kwargs: Any) -> Dict[str, Any]:
    """Send an HTTP request and return the JSON payload.

    The function raises ``httpx.HTTPStatusError`` if the response status is an
    error. Additional keyword arguments are forwarded to ``httpx.Client.request``.
    """

    if httpx is None:
        raise ImportError("httpx is required to use fetch_json")

    with httpx.Client() as client:
        response = client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
