from datetime import datetime

import pytz

from bot.config import settings


def formatted_now() -> str:
    """Consistent timestamp format used across embeds."""
    tz = pytz.timezone(settings.time_zone)
    return datetime.now(tz).strftime('%d %B %Y %I:%M:%S %p')