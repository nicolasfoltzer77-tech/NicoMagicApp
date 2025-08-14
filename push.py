#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

# 📌 Fichier .env à lire
ENV_PATH = "/notebooks/.env"

def run(cmd, cwd=None):
    """Exécute une commande shell"""
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

# 🔹 Lecture des variables du .env
def load_env(path):
    env_vars = {}
    with open(path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                env_vars[key] = value
    return env_vars

def main():
    env = load_env(ENV_PATH)

    user = env.get("GIT_USER") or "nicolasfoltzer77-tech"
    token = env.get("GIT_TOKEN")
    repo = env.get("GIT_REPO") or "NicoMagicApp"
    branch = env.get("GIT_BRANCH") or "main"
    repo_path = env.get("REPO_PATH") or "/notebooks"

    if not token:
        print("❌ Erreur : GIT_TOKEN manquant dans .env")
        return

    # 🔹 Assemblage de l’URL complète
    git_url = f"https://{user}:{token}@github.com/{user}/{repo}.git"
    print(f"📌 Remote 'origin' = {git_url}")

    # 🔹 Git add / commit / push
    run(["git", "remote", "set-url", "origin", git_url], cwd=repo_path)
    run(["git", "add", "-A"], cwd=repo_path)
    run(["git", "commit", "-m", "update"], cwd=repo_path)
    run(["git", "push", "-u", "origin", branch], cwd=repo_path)

if __name__ == "__main__":
    main()