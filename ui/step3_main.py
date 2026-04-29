import os
import tkinter as tk
import threading
import time
from datetime import datetime
from config import CONFIG_PATH
from services import (
    ping_api,
    fetch_event,
    validate_card,
    open_door,
    validate_acs_event,
    validate_event_reader,
    validate_event_card,
)


def is_night():
    now = datetime.now().hour
    return now >= 22 or now < 8


class MainWindow:
    def __init__(self, root, config, texts):
        self.root = root
        self.config = config
        self.texts = texts

        self.server_ok = False
        self.panel_ok = False
        self.last_event_id = 0
        self.last_panel_ok = time.time()

        self.build_ui()
        self.start_threads()
        self.update_time()

    def logout(self):
        # delete config file
        try:
            if os.path.exists(CONFIG_PATH):
                os.remove(CONFIG_PATH)
        except:
            pass

        # restart app cleanly
        self.root.destroy()

    def build_ui(self):
        self.root.title(self.texts["title"])
        self.root.geometry("320x320")
        self.root.resizable(False, False)

        # Title
        tk.Label(self.root, text=self.texts["title"], font=("Arial", 12, "bold")).pack(pady=5)

        # Description
        tk.Label(self.root, text=self.texts["description"], wraplength=280, justify="center").pack(pady=(0, 10))

        # Status row
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text=f"{self.texts["api_label"]}: ").pack(side=tk.LEFT)
        self.server_dot = tk.Canvas(frame, width=15, height=15)
        self.server_dot.pack(side=tk.LEFT, padx=5)

        tk.Label(frame, text=f"{self.texts["panel_label"]}: ").pack(side=tk.LEFT)
        self.panel_dot = tk.Canvas(frame, width=15, height=15)
        self.panel_dot.pack(side=tk.LEFT, padx=5)

        # Station label
        tk.Label(self.root, text=f"{self.texts["station_label"]}: {self.config.get('station', "")}").pack(pady=5)

        # Time
        self.time = tk.Label(self.root, font=("Arial", 11))
        self.time.pack(pady=5)

        # Logout button
        tk.Button(self.root, text=self.texts["logout_label"], command=self.logout).pack(pady=10)

        # Error
        self.error = tk.Label(self.root, fg="red")
        self.error.pack(pady=5)

    def draw(self):
        self.server_dot.delete("all")
        self.panel_dot.delete("all")

        self.server_dot.create_oval(2, 2, 12, 12, fill="green" if self.server_ok else "red")
        self.panel_dot.create_oval(2, 2, 12, 12, fill="green" if self.panel_ok else "red")

    def update_time(self):
        now = datetime.now()
        self.time.config(text=now.strftime("%H:%M:%S"), fg="red" if is_night() else "black")
        self.root.after(1000, self.update_time)

    def ping_loop(self):
        while True:
            self.server_ok = ping_api(self.config)
            self.root.after(0, self.draw)
            time.sleep(3)

    def event_loop(self):
        while True:
            event, new_id = fetch_event(self.config, self.last_event_id)

            # -----------------------------
            # 1. PANEL HEALTH SIGNAL
            # -----------------------------
            if new_id is not None:
                self.panel_ok = True
                self.last_panel_ok = time.time()

            is_new_event = event and new_id != self.last_event_id

            # update last seen always (for polling cursor)
            if new_id is not None:
                self.last_event_id = new_id

            # -----------------------------
            # 2. ONLY PROCESS NEW EVENTS
            # -----------------------------
            if is_new_event:
                reader_valid = validate_event_reader(event)
                card_valid = validate_event_card(event)

                if card_valid and reader_valid:
                    reader = event.get("Reader")

                    if not self.server_ok:
                        if reader == "OUT":
                            open_door(self.config)
                    else:
                        data = validate_acs_event(self.config, event)

                        if reader == "OUT":
                            open_door(self.config)
                        elif data:
                            nighttime = is_night()
                            api_allow = data.get("allow")
                            api_error = data.get("error")

                            if api_allow and not nighttime:
                                open_door(self.config)

                            self.error.config(text=api_error)
                        else:
                            self.error.config(text=self.texts["error"])
            # -----------------------------
            # 3. PANEL DOWN DETECTION
            # -----------------------------
            else:
                if time.time() - self.last_panel_ok > 5:
                    self.panel_ok = False

            self.root.after(0, self.draw)
            time.sleep(0.5)

    def start_threads(self):
        threading.Thread(target=self.ping_loop, daemon=True).start()
        threading.Thread(target=self.event_loop, daemon=True).start()
