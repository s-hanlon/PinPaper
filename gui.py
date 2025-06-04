import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
import subprocess
import sys
import threading
import schedule
import time
from PIL import Image
import pystray

def save_config():
    board_url = board_url_var.get()
    download_dir = download_dir_var.get()
    interval_text = interval_var.get()
    pin_hint = pin_count_var.get()

    interval_map = {
        "10 minutes": 10,
        "1 hour": 60,
        "12 hours": 720,
        "24 hours": 1440
    }
    interval = interval_map.get(interval_text)

    if not board_url or not download_dir or not interval:
        messagebox.showwarning("Missing Info", "Please complete all fields.")
        return

    config = {
        "board_url": board_url,
        "download_dir": download_dir,
        "update_frequency_minutes": interval,
        "pin_count_hint": pin_hint
    }

    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    messagebox.showinfo("Saved", "Configuration saved successfully!")

def browse_directory():
    path = filedialog.askdirectory()
    if path:
        download_dir_var.set(path)

def run_wallpaper_update():
    try:
        import pinpaper
        pinpaper.run_pinpaper()
    except Exception as e:
        print(f"[Error] Wallpaper update failed: {e}")

def schedule_wallpaper_updates():
    interval_text = interval_var.get()
    interval_map = {
        "10 minutes": 10,
        "1 hour": 60,
        "12 hours": 720,
        "24 hours": 1440
    }
    minutes = interval_map.get(interval_text, 60)

    run_wallpaper_update()
    messagebox.showinfo("Started", f"Wallpaper will update every {interval_text}.")

    def loop():
        schedule.every(minutes).minutes.do(run_wallpaper_update)
        while True:
            schedule.run_pending()
            time.sleep(10)

    threading.Thread(target=loop, daemon=True).start()
    show_tray_icon()
    root.withdraw()

def on_exit(icon=None, item=None):
    if icon:
        icon.stop()
    os._exit(0)
    return True

def show_tray_icon():
    def resource_path(relative_path):
        """ Get absolute path to resource, works for PyInstaller and normal run """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(__file__), relative_path)

    icon_path = resource_path("icon.png")

    if not os.path.exists(icon_path):
        print("Missing icon.png for tray icon")
        return

    image = Image.open(icon_path)
    menu = pystray.Menu(
        pystray.MenuItem("Update Now", on_update_now),
        pystray.MenuItem("Settings", on_open_settings),
        pystray.MenuItem("Exit", on_exit)
    )



    icon = pystray.Icon("PinPaper", image, "PinPaper", menu)
    threading.Thread(target=icon.run, daemon=True).start()

def on_close():
    root.withdraw()

def on_update_now(icon, item):
    run_wallpaper_update()
    return True

def on_open_settings(icon, item):
    root.deiconify()
    return True


root = tb.Window(themename="darkly")
root.title("PinPaper Setup")
root.geometry("1200x500")
root.protocol("WM_DELETE_WINDOW", on_close)

board_url_var = tk.StringVar()
download_dir_var = tk.StringVar()
interval_var = tk.StringVar()
pin_count_var = tk.StringVar()

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        try:
            config = json.load(f)
            board_url_var.set(config.get("board_url", ""))
            download_dir_var.set(config.get("download_dir", ""))
            interval_minutes = config.get("update_frequency_minutes", 60)
            reverse_map = {
                10: "10 minutes",
                60: "1 hour",
                720: "12 hours",
                1440: "24 hours"
            }
            interval_var.set(reverse_map.get(interval_minutes, "1 hour"))
            pin_count_var.set(config.get("pin_count_hint", "<100"))
        except json.JSONDecodeError:
            pass

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

# Board URL
ttk.Label(frame, text="Pinterest Board URL").grid(row=0, column=0, sticky="w")
ttk.Entry(frame, textvariable=board_url_var, width=40).grid(row=0, column=1, pady=5)

# Download Directory
ttk.Label(frame, text="Download Directory").grid(row=1, column=0, sticky="w")
ttk.Entry(frame, textvariable=download_dir_var, width=30).grid(row=1, column=1, pady=5)
ttk.Button(frame, text="Browse", command=browse_directory).grid(row=1, column=2, padx=5)

# Update Interval Dropdown
ttk.Label(frame, text="Update Frequency").grid(row=2, column=0, sticky="w")
interval_menu = ttk.Combobox(frame, textvariable=interval_var, values=["10 minutes", "1 hour", "12 hours", "24 hours"], state="readonly")
interval_menu.grid(row=2, column=1, pady=5)
interval_menu.set("1 hour")

# Pin count dropdown
ttk.Label(frame, text="Approximate Pin Count").grid(row=3, column=0, sticky="w")
pin_count_menu = ttk.Combobox(frame, textvariable=pin_count_var, values=["<20", "<40", "<60", "<100", "<200"], state="readonly")
pin_count_menu.grid(row=3, column=1, pady=5)
pin_count_menu.set("<100")

# Buttons
save_btn = ttk.Button(frame, text="Save Config", command=save_config)
save_btn.grid(row=4, column=0, columnspan=2, pady=10)

start_btn = ttk.Button(frame, text="Start Updating Now", bootstyle="success", command=schedule_wallpaper_updates)
start_btn.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
