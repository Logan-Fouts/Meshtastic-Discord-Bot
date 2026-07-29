import asyncio
import logging
import discord

from bot.cogs.commands import register_commands
from bot.config import settings
from bot.core.discord_client import MeshBot


async def run_discord_bot():
    client = MeshBot(intents=discord.Intents.default())
    register_commands(client)

    @client.event
    async def on_ready():
        await client.tree.sync()
        print(f"Logged in as {client.user}")

    try:
        await client.start(settings.token)
    except Exception as e:
        logging.error(f"An error occurred while running the bot: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run_discord_bot())