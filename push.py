#!/usr/bin/env python3
import os
import subprocess

# Récupération depuis .env
env_path = ".env"
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

TOKEN = os.getenv("GIT_TOKEN")
USER = os.getenv("GIT_USER")
REPO = os.getenv("GIT_REPO")
BRANCH = os.getenv("GIT_BRANCH", "main")
REPO_PATH = os.getenv("REPO_PATH", ".")

if not all([TOKEN, USER, REPO]):
    print("❌ Variables GIT_TOKEN, GIT_USER ou GIT_REPO manquantes dans .env")
    exit(1)

# Construit l'URL correcte
git_url = f"https://{USER}:{TOKEN}@github.com/{USER}/{REPO}.git"

def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

print(f"📂 Dossier cible : {REPO_PATH}")

# Met à jour l'origin
run(["git", "remote", "set-url", "origin", git_url])
print(f"🔗 Remote 'origin' mis à jour : {git_url}")

# Commit et push
run(["git", "add", "-A"], cwd=REPO_PATH)
run(["git", "commit", "-m", "update"], cwd=REPO_PATH)
run(["git", "push", "-u", "origin", BRANCH], cwd=REPO_PATH)