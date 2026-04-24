import json
import os

CONFIG_PATH = os.path.join("storage", "config.json")
TRANSLATIONS_PATH = os.path.join("storage", "translations.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def load_translations():
    if not os.path.exists(TRANSLATIONS_PATH):
        return {}
    with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data: dict):
    os.makedirs("storage", exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
