from datetime import datetime


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return a formatted datetime string."""
    return dt.strftime(fmt)
