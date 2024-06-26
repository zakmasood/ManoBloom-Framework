import discord
from discord.ext import commands, tasks
# Misc
import os
from dotenv import load_dotenv
# DB and Networking
import requests
import asyncio
import sqlite3
# Date / Time
from datetime import datetime, timedelta
from dateutil import parser
import time

#----------------------------------------------------------------

load_dotenv()
token = os.getenv('DiscordToken')
loggingChannelID = os.getenv('LoggingChannelID')
muteRoleID = os.getenv('MuteRoleID')

# Connect to the SQLite database
conn = sqlite3.connect('./launchpad.db')
c = conn.cursor()

def handleNewUser(UserID, Username, Avatar, IsBot):
    startTime = time.time()
    c.execute("SELECT * FROM User WHERE UserID = ?", (UserID,))
    user = c.fetchone()
    
    if not user:
        c.execute("INSERT INTO User (UserID, Username, Avatar, IsBot) VALUES (?, ?, ?, ?)",
                    (UserID, Username, Avatar, IsBot))
        conn.commit()
        
    endTime = time.time()
    writeTime = endTime - startTime
    print(f"Total WRITE time for user {UserID}: {writeTime} seconds")

# Set the bot's command prefix
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

#--------------------------------[Events]--------------------------------

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} is up and running!')

@bot.event
async def on_message(message):
    # Return if the message author is self
    if message.author.bot:
        return
    
    userID = message.author.id
    username = message.author.name
    avatar = str(message.author.avatar.url)
    isBot = message.author.bot
    
    handleNewUser(userID, username, avatar, isBot)
    
    # Increment total messages count for the user
    try:
        c.execute("UPDATE User SET TotalMessages = TotalMessages + 1 WHERE UserID = ?", (userID,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating total messages count: {e}")

    await bot.process_commands(message)
    
@bot.event
async def on_reaction_add(reaction, user):
    # Return if the reaction is added by a bot
    if user.bot:
        return

    userID = user.id

    # Increment total reactions count for the user
    try:
        c.execute("UPDATE User SET TotalReactions = TotalReactions + 1 WHERE UserID = ?", (userID,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating total reactions count: {e}")
        
        
#--------------------------------[Commands]--------------------------------

# Run the bot with your bot token
bot.run(token)