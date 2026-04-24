import tkinter as tk

from config import load_config, save_config, load_translations
from services import check_panel, ping_api

from ui.step1_panel import PanelLoginWindow
from ui.step2_api import ApiLoginWindow
from ui.step3_main import MainWindow


def run():
    root = tk.Tk()
    root.withdraw()
    root.resizable(False, False)

    config = load_config()
    translations = load_translations()

    lang = config.get("language", "en")

    # fallback safety
    if lang not in translations:
        lang = "en"

    texts = translations.get(lang, {})

    if not texts:
        root.destroy()
        raise RuntimeError("Missing translations for language")

    # STEP 1
    if not config.get("panel_token") or not check_panel(config):
        data = PanelLoginWindow(root, texts["step1"]).run()
        if not data:
            return

        config.update(data)
        save_config(config)

    # STEP 2
    if not config.get("api_token") or not ping_api(config):
        data = ApiLoginWindow(root, texts["step2"]).run()
        if not data:
            return

        config.update(data)
        save_config(config)

    # STEP 3
    root.deiconify()
    MainWindow(root, config, texts["step3"])
    root.mainloop()


if __name__ == "__main__":
    run()
