"""Build Limiter on Windows: py build_app.py

Install build dependencies first:
    py -m pip install -r requirements.txt pyinstaller
This developer utility runs separately from the normal main.py GUI.
"""

from pathlib import Path
import subprocess
import sys


class AppBuilder:
    def __init__(self, project_dir=None):
        self.project_dir = Path(project_dir) if project_dir else Path(__file__).resolve().parent

    def build(self, console=False):
        """Create dist/Limiter.exe using the same Python running this script."""
        if sys.platform != "win32":
            raise RuntimeError("Build the Windows executable on Windows.")
        required = (
            "main.py", "app_storage.py", "assignment_picker.py", "calendar_view.py",
            "dashboard_view.py", "settings.py", "sidebar_view.py", "blocker.py", "assets/icon.png",
        )
        missing = [name for name in required if not (self.project_dir / name).is_file()]
        if missing:
            raise FileNotFoundError("Copy these project files into this folder first: " + ", ".join(missing))
        try:
            import PyInstaller  # noqa: F401 - fail clearly before starting the build
            import psutil  # noqa: F401
        except ImportError as error:
            raise RuntimeError("Install dependencies with: py -m pip install -r requirements.txt pyinstaller") from error
        command = [
            sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "--onefile",
            "--name", "Limiter", "--add-data", "assets:assets",
        ]
        if not console:
            command.append("--windowed")
        # Project preferences are initial defaults; progress stays outside the executable.
        if (self.project_dir / "settings.json").is_file():
            command.extend(["--add-data", "settings.json:."])
        if (self.project_dir / "assets" / "icon.ico").is_file():
            command.extend(["--icon", "assets/icon.ico"])
        command.append("main.py")
        subprocess.run(command, cwd=self.project_dir, check=True)
        return self.project_dir / "dist" / "Limiter.exe"


if __name__ == "__main__":
    try:
        executable = AppBuilder().build(console="--console" in sys.argv[1:])
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Built: {executable}")
    print("Double-click Limiter.exe to launch without VS Code.")
