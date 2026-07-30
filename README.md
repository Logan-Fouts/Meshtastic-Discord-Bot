<h1 align="center">Meshtastic Discord Bot</h1>

## Purpose

> This project is a fork of [Kavitate/Meshtastic-Discord-Bot](https://github.com/Kavitate/Meshtastic-Discord-Bot). Credit to the original author for the base bot design and command structure — this fork extends it with environment-variable configuration, Docker support, and some auto-reply fixes.

This Discord bot bridges a [Meshtastic](https://meshtastic.org/) mesh network directly into a Discord server, using a Meshtastic-compatible device connected over serial/USB.

Having a Discord bot directly connected to the Meshtastic network lets multiple user interact with the mesh through one device and lessesn the barrier of entry for less technical users. Also, test your devices and get instant feedback on whether another node has received a message. It also lets you communicate on your local mesh network from anywhere in the world, right from Discord.

This project was inspired by the [Meshtastic Discord Bridge](https://github.com/raudette/meshtastic_discord_bridge) created by [raudette](https://github.com/raudette).

## Requirements

- Python 3.11+ (if running without Docker)
- A [Meshtastic-compatible device](https://meshtastic.org/docs/hardware/devices/) connected to the host machine via serial/USB
- A Discord bot application and token (see below)
- Docker + Docker Compose (optional, if running containerized) recommended

## Creating a Discord Bot

Before configuring the bot, you'll need a Discord application and bot token:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**.
2. Under **Bot**, click **Reset Token** (or **Add Bot** if prompted) and copy the token somewhere safe — you'll need it for the `DISCORD_TOKEN` variable below. Treat this token like a password; never commit it to source control.
3. Under **Bot** settings, make sure **Message Content Intent** is enabled if you plan to use any features that read message content.
4. Under **OAuth2 → URL Generator**, select the `bot` and `applications.commands` scopes, then under **Bot Permissions** select at minimum: `Send Messages`, `Read Message History`, `Use Slash Commands`, and `Embed Links`.
5. Copy the generated URL, open it in a browser, and invite the bot to your server.
6. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode), then right-click the channel you want the bot to post in and select **Copy Channel ID**. This is your `DISCORD_CHANNEL_ID`.

More detailed walkthroughs are available in [discord.py's bot setup guide](https://discordpy.readthedocs.io/en/stable/discord.html) and [Discord's own docs on finding IDs](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID).

## Configuration

The bot is configured entirely through environment variables. Create a `.env` file in the project root:

```
DISCORD_TOKEN=your-discord-bot-token
DISCORD_CHANNEL_ID=your-discord-channel-id
TIME_ZONE=America/New_York
COLOR=0x00FF00
```

Notes:
- `TIME_ZONE` should be a valid [tz database name](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568) (e.g. `America/Chicago`, `Europe/London`).
- Channel-to-command mappings (which mesh channel index maps to which slash command name) are also defined in your config — update these to match the channel names configured on your radio. All channel names must be unique. If you don't use all available channels, you can leave the extras unset or remove them.
- Never commit your `.env` file. Add it to `.gitignore`.

> Adjust the variable names above to match whatever your `bot/config.py` actually reads via `os.environ[...]` — update this section if your config differs.

## Running Locally (without Docker)

1. Clone the repository and enter the project directory:
   ```bash
   git clone https://github.com/Logan-Fouts/meshtastic-discord-bot.git
   cd Meshtastic-Discord-Bot
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create your `.env` file as described above, and make sure it's loaded into your shell environment (e.g. via `export $(cat .env | xargs)` or a tool like `python-dotenv`, depending on how `config.py` reads it).
5. Connect your Meshtastic device via USB. If you have multiple serial devices connected and need to target a specific one, update the `SerialInterface()` call in `bot/core/meshtastic_io.py` to pass an explicit port:
   ```python
   meshtastic.serial_interface.SerialInterface(devPath="/dev/YOUR_PORT")
   ```
6. Run the bot:
   ```bash
   python3 run.py
   ```

## Running with Docker

1. Make sure Docker and the Docker Compose plugin are installed:
   ```bash
   sudo apt install docker.io docker-compose-v2
   sudo usermod -aG docker $USER   # then log out/in, or run `newgrp docker`
   ```
2. Create your `.env` file as described above.
3. Identify the serial device path for your Meshtastic radio:
   ```bash
   ls /dev/ttyUSB* /dev/serial/by-id/
   ```
4. Update `docker-compose.yml` with the correct device path if it differs from `/dev/ttyUSB0`.
5. Build and start the container:
   ```bash
   docker compose up --build -d
   ```
6. View logs:
   ```bash
   docker compose logs -f
   ```

**Note on serial devices in Docker:** the container needs direct access to the Meshtastic device's serial port. If you're running in an environment where `/dev/ttyUSB0` doesn't appear or changes on reconnect (e.g. WSL2, which doesn't pass through USB devices by default), you may need [usbipd-win](https://github.com/dorssel/usbipd-win) on Windows, or a stable path from `/dev/serial/by-id/` instead. If you keep hitting permission errors, running the container with `privileged: true` is a simpler (but less locked-down) fallback.

## Commands

Once configured and running, the following slash commands are available in Discord:

- `/reply` — reply to whoever most recently sent a message (or broadcast), automatically routing to a DM or channel broadcast as appropriate.
- `/sendid` — send a direct message to a node by its hex node ID, e.g. `/sendid !7c5acfa4 Hello!`
- `/sendnum` — send a direct message to a node by its decimal node number, e.g. `/sendnum 2086326180 Hello!`
- `/active` — list active nodes seen in the last 15 minutes.
- `/help` — show a list of available bot commands.
- One command per configured mesh channel (e.g. `/your_channel_0`, `/your_channel_1`, etc.) — sends a message on that channel. These command names depend on your channel configuration.

## Quirks

After running the bot for months at a time, it can occasionally stop receiving mesh messages until the bot and radio are both rebooted. It's unclear whether this is a bot-side or radio-side issue — it has been observed running a LilyGO T-Beam Supreme.

A simple workaround is to schedule the bot to restart nightly (e.g. via a systemd timer, cron, or Docker's `restart: unless-stopped` combined with a scheduled `docker compose restart`). Since adopting a nightly restart, no further message hangs have been observed.

## Credits

Inspired by the [Meshtastic Discord Bridge](https://github.com/raudette/meshtastic_discord_bridge) created by [raudette](https://github.com/raudette).
