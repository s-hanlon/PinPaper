import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# === CONFIG SETUP ===
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULTS = {
    "board_url": "https://www.pinterest.com/seanhanlon126/u-kno-the-vibes/",
    "download_dir": os.path.join(os.path.expanduser("~"), "Pictures", "PinPaper"),
    "update_frequency_minutes": 1440  # Default: 24 hours
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

# === GUI ===
config = load_config()

root = tk.Tk()
root.title("PinPaper Settings")
root.geometry("400x220")

# Pinterest Board URL
tk.Label(root, text="Pinterest Board URL:").pack(anchor="w", padx=10, pady=(10, 0))
url_entry = tk.Entry(root, width=50)
url_entry.insert(0, config.get("board_url", ""))
url_entry.pack(padx=10, pady=5)

# Update Frequency Dropdown
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

# Save Button
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

tk.Button(root, text="Save Settings", command=save_settings).pack(pady=15)

root.mainloop()
