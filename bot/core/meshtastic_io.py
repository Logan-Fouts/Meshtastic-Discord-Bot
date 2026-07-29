import discord
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

from bot.config import settings
from bot.core.queues import meshtodiscord
from bot.utils.utils import formatted_now


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
            print("Text message packet received")  # For debugging.
            print(f"Packet: {packet}")  # Print the entire packet for debugging.

            # Check if 'channel' is present in the top-level packet.
            if 'channel' in packet:
                channel_index = packet['channel']
            else:
                # Check if 'channel' is present in the decoded packet.
                if 'channel' in packet['decoded']:
                    channel_index = packet['decoded']['channel']
                else:
                    channel_index = 0  # Default to channel 0 if not present.
                    print("Channel not found in packet, defaulting to channel 0")  # For debugging.

            channel_name = settings.channel_names.get(channel_index, f"Unknown Channel ({channel_index})")

            current_time = formatted_now()

            nodes = interface.nodes
            from_long_name = get_long_name(packet['fromId'], nodes)
            to_long_name = get_long_name(packet['toId'], nodes) if packet['toId'] != '^all' else 'All Nodes'

            embed = discord.Embed(title="Message Received", description=packet['decoded']['text'], color=settings.color)
            embed.add_field(name="From Node", value=f"{from_long_name} ({packet['fromId']})", inline=True)
            embed.set_footer(text=f"{current_time}")

            if packet['toId'] == '^all':
                embed.add_field(name="To Channel", value=channel_name, inline=True)
            else:
                embed.add_field(name="To Node", value=f"{to_long_name} ({packet['toId']})", inline=True)

            meshtodiscord.put(embed)

    except KeyError:  # Catch empty packet.
        pass
    except Exception as e:  # Catch any other exceptions.
        print(f"Unexpected error: {e}")  # For debugging.
        pass


def connect_interface():
    """Subscribes mesh callbacks and opens the serial interface. Raises on failure."""
    pub.subscribe(on_receive_mesh, "meshtastic.receive")
    pub.subscribe(on_connection_mesh, "meshtastic.connection.established")
    return meshtastic.serial_interface.SerialInterface()