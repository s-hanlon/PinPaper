import os
import json
import ctypes
import random
from datetime import datetime
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def run_pinpaper():
    # === LOAD CONFIG ===
    DEFAULT_BOARD_URL = "https://www.pinterest.com/seanhanlon126/pinpaper/"
    DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "PinPaper")
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        BOARD_URL = config.get("board_url", DEFAULT_BOARD_URL)
        DOWNLOAD_DIR = config.get("download_dir", DEFAULT_DIR)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ Could not load config.json — using default settings.")
        BOARD_URL = DEFAULT_BOARD_URL
        DOWNLOAD_DIR = DEFAULT_DIR

    WALLPAPER_PATH = os.path.join(DOWNLOAD_DIR, "pin_today.jpg")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # === SETUP SELENIUM (HEADLESS BROWSER) ===
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1920x3000")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(BOARD_URL)

    # === SCROLL TO LOAD MORE PINS ===
    scroll_pause = 3
    scroll_attempts = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(scroll_attempts):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # === PARSE IMAGE TAGS ===
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    def extract_img_urls(soup):
        img_tags = soup.find_all("img")
        return [
            img["src"] for img in img_tags
            if "pinimg.com" in img.get("src", "") and "/236x/" in img.get("src", "")
        ]

    img_urls = list(set(extract_img_urls(soup)))
    if not img_urls:
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        img_urls = list(set(extract_img_urls(soup)))

    if not img_urls:
        raise Exception("No Pinterest images found.")

    # === SELECT + UPGRADE IMAGE QUALITY ===
    base_url = random.choice(img_urls)
    quality_paths = ["/originals/", "/736x/", "/564x/", "/236x/"]
    img_url = None
    img_resp = None

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

    if not img_resp or not img_url:
        raise Exception("Could not retrieve a valid image from any quality level.")

    # === DOWNLOAD IMAGE ===
    with open(WALLPAPER_PATH, 'wb') as f:
        f.write(img_resp.content)

    # === SET AS WALLPAPER (Windows only) ===
    ctypes.windll.user32.SystemParametersInfoW(20, 0, WALLPAPER_PATH, 3)
    print(f"[{datetime.now()}] Wallpaper updated from: {img_url}")

if __name__ == "__main__":
    run_pinpaper()
