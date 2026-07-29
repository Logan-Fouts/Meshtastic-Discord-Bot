import discord
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

from bot.config import settings
from bot.core import queues
from bot.core.queues import meshtodiscord
from bot.utils.utils import formatted_now

debug = True

def on_connection_mesh(interface, topic=pub.AUTO_TOPIC):
    print(interface.myInfo)

def get_long_name(node_id, nodes):
    if node_id in nodes:
        return nodes[node_id]['user'].get('longName', 'Unknown')
    return 'Unknown'


def on_receive_mesh(packet, interface):
    """Called when a packet arrives from the mesh network."""
    try:
        if packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':

            if debug:
                print("Text message packet received")
                print(f"Packet: {packet}")

            # Check if 'channel' is present in the top-level packet.
            if 'channel' in packet:
                channel_index = packet['channel']
            else:
                # Check if 'channel' is present in the decoded packet.
                if 'channel' in packet['decoded']:
                    channel_index = packet['decoded']['channel']
                else:
                    channel_index = 0  # Default to channel 0 if not present.

                    if debug:
                        print("Channel not found in packet, defaulting to channel 0")

            channel_name = settings.channel_names.get(channel_index, f"Unknown Channel ({channel_index})")
            current_time = formatted_now()
            nodes = interface.nodes

            from_long_name = get_long_name(packet['fromId'], nodes)
            to_long_name = get_long_name(packet['toId'], nodes) if packet['toId'] != '^all' else 'All Nodes'

            # Set Auto Reply
            if packet['toId'] == '^all':
                destination = "brdcst"
                queues.autoreplydest = "broadcast"
            else:
                destination = "dm"
                queues.autoreplydest = packet['fromId']

            if debug:
                print("Set Auto Reply To:", queues.autoreplydest)

            embed = discord.Embed(
                title=f"{from_long_name} ({packet['fromId']})",
                description=packet['decoded']['text'],
                color=settings.color
            )
            embed.add_field(name="", value=destination, inline=False)
            embed.set_footer(text=f"{current_time}")

            meshtodiscord.put(embed)
    except Exception as e:
        print(f"Error handling mesh packet: {e}")


def connect_interface():
    """Subscribes mesh callbacks and opens the serial interface. Raises on failure."""
    pub.subscribe(on_receive_mesh, "meshtastic.receive")
    pub.subscribe(on_connection_mesh, "meshtastic.connection.established")
    return meshtastic.serial_interface.SerialInterface()