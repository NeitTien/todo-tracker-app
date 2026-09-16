import tkinter as tk
import calendar
import datetime

#This create a window object to use Tkinter function
window = tk.Tk()
#This create title
window.title("Limiter")
#This create the resolution of the window
window.geometry("1600x900")

#Get the current year, month, day
today = datetime.date.today()
current_year = today.year
current_month = today.month
current_day = today.day
current_day_of_month = calendar.monthcalendar(current_year, current_month)


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

def update_month_label():
    month_label.config(text=months[current_month - 1])

def update_year_label():
    year_label.config(text=current_year)

def update_day_labebl():
    day_label.config(text=str(current_day_of_month[week][day]))

def next_month():
    global current_month
    global current_year
    current_month += 1

    if current_month > 12:
        current_month = 1
        current_year += 1

    update_month_label()
    update_year_label()
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
    print(current_month)

calendar = tk.Frame(window)
calendar.pack(pady=100)

month_label = tk.Label(
    calendar,
    text=months[current_month - 1],
    font=("Arial", 12)
)
month_label.grid(row=0, column=3, padx=10, pady=10)

year_label = tk.Label(
    calendar,
    text=current_year,
    font=("Arial", 12)
)
year_label.grid(row=0, column=5, padx=0, pady=0)

button_next_month = tk.Button(
    calendar,
    text="Next Month",
    command=next_month
)
button_next_month.grid(row=0, column=6, padx=10, pady=10)

button_prev_month = tk.Button(
    calendar,
    text="Previous Month",
    command=prev_month
)
button_prev_month.grid(row=0, column=0, padx=10, pady=10)

for column, day in enumerate(days):
    label = tk.Label(
        calendar,
        text=day,
        font=("Arial", 12)
    )

    label.grid(row=1, column=column, padx=10, pady=10)

week_size = len(current_day_of_month)
day_of_week = len(current_day_of_month[0])
for week in range(0, week_size):
    row = week + 2
    for day in range(0, day_of_week):
        column = day
        day_label = tk.Label(
            calendar,
            text=str(current_day_of_month[week][day]),
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

#This make the app stay opened and not instantly close after opening
window.mainloop()