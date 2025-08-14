#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
save_url_with_token.py
Construit une URL GitHub avec username + token + repo, puis l'enregistre dans .env.
"""

import sys
from pathlib import Path

ENV_FILE = Path(".env")

def main():
    # --- Modifier ces 3 lignes directement si besoin ---
    username = "nicolasfoltzer77-tech"
    token = "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"
    repo = "NicoMagicApp"
    GIT_BRANCH=main
    REPO_PATH=/notebooks
    GIT_USER=nicolasfoltzer77-tech
    GIT_TOKEN=ghp_votreTokenIci
    GIT_REPO=NicoMagicApp
    GIT_BRANCH=main
    REPO_PATH=/notebooks
    # ---------------------------------------------------

    if not all([username, token, repo]):
        print("❌ Veuillez renseigner username, token et repo dans le code.")
        sys.exit(1)

    url = f"https://{username}:{token}@github.com/{username}/{repo}.git"

    lines = []
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    lines = [l for l in lines if not l.startswith("GIT_URL=")]
    lines.append(f"GIT_URL={url}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ URL avec token enregistrée dans {ENV_FILE.resolve()}")
    print(f"   GIT_URL={url}")

if __name__ == "__main__":
    main()
