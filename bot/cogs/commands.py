import asyncio

import discord

from bot.config import settings
from bot.core.queues import discordtomesh, nodelistq
from bot.ui.ui import HelpView
from bot.utils.utils import formatted_now


def register_commands(client):
    """Attaches all slash commands to the given MeshBot's command tree."""
    channel_names = settings.channel_names

    @client.tree.command(name="help", description="Shows the help message.")
    async def help_command(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        help_text = ("**Command List**\n"
                     "`/sendid` - Send a message to another node.\n"
                     "`/sendnum` - Send a message to another node.\n"
                     "`/active` - Shows all active nodes.\n"
                     "`/help` - Shows this help message.\n")

        for _, channel_name in channel_names.items():
            help_text += f"`/{channel_name.lower()}` - Send a message in the {channel_name} channel.\n"

        embed = discord.Embed(title="Meshtastic Bot Help", description=help_text, color=settings.color)
        embed.set_footer(text="Meshtastic Discord Bot by Kavitate")
        embed.set_image(url="https://i.imgur.com/qvo2NkW.jpeg")

        view = HelpView()
        await interaction.followup.send(embed=embed, view=view)

    @client.tree.command(name="sendid", description="Send a message to a specific node.")
    async def sendid(interaction: discord.Interaction, nodeid: str, message: str):
        try:
            # Strip the leading '!' if present.
            if nodeid.startswith('!'):
                nodeid = nodeid[1:]

            # Convert hexadecimal node ID to decimal.
            nodenum = int(nodeid, 16)

            embed = discord.Embed(title="Sending Message", description=message, color=settings.color)
            embed.add_field(name="To Node:", value=f"!{nodeid}", inline=True)
            embed.set_footer(text=formatted_now())
            await interaction.response.send_message(embed=embed, ephemeral=False)
            discordtomesh.put(f"nodenum={nodenum} {message}")
        except ValueError:
            error_embed = discord.Embed(title="Error", description="Invalid hexadecimal node ID.", color=settings.color)
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @client.tree.command(name="sendnum", description="Send a message to a specific node.")
    async def sendnum(interaction: discord.Interaction, nodenum: int, message: str):
        embed = discord.Embed(title="Sending Message", description=message, color=settings.color)
        embed.add_field(name="To Node:", value=str(nodenum), inline=True)
        embed.set_footer(text=formatted_now())
        await interaction.response.send_message(embed=embed)
        discordtomesh.put(f"nodenum={nodenum} {message}")

    # Dynamically create one command per configured mesh channel.
    def _make_channel_command(index: int, name: str):
        @client.tree.command(name=name.lower(), description=f"Send a message in the {name} channel.")
        async def send_channel_message(interaction: discord.Interaction, message: str):
            embed = discord.Embed(title=f"Sending Message to {name}:", description=message, color=settings.color)
            embed.set_footer(text=formatted_now())
            await interaction.response.send_message(embed=embed)
            discordtomesh.put(f"channel={index} {message}")
        return send_channel_message

    for channel_index, channel_name in channel_names.items():
        _make_channel_command(channel_index, channel_name)

    @client.tree.command(name="active", description="Lists all active nodes.")
    async def active(interaction: discord.Interaction):
        await interaction.response.defer()
        nodelistq.put(True)
        await asyncio.sleep(1)
        await interaction.delete_original_response()