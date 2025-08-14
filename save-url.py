#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
save_url.py
Enregistre l'URL GitHub dans un fichier .env (variable GIT_URL).
"""

import sys
from pathlib import Path

ENV_FILE = Path(".env")

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
    else:
        url = "https://github.com/nicolasfoltzer77-tech/NicoMagicApp.git"
        
        
    if not url.startswith("http"):
        print("❌ URL invalide. Elle doit commencer par http(s)://")
        sys.exit(1)

    lines = []
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    lines = [l for l in lines if not l.startswith("GIT_URL=")]
    lines.append(f"GIT_URL={url}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ URL enregistrée dans {ENV_FILE.resolve()}")
    print(f"   GIT_URL={url}")

if __name__ == "__main__":
    main()