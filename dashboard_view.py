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



def create_dashboard(parent):
    dashboard_frame = tk.Frame(
        parent,
        highlightbackground="blue",
        highlightthickness=1
    )

    placeholder_label = tk.Label(
        dashboard_frame,
        text="This is a placeholder label",
        font=("Arial", 12)
    )
    placeholder_label.grid(row=0, column=0)

    return dashboard_frame