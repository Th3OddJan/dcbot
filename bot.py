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
