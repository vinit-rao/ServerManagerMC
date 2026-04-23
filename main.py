import discord
import os
import subprocess
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# ----------------------------
# Configuration
# ----------------------------
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Server Config
MC_FOLDER = "/home/vinit/mc-server-venus"
SERVER_JAR = "server.jar"
MAX_RAM = "4G"
SCREEN_NAME = "mc_server"
ALLOWED_USER = "vxtl"

# Channels
TERMINAL_CHANNEL_NAME = "terminal-mc"
CHAT_CHANNEL_NAME = "chat-mc"

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# State Variables for Terminal
terminal_message = None
terminal_lines = []
MAX_TERMINAL_LINES = 20

# State Variables for Chat
chat_message = None
chat_lines = []
MAX_CHAT_LINES = 30

ANSI_RED = "\u001b[31m"      # Errors & Deaths
ANSI_WHITE = "\u001b[37m"    # Regular Chat
ANSI_BRIGHT_RED = "\u001b[1;31m" # Discord User Tags
ANSI_RESET = "\u001b[0m"
ANSI_GREEN = "\u001b[32m"  # Server Start/Stop
ANSI_YELLOW = "\u001b[33m"  # Joins, Leaves, Advancements
ANSI_BLUE = "\u001b[34m"  # Discord tags
ANSI_CYAN = "\u001b[36m"  # Discord Messages


# ----------------------------
# UI Core Mechanics
# ----------------------------
async def update_terminal(action: str):
    global terminal_message, terminal_lines

    terminal_lines.append(action)
    if len(terminal_lines) > MAX_TERMINAL_LINES:
        terminal_lines.pop(0)

    display_text = "```ansi\n====== MC SERVER TERMINAL ======\n\n"
    display_text += "\n".join(terminal_lines)
    display_text += "\n```"

    if terminal_message:
        try:
            await terminal_message.edit(content=display_text)
        except discord.NotFound:
            pass


async def update_chat(formatted_line: str):
    """Updates the live chat message block."""
    global chat_message, chat_lines

    chat_lines.append(formatted_line)
    if len(chat_lines) > MAX_CHAT_LINES:
        chat_lines.pop(0)

    display_text = "```ansi\n====== LIVE SERVER CHAT ======\n\n"
    display_text += "\n".join(chat_lines)
    display_text += "\n```"

    if chat_message:
        try:
            await chat_message.edit(content=display_text)
        except discord.NotFound:
            pass


# ----------------------------
# MC -> Discord Log Reader
# ----------------------------
async def tail_minecraft_log():
    """Reads the Minecraft log file in real-time and updates the chat block."""
    log_path = os.path.join(MC_FOLDER, "logs", "latest.log")

    while not os.path.exists(log_path):
        await asyncio.sleep(2)

    with open(log_path, "r", encoding="utf-8") as f:
        f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.5)
                continue

            if "[Server thread/INFO]:" in line:
                clean_line = line.split("[Server thread/INFO]:")[-1].strip()

                # Filter out boring server noises
                boring_stuff = ["UUID of player", "logged in with entity id", "Preparing spawn area", "Done ("]
                if any(noise in clean_line for noise in boring_stuff):
                    continue

                # --- COLOR FILTERING ENGINE ---
                color = ANSI_RESET

                # 1. Player Chat (starts with <Username>)
                if clean_line.startswith("<"):
                    color = ANSI_RESET
                    # 2. Server Events (Joins, Leaves, Advancements)
                elif any(x in clean_line for x in [" joined the game", " left the game", "has made the advancement"]):
                    color = ANSI_YELLOW
                # 3. Discord Messages echoing in log
                elif clean_line.startswith("[Discord]"):
                    continue  # Skip these so we don't double-print Discord messages
                # 4. Death Messages (No brackets, just text like "Steve fell from a high place")
                elif not clean_line.startswith("["):
                    color = ANSI_RED

                # Update the chat UI
                await update_chat(f"{color}{clean_line}{ANSI_RESET}")


@bot.event
async def on_ready():
    global terminal_message, chat_message, terminal_lines, chat_lines
    print(f"✅ {bot.user} is online!")

    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="vinitrao.com"
    ))

    # Setup Terminal Channel
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == TERMINAL_CHANNEL_NAME:
                await channel.purge(limit=100)
                terminal_lines = ["Terminal initialized. Awaiting commands..."]
                # Added a little style to the header
                initial_text = "```ansi\n\u001b[1;31m┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃      MC SERVER TERMINAL v2.0       ┃\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\u001b[0m\n```"
                terminal_message = await channel.send(initial_text)
                break

    # Setup Chat Channel
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == CHAT_CHANNEL_NAME:
                await channel.purge(limit=100)
                chat_lines = [f"{ANSI_GREEN}Chat bridge initialized. Awaiting messages...{ANSI_RESET}"]
                # Added a little style to the header
                initial_chat_text = "```ansi\n\u001b[1;31m┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃       LIVE SERVER CHAT LOG        ┃\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\u001b[0m\n```"
                chat_message = await channel.send(initial_chat_text)
                break

    # Start the log reader
    bot.loop.create_task(tail_minecraft_log())

# ----------------------------
# Message Routing (Discord -> MC)
# ----------------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == TERMINAL_CHANNEL_NAME:
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        await bot.process_commands(message)
        return

    if message.channel.name == CHAT_CHANNEL_NAME:
        # Instantly delete the Discord user's message
        try:
            await message.delete()
        except discord.Forbidden:
            pass

        safe_text = message.clean_content.replace('\n', ' ').replace('"', '\\"')
        safe_user = message.author.display_name.replace('"', '\\"')

        # Send it to the Minecraft Server using tellraw
        mc_json = f'{{"text":"[Discord] {safe_user}: {safe_text}", "color":"aqua"}}'
        tellraw_cmd = f'tellraw @a {mc_json}\n'

        try:
            command = ['screen', '-S', SCREEN_NAME, '-p', '0', '-X', 'stuff', tellraw_cmd]
            subprocess.run(command, check=True)

            # Instantly update the Discord UI so the user sees their message
            discord_log_line = f"{ANSI_CYAN}[Discord] {safe_user}: {safe_text}{ANSI_RESET}"
            await update_chat(discord_log_line)

        except Exception as e:
            print(f"Error sending message to game: {e}")
            await update_chat(f"{ANSI_RED}>> ERROR: Failed to send message to game.{ANSI_RESET}")

    await bot.process_commands(message)


# ----------------------------
# Commands
# ----------------------------
@bot.command()
async def help(ctx):
    await update_terminal(f"[{ctx.author.name}] requested help.")
    help_text = (
        "--- AVAILABLE COMMANDS ---\n"
        "!startserver  : Boots up the Minecraft server\n"
        "!stopserver   : Safely saves and shuts down the server\n"
        "!version      : Shows the current modpack/version info\n"
        f"!server <cmd> : Run console commands (Restricted to {ALLOWED_USER})\n"
        "--------------------------"
    )
    help_msg = await ctx.send(f"```text\n{help_text}\n```")
    await help_msg.delete(delay=15)


@bot.command()
async def startserver(ctx):
    await update_terminal(f"[{ctx.author.name}] initiated server boot sequence...")
    try:
        command = ['screen', '-dmS', SCREEN_NAME, 'java', f'-Xmx{MAX_RAM}', '-jar', SERVER_JAR, 'nogui']
        subprocess.run(command, cwd=MC_FOLDER, check=True)
        await update_terminal(">> SUCCESS: Server is starting in the background.")
        await update_chat(f"{ANSI_GREEN}>> Server is starting up...{ANSI_RESET}")
    except Exception as e:
        await update_terminal(f">> ERROR: Failed to start server. ({e})")


@bot.command()
async def stopserver(ctx):
    await update_terminal(f"[{ctx.author.name}] initiated server shutdown...")
    try:
        command = ['screen', '-S', SCREEN_NAME, '-p', '0', '-X', 'stuff', 'stop\n']
        subprocess.run(command, check=True)
        await update_terminal(">> SUCCESS: Stop command sent. Saving chunks...")
        await update_chat(f"{ANSI_RED}>> Server is shutting down...{ANSI_RESET}")
    except Exception as e:
        await update_terminal(f">> ERROR: Could not send stop command. Is the server running?")


@bot.command()
async def server(ctx, *, mc_command: str):
    if ctx.author.name.lower() != ALLOWED_USER.lower():
        await update_terminal(f"⚠️ [SECURITY] {ctx.author.name} attempted unauthorized console access.")
        return

    await update_terminal(f"[{ctx.author.name}] ran console command: /{mc_command}")
    try:
        command = ['screen', '-S', SCREEN_NAME, '-p', '0', '-X', 'stuff', f'{mc_command}\n']
        subprocess.run(command, check=True)
    except Exception as e:
        await update_terminal(f">> ERROR: Failed to execute command. ({e})")


@bot.command()
async def version(ctx):
    version_file = os.path.join(MC_FOLDER, "version.txt")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            v_info = f.read().strip()
        await update_terminal(f"[{ctx.author.name}] checked version: {v_info}")
    else:
        await update_terminal(f"[{ctx.author.name}] checked version: (No version.txt found)")


bot.run(token)