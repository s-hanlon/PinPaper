import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb

def save_config():
    board_url = board_url_var.get()
    download_dir = download_dir_var.get()
    interval = interval_var.get()
    pin_hint = pin_count_var.get()

    if not board_url or not download_dir:
        messagebox.showwarning("Missing Info", "Please complete all fields.")
        return

    config = {
        "board_url": board_url,
        "download_dir": download_dir,
        "update_interval": interval,
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

root = tb.Window(themename="darkly")
root.title("PinPaper Setup")
root.geometry("400x400")

board_url_var = tk.StringVar()
download_dir_var = tk.StringVar()
interval_var = tk.StringVar()
pin_count_var = tk.StringVar()

# Load config if exists
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        try:
            config = json.load(f)
            board_url_var.set(config.get("board_url", ""))
            download_dir_var.set(config.get("download_dir", ""))
            interval_var.set(config.get("update_interval", ""))
            pin_count_var.set(config.get("pin_count_hint", "<100"))
        except json.JSONDecodeError:
            pass

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

ttkwidgets = [
    ("Pinterest Board URL", board_url_var),
    ("Download Directory", download_dir_var),
    ("Update Interval", interval_var)
]

for i, (label, var) in enumerate(ttkwidgets):
    ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w")
    entry = ttk.Entry(frame, textvariable=var, width=40)
    entry.grid(row=i, column=1, pady=5)
    if label == "Download Directory":
        ttk.Button(frame, text="Browse", command=browse_directory).grid(row=i, column=2, padx=5)

# Pin count dropdown
ttk.Label(frame, text="Approximate Pin Count").grid(row=3, column=0, sticky="w")
pin_count_menu = ttk.Combobox(frame, textvariable=pin_count_var, values=["<20", "<40", "<60", "<100", "<200"], state="readonly")
pin_count_menu.grid(row=3, column=1, pady=5)
pin_count_menu.current(3)  # Default to <100

save_btn = ttk.Button(frame, text="Save Config", command=save_config)
save_btn.grid(row=4, column=0, columnspan=2, pady=20)

root.mainloop()
