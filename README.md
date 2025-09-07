
# **Strack Discord Bot**

Hey there! Meet **Strack**, your friendly neighborhood Discord bot that’s here to track message activity and spice up your server with awesome leaderboards! Built with Python and the `discord.py` library, Strack is perfect for communities, gaming crews, or any server where roles matter. It’s all about celebrating your most chatty members in style!

## INVITE STRACK TO YOUR SERVER: 
https://discord.com/oauth2/authorize?client_id=1377959085973966898&permissions=9897552522385&integration_type=0&scope=applications.commands+bot


## **Welcome to Strack!**

Imagine a bot that not only keeps an eye on who’s chatting the most but also rolls out cool leaderboards to show off their skills. That’s **Strack** for you! It watches messages in real-time, skips the bot spam and a channel you pick, and lets you see who’s dominating the convo—whether it’s the "Agent" role or any other crew you’ve got. With a snazzy embed design and simple commands, Strack is ready to bring some fun to your server!

## **What Strack Can Do**

- **Message Tracking**: Counts messages from folks with roles (no bots or your chosen quiet zone included).
- **Role-Based Leaderboards**: Check out the top talkers for "Agent" or any role you name.
- **Easy Navigation**: Flip through leaderboards (10 peeps per page) with `⬅️` and `➡️` reactions.
- **Admin Power**: Reset those counts with `/resetcounts` if you’re an admin.
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
  pip install discord.py python-dotenv
  ```
  - Added `python-dotenv` to handle the `.env` file.

### **Step 3: Set Up Your `.env` File**
- Create a file named `.env` in the `yourrepo` folder using a text editor.
- Add these lines (keep them secret!):
  ```
  BOT_TOKEN=your-actual-discord-bot-token-here
  EXCLUDED_CHANNEL_ID=123456789012345678
  ```
  - Get your `BOT_TOKEN` from the Discord Developer Portal.
  - Find `EXCLUDED_CHANNEL_ID` by enabling Developer Mode in Discord, right-clicking the channel to exclude, and copying its ID.
  - Save the file—don’t commit it to GitHub (it’s ignored by `.gitignore`).

### **Step 4: Run the Bot**
- Start the bot with:
  ```bash
  python bot.py
  ```
- Invite Strack to your server using its OAuth2 URL from the Discord Developer Portal.

### **Step 5: Generate Data Files**
- Run the bot once (`python bot.py`) to automatically create `message_counts.json` and `bot_logs.json` with default structures. These files will track messages and logs, so no need to add them manually!

 ## RUN STRACK ON YOUR TERMINAL (NO HOSTING NEEDED!)

Don’t have a fancy hosting service? No problem! You can fire up **Strack** right on your own computer using the terminal. It’s super easy, and we’ll walk you through it step by step. All you need is your PC or laptop and a bit of patience—let’s get Strack chatting in your server!

### **What You’ll Need**
- A computer with **Python** installed (grab it from [python.org](https://www.python.org/) if you don’t have it—version 3.8 or higher works best).
- An internet connection (Strack needs it to talk to Discord!).
- Your Discord bot token (get it from the Discord Developer Portal).

### **Step-by-Step Guide**

#### **Step 1: Clone the Repository**
- Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux, or any code editor’s terminal).
- Type this command to grab Strack’s code from GitHub:
  ```bash
  git clone https://github.com/yourusername/yourrepo.git
  ```
  - Swap `https://github.com/yourusername/yourrepo.git` with your actual repo URL.
- Hit Enter, and the files will download to a folder named `yourrepo`.

#### **Step 2: Navigate to the Folder**
- Move into the `yourrepo` folder by typing:
  ```bash
  cd yourrepo
  ```
- This tells your terminal where Strack lives—double-check you’re in the right spot!

#### **Step 3: Install the Required Tools**
- Strack needs `discord.py` and `python-dotenv` to work its magic. Install them with:
  ```bash
  pip install discord.py python-dotenv
  ```
- If you see an error, try `pip3 install discord.py python-dotenv` or ensure Python is added to your system’s PATH.

#### **Step 4: Tweak the `.env` File**
- Create or edit the `.env` file in the `yourrepo` folder with:
  ```
  BOT_TOKEN=your-actual-discord-bot-token-here
  EXCLUDED_CHANNEL_ID=123456789012345678
  ```
  - Replace `your-actual-discord-bot-token-here` with your token.
  - Replace `123456789012345678` with your excluded channel ID.
  - Save it and keep it private!

#### **Step 5: Launch Strack**
- In the terminal, type:
  ```bash
  python bot.py
  ```
- Hit Enter, and Strack should start! You’ll see some log messages pop up, and it’ll begin tracking messages.
- If it works, the terminal will stay open, and Strack will be active in your server. If you get errors, check the next section.

#### **Step 6: Keep It Running**
- Leave the terminal window open while Strack is active. Closing it will stop the bot.
- To stop Strack, just press `Ctrl + C` in the terminal.

### **Troubleshooting Tips**
- **Error: "python is not recognized"**: You might need to install Python or add it to your PATH. Reinstall from [python.org](https://www.python.org/) and check "Add Python to PATH" during setup.

- **Error: "Invalid token"**: Double-check your `BOT_TOKEN` in `.env`—it’s case-sensitive!

- **No Response**: Ensure the bot is invited to your server with proper permissions (e.g., read/send messages) via the OAuth2 URL.

- **JSON Files Missing**: Don’t worry! Strack will create `message_counts.json` and `bot_logs.json` the first time it runs—check the folder after starting.

- **ModuleNotFoundError: dotenv**: Make sure you installed `python-dotenv` with `pip install python-dotenv`.

## **Strack’s Commands**

### **/leaderboard**
- **What It Does**: Shows off a leaderboard for the "Agent" role’s top talkers.
- **How to Use**: `/leaderboard`
- **Who Can Use**: Anyone!
- **Fun Stuff**: Pages through 10 folks at a time with `⬅️` and `➡️` to scroll.

### **/rolecount <role_name>**
- **What It Does**: Pulls up a leaderboard for any role you name.
- **How to Use**: `/rolecount <role_name>` (e.g., `/rolecount Agent` or `/rolecount "Trusted Member"`)
- **Who Can Use**: Anyone!
- **Fun Stuff**: Pages through 10 folks at a time with `⬅️` and `➡️` to scroll.

### **/resetcounts**
- **What It Does**: Wipes the slate clean and resets all message counts.
- **How to Use**: `/resetcounts`
- **Who Can Use**: Admins only!
- **Fun Stuff**: Lets you start fresh with a quick confirmation message.

### **/setexcludedchannel**
- **What It Does**: Sets or updates the channel ID to exclude from message counting.
- **How to Use**: `/setexcludedchannel` followed by the channel ID in the next message (e.g., `123456789012345678`) or ‘cancel’ to abort.
- **Who Can Use**: Admins only!
- **Fun Stuff**: Strack will ask for the ID, update its settings, and ignore that channel moving forward. Enable Developer Mode in Discord to get the ID!

### **/ping**
- **Checks whether the bot is responsive**

## **What’s in the Folder**
- `discord_bot.py`: The heart of Strack—where the magic happens.
- `create_message_counts.json`: Keeps track of who’s chatted and when it last reset (starts with sample data).
- `bot_logs.json`: Logs all the bot’s adventures (starts empty).
- `README.md`: This handy guide!
- `LICENSE`: MIT License so you can use and share Strack freely.
- `.gitignore`: Tells Git what to skip.
- `.env`: Stores your bot token and channel ID (keep it secret!).

## **Join the Fun!**
Spot a glitch or have a cool idea? Drop an issue on this GitHub repo or send a pull request. We’d love your input to make Strack even better!

## **License**
Strack comes with the [MIT License](LICENSE), meaning you can use, tweak, and share it as long as you give a shoutout. Check the `LICENSE` file for the full scoop.

## **Quick Tips**
- **Setup**: Make sure your `.env` file is set up with `BOT_TOKEN` and `EXCLUDED_CHANNEL_ID` before launching.
- **Logs**: Peek at `bot_logs.json` to see what Strack’s been up to.
- **Help**: Got questions? Hit up the maintainers via GitHub Issues.

---

# Customization Notes

- **Repository URL**: Swap `https://github.com/yourusername/yourrepo.git` with your actual GitHub link.
- **.env Security**: Users must create their own `.env` file and never commit it. The `.gitignore` already excludes it.
- **License**: Update the `LICENSE` file with your name or team (e.g., "Your Name" or "Strack Crew").
- **.gitignore**: Use the updated version above, ensuring `.env` is ignored.

# How to Use

1. Save the updated `bot.py` and create the `.env` file in your repo root.
2. Update `README.md` with the content above.
3. Commit and push changes:
   ```bash
   git add bot.py README.md .env .gitignore
   git commit -m "Add .env support and update README"
   git push origin main
   ```
   - Note: The `.env` file won’t be tracked due to `.gitignore`, but add it locally for testing.
4. Install `python-dotenv` as instructed in the README.

