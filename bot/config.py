import os
import json
import logging


class Settings:
    """Loads and exposes config.json values as attributes."""

    def __init__(self, config_path="config.json"):
        self.token = os.environ["DISCORD_TOKEN"]
        self.channel_id = int(os.environ["DISCORD_CHANNEL_ID"])

        raw = os.environ.get("CHANNEL_NAMES", '{"0":"Broadcast"}')
        self.channel_names = {int(k): v for k, v in json.loads(raw).items()}

        self.time_zone = str(os.environ["TIME_ZONE"])
        self.color = int(os.environ["COLOR"].lstrip('#'), 16) # Convert from hex to int

settings = Settings()
