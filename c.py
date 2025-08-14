#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
c.py — crée le fichier GitHub Actions CI dans un projet local.
- Crée le chemin .github/workflows/ si besoin
- Écrit le fichier ci.yml avec un workflow simple (smoke + lint)
- Affiche l'emplacement final

Usage :
  python3 c.py /chemin/vers/ton/projet
  # ex: python3 c.py /mnt/data/telegram-jokes-bot

Si aucun chemin n'est fourni, par défaut: répertoire courant (".")
"""

import os
import sys

CI_CONTENT = """name: CI

on:
  push:
  pull_request:

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Syntax check
        run: python -m py_compile bot.py

      - name: Import smoke test
        run: |
          python - <<'PY'
          import bot
          print(\\"✅ bot.py import OK (no runtime executed)\\")
          PY

  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install ruff (fast linter)
        run: pip install ruff

      - name: Ruff check
        run: ruff check .
"""

def main():
    # cible: arg1 ou "."
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    target = os.path.abspath(target)

    if not os.path.isdir(target):
        print(f"❌ Dossier introuvable: {target}")
        sys.exit(1)

    ci_dir = os.path.join(target, ".github", "workflows")
    os.makedirs(ci_dir, exist_ok=True)

    ci_path = os.path.join(ci_dir, "ci.yml")
    with open(ci_path, "w", encoding="utf-8") as f:
        f.write(CI_CONTENT)

    print("✅ Workflow CI créé.")
    print(f"📄 Fichier: {ci_path}")
    print("\\nProchaines étapes :")
    print(f"  cd {target}")
    print("  git add .github/workflows/ci.yml")
    print("  git commit -m \"ci: add GitHub Actions\"")
    print("  git push -u origin main")

if __name__ == "__main__":
    main()
