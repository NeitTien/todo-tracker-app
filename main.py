import tkinter as tk
import datetime

#This create a window object to use Tkinter function
window = tk.Tk()
#This create title
window.title("Limiter")
#This create the resolution of the window
window.geometry("1600x900")

#Get the current year, month, day
current_year = datetime.datetime.now().year
current_month = datetime.datetime.now().month
current_day = datetime.datetime.now().day

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

def next_month():
    global current_month
    global current_year
    current_month += 1

    if current_month > 12:
        current_month = 1
        current_year += 1

    update_month_label()
    print(current_month)

def prev_month():
    global current_month
    global current_year
    current_month -= 1

    if current_month < 1:
        current_month = 12
        current_year -= 1
        
    update_month_label()
    print(current_month)

calendar = tk.Frame(window)
calendar.pack(pady=100)

month_label = tk.Label(
    calendar,
    text=months[current_month - 1],
    font=("Arial", 12)
)
month_label.grid(row=0, column=3, padx=10, pady=10)

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

for day in range(1, 31):
    row = ((day - 1) // 7) + 2
    column = (day - 1) % 7

    label = tk.Label(
        calendar,
        text=str(day),
        width=12,
        height=5,
        relief="solid"
    )

    label.grid(
        row=row,
        column=column,
        padx=2,
        pady=2
    )

#This make the app stay opened and not instantly close after opening
window.mainloop()