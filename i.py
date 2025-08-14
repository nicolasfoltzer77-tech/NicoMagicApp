#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i_all_in_one_v2.py — version robuste
- Tolère git config --get qui retourne un code d'erreur quand la valeur est absente.
- Fait le setup CI + Git + remote + push.

👉 REMPLIS la variable GIT_URL ci-dessous.
"""

import os
import sys
import subprocess
from pathlib import Path

# ======= REMPLIS-MOI =======
GIT_URL = "https://github.com/nicolasfoltzer77-tech/NicoMagicApp.git"  # <-- colle l'URL HTTPS de ton repo GitHub
# ===========================

CI_YAML = """name: CI

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
          print("✅ bot.py import OK (no runtime executed)")
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

def run(cmd, cwd=None, check=True, capture_output=False, text=True):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=capture_output, text=text)

def ensure_ci_file(root: Path):
    ci_dir = root / ".github" / "workflows"
    ci_dir.mkdir(parents=True, exist_ok=True)
    ci_file = ci_dir / "ci.yml"
    if not ci_file.exists():
        ci_file.write_text(CI_YAML, encoding="utf-8")
        print(f"✅ CI créé : {ci_file}")
    else:
        print(f"ℹ️ CI déjà présent : {ci_file}")
    return ci_file

def is_git_repo(root: Path) -> bool:
    try:
        r = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root, capture_output=True)
        return r.stdout.strip() == "true"
    except subprocess.CalledProcessError:
        return False

def current_branch(root: Path) -> str:
    r = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root, capture_output=True)
    return r.stdout.strip()

def ensure_git(root: Path):
    if not is_git_repo(root):
        run(["git", "init"], cwd=root)
    # Branche main
    try:
        br = current_branch(root)
    except subprocess.CalledProcessError:
        br = None
    if br in (None, "HEAD"):
        run(["git", "checkout", "-b", "main"], cwd=root)
    elif br != "main":
        run(["git", "branch", "-M", "main"], cwd=root)

def git_config_get(root: Path, key: str) -> str:
    # Ne pas planter si absent
    r = subprocess.run(["git", "config", "--get", key], cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        return ""
    return r.stdout.strip()

def ensure_user_config(root: Path):
    name = git_config_get(root, "user.name")
    email = git_config_get(root, "user.email")
    changed = False
    if not name:
        run(["git", "config", "user.name", "paperspace-user"], cwd=root, check=True)
        changed = True
    if not email:
        run(["git", "config", "user.email", "user@example.com"], cwd=root, check=True)
        changed = True
    if changed:
        print("ℹ️ user.name / user.email configurés (modifie-les plus tard si besoin).")

def ensure_remote(root: Path, url: str):
    if not url:
        print("❌ GIT_URL est vide. Ouvre i_all_in_one_v2.py et colle ton URL HTTPS dans GIT_URL.")
        sys.exit(1)
    remotes = run(["git", "remote"], cwd=root, capture_output=True).stdout.splitlines()
    if "origin" in [r.strip() for r in remotes]:
        run(["git", "remote", "set-url", "origin", url], cwd=root)
        print(f"🔗 Remote 'origin' mis à jour : {url}")
    else:
        run(["git", "remote", "add", "origin", url], cwd=root)
        print(f"🔗 Remote 'origin' ajouté : {url}")

def add_commit(root: Path):
    run(["git", "add", "-A"], cwd=root)
    status = run(["git", "status", "--porcelain"], cwd=root, capture_output=True).stdout.strip()
    if status:
        run(["git", "commit", "-m", 'chore: initial setup (CI + files)'], cwd=root)
        print("✅ Commit initial effectué.")
    else:
        print("ℹ️ Aucun changement à committer.")

def push_main(root: Path):
    try:
        run(["git", "push", "-u", "origin", "main"], cwd=root)
        print("🎉 Push vers origin/main réussi.")
    except subprocess.CalledProcessError:
        print("❌ Échec du push.")
        print("   Vérifie tes droits et l'URL. Pour HTTPS + token :")
        print("   https://<TOKEN>@github.com/<USER>/<REPO>.git")
        sys.exit(1)

def main():
    root = Path(os.getcwd())
    print(f"📁 Dossier projet : {root}")
    ensure_ci_file(root)
    ensure_git(root)
    ensure_user_config(root)
    ensure_remote(root, GIT_URL)
    add_commit(root)
    push_main(root)
    print("\nTerminé. Pour mettre ton identité Git :")
    print("  git config user.name \"Ton Nom\"")
    print("  git config user.email \"toi@example.com\"")

if __name__ == "__main__":
    main()
