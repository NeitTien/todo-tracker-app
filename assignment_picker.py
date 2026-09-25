"""Limiter calendar with a right-click menu on every date.

Run: python limiter_calendar.py
Uses only Python's standard library and Tkinter.

Data is kept in memory: changing months preserves it, closing the app clears it.
Edit time changes an assignment's due time, using a 24-hour HH:MM value.
Blocked dates reject new assignments; existing ones can still be managed.
"""

import calendar
import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox

# The FULL date is the key, so September 5 and October 5 have separate data.
# Example: assignments[datetime.date(2026, 9, 23)] = [
#     {"title": "Finish Python homework", "time": "14:30"}
# ]

date_buttons = {}

class AssignmentManager:
    def __init__(self, parent, on_change=None):
        self.parent = parent #Parent is the main_frame

        #Create variable related to the assignment
        self.assignments = {}
        self.blocked_dates = set()
        self.selected_date = datetime.date.today()

        self.status = tk.StringVar(
            master=parent,
            value="Left-click a date to view assignments; right-click it for options."
        )

        self.is_macos = parent.tk.call("tk", "windowingsystem") == "aqua"
        self.context_click = "<Button-2>" if self.is_macos else "<Button-3>"

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

    def choose_assignment(self, date, action):
        items = assignments.get(date, [])
        if not items:
            messagebox.showinfo(
                action, "There are no assignments on this date.", parent=window
            )
            return None
        # Dialog provides OK/Cancel and returns None when cancelled or closed.
        return AssignmentPicker(window, date, action, items).result

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


# SELECT A DATE AND OPEN ITS CONTEXT MENU
def update_selected_details(self):
    if self.selected_date_label is None or self.assignment_list is None:
        return #attach_details_widgets() hasnt been called yet

    blocked = " - BLOCKED" if self.selected_date in self.blocked_dates else ""

    self.selected_date_label.config(text=f"{date_text(selected_date)}{blocked}")
    self.assignment_list.delete(0, tk.END)

    items = self.assignments.get(self.selected_date, [])
    for assignment in items:
        self.assignment_list.insert(tk.END, assignment_text(assignment))
    if not items:
        self.assignment_list.insert(tk.END, "No assignments on this date.")


def select_date(self, date):
    self.selected_date = date
    self.update_selected_details()
    #Cell restyling (highlight border) is CalendarView part
    #since it owns the frams - on_change triggers that redraw
    self.notify_change()
    for button_date, button in date_buttons.items():
        button.config(relief="sunken" if button_date == date else "raised")
    update_selected_details()


def show_menu(event, date):
    select_date(date)
    has_assignments = bool(assignments.get(date))

    # Indices match the menu entries created in create_gui(); 2 is a separator.
    menu.entryconfig(0, state="disabled" if date in blocked_dates else "normal")
    menu.entryconfig(1, state="normal" if has_assignments else "disabled")
    menu.entryconfig(
        3, label="Unblock date" if date in blocked_dates else "Block out date"
    )
    menu.entryconfig(4, state="normal" if has_assignments else "disabled")
    menu.tk_popup(event.x_root, event.y_root)
    return "break"


# CALENDAR VIEW FUNCTIONS
def update_calendar_day():
    global current_day_of_month
    # Redraw widgets only. Assignments and blocked dates live in separate data.
    for widget in calendar_grid.winfo_children():
        widget.destroy()
    date_buttons.clear()
    current_day_of_month = cal.monthdatescalendar(current_year, current_month)

    # Keeping weekday headings and date cells in one grid aligns their columns.
    for column, day_name in enumerate(days):
        calendar_grid.columnconfigure(column, weight=1, uniform="days")
        tk.Label(calendar_grid, text=day_name, font=("Arial", 12)).grid(
            row=0, column=column, padx=2, pady=8
        )

    for row, week in enumerate(current_day_of_month, start=1):
        for column, cell_date in enumerate(week):
            count = len(assignments.get(cell_date, []))
            background_color = "#FFFFFF" if cell_date.month == current_month else "#B8B8B8"
            lines = [str(cell_date.day)]
            if cell_date in blocked_dates:
                background_color = "#F1BABA"
                lines.append("BLOCKED")
            if count:
                lines.append(f"{count} assignment" if count == 1 else f"{count} assignments")

            day_button = tk.Button(
                calendar_grid, text="\n".join(lines), font=("Arial", 12),
                width=11, height=5, background=background_color,
                relief="sunken" if cell_date == selected_date else "raised",
                command=lambda date=cell_date: select_date(date),
            )
            day_button.grid(row=row, column=column, padx=2, pady=2, sticky="nsew")
            date_buttons[cell_date] = day_button

            # The default argument saves THIS cell's date for its callback.
            day_button.bind(
                context_click,
                lambda event, date=cell_date: show_menu(event, date),
            )
            if is_macos:
                day_button.bind(
                    "<Control-Button-1>",
                    lambda event, date=cell_date: show_menu(event, date),
                )
    update_selected_details()


#def change_month(offset):

    #selected_date = datetime.date(current_year, current_month, 1)

    #status.set("Left-click a date to view assignments; right-click it for options.")

# SIDEBAR FUNCTIONS

def create_gui():
    """Build the existing Limiter window, its views, and its single menu."""
    global window, calendar_view, dashboard_view, calendar_grid
    global month_label, year_label, selected_date_label, assignment_list
    global status, menu, is_macos, context_click

    details_frame = tk.Frame(calendar_view)
    details_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
    details_frame.columnconfigure(0, weight=1)
    selected_date_label = tk.Label(details_frame, font=("Arial", 12, "bold"), anchor="w")
    selected_date_label.grid(row=0, column=0, sticky="ew")
    assignment_list = tk.Listbox(details_frame, height=4, font=("Arial", 11))
    assignment_list.grid(row=1, column=0, sticky="ew", pady=5)
    scrollbar = tk.Scrollbar(details_frame, command=assignment_list.yview)
    scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
    assignment_list.config(yscrollcommand=scrollbar.set)

    status = tk.StringVar(
        master=window,
        value="Left-click a date to view assignments; right-click it for options.",
    )
    tk.Label(calendar_view, textvariable=status, anchor="w", wraplength=1000).grid(
        row=3, column=0, sticky="ew", pady=6
    )
    tk.Label(calendar_view,
             text="Session only: closing Limiter clears assignments and blocked dates.",
             anchor="w", fg="#555555").grid(row=4, column=0, sticky="ew")

    # One menu belongs to the existing window; no second tk.Tk() is needed.
    menu = tk.Menu(window, tearoff=False)
    menu.add_command(label="Add assignment", command=add_assignment)
    menu.add_command(label="Remove assignment", command=remove_assignment)
    menu.add_separator()
    menu.add_command(label="Block out date", command=block_out)
    menu.add_command(label="Edit time", command=edit_time)

    is_macos = window.tk.call("tk", "windowingsystem") == "aqua"
    context_click = "<Button-2>" if is_macos else "<Button-3>"
    update_calendar_day()  # Same renderer is used at startup and after navigation.
    switch_calendar_view()
    return window
