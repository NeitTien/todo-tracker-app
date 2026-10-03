import tkinter as tk
import datetime
import calendar

#DASHBOARD GUI
#This is enum for Months and Days
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

days = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]

class DashboardView:
    def __init__(self, parent):
        #This function run when creating a DashboardView object
        self.parent = parent #Parent is main_frame

        #Execute those functions
        self.create_widgets()
        self.create_basic_label()

    def create_widgets(self):
        self.dashboard_view = tk.Frame(
            self.parent,
            highlightbackground="blue",
            highlightthickness=1
        )
        self.dashboard_view.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        
    def create_basic_label(self):
        #Placeholder label
        self.placeholder_label = tk.Label(
            self.dashboard_view,
            text="This is a placeholder label",
            font=("Arial", 12)
        )
        self.placeholder_label.grid(row=0, column=0)