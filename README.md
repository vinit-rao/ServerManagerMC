# ServerManagerMC

A custom-built Discord bot designed to manage, monitor, and bridge chat for **My Minecraft Server** (vinitrao.com). Built in Python, this bot creates a seamless two-way connection between a Linux-hosted Minecraft server and Discord.


## ✨ Features

* **Live Chat Bridge:** Real-time two-way communication between the Discord `#chat-mc` channel and the in-game Minecraft chat.
<img width="1635" height="417" alt="image" src="https://github.com/user-attachments/assets/2ada0d92-11d3-4bc2-89c0-07d99f955284" />

* **Color-Coded Event Tracking:** In-game events (player joins, advancements, and deaths) are dynamically color-coded in the Discord log for easy reading.
* **Red Theme Terminal:** A stylized, auto-updating ANSI terminal directly inside Discord for monitoring server logs.
<img width="558" height="122" alt="image" src="https://github.com/user-attachments/assets/d737d119-7d42-4873-a4f6-351e6fda6716" />

* **Server Power Controls:** Start and safely stop the Minecraft server directly from Discord using `!startserver` and `!stopserver`.
<img width="487" height="156" alt="image" src="https://github.com/user-attachments/assets/4df69d30-f634-4e67-9244-b32ace6d375c" />

* **Dynamic MOTD Injection:** Automatically reads `version.txt` and updates the server's multiplayer menu description before booting.
<img width="620" height="80" alt="image" src="https://github.com/user-attachments/assets/451daab7-6aac-4c2b-92e2-5917c8e658b4" />
* **Admin Console Execution:** Authorized users can send raw server commands directly to the Ubuntu `screen` session via Discord.
<img width="1529" height="184" alt="image" src="https://github.com/user-attachments/assets/fae52396-4f37-4dd1-9c21-fe74b027e932" />

* **Rich Presence:** Displays a custom "Watching vinitrao.com" status in the Discord member list.
<img width="250" height="67" alt="image" src="https://github.com/user-attachments/assets/13aa3b71-ddee-4f4f-9699-6d8bc6a0b479" />

## 🛠️ Prerequisites

To run this bot, your server environment needs:
* **OS:** Ubuntu / Linux (Relies on the `screen` utility for background processing).
* **Python:** Python 3.8+
* **Dependencies:** `discord.py`, `python-dotenv`
* **Minecraft:** Java 25 (if running Minecraft 1.21.2+).

## 🚀 Setup & Installation

**1. Clone the repository:**
```bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd your-repo-name
```

Make a .env file and put your Discord bot key into that file:
```
DISCORD_TOKEN="your discord bot token here"
```

In main.py change line 15 (the directory to your mc server files) to have the bot read your code:
```
MC_FOLDER = "your server file directory here"
```
make sure in discord you have two text channels with the following names:
terminal-mc*
chat-mc*

Also make sure the bot has administrator perms*



BTW u need to know how to do port forwarding and all that other stuff so just this wont be enought to have the server setup btw.
