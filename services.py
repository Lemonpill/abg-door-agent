import json
import requests
import base64

TIMEOUT = 5


# ---- PANEL ----


def build_basic_auth(username: str, password: str) -> str:
    raw = f"{username}:{password}".encode("utf-8")
    encoded = base64.b64encode(raw).decode("utf-8")
    return f"Basic {encoded}"


def panel_login(url, username, password):
    try:
        auth = build_basic_auth(username, password)

        r = requests.get(
            f"{url}/GEvent.xml",
            headers={"Authorization": auth},
            timeout=TIMEOUT,
        )

        if r.status_code == 200:
            return auth  # store FULL header value
    except:
        pass
    return None


def check_panel(config):
    try:
        r = requests.get(
            f"{config['panel_url']}/GEvent.xml",
            headers={"Authorization": config["panel_token"]},
            timeout=TIMEOUT,
        )
        return r.status_code == 200
    except:
        return False


# ---- API ----


def api_login(url, username, password):
    try:
        r = requests.post(
            f"{url}/api/token/",
            json={"username": username, "password": password},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("token")
    except:
        pass
    return None


def ping_api(config):
    try:
        r = requests.get(
            f"{config['api_url']}/api/kiosk/ping",
            headers={"Authorization": f"Token {config['api_token']}"},
            timeout=TIMEOUT,
        )
        return 200 <= r.status_code < 300
    except:
        return False


# ---- DOOR ----


def validate_card(config, card, reader):
    try:
        r = requests.post(
            f"{config['api_url']}/api/opendoor",
            json={
                "magnetic_card": card,
                "reader": reader,
                "station": config["station"],
            },
            headers={"Authorization": f"Token {config['api_token']}"},
            timeout=TIMEOUT,
        )
        return r.status_code in [200, 201]
    except:
        return False


def open_door(config):
    try:
        requests.get(
            f"{config['panel_url']}/cdor.cgi",
            params={"open": 1, "door": 0},
            headers={"Authorization": config["panel_token"]},
            timeout=TIMEOUT,
        )
    except:
        pass


def fetch_event(config, last_id):
    try:
        r = requests.get(
            f"{config['panel_url']}/GEvent.xml",
            params={"ID": last_id},
            headers={"Authorization": config["panel_token"]},
            timeout=TIMEOUT,
        )
        text = r.text
        if "#GLEvent" not in text:
            return None, last_id

        json_str = text.split("-->")[1].split("</response")[0].strip()
        event = json.loads(json_str)

        new_id = int(event.get("ID", last_id))
        if new_id == last_id:
            return None, last_id

        return event, new_id
    except:
        return None, last_id


# ---- ACS ----


def validate_acs_event(config: dict, event: dict) -> dict:
    res_code = None
    try:
        gate = config["station"]
        r = requests.post(
            f"{config['api_url']}/api/acs/smartgates/{gate}/events",
            json=event,
            headers={"Authorization": f"Token {config['api_token']}"},
            timeout=TIMEOUT,
        )
        res_code = r.status_code
        return r.json()
    except:
        return {"allow": False, "error": f"Response code {res_code}"}


def validate_event_card(event: dict):
    card = event.get("Card", None)
    return card and card != "-"


def validate_event_reader(event: dict):
    reader = event.get("Reader", None)
    return reader in ("IN", "OUT")
