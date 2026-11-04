import tkinter as tk
import datetime
import calendar
from assignment_picker import difficulty_color

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
    def __init__(self, parent, assignment_manager):
        #This function run when creating a DashboardView object
        self.parent = parent #Parent is main_frame
        self.assignment_manager = assignment_manager

        #Execute those functions
        self.create_widgets()
        self.create_basic_label()
        self.create_scrollbar_area()
        self.populate_dashboard()

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

        self.dashboard_view.grid_rowconfigure(1, weight=1)
        self.dashboard_view.grid_columnconfigure(0, weight=1)

    def create_basic_label(self):
        self.title_label = tk.Label(
            self.dashboard_view,
            text="Dashboard",
            font=("Arial", 12),
            anchor="w"
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=10
        )

    def create_scrollbar_area(self):
        #Canvas frame for the scrollbar
        self.canvas = tk.Canvas(
            self.dashboard_view,
            highlightbackground="black", #Debug purpose
            highlightthickness=1
        )

        #Scrollbar for Canvas
        self.scrollbar = tk.Scrollbar(
            self.dashboard_view,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        #Position of Canvas and scrollbar
        self.canvas.grid(
            row=1,
            column=0,
            sticky="nsew"
        )
        self.scrollbar.grid(
            row=1,
            column=1,
            sticky="ns"
        )

        #Frame for date and assignment
        self.content_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.content_frame,
            anchor="nw"
        )

        #Update the scrollable region when content changes
        self.content_frame.bind(
            "<Configure>",
            self.update_scroll_region
        )

        #Scale the content frame to the canvas width, 
        # similar to Canvas dashboard
        self.canvas.bind(
            "<Configure>",
            self.resize_content_frame
        )

    def update_scroll_region(self, event=None):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def resize_content_frame(self, event):
        self.canvas.itemconfigure(
            self.canvas_window,
            width=event.width
        )

    def populate_dashboard(self):
        today = datetime.date.today()


        for day_offset in range(30):
            due_date = today + datetime.timedelta(days=day_offset)

            assignments = self.assignment_manager.get_assignments(due_date)

            if assignments:
                    self.create_date_group(due_date, assignments)

        """
        assignments_by_date = {
            today: [
                "Database Homework",
                "Chapter Review"
            ],
            today + datetime.timedelta(days=1): [
                "SQL Practice Problems"
            ],
            today + datetime.timedelta(days=3): [
                "Project Milestone"
            ]
        }
        """

        #for due_date, assignments in assignments_by_date.items():
        #self.create_date_group(due_date, assignments)

        
    
    def create_date_group(self, due_date, assignments):
        date_frame = tk.Frame(self.content_frame)

        date_frame.pack(
            fill="x",
            padx=15,
            pady=(10, 5)
        )

        #Date header
        date_label = tk.Label(
            date_frame,
            text=due_date.strftime("%A, %B, %d"),
            font=("Arial", 12),
            anchor="w"
        )  
        date_label.pack(fill="x", pady=(0, 5))

        #Assignment list
        for assignment in assignments:
            assignment_frame = tk.Frame(
                date_frame,
                bd=1,
                relief="solid",
                padx=10,
                pady=10
            )
            assignment_frame.pack(fill="x", pady=3)

            assignment_label = tk.Label(
                assignment_frame,
                text=assignment["title"],
                font=("Arial", 11),
                anchor="w"
            )
            assignment_label.pack(fill="x")

            #** DIFFICULTY: color the title green / yellow / red (white card keeps it readable);
            #no difficulty keeps the normal look
            color = difficulty_color(assignment.get("difficulty", ""))
            if color:
                assignment_frame.config(background="#FFFFFF")
                assignment_label.config(background="#FFFFFF", foreground=color)
    def refresh_dashboard(self):
        #Remove old date groups
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        #Rebuild
        self.populate_dashboard()
