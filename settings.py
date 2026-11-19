import json
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from assignment_picker import REMINDER_UNITS, DEFAULT_REMINDER_MINUTES, MAX_REMINDER_AMOUNT

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
        self.storage = getattr(parent, "storage", None)
        

    def open_settings(self):
        #Create the setting window
        self.settings_view = tk.Toplevel(self.parent)
        self.settings_view.title("Settings")
        self.settings_view.geometry("900x600")

        #Expand the frame
        self.settings_view.columnconfigure(0, weight=1)
        self.settings_view.rowconfigure(0, weight=1)

        #Create the settings section
        self.frame_default()

        #Save button
        self.save_button = tk.Button(
            self.settings_view,
            text="Save",
            command=self.save_user_settings
        )
        self.save_button.grid(row=1, column=0, pady=20, sticky="s")

    def load_settings(self):
        if self.storage is not None:
            return self.storage.load_settings()
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)

    def save_settings(self, settings):
        if self.storage is not None:
            return self.storage.save_settings(settings)
        with open(SETTINGS_FILE, "w") as file:
            return json.dump(settings, file, indent=4)

    def get_default_view(self):
        #Read default_view value directly from the json
        return self.load_settings().get("default_view", "calendar")

    def get_task_sort(self):
        #How tasks are ordered in each date: "difficulty" (default) or "time"
        value = self.load_settings().get("task_sort", "difficulty")
        return value if value in ("difficulty", "time") else "difficulty"

    #Default reminder for new tasks, in minutes before they are due (None = no reminder)
    def get_default_reminder(self):
        settings = self.load_settings()
        if not settings.get("reminder_enabled", True):
            return None
        unit = settings.get("reminder_unit", "hours")
        amount = settings.get("reminder_amount", 1)
        if unit not in REMINDER_UNITS or type(amount) is not int or not (1 <= amount <= MAX_REMINDER_AMOUNT):
            return DEFAULT_REMINDER_MINUTES
        return amount * REMINDER_UNITS[unit]

    #Show a "due today" popup when Limiter opens (on unless turned off)
    def get_daily_summary(self):
        return self.load_settings().get("daily_summary", True) is True

    def frame_default(self):
        self.default_frame = tk.Frame(
            self.settings_view,
            highlightbackground="black",
            highlightthickness=1
        )
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
            sticky="nw"
        )

        calendar_default = tk.Radiobutton(
            self.default_frame,
            text="Calendar",
            variable=self.default_view,
            value="calendar"
        )
        calendar_default.grid(row=1, column=0, sticky="nw")

        dashboard_default = tk.Radiobutton(
            self.default_frame,
            text="Dashboard",
            variable=self.default_view,
            value="dashboard"
        )
        dashboard_default.grid(row=2, column=0, sticky="nw")

        #** SORT SETTING: how the tasks in a date are ordered
        self.task_sort = tk.StringVar(value=self.get_task_sort())

        sort_label = tk.Label(
            self.default_frame,
            text="Sort Tasks By"
        )
        sort_label.grid(row=3, column=0, sticky="nw", pady=(20, 0))

        sort_difficulty = tk.Radiobutton(
            self.default_frame,
            text="Difficulty (Hard first, then Medium, Easy, none)",
            variable=self.task_sort,
            value="difficulty"
        )
        sort_difficulty.grid(row=4, column=0, sticky="nw")

        sort_time = tk.Radiobutton(
            self.default_frame,
            text="Time due (earliest first)",
            variable=self.task_sort,
            value="time"
        )
        sort_time.grid(row=5, column=0, sticky="nw")

        #** REMINDERS: the reminder every new task starts with (it can still be changed per task)
        saved = self.load_settings()
        self.reminder_enabled = tk.BooleanVar(value=saved.get("reminder_enabled", True))
        self.reminder_amount = tk.StringVar(value=str(saved.get("reminder_amount", 1)))
        self.reminder_unit = tk.StringVar(value=saved.get("reminder_unit", "hours"))

        reminder_label = tk.Label(
            self.default_frame,
            text="Default Reminder For New Tasks"
        )
        reminder_label.grid(row=6, column=0, sticky="nw", pady=(20, 0))

        reminder_row = tk.Frame(self.default_frame)
        reminder_row.grid(row=7, column=0, sticky="nw")
        tk.Checkbutton(
            reminder_row, text="Remind me", variable=self.reminder_enabled
        ).grid(row=0, column=0)
        tk.Spinbox(
            reminder_row, from_=1, to=MAX_REMINDER_AMOUNT, width=4, wrap=True,
            textvariable=self.reminder_amount, justify="center"
        ).grid(row=0, column=1)
        tk.OptionMenu(reminder_row, self.reminder_unit, *REMINDER_UNITS).grid(row=0, column=2, padx=4)
        tk.Label(reminder_row, text="before the task is due").grid(row=0, column=3)

        #** DUE TODAY: popup listing today's tasks when Limiter opens
        self.daily_summary = tk.BooleanVar(value=saved.get("daily_summary", True) is True)
        tk.Label(
            self.default_frame,
            text="When Limiter Opens"
        ).grid(row=8, column=0, sticky="nw", pady=(20, 0))
        tk.Checkbutton(
            self.default_frame,
            text="Show a popup of the tasks due today",
            variable=self.daily_summary
        ).grid(row=9, column=0, sticky="nw")
    
    def save_user_settings(self):
        settings = self.load_settings()

        #Update the default view setting
        settings["default_view"] = self.default_view.get()
        settings["task_sort"] = self.task_sort.get()

        #Update the default reminder (checked first so a bad number is not saved)
        try:
            amount = int(self.reminder_amount.get())
            if not (1 <= amount <= MAX_REMINDER_AMOUNT):
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid reminder",
                f"Enter a whole number from 1 to {MAX_REMINDER_AMOUNT} for the reminder.",
                parent=self.settings_view,
            )
            return
        settings["daily_summary"] = bool(self.daily_summary.get())
        settings["reminder_enabled"] = bool(self.reminder_enabled.get())
        settings["reminder_amount"] = amount
        settings["reminder_unit"] = self.reminder_unit.get()

        #Write the setting to JSON file
        try:
            self.save_settings(settings)
        except (OSError, ValueError, TypeError) as error:
            messagebox.showerror("Could not save settings", str(error), parent=self.settings_view)
            return

        #Apply the sort choice to the tasks right away (the calendar and dashboard refresh and save)
        calendar = getattr(self.parent, "calendar", None)
        if calendar is not None:
            calendar.assignment_manager.set_default_reminder(self.get_default_reminder())
            calendar.assignment_manager.set_sort_mode(self.task_sort.get())

        #Close the settings window
        self.settings_view.destroy()