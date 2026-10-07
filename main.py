import tkinter as tk
# ADDED: dialogs used by the calendar menu.
from tkinter import messagebox, simpledialog
import calendar
import datetime
#import holidays

#This INIT a WINDOW object for Tkinter Function
window = tk.Tk()
window.title("Limiter")
window.geometry("1600x900")

#CALENDAR GUI
#Grid of children frame are relative to parent frame
#Meaning they are inside main_frame

#Sidebar Frame with Window as Parent
sidebar = tk.Frame(window)
sidebar.grid(row=0, column=0)

#Main Frame with Window as Parent
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=1)

#Calendar View with Main Frame as Parent
calendar_view = tk.Frame(main_frame)
calendar_view.grid(row=0, column=0)

#Calendar Header with Calendar View as Parent
calendar_header = tk.Frame(calendar_view)
calendar_header.grid(row=0, column=0) #padx=500, pady=(100,0)

#Calendar Grid with Calendar View as Parent
calendar_grid = tk.Frame(calendar_view)
calendar_grid.grid(row=1, column=0)

#Dashboard View with Main Frame as Parent
dashboard_view = tk.Frame(main_frame)
dashboard_view.grid(row=0, column=0)

#To-do List View with Main Frame as Parent (currently unused)
#todolist_view = tk.Frame(main_frame)

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

place_holder_value=1
#FUNCTION SECTION

# ADDED: right-click menu data and functions.
# Full dates keep the same day number in different months separate.
# Data survives calendar redraws, but closing the app clears it.
selected_date = today
assignments = {}
blocked_dates = set()


def date_text(date):
    return date.strftime("%A, %B %d, %Y")


def assignment_text(assignment):
    time_text = assignment["time"] or "No time set"
    return f"{time_text} - {assignment['title']}"


def normalize_time(value):
    """Return HH:MM, allow blank for no time, or raise ValueError."""
    value = value.strip()
    if not value:
        return ""
    return datetime.datetime.strptime(value, "%H:%M").strftime("%H:%M")


def ask_for_time(date, assignment_title, initial_value=""):
    """None means Cancel; an empty string means the user cleared the time."""
    while True:
        value = simpledialog.askstring(
            f"Assignment time - {date.isoformat()}",
            f"Time for: {assignment_title}\n\n"
            "Use 24-hour HH:MM, for example 14:30.\n"
            "Leave blank for no time.",
            initialvalue=initial_value,
            parent=window,
        )
        if value is None:
            return None

        try:
            return normalize_time(value)
        except ValueError:
            messagebox.showerror(
                "Invalid time",
                "Enter a time from 00:00 to 23:59, or leave it blank.",
                parent=window,
            )
            initial_value = value


class AssignmentPicker(simpledialog.Dialog):
    """A child dialog for choosing which assignment to remove or edit."""

    def __init__(self, parent, date, action, items):
        self.items = items
        self.action = action
        super().__init__(parent, title=f"{action} - {date.isoformat()}")

    def body(self, frame):
        tk.Label(frame, text="Choose an assignment:").pack(anchor="w")
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True, pady=8)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.listbox = tk.Listbox(
            list_frame, width=64, height=min(8, len(self.items)),
            exportselection=False, yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        for item in self.items:
            self.listbox.insert(tk.END, assignment_text(item))
        self.listbox.selection_set(0)
        return self.listbox

    def validate(self):
        return bool(self.listbox.curselection())

    def apply(self):
        self.result = self.listbox.curselection()[0]


def choose_assignment(date, action):
    items = assignments.get(date, [])
    if not items:
        messagebox.showinfo(
            action, "There are no assignments on this date.", parent=window
        )
        return None
    # Dialog provides OK/Cancel and returns None when cancelled or closed.
    return AssignmentPicker(window, date, action, items).result


# MENU ACTIONS
def add_assignment():
    date = selected_date
    if date in blocked_dates:
        messagebox.showinfo(
            "Date blocked", "Unblock this date before adding an assignment.",
                        parent=window,
        )
        return

    title = simpledialog.askstring(
        f"Add assignment - {date.isoformat()}",
        f"Assignment name for {date_text(date)}:",
        parent=window,
    )
    if title is None:
        return
    title = " ".join(title.split())
    if not title:
        messagebox.showerror("Name required", "Enter an assignment name.", parent=window)
        return

    time_value = ask_for_time(date, title)
    if time_value is None:
        return  # Cancelling either dialog leaves the calendar data unchanged.

    assignments.setdefault(date, []).append({"title": title, "time": time_value})
    update_calendar_day()
    status.set(f"Added '{title}' to {date.isoformat()}.")


def remove_assignment():
    date = selected_date
    index = choose_assignment(date, "Remove assignment")
    if index is None:
        return
        removed = assignments[date].pop(index)
    if not assignments[date]:
        del assignments[date]
    update_calendar_day()
    status.set(f"Removed '{removed['title']}' from {date.isoformat()}.")


def block_out():
    date = selected_date
    if date in blocked_dates:
        blocked_dates.remove(date)
        message = f"Unblocked {date.isoformat()}."
    else:
        blocked_dates.add(date)
        message = f"Blocked {date.isoformat()}. Existing assignments are kept."
    update_calendar_day()
    status.set(message)


def edit_time():
    date = selected_date
    index = choose_assignment(date, "Edit time")
    if index is None:
        return
    assignment = assignments[date][index]
    new_time = ask_for_time(date, assignment["title"], assignment["time"])
    if new_time is None:
        return
    assignment["time"] = new_time
    update_calendar_day()
    status.set(f"Updated time for '{assignment['title']}' on {date.isoformat()}.")


def connect_calendar_menu(day_label, date):
    """Connect an existing Label to the menu without replacing the widget."""
    lines = [str(date.day)]
    if date in blocked_dates:
        lines.append("BLOCKED")
    count = len(assignments.get(date, []))
    if count:
        lines.append(f"{count} assignment" if count == 1 else f"{count} assignments")
    day_label.config(text="\n".join(lines))

    # date=date saves this label's full date when the callback is created.
    day_label.bind(
        "<Button-3>",
        lambda event, date=date: show_menu(event, date),
    )


def show_menu(event, date):
    global selected_date
    selected_date = date
    status.set(f"Selected: {date_text(date)}")
    has_assignments = bool(assignments.get(date))
    menu.entryconfig(0, state="disabled" if date in blocked_dates else "normal")
    menu.entryconfig(1, state="normal" if has_assignments else "disabled")
    menu.entryconfig(
        3, label="Unblock date" if date in blocked_dates else "Block out date"
    )
    menu.entryconfig(4, state="normal" if has_assignments else "disabled")
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()
    return "break"
# END ADDED: right-click menu data and functions.

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
            # ADDED: reconnect each date after the calendar is redrawn.
            connect_calendar_menu(day_label, current_day_of_month[week][day])
            
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

#SIDEBAR FUNCTION
def switch_calendar_view():
    calendar_view.tkraise()

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
button_dashboard_view.grid(row=1, column=0, pady=30)

#CALENDAR
month_label = tk.Label(
    calendar_header,
    text=months[current_month - 1],
    width=11,
        font=("Arial", 12)
)
month_label.grid(row=0, column=3)

year_label = tk.Label(
    calendar_header,
    text=current_year,
    width=11,
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
         # ADDED: connect each date when the calendar first opens.
        connect_calendar_menu(day_label, current_day_of_month[week][day])

#DASHBOARD
placeholder_label = tk.Label(
    dashboard_view,
    text="This is place holder",
    font=("Arial", 12)
)
placeholder_label.grid(row=0, column=0)
# ADDED: the menu belongs to your existing window.
# This replaces the separate root window and sample "Current date" button.
status = tk.StringVar(
    master=window,
    value="Right-click a calendar date for options. Changes last until the app closes."
)
status_label = tk.Label(
    calendar_view,
    textvariable=status,
    font=("Arial", 12),
    wraplength=800
)
status_label.grid(row=2, column=0, pady=10)

menu = tk.Menu(window, tearoff=False)
menu.add_command(label="Add assignment", command=add_assignment)
menu.add_command(label="Remove assignment", command=remove_assignment)
menu.add_separator()
menu.add_command(label="Block out date", command=block_out)
menu.add_command(label="Edit time", command=edit_time)
# END ADDED: menu setup must come before the existing mainloop.

#This make the app stay opened and not instantly close after opening
window.mainloop()


"""
import tkinter as tk
import calendar
import datetime
#import holidays

#This INIT a WINDOW object for Tkinter Function
window = tk.Tk()
window.title("Limiter")
window.geometry("1600x900")

#CALENDAR GUI
#Grid of children frame are relative to parent frame
#Meaning they are inside main_frame

#Sidebar Frame with Window as Parent
sidebar = tk.Frame(window)
sidebar.grid(row=0, column=0)

#Main Frame with Window as Parent
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=1)

#Calendar View with Main Frame as Parent
calendar_view = tk.Frame(main_frame)
calendar_view.grid(row=0, column=0)

#Calendar Header with Calendar View as Parent
calendar_header = tk.Frame(calendar_view)
calendar_header.grid(row=0, column=0) #padx=500, pady=(100,0)

#Calendar Grid with Calendar View as Parent
calendar_grid = tk.Frame(calendar_view)
calendar_grid.grid(row=1, column=0)

#Dashboard View with Main Frame as Parent
dashboard_view = tk.Frame(main_frame)
dashboard_view.grid(row=0, column=0)

#To-do List View with Main Frame as Parent (currently unused)
#todolist_view = tk.Frame(main_frame)

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

place_holder_value=1
#FUNCTION SECTION

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

#SIDEBAR FUNCTION
def switch_calendar_view():
    calendar_view.tkraise()

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
button_dashboard_view.grid(row=1, column=0, pady=30)

#CALENDAR
month_label = tk.Label(
    calendar_header,
    text=months[current_month - 1],
    width=11,
    font=("Arial", 12)
)
month_label.grid(row=0, column=3)

year_label = tk.Label(
    calendar_header,
    text=current_year,
    width=11,
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

#DASHBOARD
placeholder_label = tk.Label(
    dashboard_view,
    text="This is place holder",
    font=("Arial", 12)
)
placeholder_label.grid(row=0, column=0)
#This make the app stay opened and not instantly close after opening
window.mainloop()

#code incorperation start here

# 1. Create the main window.
root = tk.Tk()
root.title("Editing calendar date") #need to add date grabber for selected date being edited
root.geometry("420x220")

# This text will change when a menu option is selected.
status = tk.StringVar(value="Right-click the date to see its options.")


# 2. Define the action for each menu option.
def add_assignment():
    status.set("You selected: Add assignment")


def remove_assignment():
    status.set("You selected: Remove assignment")


def block_out():
    status.set("You selected: Block out date")


def edit_time():
    status.set("You selected: Edit time")


# 3. Create the menu and connect its options to those functions.
menu = tk.Menu(root, tearoff=False)
menu.add_command(label="Add assignment", command=add_assignment)
menu.add_command(label="Remove assignment", command=remove_assignment)
menu.add_separator()
menu.add_command(label="Block out date", command=block_out)
menu.add_command(label="Edit time", command=edit_time)


# 4. Show the menu at the mouse pointer's screen position.
def show_menu(assignment):
    menu.tk_popup(assignment.x_root, assignment.y_root)
    return "break"


# 5. Create a button representing one calendar date.
date_button = ttk.Button(root, text="Current date", padding=15) #need to grab the date that was clicked on
date_button.pack(pady=25)

# This acts as the prompt to open up the menu
date_button.bind("<Button-3>", show_menu)

ttk.Label(root, textvariable=status).pack(pady=10)

# 6. Start listening for clicks and other window events.
root.mainloop()
#this code will keep running until a final decision is made in the secondary windows
"""