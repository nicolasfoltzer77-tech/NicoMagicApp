#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot blagues Telegram – envoie une blague en français à intervalle régulier
(10 minutes par défaut). Aucune dépendance externe : uniquement la bibliothèque
standard Python.

CONFIGURATION :
1) Remplir BOT_TOKEN et CHAT_ID ci-dessous (ou définir les variables d'env
   TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID).
2) Lancer :  python3 bot.py &

Astuce : CTRL+C pour arrêter (ou pkill -f bot.py).
"""

import json
import os
import signal
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

# ====== À REMPLIR ======
# Les identifiants Telegram doivent être fournis via des variables d'environnement
# ou en modifiant les lignes ci-dessous. Les valeurs par défaut sont vides afin
# d'éviter toute fuite accidentelle de jeton.
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")  # ex: 123456:ABC-...
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")      # ex: 123456789
INTERVAL_MINUTES = int(os.getenv("JOKE_INTERVAL_MIN", "10"))  # 10 par défaut
# =======================

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

def handle_signal(signum, frame):
    global RUNNING
    RUNNING = False
    _log("Arrêt demandé, on termine proprement...")
    send_telegram_message(BOT_TOKEN, CHAT_ID, "🛑 Bot blagues arrêté.")

def validate_config() -> bool:
    ok = True
    if not BOT_TOKEN or BOT_TOKEN == "TON_TOKEN_BOT":
        _log("⚠️  BOT_TOKEN n'est pas renseigné. Modifie le fichier ou définis TELEGRAM_BOT_TOKEN.")
        ok = False
    if not CHAT_ID or CHAT_ID == "TON_CHAT_ID":
        _log("⚠️  CHAT_ID n'est pas renseigné. Modifie le fichier ou définis TELEGRAM_CHAT_ID.")
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
        f"🚀 Bot blagues démarré ! Je t'enverrai une blague toutes les {INTERVAL_MINUTES} minutes 😉",
    )

    interval = max(1, INTERVAL_MINUTES) * 60
    while RUNNING:
        joke = get_joke_fr()
        send_telegram_message(BOT_TOKEN, CHAT_ID, joke)
        for _ in range(interval):
            if not RUNNING:
                break
            time.sleep(1)

if __name__ == "__main__":
    main()
