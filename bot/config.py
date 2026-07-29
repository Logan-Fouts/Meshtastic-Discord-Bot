import json
import logging


class Settings:
    """Loads and exposes config.json values as attributes."""

    def __init__(self, config_path="config.json"):
        config = self._load_config(config_path)
        self.token = config["discord_bot_token"]
        self.channel_id = int(config["discord_channel_id"])
        self.channel_names = config["channel_names"]
        self.time_zone = config["time_zone"]
        self.color = int(config["color"].lstrip('#'), 16)

    @staticmethod
    def _load_config(config_path):
        try:
            with open(config_path, "r") as config_file:
                config = json.load(config_file)
                config["channel_names"] = {int(k): v for k, v in config["channel_names"].items()}
                return config
        except FileNotFoundError:
            logging.critical(f"The {config_path} file was not found.")
            raise
        except json.JSONDecodeError:
            logging.critical(f"{config_path} is not a valid JSON file.")
            raise
        except Exception as e:
            logging.critical(f"An unexpected error occurred while loading {config_path}: {e}")
            raise


settings = Settings()
