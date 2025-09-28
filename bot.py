import os
import discord
from discord.ext import tasks, commands
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from aiohttp import web
import asyncio

# ==================== CONFIG ====================
CHANNEL_ID = 1421873779163922502
POSTED_FILE = "posted_codes.txt"
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== SCRAPER ====================

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
        valid_codes.append(c_
