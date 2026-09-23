import tkinter as tk
import calendar
import datetime
import holidays
import settings
import dashboard_view
import calendar_view
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

#CALENDAR GUI
#Grid of children frame are relative to parent frame
#Meaning they are inside main_frame

#Sidebar Frame with Window as Parent
sidebar = tk.Frame(
    window,
    highlightbackground="purple",
    highlightthickness=1
)
sidebar.grid(row=0, column=0, padx=(0, 50), pady=30, sticky="nsew")

#Main Frame with Window as Parent
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=1, pady= 30, sticky="nsew")

#Calendar View
calendar = calendar_view.CalendarView(main_frame)

#Dashboard View with Main Frame as Parent
dashboard_view = dashboard_view.create_dashboard(main_frame)
dashboard_view.grid(row=0, column=0, sticky="nsew")

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
#FUNCTION SECTION

#SIDEBAR FUNCTION
def switch_calendar_view():
    calendar.calendar_view.tkraise()

def switch_dashboard_view():
    dashboard_view.tkraise()

#DASHBOARD_VIEW FUNCTION

#LABEL, BUTTON SECTION
#SIDEBAR
button_calendar_view = tk.Button(
    sidebar,
    text="Calendar View",
    font=("Arial", 12),
    command=switch_calendar_view
)
button_calendar_view.grid(row=0, column=0)

button_dashboard_view = tk.Button(
    sidebar,
    text="Dashboard View",
    font=("Arial", 12),
    command=switch_dashboard_view
)
button_dashboard_view.grid(row=1, column=0, pady=(30,30))

button_settings = tk.Button(
    sidebar,
    text="Settings",
    font=("Arial", 12),
    command=lambda: settings.open_settings(window)
)
button_settings.grid(row=2, column=0, pady= (0,30))

#This make the app stay opened and not instantly close after opening
window.mainloop()