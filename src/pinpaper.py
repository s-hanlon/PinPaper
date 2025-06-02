import feedparser
import requests
import os
import ctypes
from datetime import datetime

# === CONFIG ===
RSS_FEED = "https://www.pinterest.com/seanhanlon126/u-kno-the-vibes/"
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "PinPaper")
WALLPAPER_PATH = os.path.join(DOWNLOAD_DIR, "pin_today.jpg")

# === CREATE FOLDER IF NEEDED ===
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === PARSE RSS ===
feed = feedparser.parse(RSS_FEED)
if not feed.entries:
    raise Exception("No entries found in feed.")

# Get latest image URL
img_url = feed.entries[0].get("media_content", [{}])[0].get("url", None)
if not img_url:
    raise Exception("No image found in feed entry.")

# === DOWNLOAD IMAGE ===
response = requests.get(img_url)
with open(WALLPAPER_PATH, 'wb') as f:
    f.write(response.content)

# === SET AS WALLPAPER (Windows only) ===
ctypes.windll.user32.SystemParametersInfoW(20, 0, WALLPAPER_PATH, 3)

print(f"[{datetime.now()}] Wallpaper updated from: {img_url}")
