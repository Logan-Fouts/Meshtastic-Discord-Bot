from datetime import datetime


def formatted_now() -> str:
    """Consistent timestamp format used across embeds."""
    return datetime.now().strftime('%d %B %Y %I:%M:%S %p')