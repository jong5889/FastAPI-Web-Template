from datetime import datetime

import pytest
from app.utils import format_datetime, format_error

try:
    from app.utils import fetch_json
    import httpx
except Exception:
    fetch_json = None

from unittest.mock import patch


def test_format_datetime():
    dt = datetime(2020, 1, 2, 3, 4, 5)
    assert format_datetime(dt) == "2020-01-02 03:04:05"


def test_format_error():
    assert format_error("fail", code=400) == {"error": "fail", "code": "400"}


@pytest.mark.skipif(fetch_json is None, reason="httpx not installed")
def test_fetch_json():
    mock_request = httpx.Request("GET", "http://example.com")
    mock_response = httpx.Response(200, json={"ok": True}, request=mock_request)
    with patch("app.utils.api_helpers.httpx.Client.request", return_value=mock_response):
        data = fetch_json("http://example.com")
        assert data == {"ok": True}
