from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from apps.common.configs.settings import Settings, get_settings


def now(*, timespec: str = "auto") -> str:
    settings: Settings = get_settings()
    return datetime.now(ZoneInfo(settings.time_zone)).isoformat(timespec=timespec)

def today(*, fmt: str = "%Y-%m-%d") -> str:
    settings: Settings = get_settings()
    return datetime.now(ZoneInfo(settings.time_zone)).strftime(fmt)
