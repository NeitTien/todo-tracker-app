import tkinter as tk
import datetime
import calendar

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
        self.parent = parent

        today = datetime.date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.current_day = today.day
        self.current_day_of_month = calendar.Calendar().monthdatescalendar(
            self.current_year, self.current_month)

        self.frame = tk.Frame(parent)

        self.create_widgets()

    def create_widgets(self):
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

        #Calendar Header
        self.calendar_header = tk.Frame(self.calendar_view)
        self.calendar_header.grid(
            row=0,
            column=0
        )

        #Calendar Grid
        self.calendar_grid = tk.Frame(self.calendar_view)
        self.calendar_grid.grid(
            row=1,
            column=0
        )

    def create_label(self):
        self.month_label = tk.Label(
            self.calendar_header,
            text=months[self.current_month - 1],
            font=("Arial", 12)
        )
        self.month_label.grid(
            row=0,
            column=3
        )

        self.year_label = tk.Label(
            self.calendar_header,
            text=self.current_year,
            font=("Arial", 12)
        )
        self.year_label.grid(
            row=0,
            column=4
        )

        for column, day in enumerate(days):
            label = tk.Label(
                self.calendar_header,
                text=day,
                width=11,
                font=("Arial", 12)
            )
            label.grid(
                row=1,
                column=column,
                padx=2,
                pady=30
            )

        week_size = len(self.current_day_of_month)
        day_of_week = len(self.current_day_of_month[0])
        for week in range(0, week_size):
            row = week
            for day in range(0, day_of_week):
                column = day

                if self.current_day_of_month[week][day].month != self.current_month:
                    background_color = "#696969"
                else:
                    background_color = "#FFFFFF"
                
                day_label = tk.Label(
                    self.calendar_grid,
                    text=str(self.current_day_of_month[week][day].day),
                    font=("Arial", 12),
                    width=11,
                    height=5,
                    relief="solid",
                    background = background_color
                )

                day_label.grid(
                    row=row,
                    column=column,
                    padx=2,
                    pady=2
                )

    
    def create_button(self):
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
    
    def update_year_label(self):
        self.year_label.config(text=self.current_year)

    def update_month_label(self):
        self.month_label.config(text=months[self.current_month - 1])

    def update_calendar_day(self):
        #This for-loop will destroy the previous grid
        #so that the calendar will not be overlapped
        #the data is not affected by this deletion
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        week_size = len(self.current_day_of_month)
        day_of_week = len(self.current_day_of_month[0])
        for week in range(0, week_size):
            row = week
            for day in range(0, day_of_week):
                column = day
                            
                #This will make days that is not of current month grayed out
                #696969 is gray color and FFFFFF is white color
                #add foreground if want to change text_color
                if self.current_day_of_month[week][day].month != self.current_month:
                    background_color = "#696969"
                else:
                    background_color = "#FFFFFF"

                day_label = tk.Label(
                    self.calendar_grid,
                    text=str(self.current_day_of_month[week][day].day),
                    font=("Arial", 12),
                    width=11,
                    height=5,
                    relief="solid",
                    background = background_color
                )

                day_label.grid(
                    row=row,
                    column=column,
                    padx=2,
                    pady=2
                )

    def next_month(self):
        self.current_month += 1

        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1

        self.current_day_of_month = calendar.Calendar().monthdatescalendar(
            self.current_year, self.current_month)

        self.update_year_label()
        self.update_month_label()
        self.update_calendar_day()
        print(self.current_month) #Debug

    def prev_month(self):
        self.current_month -= 1

        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        self.current_day_of_month = calendar.Calendar().monthdatescalendar(
            self.current_year, self.current_month)

        self.update_year_label()
        self.update_month_label()
        self.update_calendar_day()
        print(self.current_month) #Debug
    

