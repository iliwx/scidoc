"""Jalali (Persian) date formatting utilities."""
import time
from datetime import datetime
from typing import Optional


def format_jalali_date(timestamp: int) -> str:
    """Format Unix timestamp as Jalali date string."""
    try:
        import jdatetime
        dt = datetime.fromtimestamp(timestamp)
        jdt = jdatetime.datetime.fromgregorian(datetime=dt)
        return jdt.strftime('%Y/%m/%d')
    except ImportError:
        # Fallback to Gregorian if jdatetime not available
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y/%m/%d')
    except Exception:
        return "نامشخص"


def format_jalali_datetime(timestamp: int) -> str:
    """Format Unix timestamp as Jalali date+time string."""
    try:
        import jdatetime
        dt = datetime.fromtimestamp(timestamp)
        jdt = jdatetime.datetime.fromgregorian(datetime=dt)
        return jdt.strftime('%Y/%m/%d %H:%M')
    except ImportError:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y/%m/%d %H:%M')
    except Exception:
        return "نامشخص"


def days_until(timestamp: int) -> int:
    """Calculate days until a timestamp."""
    now = int(time.time())
    if timestamp <= now:
        return 0
    return (timestamp - now) // 86400


def format_remaining_days(timestamp: int) -> str:
    """Format remaining days as Persian string."""
    days = days_until(timestamp)
    if days == 0:
        return "امروز"
    elif days == 1:
        return "1 روز"
    else:
        return f"{days} روز"


def format_duration_days(days: int) -> str:
    """Format duration days as Persian string."""
    if days < 30:
        return f"{days} روزه"
    elif days % 30 == 0:
        months = days // 30
        return f"{months} ماهه"
    else:
        return f"{days} روزه"


def format_price(price: int) -> str:
    """Format price with thousands separator."""
    return f"{price:,}"
