import tkinter as tk
import datetime
import calendar

#Classes in file created
import settings
import calendar_view
import dashboard_view

class SidebarView:
    def __init__(self, parent, calendar, dashboard, settings):
        self.parent = parent
        self.calendar = calendar
        self.dashboard = dashboard
        self.settings = settings

        #Execute those functions
        self.create_widgets()
        self.create_button()

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
        self.button_calendar = tk.Button(
            self.sidebar_view,
            text="Calendar View",
            font=("Arial", 12),
            command=self.switch_calendar_view
        )
        self.button_calendar.grid(row=0, column=0)

        self.button_dashboard = tk.Button(
            self.sidebar_view,
            text="Dashboard View",
            font=("Arial", 12),
            command=self.switch_dashboard_view
        )
        self.button_dashboard.grid(row=1, column=0, pady=(30, 30))

        self.button_settings = tk.Button(
            self.sidebar_view,
            text="Settings",
            font=("Arial", 12),
            command=lambda: self.settings.open_settings()
        )
        self.button_settings.grid(row=2, column=0, pady=(0, 30))

    def switch_calendar_view(self):
        self.calendar.calendar_view.tkraise()

    def switch_dashboard_view(self):
        self.dashboard.dashboard_view.tkraise()

