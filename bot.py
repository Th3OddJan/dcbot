# bot.py - Borderlands 4 SHiFT-Code Bot (Postet sofort + alle 24h)
import os
import discord
from discord.ext import tasks, commands
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
import threading
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
            expire
