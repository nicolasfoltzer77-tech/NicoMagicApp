#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
push_interactive.py — Assistant de push Git (interactive & auto-configurant)

Fonctions :
- Vérifie si le dossier est un repo Git, sinon propose de l'initialiser
- S'assure que la branche 'main' existe/devient la branche actuelle
- Vérifie/ajoute le remote 'origin' (demande l'URL si manquant)
- (Optionnel) Configure user.name et user.email si absents
- Ajoute, commit (si modifications) et push (avec -u origin main)

Usage :
  python3 push_interactive.py [chemin_du_projet]

Conseil URL remote :
- Utilise HTTPS : https://github.com/<USER>/<REPO>.git
- Si authentification requise, tu peux coller une URL avec PAT :
  https://<TOKEN>@github.com/<USER>/<REPO>.git
"""

import os
import sys
import subprocess
from shutil import which

def run(cmd, cwd=None, check=True, capture_output=False, text=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=capture_output, text=text)

def git_available():
    return which("git") is not None

def is_git_repo(path):
    try:
        r = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=path, capture_output=True)
        return r.stdout.strip() == "true"
    except subprocess.CalledProcessError:
        return False

def get_current_branch(path):
    r = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path, capture_output=True)
    return r.stdout.strip()

def has_remote_origin(path):
    r = run(["git", "remote"], cwd=path, capture_output=True)
    remotes = [x.strip() for x in r.stdout.splitlines() if x.strip()]
    return "origin" in remotes

def get_remote_url(path):
    try:
        r = run(["git", "remote", "get-url", "origin"], cwd=path, capture_output=True)
        return r.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def user_configured(path):
    name = run(["git", "config", "--get", "user.name"], cwd=path, capture_output=True).stdout.strip()
    email = run(["git", "config", "--get", "user.email"], cwd=path, capture_output=True).stdout.strip()
    return name, email

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    target = os.path.abspath(target)
    print(f"📁 Dossier cible : {target}")

    if not os.path.isdir(target):
        print("❌ Dossier introuvable.")
        sys.exit(1)

    if not git_available():
        print("❌ Git n'est pas installé ou pas dans le PATH.")
        sys.exit(1)

    # 1) Repo ?
    if not is_git_repo(target):
        ans = input("Ce dossier n'est pas un dépôt Git. L'initialiser ? [O/n] ").strip().lower() or "o"
        if ans.startswith("o"):
            run(["git", "init"], cwd=target)
        else:
            print("🚫 Abandon.")
            sys.exit(0)

    # 2) Branche main
    try:
        branch = get_current_branch(target)
    except subprocess.CalledProcessError:
        branch = None
    if branch in (None, "HEAD"):
        # dépôt vide : crée main
        run(["git", "checkout", "-b", "main"], cwd=target)
        branch = "main"
    elif branch != "main":
        ans = input(f"Branche courante '{branch}'. Basculer/renommer en 'main' ? [O/n] ").strip().lower() or "o"
        if ans.startswith("o"):
            # essayer de renommer
            try:
                run(["git", "branch", "-M", "main"], cwd=target)
            except subprocess.CalledProcessError:
                run(["git", "checkout", "main"], cwd=target)
        branch = "main"

    # 3) Remote origin
    if not has_remote_origin(target):
        url = input("Aucun remote 'origin'. Entre l'URL du dépôt GitHub (HTTPS) : ").strip()
        while not url:
            url = input("URL invalide. Recommence : ").strip()
        run(["git", "remote", "add", "origin", url], cwd=target)
        print(f"🔗 Remote 'origin' ajouté : {url}")
    else:
        print(f"🔗 Remote 'origin' : {get_remote_url(target)}")

    # 4) Config user si manquante
    name, email = user_configured(target)
    if not name:
        name = input("git user.name est vide. Entre un nom (ex: Ton Nom) : ").strip()
        if name:
            run(["git", "config", "user.name", name], cwd=target)
    if not email:
        email = input("git user.email est vide. Entre un email (ex: toi@example.com) : ").strip()
        if email:
            run(["git", "config", "user.email", email], cwd=target)

    # 5) Stage & commit
    run(["git", "add", "-A"], cwd=target)
    status = run(["git", "status", "--porcelain"], cwd=target, capture_output=True).stdout.strip()
    if status:
        msg = input("Message de commit (défaut: 'update'): ").strip() or "update"
        run(["git", "commit", "-m", msg], cwd=target)
    else:
        print("ℹ️  Aucun changement à committer.")

    # 6) Push
    try:
        run(["git", "push", "-u", "origin", "main"], cwd=target)
        print("✅ Push effectué vers origin/main.")
    except subprocess.CalledProcessError as e:
        print("❌ Échec du push. Vérifie l'URL du remote et tes droits (token/SSH).")
        print("   Astuce HTTPS avec token : https://<TOKEN>@github.com/<USER>/<REPO>.git")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
