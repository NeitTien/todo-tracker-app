import tkinter as tk
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

        #Storage is separate from the original views.
        self.storage = AppStorage(self.BASE_DIR)
        self.storage_ready = False
        self.autosave_job = None

        #Execute these function
        self.create_frames()
        #Keep the existing close handler, including any blocker cleanup.
        self.original_close_command = self.protocol("WM_DELETE_WINDOW")
        try:
            self.storage.load_data(self)
        except (OSError, ValueError, TypeError) as error:
            messagebox.showerror(
                "Could not load progress",
                f"{error}\n\nSave file: {self.storage.data_file}\n"
                "The existing save has not been overwritten.",
                parent=self,
            )
            self.finish_close()
            raise SystemExit(1)
        self.storage_ready = True
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.some_logic()
        self.app_scaling()
        self.autosave_job = self.after(1000, self.autosave_progress)
    
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
        self.dashboard = dashboard_view.DashboardView(self.main_frame, self.calendar.assignment_manager)

        #Settings Option object
        self.settings = settings.Settings(self)

        #** BLOCKER FEATURE: Blocker object (blocks sites/apps)
        self.blocker = blocker.Blocker(self)

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
        print("Refreshing both views")
        self.calendar.update_calendar_day()
        self.dashboard.refresh_dashboard()
        self.save_progress()

    def save_progress(self, show_error=True):
        if not self.storage_ready:
            return False
        try:
            self.storage.save_data(self)
        except (OSError, ValueError, TypeError) as error:
            if show_error:
                messagebox.showerror(
                    "Could not save progress",
                    f"{error}\n\nSave file: {self.storage.data_file}\n"
                    "Keep Limiter open and try again after fixing the problem.",
                    parent=self,
                )
            else:
                self.calendar.assignment_manager.status.set(
                    "Progress could not be saved. Keep Limiter open and check the save folder."
                )
            return False
        return True

    def autosave_progress(self):
        #Also captures month navigation and compatible blocker-list changes.
        #AppStorage skips disk writes when the data has not changed.
        self.autosave_job = None
        self.save_progress(show_error=False)
        self.autosave_job = self.after(1000, self.autosave_progress)

    def close_app(self):
        if self.save_progress():
            self.finish_close()

    def finish_close(self):
        if self.autosave_job is not None:
            self.after_cancel(self.autosave_job)
            self.autosave_job = None
        if self.original_close_command:
            #Run the original Tk close callback, preserving blocker cleanup.
            self.tk.call("eval", self.original_close_command)
        else:
            self.destroy()




    
#To-do List View with Main Frame as Parent (currently unused)
#todolist_view = tk.Frame(main_frame)


place_holder_value=1

#This make the app stay opened and not instantly close after opening
if __name__ == "__main__":
    app = App()
    app.mainloop()