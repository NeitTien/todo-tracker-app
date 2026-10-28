"""Local storage for Limiter's calendar, preferences, and blocker lists."""

import calendar
import copy
import datetime
import json
import os
from pathlib import Path
import sys
import tempfile


class AppStorage:
    def __init__(self, base_dir, data_file=None):
        self.base_dir = Path(base_dir)
        if data_file is None:
            # Use a stable user folder, independent of the launch directory.
            if sys.platform == "win32":
                base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
            elif sys.platform == "darwin":
                base = Path.home() / "Library" / "Application Support"
            else:
                base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
            data_file = base / "Limiter" / "progress.json"
        self.data_file = Path(data_file)
        self._settings = {"default_view": "calendar"}
        self._app = None
        self._loaded = False

    def load_data(self, app):
        """Restore progress after main.py has created the existing views.

        Missing saves are normal on first use. Invalid or unreadable saves
        raise an error so startup cannot overwrite them with an empty state.
        """
        self._loaded = False
        self._app = None
        try:
            text = self.data_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            self._settings = self._legacy_settings()
            self._app = app
            self._loaded = True
            return False

        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError("The saved progress file is not valid JSON.") from error

        legacy = self._legacy_settings() if isinstance(data, dict) and data.get("version") == 1 else None
        state = self._decode_data(data, legacy, app.blocker)

        # Apply only after the complete file has passed validation.
        manager = app.calendar.assignment_manager
        manager.assignments.clear()
        manager.assignments.update(state["assignments"])
        manager.blocked_dates.clear()
        manager.blocked_dates.update(state["blocked_dates"])
        manager.selected_date = state["selected_date"]
        app.calendar.current_year = state["current_year"]
        app.calendar.current_month = state["current_month"]
        app.blocker.blocked_sites[:] = state["blocked_sites"]
        app.blocker.blocked_apps[:] = state["blocked_apps"]
        self._settings = state["settings"]
        self._app = app

        app.calendar.update_year_label()
        app.calendar.update_month_label()
        app.calendar.update_calendar_day()
        manager.update_selected_details()
        app.blocker.refresh_site_listbox()
        app.blocker.refresh_app_listbox()
        # Blocker starts OFF as before. Loading lists never edits hosts or
        # starts process blocking; the existing toggle button controls that.
        self._loaded = True
        return True

    def save_data(self, app):
        """Save current state after a change and before closing the app."""
        if not self._loaded:
            raise ValueError("Progress must load successfully before it can be saved.")
        manager = app.calendar.assignment_manager
        data = {
            "version": 2,
            "assignments": {date.isoformat(): items for date, items in manager.assignments.items()},
            "blocked_dates": sorted(date.isoformat() for date in manager.blocked_dates),
            "selected_date": manager.selected_date.isoformat(),
            "current_year": app.calendar.current_year,
            "current_month": app.calendar.current_month,
            "settings": self._settings,
            "blocked_sites": list(app.blocker.blocked_sites),
            "blocked_apps": list(app.blocker.blocked_apps),
        }
        self._decode_data(data)
        text = json.dumps(data, indent=4, ensure_ascii=False, allow_nan=False)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = None
        try:
            # Finish and close a temporary file before replacing the old save.
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.data_file.parent,
                prefix=self.data_file.name + ".", suffix=".tmp", delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(text)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, self.data_file)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def load_settings(self):
        """Keep Settings' existing interface; return a copy for editing."""
        return copy.deepcopy(self._settings)

    def save_settings(self, settings):
        """Save the Settings dialog without discarding other app progress."""
        self._check_settings(settings)
        previous = self._settings
        self._settings = copy.deepcopy(settings)
        try:
            self.save_data(self._app)
        except (OSError, ValueError, TypeError):
            self._settings = previous
            raise

    def _legacy_settings(self):
        # Import the existing preference file on first use, or when upgrading
        # an earlier calendar-only save. Later launches read the user save.
        path = self.base_dir / "def_settings.json"
        if not path.exists():
            path = self.base_dir / "settings.json"
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            settings = {"default_view": "calendar"}
        self._check_settings(settings)
        return settings

    @staticmethod
    def _check_settings(settings):
        if not isinstance(settings, dict):
            raise ValueError("Saved settings must be a JSON object.")
        if settings.get("default_view", "calendar") not in ("calendar", "dashboard"):
            raise ValueError("The default view must be calendar or dashboard.")
        if "dark_mode" in settings and type(settings["dark_mode"]) is not bool:
            raise ValueError("The dark_mode preference must be true or false.")

    @staticmethod
    def _decode_data(data, legacy_settings=None, blocker=None):
        """Check all fields and rebuild date keys and the blocked-date set."""
        if not isinstance(data, dict) or type(data.get("version")) is not int:
            raise ValueError("The saved progress format is not supported.")
        version = data["version"]
        if version not in (1, 2):
            raise ValueError("The saved progress version is not supported.")

        year, month = data.get("current_year"), data.get("current_month")
        if type(year) is not int or type(month) is not int:
            raise ValueError("The saved year and month must be whole numbers.")
        if not 1 <= year <= 9999 or not 1 <= month <= 12:
            raise ValueError("The saved year or month is out of range.")
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

        selected_date = read_date(data.get("selected_date"))
        raw_assignments = data.get("assignments")
        raw_blocks = data.get("blocked_dates")
        if not isinstance(raw_assignments, dict) or not isinstance(raw_blocks, list):
            raise ValueError("The saved assignments or blocked dates have an invalid format.")
        assignments = {}
        for key, items in raw_assignments.items():
            date = read_date(key)
            if not isinstance(items, list):
                raise ValueError("Each date's assignments must be a list.")
            for item in items:
                if not isinstance(item, dict):
                    raise ValueError("Each saved assignment must be an object.")
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
            assignments[date] = items

        if version == 1:
            settings = data.get("settings", legacy_settings or {"default_view": "calendar"})
            sites = data.get("blocked_sites", list(blocker.blocked_sites) if blocker else [])
            apps = data.get("blocked_apps", list(blocker.blocked_apps) if blocker else [])
        else:
            settings, sites, apps = data.get("settings"), data.get("blocked_sites"), data.get("blocked_apps")
        AppStorage._check_settings(settings)
        for values in (sites, apps):
            if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError("Blocker lists must contain nonempty text entries.")

        return {
            "assignments": assignments,
            "blocked_dates": {read_date(value) for value in raw_blocks},
            "selected_date": selected_date,
            "current_year": year,
            "current_month": month,
            "settings": settings,
            "blocked_sites": sites,
            "blocked_apps": apps,
        }
