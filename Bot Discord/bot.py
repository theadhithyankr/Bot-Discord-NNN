import discord
from discord.ext import commands, tasks
import json
from datetime import datetime
import os

# Directly set token
TOKEN = "MTI5OTk4ODQwMjI1ODg0MTY0MA.GDjdJj.d9-A9Ahfke7JVO65uzzPsw_tDJFFkl6RNiUCkI"

# Check if the token is loaded correctly
if TOKEN is None:
    raise ValueError("No token found. Please set the DISCORD_TOKEN environment variable.")

# Load streak data from a JSON file or initialize if it doesn’t exist
try:
    with open('streaks.json', 'r') as f:
        streaks = json.load(f)
except FileNotFoundError:
    streaks = {}

# Helper functions
def update_streak(user_id, reset=False):
    today = datetime.now().date()
    user_data = streaks.get(user_id, {"streak": 0, "last_checked_in": str(today)})
    last_checked_in = datetime.strptime(user_data["last_checked_in"], '%Y-%m-%d').date()
    
    # Reset or increment the streak
    if reset or (today - last_checked_in).days > 1:
        user_data["streak"] = 0 if reset else 1
    elif today == last_checked_in:  # Prevent multiple check-ins in a single day
        return False
    
    else:
        user_data["streak"] += 1
    
    user_data["last_checked_in"] = str(today)
    streaks[user_id] = user_data
    save_streaks()
    return True

def save_streaks():
    with open('streaks.json', 'w') as f:
        json.dump(streaks, f, indent=4)

# Leaderboard function
def get_leaderboard():
    sorted_streaks = sorted(streaks.items(), key=lambda x: x[1]["streak"], reverse=True)
    leaderboard = "\n".join([f"{i+1}. <@{user_id}> - {data['streak']} days" for i, (user_id, data) in enumerate(sorted_streaks[:10])])
    return leaderboard if leaderboard else "No streaks yet."

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    daily_leaderboard.start()  # Start daily leaderboard task

@bot.command(name="checkin")
async def checkin(ctx):
    user_id = str(ctx.author.id)
    if update_streak(user_id):
        await ctx.send(f'{ctx.author.name}, streak updated! Current streak: {streaks[user_id]["streak"]} days')
    else:
        await ctx.send(f'{ctx.author.name}, you have already checked in today!')

@bot.command(name="fail")
async def fail(ctx):
    user_id = str(ctx.author.id)
    update_streak(user_id, reset=True)
    await ctx.send(f'{ctx.author.name}, you are a fuckin loser go die a virgin .Your streak has been reset.')

@bot.command(name="streak")
async def streak(ctx):
    user_id = str(ctx.author.id)
    streak_count = streaks.get(user_id, {}).get("streak", 0)
    await ctx.send(f'{ctx.author.name}, Bro you are doing brotastically it,your current streak is {streak_count} days')

@bot.command(name="leaderboard")
async def leaderboard(ctx):
    leaderboard_message = get_leaderboard()
    await ctx.send(f"**Leaderboard:**\n{leaderboard_message}")

# Daily task for displaying the leaderboard
@tasks.loop(hours=24)
async def daily_leaderboard():
    channel_id = 1300003051540582500  # Replace with your channel ID
    channel = bot.get_channel(channel_id)
    if channel:
        leaderboard_message = get_leaderboard()
        await channel.send(f"**Daily Leaderboard:**\n{leaderboard_message}")
    else:
        print("Channel not found for daily leaderboard.")

# Run the bot
bot.run(TOKEN)
