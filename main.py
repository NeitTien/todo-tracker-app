import tkinter as tk
# ADDED: storage is separate from the existing views.
from tkinter import messagebox
from app_storage import AppStorage
import calendar
import datetime
from pathlib import Path
#import holidays #Potentially can be used to insert holidays to the calendar
import settings
import dashboard_view
import calendar_view
import sidebar_view
import blocker #** BLOCKER FEATURE

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

        # ADDED: Settings can use the same storage object as the calendar.
        self.storage = AppStorage(self.BASE_DIR)
        self.storage_ready = False

        #Execute these function
        self.create_frames()
        # ADDED: restore data before selecting the default view.
        try:
            self.storage.load_data(self)
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Could not load progress",
                f"Could not load {self.storage.data_file}.\n\n{error}\n\n"
                "The saved file has not been overwritten. The app will close.",
                parent=self
            )
            self.blocker.on_close()
            raise SystemExit(1)
        self.storage_ready = True
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.some_logic()
        self.app_scaling()
    
    # ADDED: save without closing if there is a storage error.
    def save_progress(self):
        if not self.storage_ready:
            return False
        try:
            self.storage.save_data(self)
        except (OSError, ValueError, TypeError) as error:
            messagebox.showerror(
                "Could not save progress",
                f"Could not save to {self.storage.data_file}.\n\n{error}\n\n"
                "Your changes are still open. Try again before closing.",
                parent=self
            )
            return False
        return True

    def close_app(self):
        if self.save_progress():
            # Preserve the existing blocker cleanup before destroying the window.
            self.blocker.on_close()

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

        #** BLOCKER FEATURE: Blocker object (blocks sites/apps)
        self.blocker = blocker.Blocker(self, on_change=self.save_progress)

        #Sidebar View object
        self.sidebar = sidebar_view.SidebarView(self, self.calendar, self.dashboard, self.settings, self.blocker) 
        #** blocker passed in

        #Refresh on_change
        self.calendar.assignment_manager.on_change = self.refresh_views

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
    def refresh_views(self):
        print("Refreshing calendar")
        self.calendar.update_calendar_day()
        self.save_progress() #ADDED: dashboard is a placeholder; save the shared calendar data.




    
#To-do List View with Main Frame as Parent (currently unused)
#todolist_view = tk.Frame(main_frame)


place_holder_value=1

#This make the app stay opened and not instantly close after opening
if __name__ == "__main__":
    app = App()
    app.mainloop()