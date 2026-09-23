import tkinter as tk
import calendar
import datetime
import holidays
import settings
import dashboard_view
import calendar_view
from pathlib import Path

#This INIT a WINDOW object for Tkinter Function
window = tk.Tk()
window.title("Limiter")
window.geometry("1600x900")


'''
today = datetime.date.today()
current_year = today.year
current_month = today.month
current_day = today.day
cal = calendar.Calendar()
current_day_of_month = cal.monthdatescalendar(current_year, current_month)
'''



#Icon for the application
BASE_DIR = Path(__file__).resolve().parent #relative Path to the main.py file
icon_path = BASE_DIR / "assets" / "icon.png" #location of icon
icon = tk.PhotoImage(file=icon_path) #icon object
window.iconphoto(True, icon) #True mean use the icon as default for this app

#CALENDAR GUI
#Grid of children frame are relative to parent frame
#Meaning they are inside main_frame

#Sidebar Frame with Window as Parent
sidebar = tk.Frame(
    window,
    highlightbackground="purple",
    highlightthickness=1
)
sidebar.grid(row=0, column=0, padx=(0, 50), pady=30, sticky="nsew")

#Main Frame with Window as Parent
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=1, pady= 30, sticky="nsew")

'''
#Calendar View with Main Frame as Parent
calendar_view = tk.Frame(
    main_frame,
    highlightbackground="red",
    highlightthickness=1
)
calendar_view.grid(row=0, column=0, sticky="nsew")

#Calendar Header with Calendar View as Parent
calendar_header = tk.Frame(calendar_view)
calendar_header.grid(row=0, column=0)

#Calendar Grid with Calendar View as Parent
calendar_grid = tk.Frame(calendar_view)
calendar_grid.grid(row=1, column=0)
'''
calendar = calendar_view.CalendarView(main_frame)

#Dashboard View with Main Frame as Parent
dashboard_view = dashboard_view.create_dashboard(main_frame)
dashboard_view.grid(row=0, column=0, sticky="nsew")

#To-do List View with Main Frame as Parent (currently unused)
#todolist_view = tk.Frame(main_frame)

#Window Grid behavior
window.grid_columnconfigure(0, weight=0) #Sidebar Frame
window.grid_columnconfigure(1, weight=1) #Main Frame
window.grid_rowconfigure(0, weight=1)

#Main Frame Grid behavior
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(0, weight=1)



place_holder_value=1
#FUNCTION SECTION

'''
#CALENDAR_VIEW FUNCTION
#This update the displayed month when pressed next month button
def update_month_label():
    month_label.config(text=months[current_month - 1])

#This update the displayed year when year change because of next month
def update_year_label():
    year_label.config(text=current_year)
#This update calendar days of a month
def update_calendar_day():
    global current_day_of_month

    #This for-loop will destroy the previous grid
    #so that the calendar will not be overlapped
    #the data is not affected by this deletion
    for widget in calendar_grid.winfo_children():
        widget.destroy()

    current_day_of_month = cal.monthdatescalendar(current_year, current_month)
    week_size = len(current_day_of_month)
    day_of_week = len(current_day_of_month[0])
    for week in range(0, week_size):
        row = week
        for day in range(0, day_of_week):
            column = day

            #This will make days that is not of current month grayed out
            #696969 is gray color and FFFFFF is white color
            #add foreground if want to change text_color
            if current_day_of_month[week][day].month != current_month:
                background_color = "#696969"
            else:
                background_color = "#FFFFFF"

            day_label = tk.Label(
                calendar_grid,
                text=str(current_day_of_month[week][day].day),
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
    print(current_month) #This is for Debug

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
    print(current_month) #This is for Debug
'''
#SIDEBAR FUNCTION
def switch_calendar_view():
    calendar.calendar_view.tkraise()

def switch_dashboard_view():
    dashboard_view.tkraise()

#DASHBOARD_VIEW FUNCTION

#LABEL, BUTTON SECTION
#SIDEBAR
button_calendar_view = tk.Button(
    sidebar,
    text="Calendar View",
    font=("Arial", 12),
    command=switch_calendar_view
)
button_calendar_view.grid(row=0, column=0)

button_dashboard_view = tk.Button(
    sidebar,
    text="Dashboard View",
    font=("Arial", 12),
    command=switch_dashboard_view
)
button_dashboard_view.grid(row=1, column=0, pady=(30,30))

button_settings = tk.Button(
    sidebar,
    text="Settings",
    font=("Arial", 12),
    command=lambda: settings.open_settings(window)
)
button_settings.grid(row=2, column=0, pady= (0,30))

#CALENDAR
'''
month_label = tk.Label(
    calendar_header,
    text=months[current_month - 1],
    font=("Arial", 12)
)
month_label.grid(row=0, column=3)

year_label = tk.Label(
    calendar_header,
    text=current_year,
    font=("Arial", 12)
)
year_label.grid(row=0, column=4)

button_next_month = tk.Button(
    calendar_header,
    text="Next Month",
    font=("Arial", 12),
    command=next_month
)
button_next_month.grid(row=0, column=6)

button_prev_month = tk.Button(
    calendar_header,
    text="Previous Month",
    font=("Arial", 12),
    command=prev_month
)
button_prev_month.grid(row=0, column=0)

#This shows Mon -> Sun
for column, day in enumerate(days):
    label = tk.Label(
        calendar_header,
        text=day,
        width=11,
        font=("Arial", 12)
    )

    label.grid(row=1, column=column, padx=2, pady=30)

#This generates the calendar days of current month
week_size = len(current_day_of_month)
day_of_week = len(current_day_of_month[0])
for week in range(0, week_size):
    row = week
    for day in range(0, day_of_week):
        column = day
        
        if current_day_of_month[week][day].month != current_month:
            background_color = "#696969"
        else:
            background_color = "#FFFFFF"

        day_label = tk.Label(
            calendar_grid,
            text=str(current_day_of_month[week][day].day),
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

'''
#This make the app stay opened and not instantly close after opening
window.mainloop()