#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot blagues Telegram – envoie une blague en français toutes les 10 minutes.
Aucune dépendance externe : uniquement la bibliothèque standard Python.

CONFIGURATION :
1) Placer BOT_TOKEN et CHAT_ID dans un fichier ``secrets.json`` (voir
   ``secrets.example.json``) ou définir les variables d'environnement
   ``TELEGRAM_BOT_TOKEN`` et ``TELEGRAM_CHAT_ID``.
2) Lancer :  python3 bot_blagues.py &

Astuce : CTRL+C pour arrêter (ou pkill -f bot_blagues.py).
"""

import base64
import json
import os
import signal
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

# ====== Chargement configuration ======
CONFIG_FILE = os.getenv("BOT_CONFIG_FILE", "secrets.json")
CONFIG = {}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            CONFIG = json.load(f)
    except Exception:
        CONFIG = {}

BOT_TOKEN = CONFIG.get("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = CONFIG.get("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID", "")
INTERVAL_MINUTES = int(
    CONFIG.get("JOKE_INTERVAL_MIN") or os.getenv("JOKE_INTERVAL_MIN", "1")
)

TWILIO_ACCOUNT_SID = CONFIG.get("TWILIO_ACCOUNT_SID") or os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = CONFIG.get("TWILIO_AUTH_TOKEN") or os.getenv("TWILIO_AUTH_TOKEN", "")
WHATSAPP_FROM = CONFIG.get("WHATSAPP_FROM") or os.getenv("WHATSAPP_FROM", "")
WHATSAPP_TO = CONFIG.get("WHATSAPP_TO") or os.getenv("WHATSAPP_TO", "")
# ======================================

JOKE_URL = "https://v2.jokeapi.dev/joke/Any?lang=fr&blacklistFlags=nsfw,racist,sexist,explicit"
TELEGRAM_API = "https://api.telegram.org"

RUNNING = True

def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def get_joke_fr() -> str:
    """Récupère une blague FR depuis JokeAPI (format texte simple)."""
    try:
        req = urllib.request.Request(JOKE_URL, headers={"User-Agent": "jokes-telegram-bot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        if data.get("type") == "single":
            return data.get("joke", "Pas de blague disponible 😅")
        # type == "twopart"
        setup = data.get("setup", "").strip()
        delivery = data.get("delivery", "").strip()
        if setup or delivery:
            return f"{setup} ... {delivery}"
        return "Pas de blague disponible 😅"
    except Exception as e:
        return f"Oups, impossible de récupérer une blague : {e}"

def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    """Envoie un message via l'API Telegram sans dépendances externes."""
    url = f"{TELEGRAM_API}/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                _log(f"Telegram a répondu {resp.status}")
    except Exception as e:
        _log(f"Erreur d'envoi Telegram : {e}")


def send_whatsapp_message(text: str) -> None:
    """Envoie un message WhatsApp via l'API Twilio (si configuré)."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, WHATSAPP_FROM, WHATSAPP_TO]):
        _log("Config WhatsApp incomplète; message non envoyé.")
        return
    url = (
        f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    )
    payload = {
        "From": f"whatsapp:{WHATSAPP_FROM}",
        "To": f"whatsapp:{WHATSAPP_TO}",
        "Body": text,
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    creds = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}".encode("utf-8")
    b64 = base64.b64encode(creds).decode("ascii")
    req.add_header("Authorization", f"Basic {b64}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status not in (200, 201):
                _log(f"Twilio a répondu {resp.status}")
    except Exception as e:
        _log(f"Erreur d'envoi WhatsApp : {e}")

def handle_signal(signum, frame):
    global RUNNING
    RUNNING = False
    _log("Arrêt demandé, on termine proprement...")
    send_telegram_message(BOT_TOKEN, CHAT_ID, "🛑 Bot blagues arrêté.")
    send_whatsapp_message("🛑 Bot blagues arrêté.")

def validate_config() -> bool:
    ok = True
    if not BOT_TOKEN:
        _log("⚠️  BOT_TOKEN n'est pas renseigné. Ajoute-le dans secrets.json ou TELEGRAM_BOT_TOKEN.")
        ok = False
    if not CHAT_ID:
        _log("⚠️  CHAT_ID n'est pas renseigné. Ajoute-le dans secrets.json ou TELEGRAM_CHAT_ID.")
        ok = False
    return ok

def main():
    if not validate_config():
        sys.exit(1)

    # Gestion Ctrl+C / arrêt système
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    _log(f"Bot démarré. Une blague toutes les {INTERVAL_MINUTES} minutes.")
    send_telegram_message(
        BOT_TOKEN,
        CHAT_ID,
        "🚀 Bot blagues démarré ! Je t'enverrai une blague toutes les 10 minutes 😉",
    )
    send_whatsapp_message(
        "🚀 Bot blagues démarré ! Je t'enverrai une blague toutes les 10 minutes 😉"
    )

    interval = max(1, INTERVAL_MINUTES) * 60
    while RUNNING:
        joke = get_joke_fr()
        send_telegram_message(BOT_TOKEN, CHAT_ID, joke)
        send_whatsapp_message(joke)
        for _ in range(interval):
            if not RUNNING:
                break
            time.sleep(1)

if __name__ == "__main__":
    main()
