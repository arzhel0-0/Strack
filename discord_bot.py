import discord
from discord.ext import commands
import json
import os
import time
import asyncio
from datetime import datetime, timezone
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

# File paths
MESSAGE_COUNTS_FILE = 'message_counts.json'
BOT_LOGS_FILE = 'bot_logs.json'

# Channel ID to exclude from message counting (from .env, default to 0 if not set)
EXCLUDED_CHANNEL_ID = int(os.getenv('EXCLUDED_CHANNEL_ID', 0))

# Custom embed border color (hex code)
EMBED_BORDER_COLOR = 0xFF0000  # Red border color

# Load message counts and metadata from file
def load_message_counts():
    default_data = {"counts": {}, "last_reset": int(time.time())}
    if not os.path.exists(MESSAGE_COUNTS_FILE):
        logger.info(f"{MESSAGE_COUNTS_FILE} does not exist, creating with default structure")
        save_message_counts(default_data)
        return default_data

    try:
        with open(MESSAGE_COUNTS_FILE, 'r') as f:
            data = json.load(f)
            # Validate JSON structure
            if not isinstance(data, dict):
                logger.error(f"{MESSAGE_COUNTS_FILE} contains invalid JSON: not a dictionary")
                save_message_counts(default_data)
                return default_data
            if "counts" not in data or not isinstance(data["counts"], dict):
                logger.warning(f"Missing or invalid 'counts' in {MESSAGE_COUNTS_FILE}, resetting")
                data["counts"] = {}
            if "last_reset" not in data or not isinstance(data["last_reset"], int):
                logger.warning(f"Missing or invalid 'last_reset' in {MESSAGE_COUNTS_FILE}, setting to current time")
                data["last_reset"] = int(time.time())
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError in {MESSAGE_COUNTS_FILE}: {e}. Creating new file.")
        save_message_counts(default_data)
        return default_data
    except PermissionError as e:
        logger.error(f"PermissionError accessing {MESSAGE_COUNTS_FILE}: {e}")
        return default_data
    except Exception as e:
        logger.error(f"Unexpected error reading {MESSAGE_COUNTS_FILE}: {e}")
        return default_data

# Save message counts and metadata to file
def save_message_counts(data):
    try:
        # Ensure data has required structure
        if not isinstance(data, dict):
            logger.error(f"Invalid data type for saving to {MESSAGE_COUNTS_FILE}: {type(data)}")
            data = {"counts": {}, "last_reset": int(time.time())}
        if "counts" not in data:
            data["counts"] = {}
        if "last_reset" not in data:
            data["last_reset"] = int(time.time())

        # Write to a temporary file first to avoid corruption
        temp_file = MESSAGE_COUNTS_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, MESSAGE_COUNTS_FILE)  # Atomic replace
        logger.info(f"Saved data to {MESSAGE_COUNTS_FILE}")
    except PermissionError as e:
        logger.error(f"PermissionError saving to {MESSAGE_COUNTS_FILE}: {e}")
    except Exception as e:
        logger.error(f"Error saving to {MESSAGE_COUNTS_FILE}: {e}")

# Load bot logs from file
def load_bot_logs():
    default_data = {"logs": []}
    if not os.path.exists(BOT_LOGS_FILE):
        logger.info(f"{BOT_LOGS_FILE} does not exist, creating with default structure")
        save_bot_log("init", f"Created {BOT_LOGS_FILE}")
        return default_data

    try:
        with open(BOT_LOGS_FILE, 'r') as f:
            data = json.load(f)
            # Validate JSON structure
            if not isinstance(data, dict):
                logger.error(f"{BOT_LOGS_FILE} contains invalid JSON: not a dictionary")
                save_bot_log("error", f"Invalid JSON in {BOT_LOGS_FILE}, resetting")
                return default_data
            if "logs" not in data or not isinstance(data["logs"], list):
                logger.warning(f"Missing or invalid 'logs' in {BOT_LOGS_FILE}, resetting")
                data["logs"] = []
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError in {BOT_LOGS_FILE}: {e}. Creating new file.")
        save_bot_log("error", f"JSONDecodeError in {BOT_LOGS_FILE}, resetting")
        return default_data
    except PermissionError as e:
        logger.error(f"PermissionError accessing {BOT_LOGS_FILE}: {e}")
        return default_data
    except Exception as e:
        logger.error(f"Unexpected error reading {BOT_LOGS_FILE}: {e}")
        return default_data

# Save bot log entry to file
def save_bot_log(event, details):
    try:
        data = load_bot_logs()
        log_entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "event": event,
            "details": details
        }
        data["logs"].append(log_entry)

        # Write to a temporary file first to avoid corruption
        temp_file = BOT_LOGS_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, BOT_LOGS_FILE)  # Atomic replace
        logger.info(f"Saved log entry: {event} - {details}")
    except PermissionError as e:
        logger.error(f"PermissionError saving to {BOT_LOGS_FILE}: {e}")
    except Exception as e:
        logger.error(f"Error saving log to {BOT_LOGS_FILE}: {e}")

# Initialize message counts and metadata
data = load_message_counts()
message_counts = data.get("counts", {})
last_reset = data.get("last_reset", int(time.time()))

# Sync slash commands on startup for all guilds
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} at {datetime.now(timezone.utc)}')
    save_bot_log("online", f"Bot logged in as {bot.user}")
    try:
        await bot.change_presence(activity=discord.Game(name="Chat Leaderboard | /help"))
        # Check for GUILD_IDS environment variable for per-guild sync
        guild_ids = os.getenv('GUILD_IDS')
        if guild_ids:
            guild_ids = [int(id.strip()) for id in guild_ids.split(',')]
            for guild_id in guild_ids:
                guild = discord.Object(id=guild_id)
                await bot.tree.sync(guild=guild)
                logger.info(f"Synced commands for guild {guild_id}")
                print(f"Registered commands for guild {guild_id}: {bot.tree.get_commands(guild=guild)}")
        else:
            # Default to global sync for universal bot
            await bot.tree.sync()
            logger.info("Synced commands globally")
            print(f"Registered commands globally: {bot.tree.get_commands()}")
    except discord.HTTPException as e:
        logger.error(f"Sync failed: {e}. Retrying with global sync.")
        await bot.tree.sync()
        logger.info("Synced commands globally as fallback")
    except Exception as e:
        logger.error(f"Error setting presence or syncing commands: {e}")

    last_reset_dt = datetime.fromtimestamp(last_reset, tz=timezone.utc)
    logger.info(f"Fetching messages since last reset: {last_reset_dt}")

    new_messages = 0
    for guild in bot.guilds:
        logger.info(f"Processing guild: {guild.name} (ID: {guild.id})")
        for channel in guild.text_channels:
            if channel.id == EXCLUDED_CHANNEL_ID:
                logger.info(f"Skipping excluded channel: {channel.name} (ID: {channel.id})")
                continue
            try:
                async for message in channel.history(after=last_reset_dt, limit=1000):
                    if message.author.bot:
                        continue
                    user_id = str(message.author.id)
                    message_counts[user_id] = message_counts.get(user_id, 0) + 1
                    new_messages += 1
                logger.info(f"Processed channel: {channel.name} (ID: {channel.id})")
            except discord.Forbidden:
                logger.warning(f'No access to channel {channel.name} (ID: {channel.id}) in guild {guild.name}')
            except discord.HTTPException as e:
                logger.error(f"HTTP error in {channel.name} (ID: {channel.id}): {e}")
            except Exception as e:
                logger.error(f"Error fetching messages in {channel.name} (ID: {channel.id}): {e}")
            await asyncio.sleep(0.1)

    if new_messages > 0:
        logger.info(f"Counted {new_messages} messages since last reset")
        try:
            channel = bot.get_channel(EXCLUDED_CHANNEL_ID)
            if channel:
                await channel.send(f'Bot started. Counted {new_messages} new messages by all users since last reset ({last_reset_dt.strftime("%Y-%m-%d %H:%M UTC")}).')
            else:
                logger.warning(f"Could not find channel with ID {EXCLUDED_CHANNEL_ID}")
        except Exception as e:
            logger.error(f"Error sending notification to channel {EXCLUDED_CHANNEL_ID}: {e}")

    data["counts"] = message_counts
    data["last_reset"] = last_reset
    save_message_counts(data)

@bot.event
async def on_disconnect():
    save_bot_log("offline", "Bot went offline")
    logger.info("Bot disconnected")

@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id == EXCLUDED_CHANNEL_ID:
        return

    try:
        user_id = str(message.author.id)
        message_counts[user_id] = message_counts.get(user_id, 0) + 1
        save_message_counts({
            "counts": message_counts,
            "last_reset": last_reset
        })
        logger.info(f"Counted message from {message.author.name} (ID: {user_id})")
    except Exception as e:
        logger.error(f"Error processing message from {message.author.name}: {e}")

    await bot.process_commands(message)

# Slash command: /ping (available to all)
@bot.tree.command(name="ping", description="Check if the bot is responsive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(bot.latency * 1000)}ms", ephemeral=True)

# Slash command: /leaderboard (available to all)
@bot.tree.command(name="leaderboard", description="Display the leaderboard for all users")
async def leaderboard(interaction: discord.Interaction):
    try:
        guild = interaction.guild
        leaderboard = []
        for member in guild.members:
            user_id = str(member.id)
            count = message_counts.get(user_id, 0)
            username = (member.name[:12] + "...") if len(member.name) > 15 else member.name
            leaderboard.append((username, count))

        leaderboard.sort(key=lambda x: (-x[1], x[0]))

        if not leaderboard:
            await interaction.response.send_message("No messages counted yet in this server!", ephemeral=True)
            logger.info(f"No messages counted in guild {guild.name}")
            return

        total_messages = sum(count for _, count in leaderboard)
        users_per_page = 10
        pages = [leaderboard[i:i + users_per_page] for i in range(0, len(leaderboard), users_per_page)]
        total_pages = len(pages)
        current_page = 0

        def generate_embed(page_num):
            page = pages[page_num]
            max_name_length = max(len(name) for name, _ in page) if page else len("Username")
            max_name_length = max(max_name_length, len("Username"))

            table = f"{'Rank':<8} | {'Username':<{max_name_length}} | {'Messages':<8}\n"
            table += "=" * 8 + "=+" + "=" * max_name_length + "=+" + "=" * 8 + "\n"
            for i, (username, count) in enumerate(page, page_num * users_per_page + 1):
                rank = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
                table += f"{rank:<8} | {username:<{max_name_length}} | {count:<8}\n"

            embed = discord.Embed(
                title=f"🏆 {guild.name} and the Leaderboard",
                description=f"```css\n{table}```",
                color=EMBED_BORDER_COLOR,
                timestamp=datetime.utcnow()
            )
            thumbnail_url = guild.icon.url if guild.icon else (bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_footer(text=f"Page {page_num + 1}/{total_pages} | Total Messages: {total_messages} | Last Reset: {datetime.fromtimestamp(last_reset).strftime('%Y-%m-%d %H:%M UTC') if last_reset else 'Never'}")
            return embed

        await interaction.response.send_message(embed=generate_embed(current_page))
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
        logger.error(f"Error in /leaderboard command: {e}")
        await interaction.response.send_message("An error occurred while generating the leaderboard. Please try again.", ephemeral=True)

# Slash command: /rolecount (available to all)
@bot.tree.command(name="rolecount", description="Display the leaderboard for a specified role")
async def rolecount(interaction: discord.Interaction, role_name: str):
    try:
        guild = interaction.guild
        target_role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), guild.roles)
        if not target_role:
            await interaction.response.send_message(f"No role named '{role_name}' found in this server! Use quotes for roles with spaces.", ephemeral=True)
            logger.warning(f"Role '{role_name}' not found in guild {guild.name}")
            return

        leaderboard = []
        for member in guild.members:
            if target_role in member.roles:
                user_id = str(member.id)
                count = message_counts.get(user_id, 0)
                username = (member.name[:12] + "...") if len(member.name) > 15 else member.name
                leaderboard.append((username, count))

        leaderboard.sort(key=lambda x: (-x[1], x[0]))

        if not leaderboard:
            await interaction.response.send_message(f"No members with the '{role_name}' role found in this server!", ephemeral=True)
            logger.info(f"No members with role '{role_name}' in guild {guild.name}")
            return

        total_messages = sum(count for _, count in leaderboard)
        users_per_page = 10
        pages = [leaderboard[i:i + users_per_page] for i in range(0, len(leaderboard), users_per_page)]
        total_pages = len(pages)
        current_page = 0

        def generate_embed(page_num):
            page = pages[page_num]
            max_name_length = max(len(name) for name, _ in page) if page else len("Username")
            max_name_length = max(max_name_length, len("Username"))

            table = f"{'Rank':<8} | {'Username':<{max_name_length}} | {'Messages':<8}\n"
            table += "=" * 8 + "=+" + "=" * max_name_length + "=+" + "=" * 8 + "\n"
            for i, (username, count) in enumerate(page, page_num * users_per_page + 1):
                rank = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
                table += f"{rank:<8} | {username:<{max_name_length}} | {count:<8}\n"

            embed = discord.Embed(
                title=f"🏆 {target_role.name} Message Leaderboard",
                description=f"```css\n{table}```",
                color=EMBED_BORDER_COLOR,
                timestamp=datetime.utcnow()
            )
            thumbnail_url = guild.icon.url if guild.icon else (bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_footer(text=f"Page {page_num + 1}/{total_pages} | Total Messages: {total_messages} | Last Reset: {datetime.fromtimestamp(last_reset).strftime('%Y-%m-%d %H:%M UTC') if last_reset else 'Never'}")
            return embed

        await interaction.response.send_message(embed=generate_embed(current_page))
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
        logger.error(f"Error in /rolecount command: {e}")
        await interaction.response.send_message("An error occurred while generating the role leaderboard. Please try again.", ephemeral=True)

# Slash command: /resetcounts (admin only)
@bot.tree.command(name="resetcounts", description="Reset all message counts (admin only)")
async def resetcounts(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        logger.warning(f"User {interaction.user.name} (ID: {interaction.user.id}) attempted /resetcounts without admin permissions in guild {interaction.guild.name}")
        return

    try:
        global message_counts, last_reset
        message_counts = {}
        last_reset = int(time.time())
        save_message_counts({
            "counts": message_counts,
            "last_reset": last_reset
        })
        save_bot_log("reset", f"Message counts reset by {interaction.user.name} (ID: {interaction.user.id})")
        await interaction.response.send_message("Message counts have been reset!", ephemeral=True)
        logger.info("Message counts reset by admin")
    except Exception as e:
        logger.error(f"Error in /resetcounts command: {e}")
        await interaction.response.send_message("An error occurred while resetting counts. Please try again.", ephemeral=True)

# Slash command: /setexcludedchannel (admin only)
@bot.tree.command(name="setexcludedchannel", description="Set the channel to exclude from message counting (admin only)")
async def setexcludedchannel(interaction: discord.Interaction):
    logger.info(f"/setexcludedchannel triggered by {interaction.user.name} (ID: {interaction.user.id}) in guild {interaction.guild.name} (ID: {interaction.guild.id})")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        logger.warning(f"User {interaction.user.name} (ID: {interaction.user.id}) attempted /setexcludedchannel without admin permissions")
        return

    try:
        await interaction.response.send_message("Please provide the channel ID you want to exclude (enable Developer Mode in Discord, right-click the channel, and copy its ID). Reply with the ID or 'cancel' to abort.", ephemeral=True)
        logger.info("Sent initial response for /setexcludedchannel")
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        response = await bot.wait_for('message', check=check, timeout=60.0)
        channel_id = response.content.strip()
        logger.info(f"Received response: {channel_id}")

        if channel_id.lower() == 'cancel':
            await interaction.followup.send("Action cancelled!", ephemeral=True)
            logger.info("Action cancelled by user")
            return

        try:
            channel_id = int(channel_id)
            # Update the EXCLUDED_CHANNEL_ID globally and in .env
            global EXCLUDED_CHANNEL_ID
            EXCLUDED_CHANNEL_ID = channel_id
            logger.info(f"Updated EXCLUDED_CHANNEL_ID to {channel_id}")

            # Update the .env file
            with open('.env', 'r') as file:
                lines = file.readlines()
            with open('.env', 'w') as file:
                for line in lines:
                    if line.startswith('EXCLUDED_CHANNEL_ID='):
                        file.write(f'EXCLUDED_CHANNEL_ID={channel_id}\n')
                    else:
                        file.write(line)
            logger.info("Updated .env file with new EXCLUDED_CHANNEL_ID")

            save_bot_log("config", f"Excluded channel set to {channel_id} by {interaction.user.name} (ID: {interaction.user.id})")
            await interaction.followup.send(f"Excluded channel set to ID {channel_id}! Strack will now ignore this channel.", ephemeral=True)
            logger.info(f"Excluded channel updated to {channel_id} by {interaction.user.name}")
        except ValueError:
            await interaction.followup.send("Invalid channel ID! Please enter a valid number or 'cancel'.", ephemeral=True)
            logger.error("Invalid channel ID provided")
        except PermissionError:
            await interaction.followup.send("I don’t have permission to update the .env file. Please check file permissions!", ephemeral=True)
            logger.error(f"Permission denied updating .env for {interaction.user.name}")
        except Exception as e:
            await interaction.followup.send("Something went wrong! Please try again.", ephemeral=True)
            logger.error(f"Error setting excluded channel: {e}")

    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long! Action cancelled.", ephemeral=True)
        logger.warning(f"Timeout setting excluded channel for {interaction.user.name}")
    except Exception as e:
        logger.error(f"Unexpected error in /setexcludedchannel: {e}")
        await interaction.followup.send("An unexpected error occurred. Please try again.", ephemeral=True)

# Bot token from .env
bot.run(os.getenv('BOT_TOKEN'))
