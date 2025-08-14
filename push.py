#!/usr/bin/env python3
import os
import subprocess

# Charger l'URL depuis .env
ENV_PATH = "/notebooks/.env"
if not os.path.exists(ENV_PATH):
    print(f"❌ Fichier {ENV_PATH} introuvable.")
    exit(1)

with open(ENV_PATH) as f:
    for line in f:
        if line.startswith("GIT_URL="):
            GIT_URL = line.strip().split("=", 1)[1]
            break
    else:
        print("❌ GIT_URL introuvable dans .env.")
        exit(1)

def run(cmd):
    subprocess.run(cmd, check=True)

try:
    print("📂 Dossier cible : /notebooks")
    run(["git", "remote", "set-url", "origin", GIT_URL])
    print(f"🔗 Remote 'origin' mis à jour : {GIT_URL}")

    run(["git", "add", "-A"])

    # On tente le commit mais on ignore l'erreur "rien à commit"
    try:
        subprocess.run(["git", "commit", "-m", "update"], check=True)
    except subprocess.CalledProcessError:
        print("ℹ️ Aucun changement à commit.")

    run(["git", "push", "-u", "origin", "main"])
    print("✅ Push effectué avec succès.")

except subprocess.CalledProcessError as e:
    print(f"❌ Erreur pendant l'exécution : {e}")