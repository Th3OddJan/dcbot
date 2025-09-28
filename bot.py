# bot.py - Borderlands 4 SHiFT-Code Bot (Postet sofort + alle 24h)
import os
import discord
from discord.ext import tasks, commands
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
import asyncio
from aiohttp import web

# === KONFIG ===
CHANNEL_ID = 1421873779163922502
POSTED_FILE = "posted_codes.txt"
# =================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ====================

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

# ----------- Scraper -----------

def scrape_gameradar():
    url = "https://www.gamesradar.com/games/borderlands/borderlands-4-shift-codes-golden-keys/"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"Fehler GamesRadar: {e}")
        return []
    codes = []
    for block in soup.find_all("li"):
        text = block.get_text(separator=" ").strip()
        if "Golden Key" in text and "-" in text:
            codes.append(text)
    return codes

def scrape_mentalmars():
    url = "https://mentalmars.com/game-news/borderlands-4-shift-codes/"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"Fehler MentalMars: {e}")
        return []
    codes = []
    for block in soup.find_all("li"):
        text = block.get_text(separator=" ").strip()
        if "Golden Key" in text and "-" in text:
            codes.append(text)
    return codes

def scrape_mobalytics():
    url = "https://mobalytics.gg/borderlands-4/shift-codes-borderlands-4"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"Fehler Mobalytics: {e}")
        return []
    codes = []
    for block in soup.find_all("li"):
        text = block.get_text(separator=" ").strip()
        if "Golden Key" in text and "-" in text:
            codes.append(text)
    return codes

def fetch_all_shift_codes():
    codes = []
    codes += scrape_gameradar()
    codes += scrape_mentalmars()
    codes += scrape_mobalytics()
    return get_valid_codes(codes)

def load_posted_codes():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_posted_codes(codes):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        for code in codes:
            f.write(code + "\n")

async def post_codes():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ FEHLER: Channel nicht gefunden!")
        return
    all_codes = fetch_all_shift_codes()
    posted_codes = load_posted_codes()
    new_codes = [c for c in all_codes if c not in posted_codes]
    if not new_codes:
        print("Keine neuen Codes gefunden.")
        return
    msg = "🔑 **Neue Borderlands 4 SHiFT-Codes:**\n\n"
    for c in new_codes:
        msg += f"• {c}\n"
    await channel.send(msg)
    save_posted_codes(posted_codes.union(new_codes))

# ==================== Tasks ====================

@bot.event
async def on_ready():
    print(f"✅ Eingeloggt als {bot.user}")
    await post_codes()  # Sofort posten
    check_codes.start()  # Task alle 24h

@tasks.loop(hours=24)
async def check_codes():
    await post_codes()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# ==================== Dummy-Webserver für Render ====================

async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

# Render stellt PORT bereit, Default 10000
asyncio.create_task(web._run_app(app, port=int(os.environ.get("PORT", 10000))))

# ==================== Bot starten ====================
bot.run(os.environ["DISCORD_TOKEN"])
