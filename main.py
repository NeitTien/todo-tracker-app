import tkinter as tk
import calendar
import datetime
from pathlib import Path
#import holidays #Potentially can be used to insert holidays to the calendar
import settings
import dashboard_view
import calendar_view
import sidebar_view

class App(tk.Tk):
    def __init__(self):
        #This INIT a WINDOW object for Tkinter Function
        super().__init__()
        self.title("Limiter")
        self.geometry("1600x900")

        #Icon for the application
        self.BASE_DIR = Path(__file__).resolve().parent #relative Path to the main.py file
        self.icon_path = self.BASE_DIR / "assets" / "icon.png" #location of icon
        self.icon = tk.PhotoImage(file=self.icon_path) #icon object
        self.iconphoto(True, self.icon) #True mean use the icon as default for this

        #Execute these function
        self.create_frames()
        self.some_logic()
        self.app_scaling()
    
    def create_frames(self):
        #Main Frame with the App as Parent
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(
            row=0,
            column=1,
            pady=30,
            sticky="nsew"
        )

        #Calendar View object
        self.calendar = calendar_view.CalendarView(self.main_frame)

        #Dashboard View object
        self.dashboard = dashboard_view.DashboardView(self.main_frame)

        #Settings Option object
        self.settings = settings.Settings(self)

        #Sidebar View object
        self.sidebar = sidebar_view.SidebarView(self, self.calendar, self.dashboard, self.settings)

    def some_logic(self):
        if self.settings.get_default_view() == "calendar":
            self.sidebar.switch_calendar_view()
        else:
            self.sidebar.switch_dashboard_view()
    def app_scaling(self):
        #Window Grid behavior
        self.grid_columnconfigure(0, weight=0) #Sidebar Frame
        self.grid_columnconfigure(1, weight=1) #Main Frame
        self.grid_rowconfigure(0, weight=1)

        #Main Frame Grid behavior
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)



    
#To-do List View with Main Frame as Parent (currently unused)
#todolist_view = tk.Frame(main_frame)


place_holder_value=1

#This make the app stay opened and not instantly close after opening
app = App()
app.mainloop()