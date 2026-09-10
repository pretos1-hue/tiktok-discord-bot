#!/usr/bin/env python3
"""
Prueft ein TikTok-Profil auf ein neues Video und postet es per Webhook nach Discord.
Der Status (zuletzt geposteter Video-ID) wird in last_tiktok_id.txt gespeichert
und vom GitHub-Actions-Workflow zurueck ins Repo committet.
"""

import json
import os
import re
import sys

import requests

# --- Konfiguration -----------------------------------------------------

TIKTOK_USERNAME = os.environ.get("TIKTOK_USERNAME", "pretos_real")  # ohne @
STATE_FILE = "last_tiktok_id.txt"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# --- Hilfsfunktionen -----------------------------------------------------


def find_item_list(node):
    """Sucht rekursiv nach dem ersten 'itemList' im TikTok-Datenblock.
    TikTok aendert die genaue Struktur gelegentlich, daher robust statt
    ueber einen festen Pfad."""
    if isinstance(node, dict):
        if "itemList" in node and isinstance(node["itemList"], list) and node["itemList"]:
            return node["itemList"]
        for value in node.values():
            result = find_item_list(value)
            if result:
                return result
    elif isinstance(node, list):
        for value in node:
            result = find_item_list(value)
            if result:
                return result
    return None


def get_latest_video():
    session = requests.Session()
    session.headers.update(HEADERS)

    # Erst die Startseite laden, damit TikTok Cookies setzt (msToken,
    # tt_webid_v2 etc.) - ohne die liefert TikTok Cloud-Servern oft nur
    # eine leere Huelle ohne Videodaten aus.
    session.get("https://www.tiktok.com/", timeout=20)

    url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    html = resp.text

    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError(
            "Konnte den Datenblock auf der TikTok-Seite nicht finden. "
            "TikTok hat vermutlich das Seitenlayout geaendert oder die "
            "Anfrage wurde blockiert."
        )

    data = json.loads(match.group(1))
    item_list = find_item_list(data)
    if not item_list:
        raise RuntimeError(
            "Keine Videos im Profil-Datenblock gefunden. TikTok liefert "
            "Cloud-Servern (z.B. GitHub Actions) manchmal eine abgespeckte "
            "Seite ohne Videodaten aus - kein Problem mit dem Profil selbst."
        )

    latest = item_list[0]
    video_id = str(latest["id"])
    desc = latest.get("desc", "").strip() or "(ohne Beschreibung)"
    video_url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/{video_id}"
    return video_id, desc, video_url


def load_last_id():
    if os.path.exists(STATE_FILE):
        return open(STATE_FILE, encoding="utf-8").read().strip()
    return None


def save_last_id(video_id):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(video_id)


def post_to_discord(desc, video_url):
    payload = {
        "username": "TikTok-Bot",
        "content": f"🎬 Neues TikTok-Video von @{TIKTOK_USERNAME}!\n{desc}\n{video_url}",
    }
    r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    r.raise_for_status()


def main():
    if not DISCORD_WEBHOOK_URL:
        print("Fehler: DISCORD_WEBHOOK_URL ist nicht gesetzt.", file=sys.stderr)
        sys.exit(1)

    video_id, desc, video_url = get_latest_video()
    last_id = load_last_id()

    if video_id != last_id:
        post_to_discord(desc, video_url)
        save_last_id(video_id)
        print(f"Neues Video gepostet: {video_id}")
    else:
        print("Kein neues Video gefunden.")


if __name__ == "__main__":
    main()
