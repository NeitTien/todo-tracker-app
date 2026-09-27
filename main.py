import tkinter as tk
import calendar
import datetime
#import holidays #Potentially can be used to insert holidays to the calendar
import settings
import dashboard_view
import calendar_view
import sidebar_view
from pathlib import Path

#This INIT a WINDOW object for Tkinter Function
window = tk.Tk()
window.title("Limiter")
window.geometry("1600x900")

#Icon for the application
BASE_DIR = Path(__file__).resolve().parent #relative Path to the main.py file
icon_path = BASE_DIR / "assets" / "icon.png" #location of icon
icon = tk.PhotoImage(file=icon_path) #icon object
window.iconphoto(True, icon) #True mean use the icon as default for this app

#Main Frame with Window as Parent
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=1, pady= 30, sticky="nsew")

#Calendar View
calendar = calendar_view.CalendarView(main_frame)

#Dashboard View
dashboard = dashboard_view.DashboardView(main_frame)

#Settings Option
settings = settings.Settings(window)

#Sidebar View
sidebar = sidebar_view.SidebarView(window, calendar, dashboard, settings)

#To-do List View with Main Frame as Parent (currently unused)
#todolist_view = tk.Frame(main_frame)

#Window Grid behavior
window.grid_columnconfigure(0, weight=0) #Sidebar Frame
window.grid_columnconfigure(1, weight=1) #Main Frame
window.grid_rowconfigure(0, weight=1)

#Main Frame Grid behavior
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(0, weight=1)

place_holder_value=1

#This make the app stay opened and not instantly close after opening
window.mainloop()