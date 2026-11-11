from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from tools._shared import err

DEFAULT_TZ = "Asia/Ho_Chi_Minh"
_FALLBACK_OFFSETS = {"Asia/Ho_Chi_Minh": 7, "UTC": 0}


def _zone(name: str):
    try:
        return ZoneInfo(name)
    except Exception:
        # Windows without tzdata: fall back for the two zones we rely on.
        if name in _FALLBACK_OFFSETS:
            return timezone(timedelta(hours=_FALLBACK_OFFSETS[name]), name)
        raise ValueError(f"unknown timezone '{name}', use an IANA name like Asia/Ho_Chi_Minh or UTC")


def get_current_time(timezone: str = DEFAULT_TZ) -> dict[str, Any]:  # noqa: A002 - arg name is the model-facing contract
    try:
        name = (timezone or DEFAULT_TZ).strip() if isinstance(timezone, str) else DEFAULT_TZ
        now = datetime.now(_zone(name))
        return {
            "tool": "get_current_time",
            "timezone": name,
            "iso": now.isoformat(timespec="seconds"),
            "date": now.strftime("%Y-%m-%d"),
            "weekday": now.strftime("%A"),
        }
    except Exception as exc:
        return err("get_current_time", exc)
