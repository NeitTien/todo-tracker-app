import json
import tkinter as tk
from pathlib import Path

#This is for debug because I use the file
#def_settings.json to test and it wont be push to github
#settings.json is the file intended for user
if Path("def_settings.json").exists():
    SETTINGS_FILE = "def_settings.json"
else:
    SETTINGS_FILE = "settings.json"

class Settings:
    def __init__(self, parent):
        self.parent = parent

    def open_settings(self):
        settings_view = tk.Toplevel(self.parent)
        settings_view.title("Settings")
        settings_view.geometry("900x600")

    def load_settings(self):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as file:
            return json.dump(settings, file, indent=4)





