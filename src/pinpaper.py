import requests
from bs4 import BeautifulSoup
import os
import ctypes
import json
import random
from datetime import datetime

# === LOAD CONFIG ===
DEFAULT_BOARD_URL = "https://www.pinterest.com/seanhanlon126/u-kno-the-vibes/"
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "PinPaper")

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    BOARD_URL = config.get("board_url", DEFAULT_BOARD_URL)
    DOWNLOAD_DIR = config.get("download_dir", DEFAULT_DIR)
except (FileNotFoundError, json.JSONDecodeError):
    print("Could not load config.json — using default settings.")
    BOARD_URL = DEFAULT_BOARD_URL
    DOWNLOAD_DIR = DEFAULT_DIR

WALLPAPER_PATH = os.path.join(DOWNLOAD_DIR, "pin_today.jpg")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === SCRAPE BOARD HTML ===
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(BOARD_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Extract all <img> tags pointing to pinimg.com
img_tags = soup.find_all("img")
img_urls = [
    img["src"] for img in img_tags
    if "pinimg.com" in img.get("src", "") and "/236x/" in img.get("src", "")
]

# Deduplicate
img_urls = list(set(img_urls))

if not img_urls:
    raise Exception("No usable Pinterest images found.")

# Choose one at random
base_url = random.choice(img_urls)

# Try higher quality versions
quality_paths = ["/originals/", "/736x/", "/564x/", "/236x/"]
img_url = None

for quality in quality_paths:
    test_url = base_url.replace("/236x/", quality)
    try:
        img_resp = requests.get(test_url, timeout=5)
        if img_resp.status_code == 200:
            img_url = test_url
            break
    except Exception as e:
        print(f"Error checking {test_url}: {e}")

if not img_url:
    raise Exception("Could not retrieve a valid image from any quality level.")

# === DOWNLOAD IMAGE ===
with open(WALLPAPER_PATH, 'wb') as f:
    f.write(img_resp.content)

# === SET AS WALLPAPER (Windows only) ===
ctypes.windll.user32.SystemParametersInfoW(20, 0, WALLPAPER_PATH, 3)

print(f"[{datetime.now()}] Wallpaper updated from: {img_url}")
