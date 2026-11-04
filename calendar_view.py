import tkinter as tk
import datetime
import calendar
import tkinter.font as tkfont

from assignment_picker import AssignmentManager, DIFFICULTY_CHOICES, difficulty_color
#CALENDAR GUI
#This is enum for Months and Days
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

days = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]


#The most lines of text a date's box shows (assignment names, or "+N more").
#Boxes that are too short for this many lines show fewer (see lines_per_cell)
MAX_LINES = 5

class CalendarView:
    def __init__(self, parent):
        #This function run when creating a CalendarView object
        self.parent = parent #Parent is main_frame

        #Get the current year, month, day, and days of a month
        self.today = datetime.date.today() #This will print today date in YYYY-MM-DD format
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.current_day = self.today.day
        
        #Create an assignment object from assignment_picker.py
        #when there is change it will trigger the update_calendar_day function
        #which will make the CalendarView class redraw the UI
        self.assignment_manager = AssignmentManager(parent, on_change=self.update_calendar_day)

        #This will return a list of lists, each list is a week of a month
        self.current_day_of_month = calendar.Calendar().monthdatescalendar(
            self.current_year, self.current_month)

        #Create the frame
        self.frame = tk.Frame(parent)

        #Execute those functions
        self.create_widgets() #Frame
        self.create_basic_label()
        self.create_weekday_label() #Monday -> Sunday
        self.create_details_panel()
        self.create_calendardays_label()
        self.create_button() #Next month, previous month button
    
    def create_widgets(self):
        #Expand the Parent Frame
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        #Calendar View
        self.calendar_view = tk.Frame(
            self.parent,
            highlightbackground="red",
            highlightthickness=1
        )
        self.calendar_view.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        #Calendar scaling configuration
        #This is needed so that header and grid can expand
        self.calendar_view.grid_columnconfigure(0, weight=1)
        self.calendar_view.grid_rowconfigure(0, weight=0) #Calendar Header
        self.calendar_view.grid_rowconfigure(1, weight=5) #Calendar Grid
        self.calendar_view.grid_rowconfigure(2, weight=1) #Details panel


        #Calendar Header
        self.calendar_header = tk.Frame(
            self.calendar_view,
            highlightbackground="yellow",
            highlightthickness=1
        )
        self.calendar_header.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        #Header scaling configuration
        self.calendar_header.grid_columnconfigure(0, weight=1)
        self.calendar_header.grid_rowconfigure(0, weight=1)

        #Calendar Grid
        self.calendar_grid = tk.Frame(
            self.calendar_view,
            highlightbackground="black",
            highlightthickness=1
        )
        self.calendar_grid.grid(
            row=1,
            column=0,
            sticky="nsew"
        )
        #Redraw the dates when the window is resized, so the right number of assignments fit in each box
        self.calendar_grid.bind("<Configure>", self.on_grid_resize)
        #No Grid scaling because we do that when we generate the days of month

    #Create label that display current month, year
    def create_basic_label(self):
        #Month Label
        self.month_label = tk.Label(
            self.calendar_header,
            text=months[self.current_month - 1],
            font=("Arial", 12)
        )
        self.month_label.grid(
            row=0,
            column=3
        )

        #Year Label
        self.year_label = tk.Label(
            self.calendar_header,
            text=self.current_year,
            font=("Arial", 12)
        )
        self.year_label.grid(
            row=0,
            column=4
        )

    #Generate label with Weekday name
    def create_weekday_label(self):
        #Monday -> Sunday Label
        for column in range(7): #A week has 7 days max
            self.calendar_header.grid_columnconfigure(column, weight=1, uniform="col")

            weekday_label = tk.Label(
                self.calendar_header,
                text=days[column],
                font=("Arial", 12),
                anchor="center"
            )
            weekday_label.grid(
                row=1,
                column=column,
                sticky="nsew",
                padx=2,
                pady=30
            )

    #Shows the selected date and its assignment list below the grid
    #Built here in CalendarView
    #passed to AssignmentManager so it knows where to write updates
    def create_details_panel(self):
        details_frame = tk.Frame(
            self.calendar_view,
            highlightbackground="green",
            highlightthickness=1
        )
        details_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
        )
        details_frame.columnconfigure(0, weight=1)

        selected_date_label = tk.Label(
            details_frame,
            font=("Arial", 12),
            anchor="w"
        )
        selected_date_label.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        #exportselection=False keeps the selected assignment highlighted while typing in the text box
        #White background / black text (like the date boxes) so the difficulty colors stay readable
        assignment_list = tk.Listbox(
            details_frame, height=4, font=("Arial", 12), exportselection=False,
            background="#FFFFFF", foreground="#000000", selectbackground="#F2F7FF", selectforeground="#000000"
        )
        assignment_list.grid(row=1, column=0, sticky="ew", pady=5)

        scrollbar = tk.Scrollbar(details_frame, command=assignment_list.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        assignment_list.config(yscrollcommand=scrollbar.set)
        
        tk.Label(
            details_frame,
            textvariable=self.assignment_manager.status,
            anchor="sw",
            wraplength=1000
        ).grid(row=4, column=0, sticky="ew", pady=6)

        #** DIFFICULTY: pick None / Easy / Medium / Hard before pressing Add (None = normal text color)
        difficulty_var = tk.StringVar(master=details_frame, value="")
        difficulty_frame = tk.Frame(details_frame)
        difficulty_frame.grid(row=3, column=0, sticky="w", pady=(0, 5))
        tk.Label(difficulty_frame, text="Difficulty:", font=("Arial", 12)).grid(row=0, column=0, padx=(0, 8))
        for column, (label, value) in enumerate(DIFFICULTY_CHOICES, start=1):
            tk.Radiobutton(
                difficulty_frame,
                text=label,
                value=value,
                variable=difficulty_var,
                font=("Arial", 12)
            ).grid(row=0, column=column, padx=4)

        #Text box under the list: type an assignment for the selected date,
        #then press Enter or click Add
        assignment_entry = tk.Entry(details_frame, font=("Arial", 12))
        assignment_entry.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        assignment_entry.bind("<Return>", lambda event: self.submit_assignment(assignment_entry))

        #Buttons next to the text box:
        #Add (becomes Save while editing), plus Edit / Remove for the assignment selected in the list
        #(double-click an assignment to edit it, Delete key removes it, Escape cancels an edit)
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=2, column=1, padx=(5, 0), pady=(0, 5))

        add_button = tk.Button(
            button_frame,
            text="Add",
            font=("Arial", 12),
            command=lambda: self.submit_assignment(assignment_entry)
        )
        add_button.grid(row=0, column=0)

        tk.Button(
            button_frame,
            text="Edit",
            font=("Arial", 12),
            command=self.assignment_manager.start_edit
        ).grid(row=0, column=1, padx=(5, 0))

        tk.Button(
            button_frame,
            text="Remove",
            font=("Arial", 12),
            command=self.assignment_manager.remove_selected
        ).grid(row=0, column=2, padx=(5, 0))

        assignment_list.bind("<Double-Button-1>", lambda event: self.assignment_manager.start_edit())
        assignment_list.bind("<Delete>", lambda event: self.assignment_manager.remove_selected())
        assignment_list.bind("<BackSpace>", lambda event: self.assignment_manager.remove_selected())
        assignment_entry.bind("<Escape>", lambda event: self.assignment_manager.cancel_edit())

        self.assignment_manager.attach_details_widgets(selected_date_label, assignment_list, assignment_entry, add_button, difficulty_var)

    #This adds the typed text as an assignment, then clears the text box if it worked
    def submit_assignment(self, entry):
        if self.assignment_manager.add_from_text(entry.get()):
            entry.delete(0, tk.END)

    #This will generate Calendar Days (Days of a month) when program first run
    def create_calendardays_label(self):
        self.build_calendar_grid()

    #Create Next month, Prev month button
    def create_button(self):
        #Next Month Button
        self.button_next_month = tk.Button(
            self.calendar_header,
            text="Next Month",
            font=("Arial", 12),
            command=self.next_month
        )
        self.button_next_month.grid(
            row=0,
            column=6
        )

        #Previous Month Button
        self.button_prev_month = tk.Button(
            self.calendar_header,
            text="Previous Month",
            font=("Arial", 12),
            command=self.prev_month
        )
        self.button_prev_month.grid(
            row=0,
            column=0
        )

    #This function handle month change logic of next_month and prev_month button
    def change_month(self, offset):
        self.current_month += offset

        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        #Update the label to dispay correctly
        self.update_year_label()
        self.update_month_label()
        self.update_calendar_day()

        print(self.current_month) #Debug

    #For Next Month button
    def next_month(self):
        self.change_month(1)

    #For Previous Month button
    def prev_month(self):
        self.change_month(-1)

    #For Year Label
    def update_year_label(self):
        #This function change the label by edit the text config
        self.year_label.config(text=self.current_year)

    #For Month Label
    def update_month_label(self):
        #This function change the label by edit the text config
        self.month_label.config(text=months[self.current_month - 1])

    #Redraws the dates once the window stops being resized (only when the grid's size really changed)
    def on_grid_resize(self, event):
        size = (event.width, event.height)
        if size == getattr(self, "last_grid_size", None):
            return
        self.last_grid_size = size
        job = getattr(self, "resize_job", None)
        if job:
            self.calendar_grid.after_cancel(job)
        self.resize_job = self.calendar_grid.after(150, self.update_calendar_day)

    #How many lines of text fit in one date's box (a month with 6 weeks has shorter boxes than one with 5)
    def lines_per_cell(self, week_size):
        height = self.calendar_grid.winfo_height()
        if height < 50: #The window is not drawn yet, so guess from the number of weeks
            return MAX_LINES if week_size <= 5 else MAX_LINES - 1
        line_height = tkfont.Font(font=("Arial", 9)).metrics("linespace")
        usable = height / week_size - 10 #Leave room for the border and padding
        return max(3, min(MAX_LINES, int(usable // line_height)))

    #For Calendar Day (Days of a month)
    def update_calendar_day(self):
        #This for-loop will destroy the previous grid
        #so that the calendar will not be overlapped
        #the data is not affected by this deletion
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        self.build_calendar_grid()

    def build_calendar_grid(self):
        #Recheck the current day of month
        self.current_day_of_month = calendar.Calendar().monthdatescalendar(
            self.current_year, self.current_month)

        week_size = len(self.current_day_of_month)
        max_lines = self.lines_per_cell(week_size)
        day_of_week = len(self.current_day_of_month[0])

        #Expand column and row of each day
        for row in range(6):
            if row < week_size:
                self.calendar_grid.grid_rowconfigure(row, weight=1, uniform="row", minsize=0)
            else:
                self.calendar_grid.grid_rowconfigure(row, weight=0, uniform="", minsize=0)

        for column in range(day_of_week):
            self.calendar_grid.grid_columnconfigure(column, weight=1, uniform="col")

        for week in range(0, week_size):
            for day in range(0, day_of_week):
                day_obj = self.current_day_of_month[week][day]

                if day_obj.month != self.current_month:
                    background_color = "#696969"
                    text_color = "#CCCCCC"
                else:
                    background_color = "#FFFFFF"
                    text_color = "#000000"

                #checking the state of the day from AssignmentManager
                day_assignments = self.assignment_manager.get_assignments(day_obj)
                #print(day_assignments)
                is_blocked = self.assignment_manager.is_blocked(day_obj)
                is_selected = (day_obj == self.assignment_manager.selected_date)

                if is_blocked:
                    background_color = "#F1BABA"

                #Frame for each day
                day_frame = tk.Frame(
                    self.calendar_grid,
                    background=background_color,
                    highlightbackground="#D0D0D0",
                    #Thicker border for selected day.
                    highlightthickness=3 if is_selected else 1,
                    bd=0
                )
                day_frame.grid(
                    row=week,
                    column=day,
                    sticky="nsew",
                    padx=1,
                    pady=1
                )

                day_frame.grid_columnconfigure(0, weight=1)
                day_frame.grid_rowconfigure(1, weight=1)
                #Prevent the frame from auto shrinking to fits the content inside
                #day_frame.grid_propagate(False) 

                day_label = tk.Label(
                    day_frame,
                    text=str(day_obj.day),
                    font=("Arial", 12),
                    background = background_color,
                    foreground = text_color,
                    anchor="ne"
                )
                day_label.grid(
                    row=0,
                    column=0,
                    sticky="ne",
                    padx=5,
                    pady=5
                )

                #Labels for BLOCKED date / assignments, one label per line so each can have its own color
                #(text_color is the normal color; an assignment with a difficulty gets green / yellow / red)
                #create when there is something
                if is_blocked:
                    surface = "blocked" #Pink background
                elif day_obj.month != self.current_month:
                    surface = "gray" #Other month's background
                else:
                    surface = "light"

                info_lines = [] #Each entry is (text, color)
                if is_blocked:
                    info_lines.append(("BLOCKED", text_color))
                if day_assignments:
                    #Show as many assignment names as fit in the date's box
                    #(if there are more, the last line is "+N more" instead of a name)
                    name_lines = max_lines - (1 if is_blocked else 0) #BLOCKED takes one line
                    shown = day_assignments if len(day_assignments) <= name_lines else day_assignments[:name_lines - 1]
                    for assignment in shown:
                        title = assignment["title"]
                        line_color = difficulty_color(assignment.get("difficulty", ""), surface) or text_color
                        info_lines.append(("- " + (title if len(title) <= 22 else title[:21] + "..."), line_color))
                    if len(shown) < len(day_assignments):
                        info_lines.append((f"+{len(day_assignments) - len(shown)} more", text_color))

                info_widgets = []
                if info_lines:
                    info_frame = tk.Frame(day_frame, background=background_color)
                    #Tasks start at the top of the date's box (the day number sits in the top right corner)
                    info_frame.grid(row=0, column=0, rowspan=2, sticky="nw", padx=5, pady=(4, 2))
                    info_widgets.append(info_frame)
                    for line_text, line_color in info_lines:
                        line_label = tk.Label(
                            info_frame,
                            text=line_text,
                            font=("Arial", 9),
                            background=background_color,
                            foreground=line_color,
                            anchor="w",
                            justify="left",
                            #No extra padding/border, so the lines sit close together
                            borderwidth=0,
                            highlightthickness=0,
                            padx=0,
                            pady=0
                        )
                        line_label.pack(anchor="w")
                        info_widgets.append(line_label)

                #Click + right-click bindings. Bound to the frame AND its
                #labels
                clickable_widgets = [day_frame, day_label] + info_widgets
                for widget in clickable_widgets:
                    widget.bind(
                        "<Button-1>",
                        lambda event, date=day_obj: self.assignment_manager.select_date(date)
                    )
                    widget.bind(
                        self.assignment_manager.context_click,
                        lambda event, date=day_obj: self.assignment_manager.show_menu(event, date)
                    )
                    if self.assignment_manager.is_macos:
                        widget.bind(
                            "<Control-Button-1>",
                            lambda event, date=day_obj: self.assignment_manager.show_menu(event, date)
                        )