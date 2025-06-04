import os
import json
import ctypes
import random
from datetime import datetime
import requests
import time
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import feedparser
from win10toast import ToastNotifier
notifier = ToastNotifier()


def scale_scrolls(pin_hint):
    if pin_hint == "<40":
        return 2
    elif pin_hint == "<60":
        return 3
    elif pin_hint == "<100":
        return 4
    else:
        return 5

def fetch_from_rss(board_url):
    rss_url = board_url.rstrip('/') + ".rss"
    feed = feedparser.parse(rss_url)
    entries = feed.entries
    if not entries:
        raise Exception("RSS feed is empty.")

    image_urls = []
    for entry in entries:
        if 'summary' in entry and 'img src="' in entry.summary:
            match = re.search(r'img src="([^"]+)"', entry.summary)
            if match:
                image_urls.append(match.group(1))

    if not image_urls:
        raise Exception("No images found in RSS entries.")

    return random.choice(image_urls)


def run_pinpaper():
    DEFAULT_BOARD_URL = "https://www.pinterest.com/seanhanlon126/pinpaper/"
    DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "PinPaper")
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        BOARD_URL = config.get("board_url", DEFAULT_BOARD_URL)
        DOWNLOAD_DIR = config.get("download_dir", DEFAULT_DIR)
        PIN_HINT = config.get("pin_count_hint", "<100")
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ Could not load config.json — using default settings.")
        BOARD_URL = DEFAULT_BOARD_URL
        DOWNLOAD_DIR = DEFAULT_DIR
        PIN_HINT = "<100"

    WALLPAPER_PATH = os.path.join(DOWNLOAD_DIR, "pin_today.jpg")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    if PIN_HINT == "<20":
        print(f"[Info] User selected pin count hint: {PIN_HINT} — using RSS.")
        base_url = fetch_from_rss(BOARD_URL)
    else:
        scrolls = scale_scrolls(PIN_HINT)
        print(f"[Info] User selected pin count hint: {PIN_HINT} — scrolling {scrolls} times.")

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--window-size=1920x3000")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(BOARD_URL)
        time.sleep(2)

        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        img_tags = soup.find_all("img")
        img_urls = list({
            img["src"] for img in img_tags
            if "pinimg.com" in img.get("src", "") and "/236x/" in img.get("src", "")
        })

        if not img_urls:
            raise Exception("No Pinterest images found via scraping.")

        base_url = random.choice(img_urls)

    quality_paths = ["/originals/", "/736x/", "/564x/", "/236x/"]
    img_url, img_resp = None, None
    for quality in quality_paths:
        test_url = base_url.replace("/236x/", quality)
        try:
            resp = requests.get(test_url, timeout=5)
            if resp.status_code == 200:
                img_url = test_url
                img_resp = resp
                break
        except:
            continue

    if not img_resp:
        raise Exception("No valid high-quality image found.")

    with open(WALLPAPER_PATH, 'wb') as f:
        f.write(img_resp.content)

    ctypes.windll.user32.SystemParametersInfoW(20, 0, WALLPAPER_PATH, 3)
    print(f"[{datetime.now()}] Wallpaper updated from: {img_url}")
    notifier.show_toast("PinPaper", "Wallpaper updated successfully!", duration=5, threaded=True)

if __name__ == "__main__":
    run_pinpaper()
