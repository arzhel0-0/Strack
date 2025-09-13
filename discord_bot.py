import discord
from discord.ext import commands
import json
import os
import time
import asyncio
import random
from datetime import datetime, timezone
import logging
from dotenv import load_dotenv

# ---------------------- SETUP ----------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

MESSAGE_COUNTS_FILE = 'message_counts.json'
BOT_LOGS_FILE = 'bot_logs.json'
EXCLUDED_CHANNEL_ID = int(os.getenv('EXCLUDED_CHANNEL_ID', 0))

PING_RESPONSES = [
    "⚡ Beep boop! I’m awake and ready, what’s up?",
    "👋 You called? I have risen from my digital nap!",
    "💡 I’m online, alive, and thriving — what do you need?",
    "✨ Hey there! The bot has entered the chat.",
    "📢 Someone pinged me? Don’t worry, I’m wide awake now!",
    "🎮 Yo, I’ve respawned! Ready for action.",
    "🤖 Bot here! Running at 100% power."
]

# ---------------------- HELPER FUNCTIONS ----------------------
def load_message_counts():
    default_data = {"counts": {}, "timestamps": {}, "last_reset": int(time.time())}
    if not os.path.exists(MESSAGE_COUNTS_FILE):
        save_message_counts(default_data)
        return default_data
    try:
        with open(MESSAGE_COUNTS_FILE, 'r') as f:
            data = json.load(f)
            data.setdefault("counts", {})
            data.setdefault("timestamps", {})
            data.setdefault("last_reset", int(time.time()))
            return data
    except Exception as e:
        logger.error(f"Error loading {MESSAGE_COUNTS_FILE}: {e}")
        save_message_counts(default_data)
        return default_data

def save_message_counts(data):
    try:
        temp_file = MESSAGE_COUNTS_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, MESSAGE_COUNTS_FILE)
    except Exception as e:
        logger.error(f"Error saving message counts: {e}")

def load_bot_logs():
    default_data = {"logs": []}
    if not os.path.exists(BOT_LOGS_FILE):
        save_bot_log("init", f"Created {BOT_LOGS_FILE}")
        return default_data
    try:
        with open(BOT_LOGS_FILE, 'r') as f:
            data = json.load(f)
            data.setdefault("logs", [])
            return data
    except Exception as e:
        logger.error(f"Error loading {BOT_LOGS_FILE}: {e}")
        return default_data

def save_bot_log(event, details):
    try:
        data = load_bot_logs()
        log_entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "event": event,
            "details": details
        }
        data["logs"].append(log_entry)
        temp_file = BOT_LOGS_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, BOT_LOGS_FILE)
    except Exception as e:
        logger.error(f"Error saving bot log: {e}")

# Flexible role resolver
def resolve_role_from_input(guild: discord.Guild, raw: str):
    if not raw or not guild:
        return None
    s = raw.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    if s.startswith("<@&") and s.endswith(">"):
        try: return guild.get_role(int(s[3:-1]))
        except: pass
    if s.isdigit():
        try: return guild.get_role(int(s))
        except: pass
    if s.startswith("@"): s = s[1:].strip()
    role = discord.utils.find(lambda r: r.name.lower() == s.lower(), guild.roles)
    if role: return role
    matches = [r for r in guild.roles if s.lower() in r.name.lower()]
    if len(matches) == 1: return matches[0]
    elif len(matches) > 1:
        try: return max(matches, key=lambda r: r.position)
        except: return matches[0]
    return None

# ---------------------- INITIALIZATION ----------------------
data = load_message_counts()
message_counts = data.get("counts", {})
message_timestamps = data.get("timestamps", {})
last_reset = data.get("last_reset", int(time.time()))

# Normalize timestamps to lists
for uid, ts in list(message_timestamps.items()):
    if not isinstance(ts, list):
        message_timestamps[uid] = [float(ts)] if ts else []

# ---------------------- EVENTS ----------------------
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} at {datetime.now(timezone.utc)}')
    save_bot_log("online", f"Bot logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Chat Leaderboard | /help"))
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


@bot.event
async def on_disconnect():
    save_bot_log("offline", "Bot went offline")
    logger.info("Bot disconnected")

@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id == EXCLUDED_CHANNEL_ID:
        return
    if bot.user.mentioned_in(message):
        await message.channel.send(random.choice(PING_RESPONSES))
    user_id = str(message.author.id)
    message_counts[user_id] = message_counts.get(user_id, 0) + 1
    message_timestamps[user_id] = message_timestamps.get(user_id, [])
    message_timestamps[user_id].append(message.created_at.timestamp())
    save_message_counts({"counts": message_counts, "timestamps": message_timestamps, "last_reset": last_reset})
    await bot.process_commands(message)

# ---------------------- /ping ----------------------
@bot.tree.command(name="ping", description="Check if the bot is responsive")
async def ping(interaction: discord.Interaction):
    fun_messages = [
        "⚡ Zooming through the wires...",
        "🚀 Faster than your WiFi!",
        "🐍 Python power engaged!",
        "🕒 Beep boop… calculating latency...",
        "🎯 Right on target!",
        "💡 Online and ready to roll!",
        "📡 Signal strong and clear!",
        "🤖 Just vibin’ and responding!"
    ]
    response = f"Pong! Latency: {round(bot.latency * 1000)}ms\n{random.choice(fun_messages)}"
    await interaction.response.send_message(response, ephemeral=True)

# ---------------------- /leaderboard ----------------------
@bot.tree.command(name="leaderboard", description="Display the leaderboard for a specific timeframe")
@discord.app_commands.describe(timeframe="Timeframe to filter the leaderboard (1h, 1d, 24h, 7d, 14d, all); defaults to 'all'")
async def leaderboard(interaction: discord.Interaction, timeframe: str = "all"):
    await interaction.response.defer()
    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("Guild not available.", ephemeral=True)
            return

        current_time = time.time()
        timeframe_options = {"1h": 3600, "1d": 86400, "24h": 86400, "7d": 604800, "14d": 1209600, "all": 0}

        if timeframe not in timeframe_options:
            await interaction.followup.send("Invalid timeframe! Use 1h, 1d, 24h, 7d, 14d, or all.", ephemeral=True)
            return

        leaderboard_list = []
        for member in guild.members:
            user_id = str(member.id)
            if timeframe == "all":
                count = message_counts.get(user_id, 0)
            else:
                threshold = current_time - timeframe_options[timeframe]
                count = sum(1 for t in message_timestamps.get(user_id, []) if t >= threshold)
            leaderboard_list.append((member.display_name, count, user_id))

        if not leaderboard_list:
            await interaction.followup.send("No members found!", ephemeral=True)
            return

        leaderboard_list.sort(key=lambda x: (-x[1], x[0]))
        total_messages = sum(count for _, count, _ in leaderboard_list)
        users_per_page = 10
        pages = [leaderboard_list[i:i + users_per_page] for i in range(0, len(leaderboard_list), users_per_page)]
        total_pages = len(pages)
        current_page = 0

        def generate_embed(page_num):
            page = pages[page_num]
            table = ""
            for i, (_, count, user_id) in enumerate(page):
                member = guild.get_member(int(user_id))
                name = member.mention if member else f"Unknown ({user_id})"
                table += f"{i + page_num * users_per_page + 1}. {name} - {count}\n"

            embed = discord.Embed(
                title=f"🏆 {guild.name} Leaderboard ({timeframe if timeframe != 'all' else 'All Time'})",
                description=table,
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(
                url=guild.icon.url if guild.icon else bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            )
            embed.set_footer(text=f"Page {page_num + 1}/{total_pages} | Total Messages: {total_messages}")
            return embed

        await interaction.followup.send(embed=generate_embed(current_page))

        if total_pages > 1:
            message = await interaction.original_response()
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

            while True:
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                    if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                        current_page += 1
                    elif str(reaction.emoji) == "⬅️" and current_page > 0:
                        current_page -= 1
                    await message.edit(embed=generate_embed(current_page))
                    await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break
                except Exception as e:
                    logger.error(f"Error in leaderboard pagination: {e}")
                    break
    except Exception as e:
        logger.error(f"Error in /leaderboard: {e}")


# ---------------------- /rolecount ----------------------
@bot.tree.command(name="rolecount", description="Display the leaderboard for a specified role")
@discord.app_commands.describe(role_name="The name of the role to filter the leaderboard (e.g., 'Admin')")
async def rolecount(interaction: discord.Interaction, role_name: str):
    await interaction.response.defer()
    try:
        guild = interaction.guild
        target_role = resolve_role_from_input(guild, role_name)
        if not target_role:
            await interaction.followup.send(f"No role matching '{role_name}' found.", ephemeral=True)
            return

        leaderboard_list = [(m.display_name, message_counts.get(str(m.id), 0), str(m.id)) for m in guild.members if target_role in m.roles]

        if not leaderboard_list:
            await interaction.followup.send(f"No members with the '{target_role.name}' role found!", ephemeral=True)
            return

        leaderboard_list.sort(key=lambda x: (-x[1], x[0]))
        total_messages = sum(count for _, count, _ in leaderboard_list)
        users_per_page = 10
        pages = [leaderboard_list[i:i + users_per_page] for i in range(0, len(leaderboard_list), users_per_page)]
        total_pages = len(pages)
        current_page = 0

        def generate_embed(page_num):
            page = pages[page_num]
            table = ""
            for i, (_, count, user_id) in enumerate(page):
                member = guild.get_member(int(user_id))
                name = member.mention if member else f"Unknown ({user_id})"
                table += f"{i + page_num * users_per_page + 1}. {name} - {count}\n"

            embed = discord.Embed(
                title=f"🏆 {target_role.name} Message Leaderboard",
                description=table,
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(
                url=guild.icon.url if guild.icon else bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            )
            embed.set_footer(text=f"Page {page_num + 1}/{total_pages} | Total Messages: {total_messages}")
            return embed

        await interaction.followup.send(embed=generate_embed(current_page))

        if total_pages > 1:
            message = await interaction.original_response()
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

            while True:
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                    if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                        current_page += 1
                    elif str(reaction.emoji) == "⬅️" and current_page > 0:
                        current_page -= 1
                    await message.edit(embed=generate_embed(current_page))
                    await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break
                except Exception as e:
                    logger.error(f"Error in rolecount pagination: {e}")
                    break
    except Exception as e:
        logger.error(f"Error in /rolecount: {e}")

# Slash command: /timer
@bot.tree.command(name="timer", description="Set a countdown timer in minutes")
@discord.app_commands.describe(minutes="Number of minutes for the timer")
async def timer(interaction: discord.Interaction, minutes: int):
    await interaction.response.send_message(f"Timer set for {minutes} minute(s). I’ll notify you when it’s done!", ephemeral=True)
    logger.info(f"Timer started for {minutes} minutes by {interaction.user.name} (ID: {interaction.user.id})")
    save_bot_log("timer", f"Timer started for {minutes} minutes by {interaction.user.name} (ID: {interaction.user.id})")
    await asyncio.sleep(minutes * 60)
    await interaction.followup.send(f"Timer finished for {interaction.user.mention}!")
    logger.info(f"Timer expired for {interaction.user.name} (ID: {interaction.user.id})")
    save_bot_log("timer", f"Timer expired for {interaction.user.name} (ID: {interaction.user.id})")

# Slash command: /resetcounts
@bot.tree.command(name="resetcounts", description="Reset all message counts (admin only)")
async def resetcounts(interaction: discord.Interaction):
    await interaction.response.defer()
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command!", ephemeral=True)
        logger.warning(f"User {interaction.user.name} attempted /resetcounts without admin permissions")
        return

    try:
        global message_counts, message_timestamps, last_reset
        message_counts = {}
        message_timestamps = {}
        last_reset = int(time.time())
        save_message_counts({
            "counts": message_counts,
            "timestamps": message_timestamps,
            "last_reset": last_reset
        })
        save_bot_log("reset", f"Message counts reset by {interaction.user.name} (ID: {interaction.user.id})")
        await interaction.followup.send("Message counts and timestamps have been reset!", ephemeral=True)
        logger.info("Message counts and timestamps reset")
    except Exception as e:
        logger.error(f"Error in /resetcounts command: {str(e)}")
        await interaction.followup.send("An error occurred while resetting counts. Please try again.", ephemeral=True)

# Slash command: /setexcludedchannel
@bot.tree.command(name="setexcludedchannel", description="Set the channel to exclude from message counting (admin only)")
@discord.app_commands.check(lambda ctx: ctx.user.guild_permissions.administrator)
async def setexcludedchannel(interaction: discord.Interaction):
    await interaction.response.send_message("Please provide the channel ID to exclude (enable Developer Mode in Discord, right-click the channel, and copy its ID). Reply with the ID or 'cancel' to abort.", ephemeral=True)

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        response = await bot.wait_for('message', check=check, timeout=60.0)
        channel_id = response.content.strip()
        if channel_id.lower() == 'cancel':
            await interaction.followup.send("Action cancelled!", ephemeral=True)
            return

        try:
            channel_id = int(channel_id)
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                await interaction.followup.send("Invalid channel ID! The bot could not find this channel.", ephemeral=True)
                return

            global EXCLUDED_CHANNEL_ID
            EXCLUDED_CHANNEL_ID = channel_id
            with open('.env', 'r') as file:
                lines = file.readlines()
            with open('.env', 'w') as file:
                for line in lines:
                    if line.startswith('EXCLUDED_CHANNEL_ID='):
                        file.write(f'EXCLUDED_CHANNEL_ID={channel_id}\n')
                    else:
                        file.write(line)

            save_bot_log("config", f"Excluded channel set to {channel_id} by {interaction.user.name} (ID: {interaction.user.id})")
            await interaction.followup.send(f"Excluded channel set to ID {channel_id}! Strack will now ignore this channel.", ephemeral=True)
            logger.info(f"Excluded channel updated to {channel_id} by {interaction.user.name}")
        except ValueError:
            await interaction.followup.send("Invalid channel ID! Please enter a valid number or 'cancel'.", ephemeral=True)
        except PermissionError:
            await interaction.followup.send("I don’t have permission to update the .env file. Please check file permissions!", ephemeral=True)
            logger.error(f"Permission denied updating .env for {interaction.user.name}")
        except Exception as e:
            await interaction.followup.send("Something went wrong! Please try again.", ephemeral=True)
            logger.error(f"Error setting excluded channel: {e}")
    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long! Action cancelled.", ephemeral=True)
        logger.warning(f"Timeout setting excluded channel for {interaction.user.name}")

# Bot token from .env
bot.run(os.getenv('BOT_TOKEN'))
