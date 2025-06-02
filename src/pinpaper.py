import feedparser
import requests
import os
import ctypes
import json
from datetime import datetime

# === LOAD CONFIG ===
DEFAULT_FEED = "https://www.pinterest.com/seanhanlon126/u-kno-the-vibes.rss"
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "PinPaper")

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    RSS_FEED = config.get("rss_feed", DEFAULT_FEED)
    DOWNLOAD_DIR = config.get("download_dir", DEFAULT_DIR)
except (FileNotFoundError, json.JSONDecodeError):
    print("⚠️ Could not load config.json — using default settings.")
    RSS_FEED = DEFAULT_FEED
    DOWNLOAD_DIR = DEFAULT_DIR

WALLPAPER_PATH = os.path.join(DOWNLOAD_DIR, "pin_today.jpg")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === PARSE RSS ===
feed = feedparser.parse(RSS_FEED)

if not feed.entries:
    raise Exception("No entries found in feed.")

# Debug: print out the first entry structure
print("=== DEBUG: First Feed Entry ===")
print(feed.entries[0])
print("===============================")

# Get latest image URL
import re

summary_html = feed.entries[0].get("summary", "")
match = re.search(r'<img src="([^"]+)"', summary_html)

if not match:
    raise Exception("No image URL found in summary HTML.")

img_url = match.group(1)

# === DOWNLOAD IMAGE ===
response = requests.get(img_url)
with open(WALLPAPER_PATH, 'wb') as f:
    f.write(response.content)

# === SET AS WALLPAPER (Windows only) ===
ctypes.windll.user32.SystemParametersInfoW(20, 0, WALLPAPER_PATH, 3)

print(f"[{datetime.now()}] Wallpaper updated from: {img_url}")
