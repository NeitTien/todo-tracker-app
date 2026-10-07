import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox
try:
    import psutil #** BLOCKER: pip install psutil
except ImportError:
    psutil = None #** BLOCKER: app still opens without psutil, the button just warns

#** ================= BLOCKER FEATURE (whole file) ================= **
#This class blocks websites (by editing the hosts file) and apps (by closing them)
class Blocker:
    HOSTS_MARK_START = "# blocker START"
    HOSTS_MARK_END = "# blocker END"

    def __init__(self, parent):
        self.parent = parent #Parent is the App window

        #** these two lists are what is blocked at startup (both can also be edited in the sidebar)
        self.blocked_sites = ["youtube.com", "discord.com"]
        self.blocked_apps = ["Discord"]

        self.blocking_active = False
        self.check_job = None #Id of the scheduled app check, so it can be cancelled

        #This makes sure the hosts file is cleaned up if the window is closed while blocking
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self, sidebar_frame):
        #Blocker on/off button, placed under the Settings button
        self.button_blocker = tk.Button(
            sidebar_frame,
            text="Blocker: OFF",
            font=("Arial", 12),
            command=self.toggle_blocker
        )
        self.button_blocker.grid(row=3, column=0)

        #Remember the normal button colors so OFF can restore them
        self.default_bg = self.button_blocker.cget("background")
        self.default_fg = self.button_blocker.cget("foreground")

        #Small frame to add/remove blocked websites without touching code
        self.sites_frame = tk.Frame(sidebar_frame)
        self.sites_frame.grid(row=4, column=0, pady=(10, 0))

        tk.Label(self.sites_frame, text="Blocked Sites", font=("Arial", 10)).pack()

        self.site_listbox = tk.Listbox(self.sites_frame, height=3, width=16)
        self.site_listbox.pack()

        self.site_entry = tk.Entry(self.sites_frame, width=16)
        self.site_entry.pack(pady=(5, 0))

        tk.Button(self.sites_frame, text="Add Site", command=self.add_site).pack(pady=(5, 0))
        tk.Button(self.sites_frame, text="Remove Selected", command=self.remove_site).pack(pady=(2, 0))

        self.refresh_site_listbox()

        #Small frame to add/remove blocked apps without touching code
        self.apps_frame = tk.Frame(sidebar_frame)
        self.apps_frame.grid(row=5, column=0, pady=(10, 10))

        tk.Label(self.apps_frame, text="Blocked Apps", font=("Arial", 10)).pack()

        self.app_listbox = tk.Listbox(self.apps_frame, height=4, width=16)
        self.app_listbox.pack()

        self.app_entry = tk.Entry(self.apps_frame, width=16)
        self.app_entry.pack(pady=(5, 0))

        tk.Button(self.apps_frame, text="Add App", command=self.add_app).pack(pady=(5, 0))
        tk.Button(self.apps_frame, text="Remove Selected", command=self.remove_app).pack(pady=(2, 0))

        self.refresh_app_listbox()

    #HOSTS FILE (websites)
    #This returns the hosts file path for the current OS
    def get_hosts_path(self):
        if platform.system() == "Windows":
            return os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
        return "/etc/hosts"

    #This clears the DNS cache so a hosts-file change is felt right away
    def flush_dns(self):
        try:
            if platform.system() == "Windows":
                subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            elif platform.system() == "Darwin":
                subprocess.run(["dscacheutil", "-flushcache"], capture_output=True)
                subprocess.run(["killall", "-HUP", "mDNSResponder"], capture_output=True)
        except Exception:
            pass

    #This cuts our marked block (if there is one) out of the hosts file text
    def strip_block(self, text):
        if self.HOSTS_MARK_START in text and self.HOSTS_MARK_END in text:
            start = text.index(self.HOSTS_MARK_START)
            end = text.index(self.HOSTS_MARK_END) + len(self.HOSTS_MARK_END)
            text = text[:start] + text[end:]
        return text

    #This redirects every site in blocked_sites to this computer (IPv4 and IPv6), which makes them unreachable
    def block_sites(self):
        path = self.get_hosts_path()
        with open(path, "r") as f:
            text = self.strip_block(f.read()) #Remove the old block first so blocks never pile up

        lines = [self.HOSTS_MARK_START]
        for site in self.blocked_sites:
            for name in (site, f"www.{site}"):
                lines.append(f"127.0.0.1 {name}")
                lines.append(f"::1 {name}") #Without this a browser can still reach the site over IPv6
        lines.append(self.HOSTS_MARK_END)

        with open(path, "w") as f:
            f.write(text.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n")
        self.flush_dns()

    #This removes the block added by block_sites(), restoring normal access
    def unblock_sites(self):
        path = self.get_hosts_path()
        with open(path, "r") as f:
            text = f.read()

        if self.HOSTS_MARK_START in text and self.HOSTS_MARK_END in text:
            with open(path, "w") as f:
                f.write(self.strip_block(text))
        self.flush_dns()

    #RUNNING PROCESSES (apps)
    #This closes anything running that matches blocked_apps,
    #then reschedules itself every 2 seconds for as long as blocking is active
    def check_blocked_apps(self):
        if not self.blocking_active:
            return
        names = [a.lower() for a in self.blocked_apps]
        for proc in psutil.process_iter(["name"]):
            try:
                pname = (proc.info["name"] or "").lower()
                if any(n in pname for n in names):
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.check_job = self.parent.after(2000, self.check_blocked_apps)

    #WEBSITE LIST
    #This turns what was typed (like https://www.TikTok.com/foo) into a plain domain (tiktok.com)
    def clean_site(self, text):
        site = text.strip().lower()
        for prefix in ("https://", "http://"):
            if site.startswith(prefix):
                site = site[len(prefix):]
        site = site.split("/")[0]
        if site.startswith("www."):
            site = site[4:]
        return site

    #This keeps the site listbox in sync with blocked_sites
    def refresh_site_listbox(self):
        self.site_listbox.delete(0, tk.END)
        for site in self.blocked_sites:
            self.site_listbox.insert(tk.END, site)

    #If blocking is already on, rewrite the hosts file so a change applies right away
    def reapply_sites(self):
        if self.blocking_active:
            try:
                self.block_sites()
            except PermissionError:
                pass

    #This adds whatever is typed in the site entry box to blocked_sites
    def add_site(self):
        site = self.clean_site(self.site_entry.get())
        if site and site not in self.blocked_sites:
            self.blocked_sites.append(site)
            self.refresh_site_listbox()
            self.reapply_sites()
        self.site_entry.delete(0, tk.END)

    #This removes the site selected in the listbox from blocked_sites
    def remove_site(self):
        selection = self.site_listbox.curselection()
        if selection:
            self.blocked_sites.pop(selection[0])
            self.refresh_site_listbox()
            self.reapply_sites()

    #APP LIST
    #This keeps the listbox in sync with blocked_apps
    def refresh_app_listbox(self):
        self.app_listbox.delete(0, tk.END)
        for app in self.blocked_apps:
            self.app_listbox.insert(tk.END, app)

    #This adds whatever is typed in the entry box to blocked_apps
    def add_app(self):
        name = self.app_entry.get().strip()
        if name and name.lower() not in [a.lower() for a in self.blocked_apps]:
            self.blocked_apps.append(name)
            self.refresh_app_listbox()
        self.app_entry.delete(0, tk.END)

    #This removes the app selected in the listbox from blocked_apps
    def remove_app(self):
        selection = self.app_listbox.curselection()
        if selection:
            self.blocked_apps.pop(selection[0])
            self.refresh_app_listbox()

    #This is the Blocker button's command: flips blocking on/off and updates the button
    def toggle_blocker(self):
        #Stop early if psutil is not installed, so the app does not crash
        if psutil is None:
            pip_cmd = "py -m pip" if platform.system() == "Windows" else "python3 -m pip"
            messagebox.showwarning(
                "Blocker",
                f"The Blocker needs psutil. Run: {pip_cmd} install -r requirements.txt"
            )
            return

        self.blocking_active = not self.blocking_active

        if self.blocking_active:
            try:
                self.block_sites()
            except PermissionError:
                if platform.system() == "Windows":
                    admin_hint = "as Administrator (right-click your terminal > Run as administrator)"
                else:
                    admin_hint = "with sudo"
                messagebox.showwarning(
                    "Blocker",
                    "Could not edit the hosts file (needs admin rights), so only "
                    f"app blocking is active. Quit and reopen this app {admin_hint} "
                    "to also block sites."
                )
            self.check_blocked_apps()
            self.button_blocker.config(text="Blocker: ON", background="#FFCCCC", foreground="#8B0000")
        else:
            if self.check_job:
                self.parent.after_cancel(self.check_job)
                self.check_job = None
            try:
                self.unblock_sites()
            except PermissionError:
                pass
            self.button_blocker.config(text="Blocker: OFF", background=self.default_bg, foreground=self.default_fg)

    #This runs when the window is closed: undo the hosts-file block, then quit
    def on_close(self):
        if self.blocking_active:
            try:
                self.unblock_sites()
            except PermissionError:
                pass
        self.parent.destroy()
#** ================= END BLOCKER FEATURE ================= **
