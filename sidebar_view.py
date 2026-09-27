import tkinter as tk
import datetime
import calendar
import settings

class SidebarView:
    def __init__(self, parent):
        self.parent = parent

    def create_widgets(self):
        #Doesnt need to expand frame because parent is window
        self.sidebar_view = tk.Frame(
            self.parent,
            highlightbackground="purple",
            highlightthickness=1
        )
        self.sidebar_view.grid(
            row=0,
            column=0,
            padx=(0, 50),
            pady=30,
            sticky="nsew"
        )
    def create_button(self):
        self.button_calendar_view = tk.Button(
            self.sidebar_view,
            text="Calendar View",
            font=("Arial", 12),
            command=
        )
        self.button_calendar_view.grid(row=0, column=0)

        self.button_dashboard_view = tk.Button(
            self.sidebar_view,
            text="Dashboard View",
            font=("Arial", 12),
            command=
        )
        self.button_dashboard_view.grid(row=1, column=0, pady=(30, 30))

        self.button_settings = tk.Button(
            self.sidebar_view,
            text="Settings",
            font=("Arial", 12)
            command=lambda:
        )