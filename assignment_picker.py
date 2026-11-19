"""Limiter calendar with a right-click menu on every date.

Run: python main.py
Uses only Python's standard library and Tkinter.

main.py connects AppStorage so assignments and blocked dates survive closing the app.
Edit time changes an assignment's due time, using a 24-hour HH:MM value.
Blocked dates reject new assignments; existing ones can still be managed.
Each assignment can have a difficulty (easy / medium / hard) that colors its text.
Each new assignment gets a due time (11:59 PM unless the user picks another one).
"""

import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox

# The FULL date is the key, so September 5 and October 5 have separate data.
# Example: assignments[datetime.date(2026, 9, 23)] = [
#     {"title": "Finish Python homework", "time": "14:30"}
# ]

#date_buttons = {} #I dont know wat this is for yet

#** DIFFICULTY COLORS: an assignment's "difficulty" is "" (none), "easy", "medium" or "hard"
#No difficulty keeps the normal text color. The shades change with the background they sit on,
#so every color stays readable (each one has at least 4.5:1 contrast with its background)
DIFFICULTY_CHOICES = [("None", ""), ("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")]
DIFFICULTY_COLORS = {
    #light background (normal dates, the assignment list, the dashboard)
    "light":   {"easy": "#1B7F3B", "medium": "#A07800", "hard": "#C62828"},
    #pink background (blocked dates) needs darker shades
    "blocked": {"easy": "#0F5A26", "medium": "#6B4E00", "hard": "#9B1111"},
    #gray background (days from the previous / next month) needs lighter shades
    "gray":    {"easy": "#C2F7CC", "medium": "#FFEB99", "hard": "#FFE9E6"},
}

#Order assignments are listed in: hard first, then medium, easy, and no difficulty last
DIFFICULTY_ORDER = {"hard": 0, "medium": 1, "easy": 2, "": 3}

#** TIME: every new assignment gets a due time, stored as 24-hour "HH:MM" text.
#It defaults to 11:59 PM of that day, and the user can pick any hour and minute next to the text box
DEFAULT_TIME = "23:59"

#** SORT SETTING: how a date's tasks are ordered (chosen in Settings)
#"difficulty" = Hard, Medium, Easy, none (same difficulty: the one due earliest first)
#"time" = due soonest first (same time: Hard, Medium, Easy, none); tasks with no time go last
SORT_MODES = ("difficulty", "time")
DEFAULT_SORT_MODE = "difficulty"

#** REMINDERS: each assignment can have "notify" = how many minutes before its due time to remind
#the user (None / missing = no reminder) and "notified" = True once that reminder has been shown.
#New assignments start with the default reminder (1 hour before, changeable in Settings)
REMINDER_UNITS = {"minutes": 1, "hours": 60, "days": 1440}
DEFAULT_REMINDER_MINUTES = 60
MAX_REMINDER_AMOUNT = 999

#90 -> (90, "minutes"), 120 -> (2, "hours"), 2880 -> (2, "days")
def split_minutes(total):
    for unit in ("days", "hours"):
        if total % REMINDER_UNITS[unit] == 0:
            return total // REMINDER_UNITS[unit], unit
    return total, "minutes"

#Wording for a number of minutes: "1 hour", "30 minutes", "2 days"
def minutes_text(total):
    amount, unit = split_minutes(total)
    return f"{amount} {unit[:-1] if amount == 1 else unit}"

#The date and time an assignment is due (None when it has no time)
def due_datetime(date, assignment):
    value = assignment.get("time", "")
    if not value:
        return None
    return datetime.datetime.combine(date, datetime.time(int(value[:2]), int(value[3:5])))

def time_to_12h(value):
    #"23:59" -> "11:59 PM" ("" -> "", for assignments that have no time)
    if not value:
        return ""
    hour, minute = int(value[:2]), value[3:5]
    return f"{(hour % 12) or 12}:{minute} {'PM' if hour >= 12 else 'AM'}"

def difficulty_color(difficulty, surface="light"):
    #Returns the text color for a difficulty, or None when there is none (use the normal color)
    return DIFFICULTY_COLORS[surface].get(difficulty)

class AssignmentManager:
    def __init__(self, parent, on_change=None, on_select=None):
        
        self.parent = parent #Parent is the main_frame
        self.on_change = on_change
        self.on_select = on_select

        #Create variable related to the assignment
        self.assignments = {}
        self.blocked_dates = set()
        self.selected_date = datetime.date.today()
        self.sort_mode = DEFAULT_SORT_MODE #Set from Settings ("difficulty" or "time")
        self.default_reminder = DEFAULT_REMINDER_MINUTES #Minutes before due for new tasks (None = no reminder)
        self.reminder_window = None #The reminder popup, while one is open
        self.summary_window = None #The "due today" popup shown when Limiter opens


        self.status = tk.StringVar(
            master=parent,
            value="Left-click a date to view assignments; right-click it for options."
        )

        self.is_macos = parent.tk.call("tk", "windowingsystem") == "aqua"
        self.context_click = "<Button-2>" if self.is_macos else "<Button-3>"

        #menu = tk.Menu(window, tearoff=False) should be (self.parent.parent.parent)
        self.menu = tk.Menu(parent, tearoff=False)
        self.menu.add_command(
            label="Add assignment",
            command=self.add_assignment
        )
        self.menu.add_command(
            label="Remove assignment",
            command=self.remove_assignment
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="Block out date",
            command=self.block_out
        )
        self.menu.add_command(
            label="Edit time",
            command=self.edit_time
        )

        # Optional: CalendarView can point these at real widgets
        # (a Label and a Listbox) via attach_details_widgets(), so
        # update_selected_details() has somewhere to write. Left as
        # None here so this class works even before that's wired up.
        self.selected_date_label = None
        self.assignment_list = None
        self.assignment_entry = None #Text box for typing a new assignment
        self.add_button = None #Button next to the text box (says Add, or Save while editing)
        self.editing_index = None #Which assignment of the selected date is being edited, if any
        self.difficulty_var = None #Difficulty choice (radio buttons) next to the text box
        self.time_vars = None #(hour, minute, AM/PM) boxes next to the text box
        self.reminder_vars = None #(on/off, amount, unit) of the "Remind me" row

    def attach_details_widgets(self, selected_date_label, assignment_list, assignment_entry=None, add_button=None, difficulty_var=None, time_vars=None, reminder_vars=None):
        #Point this at the widgets that show the selected
        #date and its assignment list, then do an initial render
        self.selected_date_label = selected_date_label
        self.assignment_list = assignment_list
        self.assignment_entry = assignment_entry
        self.add_button = add_button
        self.difficulty_var = difficulty_var
        self.time_vars = time_vars
        self.reminder_vars = reminder_vars
        self.set_chosen_reminder(self.default_reminder)
        self.update_selected_details()

    def notify_change(self):
        if self.on_change:
            self.on_change()

    def notify_select(self):
        if self.on_select:
            self.on_select()

    def get_assignments(self, date):
        #Debug purpose
        #print(self.assignments)
        return self.assignments.get(date, [])
    
    def is_blocked(self, date):
        return date in self.blocked_dates

    def date_text(self, date):
        return date.strftime("%A, %B %d, %Y")

    def assignment_text(self, assignment):
        #Only show a time in front of the name when one was set
        if not assignment["time"]:
            return assignment["title"]
        return f"{time_to_12h(assignment['time'])} - {assignment['title']}"

    #Sort key for one assignment, depending on the sort mode picked in Settings
    #(sort is stable, so tasks that tie stay in the order they were added)
    def sort_key(self, assignment):
        difficulty = DIFFICULTY_ORDER.get(assignment.get("difficulty", ""), 3)
        time_value = assignment.get("time", "")
        no_time = 0 if time_value else 1 #Tasks without a time go after the ones that have one
        if self.sort_mode == "time":
            return (no_time, time_value, difficulty)
        return (difficulty, no_time, time_value)

    #Puts a date's assignments in order (see sort_mode)
    def sort_assignments(self, date):
        items = self.assignments.get(date)
        if items:
            items.sort(key=self.sort_key)

    #Changes how tasks are ordered and re-sorts every date right away
    def set_sort_mode(self, mode, notify=True):
        self.sort_mode = mode if mode in SORT_MODES else DEFAULT_SORT_MODE
        for date in self.assignments:
            self.sort_assignments(date)
        self.set_editing(None) #Row positions just changed, so drop any edit in progress
        self.update_selected_details()
        if notify:
            self.notify_change()

    #The difficulty currently picked next to the text box ("" when None is picked)
    def chosen_difficulty(self):
        return self.difficulty_var.get() if self.difficulty_var is not None else ""

    def set_chosen_difficulty(self, value):
        if self.difficulty_var is not None:
            self.difficulty_var.set(value)

    #The time picked next to the text box as "HH:MM" (24-hour),
    #or None if the hour / minute boxes hold something that is not a real time
    def chosen_time(self):
        if self.time_vars is None:
            return DEFAULT_TIME
        hour_var, minute_var, ampm_var = self.time_vars
        try:
            hour, minute = int(hour_var.get()), int(minute_var.get())
        except ValueError:
            return None
        if not (1 <= hour <= 12 and 0 <= minute <= 59):
            return None
        hour = hour % 12 + (12 if ampm_var.get() == "PM" else 0)
        return f"{hour:02d}:{minute:02d}"

    #Show a time ("HH:MM") in the boxes; no time (or a missing one) shows the default, 11:59 PM
    def set_chosen_time(self, value):
        if self.time_vars is None:
            return
        hour_var, minute_var, ampm_var = self.time_vars
        value = value or DEFAULT_TIME
        hour = int(value[:2])
        hour_var.set(str((hour % 12) or 12))
        minute_var.set(value[3:5])
        ampm_var.set("PM" if hour >= 12 else "AM")

    #The reminder picked next to the text box: (True, minutes before due), (True, None) when the
    #number is not valid, or (False, None) when reminders are switched off for this assignment
    def chosen_reminder(self):
        if self.reminder_vars is None:
            return True, self.default_reminder
        on_var, amount_var, unit_var = self.reminder_vars
        if not on_var.get():
            return False, None
        try:
            amount = int(amount_var.get())
        except ValueError:
            return True, None
        if not (1 <= amount <= MAX_REMINDER_AMOUNT) or unit_var.get() not in REMINDER_UNITS:
            return True, None
        return True, amount * REMINDER_UNITS[unit_var.get()]

    #Show a reminder (minutes before due, or None for off) in the "Remind me" row;
    #a missing reminder (older assignments) shows the default
    def set_chosen_reminder(self, minutes):
        if self.reminder_vars is None:
            return
        on_var, amount_var, unit_var = self.reminder_vars
        if minutes is None:
            on_var.set(False)
            minutes = self.default_reminder or DEFAULT_REMINDER_MINUTES
        else:
            on_var.set(True)
        amount, unit = split_minutes(minutes)
        amount_var.set(str(amount))
        unit_var.set(unit)

    #Changes the reminder new assignments start with (from Settings); None = no reminder
    def set_default_reminder(self, minutes):
        self.default_reminder = minutes
        if self.editing_index is None:
            self.set_chosen_reminder(minutes)

    #Stores the reminder on an assignment. If the due time has already passed there is nothing
    #left to remind about, so it is marked as done; otherwise it will show when its time comes.
    def apply_reminder(self, date, assignment, minutes):
        assignment["notify"] = minutes
        due = due_datetime(date, assignment)
        assignment["notified"] = due is None or due <= datetime.datetime.now()

    #Checks every assignment and shows a popup for the ones whose reminder time has come.
    #Called every 30 seconds by main.py. Returns the list of reminders that were shown.
    def check_reminders(self, now=None):
        now = now or datetime.datetime.now()
        due_now = []
        for date, items in self.assignments.items():
            for assignment in items:
                minutes = assignment.get("notify")
                due = due_datetime(date, assignment)
                if minutes is None or due is None or assignment.get("notified"):
                    continue
                if now >= due - datetime.timedelta(minutes=minutes):
                    due_now.append((due, date, assignment))
        if not due_now:
            return []
        due_now.sort(key=lambda entry: entry[0])
        for due, date, assignment in due_now:
            assignment["notified"] = True #Only remind once
        self.notify_change() #Saves that these reminders were shown
        self.show_reminders(due_now, now)
        return due_now

    #** DUE TODAY: the popup shown when Limiter opens, listing everything due today
    #(in the same order as the list in the details panel). Does nothing when nothing is due today.
    #Returns the list of tasks it showed.
    def show_daily_summary(self, today=None, now=None):
        now = now or datetime.datetime.now()
        today = today or now.date()
        items = list(self.assignments.get(today, []))
        if not items:
            return []
        self.display_daily_summary(today, items, now)
        return items

    #The popup itself (non-modal, like the reminder popup)
    def display_daily_summary(self, today, items, now):
        MAX_SHOWN = 12
        if self.summary_window is not None and self.summary_window.winfo_exists():
            self.summary_window.destroy()
        window = tk.Toplevel(self.parent)
        self.summary_window = window
        window.title("Due today")
        window.attributes("-topmost", True)
        window.resizable(False, False)
        count = f"{len(items)} task{'s' if len(items) != 1 else ''}"
        tk.Label(window, text=f"Due today - {count}", font=("Arial", 14, "bold")).pack(padx=20, pady=(15, 0))
        tk.Label(window, text=self.date_text(today), font=("Arial", 11)).pack(padx=20, pady=(0, 8))
        body = tk.Frame(window, bg="white", highlightbackground="gray", highlightthickness=1)
        body.pack(padx=20, fill="x")
        for assignment in items[:MAX_SHOWN]:
            due = due_datetime(today, assignment)
            line = self.assignment_text(assignment)
            if due is not None and due <= now:
                line += "  (time has passed)"
            tk.Label(
                body, text=line, font=("Arial", 12), bg="white", anchor="w", justify="left", wraplength=420,
                fg=difficulty_color(assignment.get("difficulty", ""), "light") or "black"
            ).pack(fill="x", padx=8, pady=2)
        if len(items) > MAX_SHOWN:
            tk.Label(body, text=f"+{len(items) - MAX_SHOWN} more", font=("Arial", 12), bg="white", anchor="w").pack(
                fill="x", padx=8, pady=2
            )
        tk.Button(window, text="OK", font=("Arial", 12), width=8, command=window.destroy).pack(pady=15)
        window.bell()

    def reminder_line(self, due, assignment, now):
        when = f"{time_to_12h(due.strftime('%H:%M'))}, {due.strftime('%a %b')} {due.day}"
        gap = round((due - now).total_seconds() / 60)
        if gap <= 0:
            return f"OVERDUE: {assignment['title']} (was due {when})"
        return f"Due in {minutes_text(gap)}: {assignment['title']} ({when})"

    #The popup itself (non-modal, so the app keeps working while it is open)
    def show_reminders(self, due_now, now):
        lines = [self.reminder_line(due, assignment, now) for due, date, assignment in due_now]
        if self.reminder_window is not None and self.reminder_window.winfo_exists():
            self.reminder_window.destroy()
        window = tk.Toplevel(self.parent)
        self.reminder_window = window
        window.title("Limiter reminder")
        window.attributes("-topmost", True)
        window.resizable(False, False)
        tk.Label(window, text="Reminder", font=("Arial", 14, "bold")).pack(padx=20, pady=(15, 5))
        for line in lines:
            tk.Label(window, text=line, font=("Arial", 12), wraplength=420, justify="left").pack(
                anchor="w", padx=20, pady=2
            )
        tk.Button(window, text="OK", font=("Arial", 12), width=8, command=window.destroy).pack(pady=15)
        window.bell()

    def normalize_time(self, value):
        """Return HH:MM, allow blank for no time, or raise ValueError."""
        value = value.strip()
        if not value:
            return ""
        return datetime.datetime.strptime(value, "%H:%M").strftime("%H:%M")
        
    def ask_for_time(self, date, assignment_title, initial_value=""):
        """None means Cancel; an empty string means the user cleared the time."""
        while True:
            value = simpledialog.askstring(
                f"Assignment time - {date.isoformat()}",
                f"Time for: {assignment_title}\n\n"
                "Use 24-hour HH:MM, for example 14:30.\n"
                "Leave blank for no time.",
                initialvalue=initial_value,
                parent=self.parent,
            )
            if value is None:
                return None
            try:
                return self.normalize_time(value)
            except ValueError:
                messagebox.showerror(
                    "Invalid time",
                    "Enter a time from 00:00 to 23:59, or leave it blank.",
                    parent=self.parent,
                )
                initial_value = value

    def choose_assignment(self, date, action):
        items = self.assignments.get(date, [])
        if not items:
            messagebox.showinfo(
                action, "There are no assignments on this date.", 
                parent=self.parent
            )
            return None
        # Dialog provides OK/Cancel and returns None when cancelled or closed.
        return AssignmentPicker(self.parent, date, action, items).result

    # MENU ACTIONS
    def add_assignment(self):
        date = self.selected_date
        if date in self.blocked_dates:
            messagebox.showinfo(
                "Date blocked",
                "Unblock this date before adding an assignment.",
                parent=self.parent,
            )
            return

        title = simpledialog.askstring(
            f"Add assignment - {date.isoformat()}",
            f"Assignment name for {self.date_text(date)}:",
            parent=self.parent,
        )

        if title is None:
            return
        title = " ".join(title.split())

        if not title:
            messagebox.showerror(
                "Name required",
                "Enter an assignment name.",
                parent=self.parent
            )
            return

        time_value = self.ask_for_time(date, title, DEFAULT_TIME) #Starts at the default, 23:59 (11:59 PM)
        if time_value is None:
            return  # Cancelling either dialog leaves the calendar data unchanged.

        difficulty = DifficultyDialog(self.parent, date, title).result
        if difficulty is None:
            return  # Cancel leaves the calendar data unchanged ("" means no difficulty)

        new_assignment = {"title": title, "time": time_value, "difficulty": difficulty}
        self.apply_reminder(date, new_assignment, self.default_reminder)
        self.assignments.setdefault(date, []).append(new_assignment)
        self.sort_assignments(date)
        self.update_selected_details()
        self.notify_change() #Redraws the calendar so the date's box shows the new assignment
        self.status.set(f"Added '{title}' to {date.isoformat()}.")

    def remove_assignment(self):
        date = self.selected_date
        index = self.choose_assignment(date, "Remove assignment")
        if index is None:
            return
        removed = self.assignments[date].pop(index)
        if not self.assignments[date]:
            del self.assignments[date]

        self.cancel_edit() #Removing an item can change the index being edited.
        self.update_selected_details()
        self.notify_change()
        self.status.set(f"Removed '{removed['title']}' from {date.isoformat()}.")

    def block_out(self):
        date = self.selected_date
        if date in self.blocked_dates:
            self.blocked_dates.remove(date)
            message = f"Unblocked {date.isoformat()}."
        else:
            self.blocked_dates.add(date)
            message = f"Blocked {date.isoformat()}. Existing assignments are kept."
        self.update_selected_details()
        self.notify_change()
        self.status.set(message)

    def edit_time(self):
        date = self.selected_date
        index = self.choose_assignment(date, "Edit time")
        if index is None:
            return

        self.assignment = self.assignments[date][index]
        new_time = self.ask_for_time(
            date, 
            self.assignment["title"], 
            self.assignment["time"]
        )

        if new_time is None:
            return
        self.assignment["time"] = new_time
        self.apply_reminder(date, self.assignment, self.assignment.get("notify")) #New time = new reminder moment
        self.update_selected_details()
        self.notify_change()
        self.status.set(f"Updated time for '{self.assignment['title']}' on {date.isoformat()}.")
    
    #Switch the button next to the text box between "Add" (new assignment) and "Save" (editing one)
    def set_editing(self, index):
        self.editing_index = index
        if self.add_button is not None:
            self.add_button.config(text="Save" if index is not None else "Add")

    #Stop editing and clear the text box (Escape, or clicking a different date)
    def cancel_edit(self):
        if self.editing_index is not None:
            self.set_editing(None)
            self.set_chosen_difficulty("")
            self.set_chosen_time(DEFAULT_TIME)
            self.set_chosen_reminder(self.default_reminder)
            if self.assignment_entry is not None:
                self.assignment_entry.delete(0, tk.END)

    #Load the selected assignment's name into the text box so it can be changed
    def start_edit(self):
        items = self.assignments.get(self.selected_date, [])
        selection = self.assignment_list.curselection() if self.assignment_list else ()
        if not items or not selection:
            self.status.set("Click an assignment in the list first, then press Edit.")
            return

        index = selection[0]
        self.set_editing(index)
        self.assignment_entry.delete(0, tk.END)
        self.assignment_entry.insert(0, items[index]["title"])
        self.set_chosen_difficulty(items[index].get("difficulty", "")) #Show its current difficulty
        self.set_chosen_time(items[index].get("time", "")) #...and its current time
        self.set_chosen_reminder(items[index].get("notify")) #...and its reminder
        self.assignment_entry.focus_set()
        self.status.set("Change the name, difficulty, time or reminder, then press Enter or Save (Escape to cancel).")

    #Delete the assignment selected in the list from the selected date
    def remove_selected(self):
        date = self.selected_date
        items = self.assignments.get(date, [])
        selection = self.assignment_list.curselection() if self.assignment_list else ()
        if not items or not selection:
            self.status.set("Click an assignment in the list first, then press Remove.")
            return

        removed = items.pop(selection[0])
        if not items:
            del self.assignments[date]
        self.cancel_edit() #The list shifted, so any edit in progress is stopped
        self.update_selected_details()
        self.notify_change()
        self.status.set(f"Removed '{removed['title']}' from {date.isoformat()}.")

    #Add an assignment typed in the text box under the list to the selected date
    #(or save the new name if an assignment is being edited)
    #Returns True if it worked, so the caller knows whether to clear the text box
    def add_from_text(self, text):
        date = self.selected_date
        title = " ".join(text.split())
        if not title:
            return False

        time_value = self.chosen_time()
        if time_value is None:
            self.status.set("Enter an hour from 1 to 12 and a minute from 0 to 59.")
            return False

        reminder_on, reminder_minutes = self.chosen_reminder()
        if reminder_on and reminder_minutes is None:
            self.status.set(f"Enter a whole number from 1 to {MAX_REMINDER_AMOUNT} for the reminder.")
            return False

        #Editing changes the assignment's name, difficulty, time and reminder
        #(allowed on blocked dates too, since existing assignments can still be managed)
        if self.editing_index is not None:
            items = self.assignments.get(date, [])
            if self.editing_index >= len(items):
                self.set_editing(None)
                return False
            items[self.editing_index]["title"] = title
            items[self.editing_index]["difficulty"] = self.chosen_difficulty()
            items[self.editing_index]["time"] = time_value
            self.apply_reminder(date, items[self.editing_index], reminder_minutes)
            self.set_editing(None)
            self.set_chosen_difficulty("") #Back to None for the next assignment
            self.set_chosen_time(DEFAULT_TIME) #...and back to 11:59 PM
            self.set_chosen_reminder(self.default_reminder) #...and the default reminder
            self.sort_assignments(date)
            self.update_selected_details()
            self.notify_change()
            self.status.set(f"Updated '{title}' on {date.isoformat()}.")
            return True

        if date in self.blocked_dates:
            self.status.set("This date is blocked. Unblock it before adding an assignment.")
            return False

        new_assignment = {"title": title, "time": time_value, "difficulty": self.chosen_difficulty()}
        self.apply_reminder(date, new_assignment, reminder_minutes)
        self.assignments.setdefault(date, []).append(new_assignment)
        self.set_chosen_difficulty("") #Back to None for the next assignment
        self.set_chosen_time(DEFAULT_TIME) #...and back to 11:59 PM
        self.set_chosen_reminder(self.default_reminder) #...and the default reminder
        self.sort_assignments(date)
        self.update_selected_details()
        self.notify_change() #Redraws the calendar so the date's box shows the new assignment
        self.status.set(f"Added '{title}' to {date.isoformat()}.")
        return True

    # SELECT A DATE AND OPEN ITS CONTEXT MENU
    def update_selected_details(self):
        if self.selected_date_label is None or self.assignment_list is None:
            return #attach_details_widgets() hasnt been called yet

        blocked = " - BLOCKED" if self.selected_date in self.blocked_dates else ""

        self.selected_date_label.config(text=f"{self.date_text(self.selected_date)}{blocked}")
        self.assignment_list.delete(0, tk.END)

        items = self.assignments.get(self.selected_date, [])
        for index, assignment in enumerate(items):
            self.assignment_list.insert(tk.END, self.assignment_text(assignment))
            color = difficulty_color(assignment.get("difficulty", ""))
            if color:
                #selectforeground keeps the color when the row is highlighted
                self.assignment_list.itemconfig(index, foreground=color, selectforeground=color)
        if not items:
            self.assignment_list.insert(tk.END, "No assignments today. Enter assignments:")


    def select_date(self, date):
        self.selected_date = date
        self.cancel_edit() #Picking another date stops any edit in progress
        self.update_selected_details()
        if self.assignment_entry is not None:
            self.assignment_entry.focus_set() #Ready to type right after clicking a date
        #Cell restyling (highlight border) is CalendarView part
        #since it owns the frams - on_change triggers that redraw

        # self.notify_change()
        self.notify_select()


    def show_menu(self, event, date):
        self.select_date(date)
        has_assignments = bool(self.assignments.get(date))

        # Indices match the menu entries created in create_gui(); 2 is a separator.
        self.menu.entryconfig(0, state="disabled" if date in self.blocked_dates else "normal")
        self.menu.entryconfig(1, state="normal" if has_assignments else "disabled")
        self.menu.entryconfig(
            3, label="Unblock date" if date in self.blocked_dates else "Block out date"
        )
        self.menu.entryconfig(4, state="normal" if has_assignments else "disabled")
        self.menu.tk_popup(event.x_root, event.y_root)
        return "break"



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
            text = f"{time_to_12h(item['time'])} - {item['title']}" if item["time"] else item["title"]
            self.listbox.insert(tk.END, text)
        self.listbox.selection_set(0)
        return self.listbox

    def validate(self):
        return bool(self.listbox.curselection())

    def apply(self):
        self.result = self.listbox.curselection()[0]


class DifficultyDialog(simpledialog.Dialog):
    """Asks how hard an assignment is. result is "" (none), "easy", "medium" or "hard"; None if cancelled."""

    def __init__(self, parent, date, title):
        self.assignment_title = title
        super().__init__(parent, title=f"Difficulty - {date.isoformat()}")

    def body(self, frame):
        tk.Label(frame, text=f"Difficulty for: {self.assignment_title}", anchor="w").pack(anchor="w", pady=(0, 6))
        self.choice = tk.StringVar(master=frame, value="")
        for label, value in DIFFICULTY_CHOICES:
            tk.Radiobutton(frame, text=label, value=value, variable=self.choice).pack(anchor="w")

    def apply(self):
        self.result = self.choice.get()
