import json
import tkinter as tk
from pathlib import Path

if Path("def_settings.json").exists():
    SETTINGS_FILE = "def_settings.json"
else:
    SETTINGS_FILE = "settings.json"
    
def load_settings():
    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)

def save_settings():
    with open(SETTINGS_FILE, "w") as file:
        return json.dump(settings, file, indent=4)

def open_settings(parent):
    settings_view = tk.Toplevel(parent)
    settings_view.title("Settings")
    settings_view.geometry("900x600")