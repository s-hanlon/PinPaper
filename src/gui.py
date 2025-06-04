import os
import json
import threading
import time
import schedule

from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from tkinter import messagebox
from PIL import Image
import pystray
from pinpaper import run_pinpaper

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
ICON_PATH = os.path.join(os.path.dirname(__file__), 'icon.png')

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

def start_scheduled_updates():
    config = load_config()
    interval = config.get("update_frequency_minutes", 1440)

    schedule.clear("pinpaper")
    schedule.every(interval).minutes.do(run_pinpaper).tag("pinpaper")

    def loop():
        while True:
            schedule.run_pending()
            time.sleep(30)

    threading.Thread(target=loop, daemon=True).start()
    print(f"[Scheduler] Updates scheduled every {interval} minutes.")

def launch_gui():
    config = load_config()
    style = Style("superhero")  # try "cosmo", "superhero", "flatly", etc.
    root = style.master
    root.title("PinPaper Settings")
    root.geometry("420x280")

    frm = ttk.Frame(root, padding=15)
    frm.pack(fill=BOTH, expand=YES)

    ttk.Label(frm, text="Pinterest Board URL:").pack(anchor=W, pady=(0, 4))
    url_entry = ttk.Entry(frm, width=50)
    url_entry.insert(0, config.get("board_url", ""))
    url_entry.pack(fill=X, pady=(0, 10))

    ttk.Label(frm, text="Update Frequency:").pack(anchor=W, pady=(0, 4))
    frequency_options = {
        "Every 10 minutes": 10,
        "Every 1 hour": 60,
        "Every 12 hours": 720,
        "Every 24 hours": 1440
    }
    dropdown = ttk.Combobox(frm, values=list(frequency_options.keys()), state="readonly", width=47, bootstyle="primary")
    current_freq = config.get("update_frequency_minutes", 1440)
    for label, minutes in frequency_options.items():
        if minutes == current_freq:
            dropdown.set(label)
            break
    dropdown.pack(fill=X, pady=(0, 12))

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

    def start_updates():
        try:
            run_pinpaper()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set wallpaper: {e}")
            return
        start_scheduled_updates()
        messagebox.showinfo("Running", "Wallpaper will now update in the background.")

    ttk.Button(frm, text="💾 Save Settings", command=save_settings, bootstyle="success").pack(pady=(0, 6), fill=X)
    ttk.Button(frm, text="▶ Start Updating", command=start_updates, bootstyle="info").pack(pady=(0, 6), fill=X)

    def minimize_to_tray():
        root.withdraw()
        icon_image = Image.open(ICON_PATH)

        def show_window():
            root.deiconify()

        def quit_app():
            tray_icon.stop()
            root.destroy()

        def force_update():
            try:
                run_pinpaper()
            except Exception as e:
                print(f"[Tray] Update failed: {e}")

        tray_menu = pystray.Menu(
            pystray.MenuItem("Force Update", lambda: force_update()),
            pystray.MenuItem("Open Settings", lambda: show_window()),
            pystray.MenuItem("Exit", lambda: quit_app())
        )

        tray_icon = pystray.Icon("PinPaper", icon_image, "PinPaper", tray_menu)
        threading.Thread(target=tray_icon.run, daemon=True).start()

    root.protocol("WM_DELETE_WINDOW", minimize_to_tray)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
