import asyncio
import logging

import discord

from bot.cogs.commands import register_commands
from bot.config import settings
from bot.core.discord_client import MeshBot


def run_discord_bot():
    client = MeshBot(intents=discord.Intents.default())
    register_commands(client)
    try:
        client.run(settings.token)
    except Exception as e:
        logging.error(f"An error occurred while running the bot: {e}")
    finally:
        asyncio.run(client.close())


if __name__ == "__main__":
    run_discord_bot()