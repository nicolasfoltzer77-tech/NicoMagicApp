#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

# Lecture du .env manuellement
def read_env_var(key, env_path="/notebooks/.env"):
    if not os.path.exists(env_path):
        return None
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith(f"{key}="):
                return line.strip().split("=", 1)[1]
    return None

def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=True)

def main():
    repo_dir = "/notebooks"
    print(f"📂 Dossier cible : {repo_dir}")

    # Charger URL depuis le .env
    git_url = read_env_var("GIT_URL")
    if not git_url:
        print("❌ GIT_URL introuvable dans .env")
        return

    # Config remote origin
    run(["git", "remote", "set-url", "origin", git_url])
    print(f"🔗 Remote 'origin' mis à jour : {git_url}")

    # Ajout / commit
    run(["git", "add", "-A"], cwd=repo_dir)
    try:
        run(["git", "commit", "-m", "update"], cwd=repo_dir)
    except subprocess.CalledProcessError:
        print("ℹ️ Aucun changement à commit.")

    # Push
    run(["git", "push", "-u", "origin", "main"], cwd=repo_dir)

if __name__ == "__main__":
    main()