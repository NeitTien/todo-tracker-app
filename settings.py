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
        self.settings_view = tk.Toplevel(self.parent)
        self.settings_view.title("Settings")
        self.settings_view.geometry("900x600")

        #Create the settings section
        self.frame_default()

        #Save button
        self.save_button = tk.Button(
            self.settings_view,
            text="Save",
            command=self.save_user_settings
        )
        self.save_button.grid(row=1, column=0, pady=20)

    def load_settings(self):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)

    def save_settings(self, settings):
        with open(SETTINGS_FILE, "w") as file:
            return json.dump(settings, file, indent=4)

    def get_default_view(self):
        #Read default_view value directly from the json
        return self.load_settings().get("default_view", "calendar")

    def frame_default(self):
        self.default_frame = tk.Frame(self.settings_view)
        self.default_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        #Load the current settings
        settings = self.load_settings()

        #Storing the default_view in the file to default_view obj.
        #If no value exist then default_view = "calendar" 
        self.default_view = tk.StringVar(
            value=self.load_settings().get("default_view", "calendar")
        )

        default_label = tk.Label(
            self.default_frame,
            text="Default View"
        )
        default_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        calendar_default = tk.Radiobutton(
            self.default_frame,
            text="Calendar",
            variable=self.default_view,
            value="calendar"
        )
        calendar_default.grid(row=1, column=0, sticky="w")

        dashboard_default = tk.Radiobutton(
            self.default_frame,
            text="Dashboard",
            variable=self.default_view,
            value="dashboard"
        )
        dashboard_default.grid(row=2, column=0, sticky="w")
    
    def save_user_settings(self):
        settings = self.load_settings()

        #Update the default view setting
        settings["default_view"] = self.default_view.get()

        #Write the setting to JSON file
        self.save_settings(settings)

        #Close the settings window
        self.settings_view.destroy()