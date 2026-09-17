import tkinter as tk
import calendar
import datetime

#This create a window object to use Tkinter function
window = tk.Tk()
#This create title
window.title("Limiter")
#This create the resolution of the window
window.geometry("1600x900")

#Get the current year, month, day, and days of a month
today = datetime.date.today()
current_year = today.year
current_month = today.month
current_day = today.day

cal = calendar.Calendar()
current_day_of_month = cal.monthdatescalendar(current_year, current_month)


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

#FUNCTION SECTION
#This update the displayed month when pressed next month button
def update_month_label():
    month_label.config(text=months[current_month - 1])

#This update the displayed year when year change because of next month
def update_year_label():
    year_label.config(text=current_year)

def update_calendar_day():
    #This for-loop will destroy the previous grid
    #so that the calendar will not be overlapped
    #the data is not affected by this deletion
    global current_day_of_month

    for widget in calendar_grid.winfo_children():
        widget.destroy()

    current_day_of_month = cal.monthdatescalendar(current_year, current_month)
    week_size = len(current_day_of_month)
    day_of_week = len(current_day_of_month[0])
    for week in range(0, week_size):
        row = week
        for day in range(0, day_of_week):
            column = day
            day_label = tk.Label(
                calendar_grid,
                text=str(current_day_of_month[week][day].day),
                width=12,
                height=5,
                relief="solid"
            )

            day_label.grid(
                row=row,
                column=column,
                padx=2,
                pady=2
            )


def next_month():
    global current_month
    global current_year
    current_month += 1

    if current_month > 12:
        current_month = 1
        current_year += 1

    update_month_label()
    update_year_label()
    update_calendar_day()
    print(current_month)

def prev_month():
    global current_month
    global current_year
    current_month -= 1

    if current_month < 1:
        current_month = 12
        current_year -= 1
        
    update_month_label()
    update_year_label()
    update_calendar_day()
    print(current_month)

#CALENDAR GUI
#Calendar Frame with Window as Parent
calendar = tk.Frame(window)
calendar.grid(row=0, column=0, padx=500, pady=(100,0))

month_label = tk.Label(
    calendar,
    text=months[current_month - 1],
    font=("Arial", 12)
)
month_label.grid(row=0, column=3)

year_label = tk.Label(
    calendar,
    text=current_year,
    font=("Arial", 12)
)
year_label.grid(row=0, column=4)

button_next_month = tk.Button(
    calendar,
    text="Next Month",
    command=next_month
)
button_next_month.grid(row=0, column=6)

button_prev_month = tk.Button(
    calendar,
    text="Previous Month",
    command=prev_month
)
button_prev_month.grid(row=0, column=0)

#This shows Mon -> Sun
for column, day in enumerate(days):
    label = tk.Label(
        calendar,
        text=day,
        font=("Arial", 12)
    )

    label.grid(row=1, column=column, padx=10, pady=30)

#Calendar_grid Frame with Calendar as Parent
calendar_grid = tk.Frame(window)
calendar_grid.grid(row=1, column=0)
week_size = len(current_day_of_month)
day_of_week = len(current_day_of_month[0])
for week in range(0, week_size):
    row = week
    for day in range(0, day_of_week):
        column = day
        day_label = tk.Label(
            calendar_grid,
            text=str(current_day_of_month[week][day].day),
            width=11,
            height=5,
            relief="solid"
        )

        day_label.grid(
            row=row,
            column=column,
            padx=2,
            pady=2
        )

#This make the app stay opened and not instantly close after opening
window.mainloop()