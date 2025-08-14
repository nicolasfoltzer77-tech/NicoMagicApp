#!/usr/bin/env python3
import os
import subprocess

# Lecture du .env
env_path = ".env"
if not os.path.exists(env_path):
    print("❌ Fichier .env introuvable")
    exit(1)

with open(env_path) as f:
    for line in f:
        if line.strip() and not line.startswith("#"):
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

# Récupération des infos
token = os.getenv("GIT_TOKEN")
user = os.getenv("GIT_USER")
repo = os.getenv("GIT_REPO")
branch = os.getenv("GIT_BRANCH", "main")
repo_path = os.getenv("REPO_PATH", ".")

if not all([token, user, repo]):
    print("❌ Variables GIT_TOKEN, GIT_USER ou GIT_REPO manquantes dans .env")
    exit(1)

# Construction de l'URL
git_url = f"https://{token}@github.com/{user}/{repo}.git"

print(f"📂 Dossier cible : {repo_path}")
print(f"🔗 Remote 'origin' = {git_url}")

def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

try:
    # Mise à jour du remote origin
    run(["git", "remote", "set-url", "origin", git_url], cwd=repo_path)

    # Add, commit, push
    run(["git", "add", "-A"], cwd=repo_path)
    run(["git", "commit", "-m", "update"], cwd=repo_path)
    run(["git", "push", "-u", "origin", branch], cwd=repo_path)

    print("✅ Push terminé avec succès")
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur : {e}")
    exit(1)