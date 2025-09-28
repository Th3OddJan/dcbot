import os
import discord
from discord.ext import tasks, commands
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from aiohttp import web
import asyncio

CHANNEL_ID = 1421873779163922502
POSTED_FILE = "posted_codes.txt"
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----- Scraper Funktionen (wie gehabt) -----
def get_valid_codes(codes_list):
    today = datetime.now()
    valid_codes = []
    for code_entry in codes_list:
        if 'expired' in code_entry.lower():
            continue
        match = re.search(r'expires (\w+ \d{1,2})', code_entry, re.IGNORECASE)
        if match:
            expire_str = match.group(1) + f' {today.year}'
            try:
                expire_date = datetime.strptime(expire_str, '%B %d %Y')
                if expire_date < today:
                    continue
            except ValueError:
                pass
        valid_codes.append(code_entry)
    return valid_codes

# Beispiel Scraper: nur für Demo, gleiche Struktur wie vorher
def scrape_demo():
    return ["Golden Key - Beispielcode"]

def fetch_all_shift_codes():
    return get_valid_codes(scrape_demo())

def load_posted_codes():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_posted_codes(codes):
    with open(POSTED_FILE, "w") as f:
        for code in codes:
            f.write(code + "\n")

async def post_codes():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel nicht gefunden")
        return
    all_codes = fetch_all_shift_codes()
    posted_codes = load_posted_codes()
    new_codes = [c for c in all_codes if c not in posted_codes]
    if not new_codes:
        return
    msg = "Neue Codes:\n" + "\n".join(new_codes)
    await channel.send(msg)
    save_posted_codes(posted_codes.union(new_codes))

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}")
    await post_codes()
    check_codes.start()

@tasks.loop(hours=24)
async def check_codes():
    await post_codes()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# ----- Webserver für Render -----
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

# ----- Start Webserver + Bot -----
async def start_services():
    # Discord Bot als Task starten
    asyncio.create_task(bot.start(TOKEN))
    # Webserver starten
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()
    print("Webserver läuft auf Port", os.environ.get("PORT", 10000))
    while True:
        await asyncio.sleep(3600)  # Prozess alive halten

asyncio.run(start_services())
