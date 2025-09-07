
# **Strack Discord Bot**

Hey there! Meet **Strack**, your friendly neighborhood Discord bot that’s here to track message activity and spice up your server with awesome leaderboards! Built with Python and the `discord.py` library, Strack is perfect for communities, gaming crews, or any server where roles matter. It’s all about celebrating your most chatty members in style!

## **Welcome to Strack!**

Imagine a bot that not only keeps an eye on who’s chatting the most but also rolls out cool leaderboards to show off their skills. That’s **Strack** for you! It watches messages in real-time, skips the bot spam and a channel you pick, and lets you see who’s dominating the convo—whether it’s the "Agent" role or any other crew you’ve got. With a snazzy embed design and simple commands, Strack is ready to bring some fun to your server!

## **What Strack Can Do**

- **Message Tracking**: Counts messages from folks with roles (no bots or your chosen quiet zone included).
- **Role-Based Leaderboards**: Check out the top talkers for "Agent" or any role you name.
- **Easy Navigation**: Flip through leaderboards (10 peeps per page) with `⬅️` and `➡️` reactions.
- **Admin Power**: Reset those counts with `!resetcounts` if you’re an admin.
- **Keep a Log**: Tracks when Strack goes online, offline, or resets in `bot_logs.json`.

## **Getting Strack Running**

Ready to bring Strack to your server? Here’s how to get started—don’t worry, it’s a breeze!

### **Step 1: Grab the Code**
- Clone this repo to your computer:
  ```bash
  git clone https://github.com/yourusername/yourrepo.git
  ```
  - Swap `https://github.com/yourusername/yourrepo.git` with your actual GitHub link.

### **Step 2: Get the Tools**
- Hop into the project folder and install what you need:
  ```bash
  cd yourrepo
  pip install discord.py
  ```

### **Step 3: Set It Up**
- Open `bot.py` in any text editor.
- Pop in your Discord bot token where it says `YOUR_BOT_TOKEN` (grab it from the Discord Developer Portal).
- Pick a channel to ignore by setting `EXCLUDED_CHANNEL_ID` (turn on Developer Mode in Discord to copy its ID).
- Example tweak in `bot.py`:
  ```python
  EXCLUDED_CHANNEL_ID = 123456789012345678  # Your channel ID here
  bot.run('YOUR_ACTUAL_TOKEN_HERE')  # Your secret token here
  ```

### **Step 4: Fire It Up**
- Run the bot with:
  ```bash
  python bot.py
  ```
- Invite Strack to your server using its OAuth2 URL from the Discord Developer Portal.

## **Strack’s Commands**

Here’s what you can do with Strack—give these a try!

### **!leaderboard**
- **What It Does**: Shows off a leaderboard for the "Agent" role’s top talkers.
- **How to Use**: `!leaderboard`
- **Who Can Use**: Anyone!
- **Fun Stuff**: Pages through 10 folks at a time with `⬅️` and `➡️` to scroll.

### **!rolecount <role_name>**
- **What It Does**: Pulls up a leaderboard for any role you name.
- **How to Use**: `!rolecount <role_name>` (e.g., `!rolecount Agent` or `!rolecount "Trusted Member"`)
- **Who Can Use**: Anyone!
- **Fun Stuff**: Pages through 10 folks at a time with `⬅️` and `➡️` to scroll.

### **!resetcounts**
- **What It Does**: Wipes the slate clean and resets all message counts.
- **How to Use**: `!resetcounts`
- **Who Can Use**: Admins only!
- **Fun Stuff**: Lets you start fresh with a quick confirmation message.

# **What’s in the Folder**
- `discord_bot.py`: The heart of Strack—where the magic happens.
- `message_counts.json`: Keeps track of who’s chatted and when it last reset (starts with sample data).
- `bot_logs.json`: Logs all the bot’s adventures (starts empty).
- `README.md`: This handy guide!
- `LICENSE`: MIT License so you can use and share Strack freely.
- `requirements.txt`: Shows the requirements
- `.gitignore`: Tells Git what to skip.

## **Join the Fun!**
Spot a glitch or have a cool idea? Drop an issue on this GitHub repo or send a pull request. We’d love your input to make Strack even better!

# **License**
Strack comes with the [MIT License](LICENSE), meaning you can use, tweak, and share it as long as you give a shoutout. Check the `LICENSE` file for the full scoop.

# **Quick Tips**
- **Setup**: Make sure `EXCLUDED_CHANNEL_ID` and `YOUR_BOT_TOKEN` are filled in before launching.
- **Logs**: Peek at `bot_logs.json` to see what Strack’s been up to.
- **Help**: Got questions? Hit up the maintainers via GitHub Issues.

---

# RUN STRACK ON YOUR TERMINAL
## Don’t have a hosting service? No problem! You can run Strack right from your own computer using the terminal. Here’s how to do it super easily:What You Need: Just a PC or laptop with Python installed (download it from python.org if you don’t have it).

Steps:Follow the Installation Steps above to clone the repo and install discord.py.
Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux).
Navigate to the yourrepo folder with cd yourrepo.
Type python discord_bot.py and hit Enter—Strack will start running!
Keep the terminal open while the bot is active. If you close it, Strack will go offline.

Tips: Make sure your internet is on—Strack needs it to chat with Discord!
If the terminal shows errors, double-check your YOUR_BOT_TOKEN and EXCLUDED_CHANNEL_ID in bot.py.

# Customization Notes

 Repository URL: Swap https://github.com/yourusername/yourrepo.git with your actual GitHub link.
 Bot Token: Users need to grab their own token from the Discord Developer Portal and keep it safe.
 Channel ID: The EXCLUDED_CHANNEL_ID placeholder (0) needs a real ID from users.
 License: Update the LICENSE file with your name or team (e.g., "Your Name" or "Strack Crew").
 .gitignore: Use the recommended version from my previous response (Option 1, ignoring message_counts.json and bot_logs.json):

 ```# Python
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
env/

# Runtime-generated files
message_counts.json
bot_logs.json

# OS generated files
.DS_Store
Thumbs.db

# IDE files
.idea/
*.sublime-workspace
*.vscode/
 ```

# Sensitive data (if using environment files)
.env ```

# How to Use
1. Save this as `README.md` in your repo root.
2. Commit and push to GitHub:
   ```bash
   git add README.md
   git commit -m "Add friendly README for Strack"
   git push origin main
   ```
3. Add the other files (`bot.py`, `message_counts.json`, `bot_logs.json`, `LICENSE`, `.gitignore`) from my previous responses.
