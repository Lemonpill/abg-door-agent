import tkinter as tk
from services import api_login


class ApiLoginWindow:
    def __init__(self, root, texts):
        self.root = tk.Toplevel(root)
        self.texts = texts
        self.root.title(self.texts["title"])
        self.root.geometry("320x320")
        self.root.resizable(False, False)

        self.result = None

        # Title
        tk.Label(self.root, text=self.texts["title"], font=("Arial", 12, "bold")).pack(pady=(10, 5))

        # Description
        tk.Label(self.root, text=self.texts["description"], wraplength=280, justify="center").pack(pady=(0, 10))

        # Form
        tk.Label(self.root, text=self.texts["form"]["url_label"]).pack(anchor="w", padx=10)
        self.url = tk.Entry(self.root)
        self.url.pack(fill="x", padx=10)

        tk.Label(self.root, text=self.texts["form"]["username_label"]).pack(anchor="w", padx=10)
        self.user = tk.Entry(self.root)
        self.user.pack(fill="x", padx=10)

        tk.Label(self.root, text=self.texts["form"]["password_label"]).pack(anchor="w", padx=10)
        self.pw = tk.Entry(self.root, show="*")
        self.pw.pack(fill="x", padx=10)

        tk.Label(self.root, text=self.texts["form"]["station_label"]).pack(anchor="w", padx=10)
        self.station = tk.Entry(self.root)
        self.station.pack(fill="x", padx=10)

        # Error
        self.error = tk.Label(self.root, fg="red")
        self.error.pack(pady=5)

        # Submit
        tk.Button(self.root, text=self.texts["form"]["submit_label"], command=self.submit).pack(pady=5)

    def submit(self):
        token = api_login(
            self.url.get().strip(),
            self.user.get().strip(),
            self.pw.get().strip(),
        )
        if token:
            self.result = {
                "api_url": self.url.get().strip(),
                "api_token": token,
                "station": self.station.get().strip(),
            }
            self.root.destroy()
        else:
            self.error.config(text=self.texts["error"])

    def run(self):
        self.root.grab_set()
        self.root.wait_window()
        return self.result
