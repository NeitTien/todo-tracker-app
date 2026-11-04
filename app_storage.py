"""Save Limiter progress without changing its existing view classes."""

import calendar
import copy
import datetime
import json
import os
from pathlib import Path
import sys
import tempfile


class AppStorage:
    """main.py calls load_data() at startup and save_data() after changes."""

    FIELDS = {
        "version", "assignments", "blocked_dates", "selected_date",
        "current_year", "current_month", "settings", "blocked_sites", "blocked_apps",
    }

    def __init__(self, base_dir, data_file=None):
        self.base_dir = Path(base_dir)
        if data_file is None:
            if sys.platform == "win32":
                folder = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
            elif sys.platform == "darwin":
                folder = Path.home() / "Library" / "Application Support"
            else:
                folder = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
            data_file = folder / "Limiter" / "progress.json"
        self.data_file = Path(data_file)
        self._settings = {"default_view": "calendar"}
        self._blocker_lists = {"blocked_sites": [], "blocked_apps": []}
        self._extra_fields = {}
        self._app = None
        self._loaded = False
        self._last_saved = None

    def load_data(self, app):
        """Load only after all the original views have been created.

        A missing file is normal on first use. An invalid file raises an error
        and disables saving, so existing progress cannot be replaced by defaults.
        """
        self._loaded = False
        self._app = None
        self._last_saved = None
        try:
            data = json.loads(self.data_file.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self._settings = self._initial_settings()
            self._blocker_lists = self._current_blocker_lists(app)
            self._extra_fields = {}
            self._app, self._loaded = app, True
            return False
        except json.JSONDecodeError as error:
            raise ValueError("The saved progress file is not valid JSON.") from error

        # Version 1 was the earlier calendar-only storage format.
        if isinstance(data, dict) and data.get("version") == 1:
            data = dict(data)
            if "settings" not in data:
                data["settings"] = self._initial_settings()
            for name, values in self._current_blocker_lists(app).items():
                data.setdefault(name, values)
        state = self._decode_data(data)

        # Validate the entire document BEFORE changing the running app.
        manager = app.calendar.assignment_manager
        manager.assignments.clear()
        manager.assignments.update(state["assignments"])
        manager.blocked_dates.clear()
        manager.blocked_dates.update(state["blocked_dates"])
        manager.selected_date = state["selected_date"]
        app.calendar.current_year = state["current_year"]
        app.calendar.current_month = state["current_month"]
        self._settings = state["settings"]
        self._blocker_lists = {name: state[name] for name in self._blocker_lists}
        self._extra_fields = {key: value for key, value in data.items() if key not in self.FIELDS}

        # Optional compatibility with the earlier Blocker interface. Do not
        # activate blocking or call any hosts-file/process-blocking functions.
        blocker = getattr(app, "blocker", None)
        for name, refresh_name in (
            ("blocked_sites", "refresh_site_listbox"),
            ("blocked_apps", "refresh_app_listbox"),
        ):
            values = getattr(blocker, name, None)
            if isinstance(values, list):
                values[:] = self._blocker_lists[name]
                refresh = getattr(blocker, refresh_name, None)
                if callable(refresh):
                    refresh()

        app.calendar.update_year_label()
        app.calendar.update_month_label()
        app.calendar.update_calendar_day()
        manager.update_selected_details()
        app.dashboard.refresh_dashboard()
        self._app, self._loaded = app, True
        return True

    def save_data(self, app):
        """Save a complete snapshot; skip disk writes when nothing changed."""
        if not self._loaded:
            raise ValueError("Progress must load successfully before it can be saved.")
        manager = app.calendar.assignment_manager
        data = dict(self._extra_fields)
        data.update({
            "version": 2,
            # Keep each entire assignment, including difficulty and future fields.
            "assignments": {date.isoformat(): items for date, items in manager.assignments.items()},
            "blocked_dates": sorted(date.isoformat() for date in manager.blocked_dates),
            "selected_date": manager.selected_date.isoformat(),
            "current_year": app.calendar.current_year,
            "current_month": app.calendar.current_month,
            "settings": self._settings,
            **self._current_blocker_lists(app),
        })
        self._decode_data(data)
        text = json.dumps(data, indent=4, ensure_ascii=False, allow_nan=False)
        if text == self._last_saved:
            return False
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            # Write and close a file beside the save, then replace the old file.
            # An interrupted/failed write therefore leaves the previous save intact.
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.data_file.parent,
                prefix=self.data_file.name + ".", suffix=".tmp", delete=False,
            ) as output:
                temporary_path = Path(output.name)
                output.write(text)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary_path, self.data_file)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        self._last_saved = text
        return True

    def load_settings(self):
        """Keep the existing Settings interface; return a separate editable copy."""
        return copy.deepcopy(self._settings)

    def save_settings(self, settings):
        self._check_settings(settings)
        previous = self._settings
        self._settings = copy.deepcopy(settings)
        try:
            self.save_data(self._app)
        except (OSError, ValueError, TypeError):
            self._settings = previous
            raise

    def _initial_settings(self):
        # Read project preferences once. Later launches use progress.json.
        path = self.base_dir / "def_settings.json"
        if not path.exists():
            path = self.base_dir / "settings.json"
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            settings = {"default_view": "calendar"}
        self._check_settings(settings)
        return settings

    def _current_blocker_lists(self, app):
        blocker = getattr(app, "blocker", None)
        result = {}
        for name, saved_values in self._blocker_lists.items():
            values = getattr(blocker, name, None)
            # If another Blocker implementation uses different attributes, keep
            # any previously saved lists rather than erasing them.
            result[name] = list(values) if isinstance(values, list) else list(saved_values)
        return result

    @staticmethod
    def _check_settings(settings):
        if not isinstance(settings, dict):
            raise ValueError("Saved settings must be a JSON object.")
        if settings.get("default_view", "calendar") not in ("calendar", "dashboard"):
            raise ValueError("The default view must be calendar or dashboard.")

    @staticmethod
    def _decode_data(data):
        if not isinstance(data, dict) or type(data.get("version")) is not int:
            raise ValueError("The saved progress format is not supported.")
        if data["version"] not in (1, 2):
            raise ValueError("The saved progress version is not supported.")
        year, month = data.get("current_year"), data.get("current_month")
        if type(year) is not int or type(month) is not int or not (1 <= year <= 9999 and 1 <= month <= 12):
            raise ValueError("The saved year or month is invalid.")
        try:
            calendar.Calendar().monthdatescalendar(year, month)
        except (ValueError, OverflowError) as error:
            raise ValueError("The saved month cannot be displayed.") from error

        def read_date(value):
            if not isinstance(value, str):
                raise ValueError("Saved dates must use YYYY-MM-DD text.")
            try:
                date = datetime.date.fromisoformat(value)
            except ValueError as error:
                raise ValueError(f"Invalid saved date: {value!r}.") from error
            if date.isoformat() != value:
                raise ValueError("Saved dates must use YYYY-MM-DD text.")
            return date

        raw_assignments, raw_blocks = data.get("assignments"), data.get("blocked_dates")
        if not isinstance(raw_assignments, dict) or not isinstance(raw_blocks, list):
            raise ValueError("Saved assignments or blocked dates have an invalid format.")
        assignments = {}
        for key, items in raw_assignments.items():
            date = read_date(key)
            if not isinstance(items, list):
                raise ValueError("Each date's assignments must be a list.")
            for item in items:
                if not isinstance(item, dict):
                    raise ValueError("Each assignment must be an object.")
                title, time = item.get("title"), item.get("time")
                if not isinstance(title, str) or not title.strip() or not isinstance(time, str):
                    raise ValueError("Each assignment needs a name and a text time.")
                if time:
                    try:
                        parsed = datetime.datetime.strptime(time, "%H:%M")
                    except ValueError as error:
                        raise ValueError("Assignment times must use 24-hour HH:MM.") from error
                    if parsed.strftime("%H:%M") != time:
                        raise ValueError("Assignment times must use 24-hour HH:MM.")
                if item.get("difficulty", "") not in ("", "easy", "medium", "hard"):
                    raise ValueError("An assignment has an invalid difficulty.")
            assignments[date] = items
        settings = data.get("settings")
        AppStorage._check_settings(settings)
        lists = {name: data.get(name) for name in ("blocked_sites", "blocked_apps")}
        for values in lists.values():
            if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError("Blocker lists must contain nonempty text entries.")
        return {
            "assignments": assignments,
            "blocked_dates": {read_date(value) for value in raw_blocks},
            "selected_date": read_date(data.get("selected_date")),
            "current_year": year, "current_month": month, "settings": settings, **lists,
        }
