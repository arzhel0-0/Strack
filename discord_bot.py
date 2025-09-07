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
intents.members = True  # Ensure members intent is enabled
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

# File paths
MESSAGE_COUNTS_FILE = 'message_counts.json'
BOT_LOGS_FILE = 'bot_logs.json'

# Channel ID to exclude from message counting (from .env, default to 0 if not set)
EXCLUDED_CHANNEL_ID = int(os.getenv('EXCLUDED_CHANNEL_ID', 0))

# Load message counts and metadata from file
def load_message_counts():
    default_data = {"counts": {}, "timestamps": {}, "last_reset": int(time.time())}
    if not os.path.exists(MESSAGE_COUNTS_FILE):
        logger.info(f"{MESSAGE_COUNTS_FILE} does not exist, creating with default structure")
        save_message_counts(default_data)
        return default_data

    try:
        with open(MESSAGE_COUNTS_FILE, 'r') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.error(f"{MESSAGE_COUNTS_FILE} contains invalid JSON: not a dictionary")
                save_message_counts(default_data)
                return default_data
            if "counts" not in data or not isinstance(data["counts"], dict):
                logger.warning(f"Missing or invalid 'counts' in {MESSAGE_COUNTS_FILE}, resetting")
                data["counts"] = {}
            if "timestamps" not in data or not isinstance(data["timestamps"], dict):
                logger.warning(f"Missing or invalid 'timestamps' in {MESSAGE_COUNTS_FILE}, resetting")
                data["timestamps"] = {}
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
        if not isinstance(data, dict):
            logger.error(f"Invalid data type for saving to {MESSAGE_COUNTS_FILE}: {type(data)}")
            data = {"counts": {}, "timestamps": {}, "last_reset": int(time.time())}
        if "counts" not in data:
            data["counts"] = {}
        if "timestamps" not in data:
            data["timestamps"] = {}
        if "last_reset" not in data:
            data["last_reset"] = int(time.time())

        temp_file = MESSAGE_COUNTS_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, MESSAGE_COUNTS_FILE)
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

        temp_file = BOT_LOGS_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, BOT_LOGS_FILE)
        logger.info(f"Saved log entry: {event} - {details}")
    except PermissionError as e:
        logger.error(f"PermissionError saving to {BOT_LOGS_FILE}: {e}")
    except Exception as e:
        logger.error(f"Error saving log to {BOT_LOGS_FILE}: {e}")

# Initialize message counts and metadata
data = load_message_counts()
message_counts = data.get("counts", {})
message_timestamps = data.get("timestamps", {})
last_reset = data.get("last_reset", int(time.time()))

# Sync slash commands on startup for all guilds
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} at {datetime.now(timezone.utc)}')
    save_bot_log("online", f"Bot logged in as {bot.user}")
    try:
        await bot.change_presence(activity=discord.Game(name="Chat Leaderboard | /help"))
        guild_ids = os.getenv('GUILD_IDS')
        if guild_ids:
            guild_ids = [int(id.strip()) for id in guild_ids.split(',')]
            for guild_id in guild_ids:
                guild = discord.Object(id=guild_id)
                await bot.tree.sync(guild=guild)
                logger.info(f"Synced commands for guild {guild_id}")
                print(f"Registered commands for guild {guild_id}: {bot.tree.get_commands(guild=guild)}")
        else:
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
                async for message in channel.history(after=last_reset_dt):  # Fetch all messages after last reset
                    if message.author.bot:
                        continue
                    user_id = str(message.author.id)
                    message_counts[user_id] = message_counts.get(user_id, 0) + 1
                    message_timestamps[user_id] = message_timestamps.get(user_id, [])
                    message_timestamps[user_id].append(message.created_at.timestamp())
                    new_messages += 1
                logger.info(f"Processed channel: {channel.name} (ID: {channel.id}) with {new_messages} messages")
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
                await channel.send(f'Bot started. Counted {new_messages} new messages since last reset ({last_reset_dt.strftime("%Y-%m-%d %H:%M UTC")}).')
            else:
                logger.warning(f"Could not find channel with ID {EXCLUDED_CHANNEL_ID}")
        except Exception as e:
            logger.error(f"Error sending notification to channel {EXCLUDED_CHANNEL_ID}: {e}")

    data["counts"] = message_counts
    data["timestamps"] = message_timestamps
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
        message_timestamps[user_id] = message_timestamps.get(user_id, [])
        message_timestamps[user_id].append(message.created_at.timestamp())
        save_message_counts({
            "counts": message_counts,
            "timestamps": message_timestamps,
            "last_reset": last_reset
        })
        logger.info(f"Counted message from {message.author.name} (ID: {user_id})")
    except Exception as e:
        logger.error(f"Error processing message from {message.author.name}: {e}")

    await bot.process_commands(message)

# Slash command: /ping
@bot.tree.command(name="ping", description="Check if the bot is responsive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(bot.latency * 1000)}ms", ephemeral=True)

# Slash command: /leaderboard
@bot.tree.command(name="leaderboard", description="Display the leaderboard for a specific timeframe")
@discord.app_commands.describe(timeframe="Timeframe to filter the leaderboard (1h, 1d, 24h, 7d, 14d, all); defaults to 'all'")
async def leaderboard(interaction: discord.Interaction, timeframe: str = "all"):
    await interaction.response.defer()  # Defer to avoid timeout
    try:
        start_time = time.time()
        guild = interaction.guild
        if not guild:
            raise ValueError("Guild not available in interaction")

        # Check if the bot can access members
        try:
            _ = guild.members  # Test member access
        except AttributeError:
            await interaction.followup.send("The bot lacks permission to view members. Please enable the 'Server Members Intent' in the Discord Developer Portal.", ephemeral=True)
            logger.error(f"Member access denied for guild {guild.name if guild else 'None'}")
            return

        logger.debug(f"Starting leaderboard generation for {timeframe} at {datetime.now(timezone.utc)}")
        current_time = time.time()
        timeframe_options = {
            "1h": 3600,    # 1 hour in seconds
            "1d": 86400,   # 1 day in seconds
            "24h": 86400,  # 24 hours in seconds
            "7d": 604800,  # 7 days in seconds
            "14d": 1209600, # 14 days in seconds
            "all": 0       # No time limit, uses data since last reset
        }

        if timeframe not in timeframe_options:
            await interaction.followup.send("Invalid timeframe! Use 1h, 1d, 24h, 7d, 14d, or all.", ephemeral=True)
            return

        leaderboard = []
        member_count = 0
        member_loop_start = time.time()
        for member in guild.members:  # Use cached members
            member_count += 1
            user_id = str(member.id)
            if timeframe == "all":
                count = message_counts.get(user_id, 0)  # Use data since last reset, default to 0 if no messages
            else:
                time_threshold = current_time - timeframe_options[timeframe]
                count = sum(1 for t in message_timestamps.get(user_id, []) if t >= time_threshold) or 0
            username = member.display_name[:15] if len(member.display_name) > 15 else member.display_name
            leaderboard.append((username, count))  # Include all members, even with 0 messages
        logger.debug(f"Member loop for {timeframe} took {time.time() - member_loop_start:.2f}s, processed {member_count} members, got {len(leaderboard)} entries")

        if not leaderboard:
            await interaction.followup.send(f"No members found in the server!" if timeframe != "all" else "No members found since last reset!", ephemeral=True)
            logger.info(f"No members found in guild {guild.name} for timeframe {timeframe}")
            return

        sort_start = time.time()
        leaderboard.sort(key=lambda x: (-x[1], x[0]))  # Sort by count (descending), then name
        logger.debug(f"Sorting took {time.time() - sort_start:.2f}s")

        total_messages = sum(count for _, count in leaderboard)
        users_per_page = 10
        pages = [leaderboard[i:i + users_per_page] for i in range(0, len(leaderboard), users_per_page)]
        total_pages = len(pages)
        current_page = 0
        current_timeframe = timeframe  # Track current timeframe

        def generate_embed(page_num, tf):
            page = pages[page_num]
            max_name_length = max(len(name) for name, _ in page) if page else 15
            table = "\n".join(f"{i + page_num * users_per_page + 1}. {name:<{max_name_length}} - {count}" for i, (name, count) in enumerate(page))
            embed = discord.Embed(
                title=f"🏆 {guild.name} Leaderboard ({tf if tf != 'all' else 'All Time'})",
                description=f"```{table}```",
                timestamp=datetime.utcnow()  # Transparent UI: No color set
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
            server_info = f"Members: {guild.member_count} | Created: {guild.created_at.strftime('%Y-%m-%d')}"
            embed.set_footer(text=f"{server_info} | Page {page_num + 1}/{total_pages} | Total Messages: {total_messages}")
            return embed

        embed_start = time.time()
        await interaction.followup.send(embed=generate_embed(current_page, current_timeframe))
        logger.debug(f"Embed generation and send took {time.time() - embed_start:.2f}s")
        if total_pages > 1:
            message = await interaction.original_response()
            try:
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")
                logger.debug(f"Added reactions ⬅️ and ➡️ to message {message.id}")
            except discord.Forbidden:
                logger.error(f"Bot lacks 'Add Reactions' permission in channel {interaction.channel.name} (ID: {interaction.channel.id})")
                await interaction.followup.send("The bot lacks permission to add reactions. Please grant 'Add Reactions' permission.", ephemeral=True)
                return
            except discord.HTTPException as e:
                logger.error(f"Failed to add reactions to message {message.id}: {e}")
                await interaction.followup.send("An error occurred while adding reaction buttons. Please try again.", ephemeral=True)
                return

            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

            while True:
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                    if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                        current_page += 1
                    elif str(reaction.emoji) == "⬅️" and current_page > 0:
                        current_page -= 1
                    await message.edit(embed=generate_embed(current_page, current_timeframe))
                    await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    logger.debug(f"Pagination timeout for message {message.id}")
                    break
                except discord.Forbidden:
                    logger.error(f"Bot lacks permission to edit/remove reactions on message {message.id}")
                    await interaction.followup.send("The bot lacks permission to manage reactions. Please grant 'Manage Messages' permission.", ephemeral=True)
                    break
                except Exception as e:
                    logger.error(f"Error in pagination for message {message.id}: {e}")
                    await interaction.followup.send("An error occurred during pagination. Please try again.", ephemeral=True)
                    break

        logger.debug(f"Total leaderboard generation took {time.time() - start_time:.2f}s")
    except discord.errors.Forbidden as e:
        logger.error(f"Forbidden error in /leaderboard: {str(e)}. Guild: {guild.name if guild else 'None'}, Timeframe: {timeframe}, Channel: {interaction.channel.name if interaction.channel else 'None'}")
        await interaction.followup.send("The bot lacks necessary permissions. Please ensure the bot has 'View Members' and 'Send Messages' permissions in the server and channel, and the 'Server Members Intent' is enabled in the Discord Developer Portal.", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in /leaderboard command: {str(e)}. Guild: {guild.name if guild else 'None'}, Timeframe: {timeframe}")
        await interaction.followup.send("An error occurred while generating the leaderboard. Please try again. Check logs.", ephemeral=True)

# Slash command: /rolecount
@bot.tree.command(name="rolecount", description="Display the leaderboard for a specified role")
@discord.app_commands.describe(role_name="The name of the role to filter the leaderboard (e.g., 'Admin')")
async def rolecount(interaction: discord.Interaction, role_name: str):
    await interaction.response.defer()
    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("Guild not available in interaction.", ephemeral=True)
            return

        # Attempt to fetch members with pagination and retry (no direct permission check, rely on intent)
        members = []
        after = None
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                fetched_members = await guild.members.fetch(limit=1000, after=after, timeout=15.0)  # Paginate with 1000 limit
                if not fetched_members:
                    break
                members.extend(fetched_members)
                after = fetched_members[-1].id
                await asyncio.sleep(1)  # Respect rate limits
            except discord.HTTPException as e:
                logger.error(f"HTTP error fetching members in guild {guild.name}: {str(e)}. Retry {retry_count + 1}/{max_retries}")
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                continue
            except Exception as e:
                logger.error(f"Unexpected error fetching members in guild {guild.name}: {str(e)}")
                break
        if not members:
            logger.warning(f"No members fetched for guild {guild.name}, falling back to cache")
            members = guild.members  # Fallback to cached members

        # Find the role (case-insensitive)
        target_role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), guild.roles)
        if not target_role:
            await interaction.followup.send(f"No role named '{role_name}' found in this server! Use quotes for roles with spaces.", ephemeral=True)
            return

        # Get members with the role
        leaderboard = []
        for member in members:
            if target_role in member.roles:
                user_id = str(member.id)
                count = message_counts.get(user_id, 0)  # Default to 0 if no messages
                username = member.display_name[:15] if len(member.display_name) > 15 else member.display_name
                leaderboard.append((username, count))

        if not leaderboard:
            await interaction.followup.send(f"No members with the '{role_name}' role found in this server!", ephemeral=True)
            return

        leaderboard.sort(key=lambda x: (-x[1], x[0]))

        total_messages = sum(count for _, count in leaderboard)
        users_per_page = 10
        pages = [leaderboard[i:i + users_per_page] for i in range(0, len(leaderboard), users_per_page)]
        total_pages = len(pages)
        current_page = 0

        def generate_embed(page_num):
            page = pages[page_num]
            max_name_length = max(len(name) for name, _ in page) if page else 15
            table = "\n".join(f"{i + page_num * users_per_page + 1}. {name:<{max_name_length}} - {count}" for i, (name, count) in enumerate(page))
            embed = discord.Embed(
                title=f"🏆 {target_role.name} Message Leaderboard",
                description=f"```{table}```",
                timestamp=datetime.utcnow()  # Transparent UI: No color set
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
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
                except discord.Forbidden:
                    await interaction.followup.send("The bot lacks permission to manage reactions. Please grant 'Manage Messages' permission.", ephemeral=True)
                    break
                except Exception as e:
                    logger.error(f"Error in pagination for message {message.id}: {str(e)}")
                    await interaction.followup.send("An error occurred during pagination. Please try again.", ephemeral=True)
                    break
    except discord.errors.Forbidden as e:
        logger.error(f"Forbidden error in /rolecount: {str(e)}. Guild: {guild.name if guild else 'None'}, Role: {role_name}")
        await interaction.followup.send("The bot lacks necessary permissions. Ensure it has 'View Members' and 'Send Messages' permissions.", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in /rolecount command: {str(e)}. Guild: {guild.name if guild else 'None'}, Role: {role_name}")
        await interaction.followup.send("An error occurred while generating the role leaderboard. Please try again. Check logs.", ephemeral=True)

# Slash command: /timer
@bot.tree.command(name="timer", description="Set a countdown timer in minutes")
@discord.app_commands.describe(minutes="Number of minutes for the timer")
async def timer(interaction: discord.Interaction, minutes: int):
    await interaction.response.send_message(f"Timer set for {minutes} minute(s). I’ll notify you when it’s done!", ephemeral=True)
    logger.info(f"Timer started for {minutes} minutes by {interaction.user.name} (ID: {interaction.user.id})")
    save_bot_log("timer", f"Timer started for {minutes} minutes by {interaction.user.name} (ID: {interaction.user.id})")
    await asyncio.sleep(minutes * 60)  # Convert minutes to seconds
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
