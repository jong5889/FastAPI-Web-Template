from typing import Dict, Optional


def format_error(message: str, *, code: Optional[int] = None) -> Dict[str, str]:
    """Return a standardized error message dictionary."""
    payload = {"error": message}
    if code is not None:
        payload["code"] = str(code)
    return payload
