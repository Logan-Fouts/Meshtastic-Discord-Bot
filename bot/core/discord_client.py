import asyncio
import queue
import sys
import time
from datetime import datetime

import discord
import pytz
from discord import app_commands

from bot.config import settings
from bot.core.meshtastic_io import connect_interface
from bot.core.queues import discordtomesh, meshtodiscord, nodelistq

debug = False

class MeshBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)
        self.iface = None  # Set once the mesh interface connects.

    async def setup_hook(self) -> None:
        self.bg_task = self.loop.create_task(self.background_task())
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    def _build_nodelist_chunks(self):
        """Builds the '/active' node list, split into chunks of 10 rows."""
        nodelist = ["**Nodes seen in the last 15 minutes:**\n"]
        nodes = self.iface.nodes

        for node in nodes:
            try:
                node_id = str(nodes[node]['user']['id'])
                longname = str(nodes[node]['user']['longName'])
                hopsaway = str(nodes[node]['hopsAway']) if "hopsAway" in nodes[node] else "0"
                snr = str(nodes[node]['snr']) if "snr" in nodes[node] else "?"

                if "lastHeard" in nodes[node]:
                    ts = int(nodes[node]['lastHeard'])
                    timezone = pytz.timezone(settings.time_zone)
                    local_time = datetime.fromtimestamp(ts, tz=pytz.utc).astimezone(timezone)
                    timestr = local_time.strftime('%d %B %Y %I:%M:%S %p')
                else:
                    ts = time.time() - (16 * 60)  # Treat as outside the 15-minute window.
                    timestr = "Unknown"

                if ts > time.time() - (15 * 60):
                    nodelist.append(
                        f"\n**ID:** {node_id} | **Long Name:** {longname} | "
                        f"**Hops:** {hopsaway} | **SNR:** {snr} | **Last Heard:** {timestr}"
                    )
            except KeyError as e:
                print(e)
                pass

        return ["".join(nodelist[i:i + 10]) for i in range(0, len(nodelist), 10)]

    async def background_task(self):
        await self.wait_until_ready()
        counter = 0
        nodelist_chunks = []  # Initialized here so it's never undefined on first pass.
        channel = self.get_channel(settings.channel_id)

        try:
            self.iface = connect_interface()
        except Exception as ex:
            print(f"Error: Could not connect {ex}")
            sys.exit(1)

        while not self.is_closed():
            counter += 1

            if counter % 12 == 1:  # ~every 1 minute (every 12th tick, 5s apart)
                nodelist_chunks = self._build_nodelist_chunks()

            # Mesh -> Discord
            try:
                meshmessage = meshtodiscord.get_nowait()
                if isinstance(meshmessage, discord.Embed):
                    await channel.send(embed=meshmessage)
                else:
                    await channel.send(meshmessage)
                meshtodiscord.task_done()
            except queue.Empty:
                pass

            # Discord -> Mesh
            try:
                meshmessage = discordtomesh.get_nowait()
            except queue.Empty:
                meshmessage = None

            if meshmessage is not None:
                try:
                    if meshmessage.startswith('channel='):
                        channel_index = int(meshmessage[8:meshmessage.find(' ')])
                        message = meshmessage[meshmessage.find(' ') + 1:]
                        self.iface.sendText(message, channelIndex=channel_index)
                    elif meshmessage.startswith('nodenum='):
                        nodenum = int(meshmessage[8:meshmessage.find(' ')])
                        self.iface.sendText(meshmessage[meshmessage.find(' ') + 1:], destinationId=nodenum)
                    else:
                        self.iface.sendText(meshmessage)
                except Exception as e:
                    print(f"Error sending to mesh: {e}")
                finally:
                    discordtomesh.task_done()

            # '/active' requests
            try:
                nodelistq.get_nowait()
                for chunk in nodelist_chunks:
                    await channel.send(chunk)
                nodelistq.task_done()
            except queue.Empty:
                pass

            await asyncio.sleep(5)