import tkinter as tk
import datetime
import calendar

#CALENDAR GUI
#This is enum for Months and Days
months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

class CalendarView:
    def __init__(self, parent):
        #This function run when creating a CalendarView object
        self.parent = parent #Parent is main_frame

        #Get the current year, month, day, and days of a month
        today = datetime.date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.current_day = today.day
        self.current_day_of_month = calendar.Calendar().monthdatescalendar(
            self.current_year, self.current_month)

        #Create the frame
        self.frame = tk.Frame(parent)

        #Execute those functions
        self.create_widgets()
        self.create_label()
        self.create_button()

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
        self.calendar_view.grid_rowconfigure(0, weight=0) #Fixed for Header
        self.calendar_view.grid_rowconfigure(1, weight=1) #Grid

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

        #Grid scaling configuration
        for column in range(7):
            self.calendar_grid.grid_columnconfigure(column, weight=1)
        for row in range(6):
            self.calendar_grid.grid_rowconfigure(row, weight=1)

    def create_label(self):
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

        #Monday -> Sunday Label
        for column, day in enumerate(days):
            label = tk.Label(
                self.calendar_header,
                text=day,
                #width=11,
                font=("Arial", 12)
            )
            label.grid(
                row=1,
                column=column,
                padx=2,
                pady=30
            )

        #Days of a month Label
        week_size = len(self.current_day_of_month)
        day_of_week = len(self.current_day_of_month[0])
        #For every week in a month
        for week in range(0, week_size):
            #For every day in a week
            for day in range(0, day_of_week):
                day_obj = self.current_day_of_month[week][day]

                #This will make days that is not of current month grayed out
                #696969 is gray color and FFFFFF is white color
                #add foreground if want to change text_color
                if day_obj.month != self.current_month:
                    background_color = "#696969"
                    text_color = "#CCCCCC"
                else:
                    background_color = "#FFFFFF"
                    text_color = "#000000"
                
                #Frame for each day
                day_frame = tk.Frame(
                    self.calendar_grid,
                    background=background_color,
                    highlightbackground="#D0D0D0",
                    highlightthickness=1,
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

    #For Next Month button
    def next_month(self):
        self.current_month += 1

        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1

        #Update the label to dispay correctly
        self.update_year_label()
        self.update_month_label()
        self.update_calendar_day()

        print(self.current_month) #Debug

    #For Previous Month button
    def prev_month(self):
        self.current_month -= 1

        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        #Update the label to dispay correctly
        self.update_year_label()
        self.update_month_label()
        self.update_calendar_day()
        print(self.current_month) #Debug
    
    def update_year_label(self):
        #This function change the label by edit the text config
        self.year_label.config(text=self.current_year)

    def update_month_label(self):
        #This function change the label by edit the text config
        self.month_label.config(text=months[self.current_month - 1])

    def update_calendar_day(self):
        #This for-loop will destroy the previous grid
        #so that the calendar will not be overlapped
        #the data is not affected by this deletion
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        #Recheck the current day of month
        self.current_day_of_month = calendar.Calendar().monthdatescalendar(
            self.current_year, self.current_month)

        week_size = len(self.current_day_of_month)
        day_of_week = len(self.current_day_of_month[0])

        #Expand column and row of each day
        for row in range(week_size):
            self.calendar_grid.grid_rowconfigure(row, weight=1, uniform="row")
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

                #Frame for each day
                day_frame = tk.Frame(
                    self.calendar_grid,
                    background=background_color,
                    highlightbackground="#D0D0D0",
                    highlightthickness=1,
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
                
    

