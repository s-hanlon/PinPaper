import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import time
import schedule

from pinpaper import run_pinpaper  # assumes pinpaper.py is in the same folder

# === CONFIG ===
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULTS = {
    "board_url": "https://www.pinterest.com/seanhanlon126/u-kno-the-vibes/",
    "download_dir": os.path.join(os.path.expanduser("~"), "Pictures", "PinPaper"),
    "update_frequency_minutes": 1440
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULTS.copy()
    with open(CONFIG_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return DEFAULTS.copy()

def save_config(data):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=4)

# === GUI SETUP ===
config = load_config()
root = tk.Tk()
root.title("PinPaper Settings")
root.geometry("400x260")

# URL Entry
tk.Label(root, text="Pinterest Board URL:").pack(anchor="w", padx=10, pady=(10, 0))
url_entry = tk.Entry(root, width=50)
url_entry.insert(0, config.get("board_url", ""))
url_entry.pack(padx=10, pady=5)

# Frequency Dropdown
tk.Label(root, text="Update Frequency:").pack(anchor="w", padx=10, pady=(10, 0))
frequency_options = {
    "Every 10 minutes": 10,
    "Every 1 hour": 60,
    "Every 12 hours": 720,
    "Every 24 hours": 1440
}
dropdown = ttk.Combobox(root, values=list(frequency_options.keys()), state="readonly", width=47)
current_freq = config.get("update_frequency_minutes", 1440)
for label, minutes in frequency_options.items():
    if minutes == current_freq:
        dropdown.set(label)
        break
dropdown.pack(padx=10, pady=5)

# Save Settings
def save_settings():
    new_url = url_entry.get().strip()
    new_freq_label = dropdown.get()
    if not new_url.startswith("https://www.pinterest.com/"):
        messagebox.showerror("Invalid URL", "Please enter a valid Pinterest board URL.")
        return
    new_config = {
        "board_url": new_url,
        "download_dir": config.get("download_dir"),
        "update_frequency_minutes": frequency_options[new_freq_label]
    }
    save_config(new_config)
    messagebox.showinfo("Success", "Settings saved successfully!")

tk.Button(root, text="Save Settings", command=save_settings).pack(pady=(5, 10))

# Start Updating Button
def start_wallpaper_loop():
    config = load_config()
    minutes = config.get("update_frequency_minutes", 1440)

    # Cancel previous jobs if any
    schedule.clear("wallpaper")

    # Schedule the update job
    schedule.every(minutes).minutes.do(run_pinpaper).tag("wallpaper")

    # Run immediately once
    try:
        run_pinpaper()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to set wallpaper: {e}")
        return

    def scheduler_loop():
        while True:
            schedule.run_pending()
            time.sleep(30)

    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    messagebox.showinfo("Running", f"Wallpaper will update every {minutes} minutes.")

tk.Button(root, text="Start Updating", command=start_wallpaper_loop).pack(pady=10)

root.mainloop()
