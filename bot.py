#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot blagues Telegram – envoie une blague en français à un intervalle choisi
par l'utilisateur.
Une seule dépendance : la bibliothèque standard Python.

CONFIGURATION :
1) Remplir BOT_TOKEN et CHAT_ID ci-dessous (ou définir les variables d'env
   TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID).
2) Lancer :  python3 bot.py &

Astuce : CTRL+C pour arrêter (ou pkill -f bot.py).
"""

import json
import os
import select
import signal
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, time as dt_time, timedelta

# ====== À REMPLIR ======
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8257199418:AAFPhbR9_ZDj-qiYM1lIm1hIe6QFYjUZ0O0")  # ex: 123456:ABC-...
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7552287774")        # ex: 123456789
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


def ask_interval() -> tuple[int, str]:
    """Demande à l'utilisateur la fréquence d'envoi des blagues.

    Retourne un tuple (interval_seconds, description_humaine).
    """
    print("Choisis la fréquence des blagues :")
    print("  [d] Défaut : 6 blagues par heure")
    print("  [c] Court  : une blague toutes les 10 secondes")
    print("  [l] Long   : une blague par jour")
    choix = input("Ton choix [d/c/l] (défaut d) : ").strip().lower()

    if choix == "c":
        return 10, "une blague toutes les 10 secondes"
    if choix == "l":
        return 24 * 60 * 60, "une blague par jour"
    return 10 * 60, "6 blagues par heure"


def ask_work_hours() -> tuple[dt_time, dt_time] | None:
    """Permet de définir des heures d'activité pour l'envoi des blagues."""
    rep = input("Limiter les heures d'envoi ? [o/N] : ").strip().lower()
    if rep != "o":
        return None

    def _parse(hhmm: str) -> dt_time:
        try:
            h, m = map(int, hhmm.split(":"))
            return dt_time(hour=h, minute=m)
        except Exception:
            return _parse(input("Format invalide, utilise HH:MM : "))

    debut = _parse(input("Heure de début (HH:MM) : "))
    fin = _parse(input("Heure de fin   (HH:MM) : "))
    return debut, fin


def check_manual_sleep() -> None:
    """Si l'utilisateur tape 'sleep N', met le bot en pause N secondes."""
    if select.select([sys.stdin], [], [], 0)[0]:
        cmd = sys.stdin.readline().strip().split()
        if cmd and cmd[0] == "sleep":
            secs = int(cmd[1]) if len(cmd) > 1 and cmd[1].isdigit() else 0
            if secs > 0:
                _log(f"Pause manuelle de {secs}s")
                for _ in range(secs):
                    if not RUNNING:
                        break
                    time.sleep(1)

def main():
    if not validate_config():
        sys.exit(1)

    # Gestion Ctrl+C / arrêt système
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    interval, desc = ask_interval()
    work_hours = ask_work_hours()

    _log(f"Bot démarré, {desc}.")
    if work_hours:
        start, end = work_hours
        _log(f"Heures actives : {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    _log("Tape 'sleep N' pour mettre en pause N secondes.")
    send_telegram_message(BOT_TOKEN, CHAT_ID, f"🚀 Bot blagues démarré ! Je t'enverrai {desc} 😉")

    while RUNNING:
        now = datetime.now().time()
        if work_hours:
            start, end = work_hours
            if start <= end:
                inside = start <= now <= end
            else:
                inside = now >= start or now <= end
            if not inside:
                today = datetime.now()
                next_start = datetime.combine(today.date(), start)
                if start <= end:
                    if now > end:
                        next_start += timedelta(days=1)
                    elif now < start:
                        pass
                else:
                    if now <= end:
                        next_start -= timedelta(days=1)
                    elif now > start:
                        next_start += timedelta(days=1)
                wait = max(1, int((next_start - today).total_seconds()))
                _log(f"En dehors des heures actives, sommeil {wait}s")
                for _ in range(wait):
                    if not RUNNING:
                        break
                    time.sleep(1)
                continue

        joke = get_joke_fr()
        send_telegram_message(BOT_TOKEN, CHAT_ID, joke)
        check_manual_sleep()
        for _ in range(interval):
            if not RUNNING:
                break
            time.sleep(1)

if __name__ == "__main__":
    main()
