"""Limiter calendar with a right-click menu on every date.

Run: python limiter_calendar.py
Uses only Python's standard library and Tkinter.

Data is kept in memory: changing months preserves it, closing the app clears it.
Edit time changes an assignment's due time, using a 24-hour HH:MM value.
Blocked dates reject new assignments; existing ones can still be managed.
"""

import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox

# The FULL date is the key, so September 5 and October 5 have separate data.
# Example: assignments[datetime.date(2026, 9, 23)] = [
#     {"title": "Finish Python homework", "time": "14:30"}
# ]

#date_buttons = {} #I dont know wat this is for yet

class AssignmentManager:
    def __init__(self, parent, on_change=None):
        
        self.parent = parent #Parent is the main_frame
        self.on_change = on_change

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

    def attach_details_widgets(self, selected_date_label, assignment_list, assignment_entry=None, add_button=None):
        #Point this at the widgets that show the selected
        #date and its assignment list, then do an initial render
        self.selected_date_label = selected_date_label
        self.assignment_list = assignment_list
        self.assignment_entry = assignment_entry
        self.add_button = add_button
        self.update_selected_details()

    def notify_change(self):
        if self.on_change:
            self.on_change()

    def get_assignments(self, date):
        return self.assignments.get(date, [])
    
    def is_blocked(self, date):
        return date in self.blocked_dates

    def date_text(self, date):
        return date.strftime("%A, %B %d, %Y")

    def assignment_text(self, assignment):
        #Only show a time in front of the name when one was set
        if not assignment["time"]:
            return assignment["title"]
        return f"{assignment['time']} - {assignment['title']}"

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

        time_value = self.ask_for_time(date, title)
        if time_value is None:
            return  # Cancelling either dialog leaves the calendar data unchanged.

        self.assignments.setdefault(date, []).append({"title": title, "time": time_value})
        self.status.set(f"Added '{title}' to {date.isoformat()}.")

    def remove_assignment(self):
        date = self.selected_date
        index = self.choose_assignment(date, "Remove assignment")
        if index is None:
            return
        removed = self.assignments[date].pop(index)
        if not self.assignments[date]:
            del self.assignments[date]

        self.status.set(f"Removed '{removed['title']}' from {date.isoformat()}.")

    def block_out(self):
        date = self.selected_date
        if date in self.blocked_dates:
            self.blocked_dates.remove(date)
            message = f"Unblocked {date.isoformat()}."
        else:
            self.blocked_dates.add(date)
            message = f"Blocked {date.isoformat()}. Existing assignments are kept."
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
        self.assignment_entry.focus_set()
        self.status.set("Change the name, then press Enter or Save (Escape to cancel).")

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

        #Editing keeps the assignment's time and only changes its name
        #(allowed on blocked dates too, since existing assignments can still be managed)
        if self.editing_index is not None:
            items = self.assignments.get(date, [])
            if self.editing_index >= len(items):
                self.set_editing(None)
                return False
            items[self.editing_index]["title"] = title
            self.set_editing(None)
            self.update_selected_details()
            self.notify_change()
            self.status.set(f"Updated '{title}' on {date.isoformat()}.")
            return True

        if date in self.blocked_dates:
            self.status.set("This date is blocked. Unblock it before adding an assignment.")
            return False

        self.assignments.setdefault(date, []).append({"title": title, "time": ""})
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
        for assignment in items:
            self.assignment_list.insert(tk.END, self.assignment_text(assignment))
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
        self.notify_change()


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
            self.listbox.insert(tk.END, assignment_text(item))
        self.listbox.selection_set(0)
        return self.listbox

    def validate(self):
        return bool(self.listbox.curselection())

    def apply(self):
        self.result = self.listbox.curselection()[0]
