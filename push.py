#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, subprocess, sys

ENV_PATH = "./.env"           # .env dans le dossier courant
DEFAULT_BRANCH = "main"       # branche par défaut

def echo(msg):
    print(msg, flush=True)

def mask_token(s: str) -> str:
    if not s: return ""
    if len(s) <= 10: return "***"
    return s[:6] + "..." + s[-4:]

def run(cmd, cwd=None, check=True):
    echo(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check)

def load_env(path):
    env = {}
    if not os.path.exists(path):
        echo(f"❌ Fichier .env introuvable: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

def current_branch():
    p = subprocess.run(["git","rev-parse","--abbrev-ref","HEAD"],
                       capture_output=True, text=True)
    if p.returncode == 0:
        return p.stdout.strip()
    return None

def ensure_branch(branch):
    cur = current_branch()
    if cur in (None, "HEAD"):
        # dépôt vierge
        run(["git","checkout","-b", branch])
    elif cur != branch:
        # renomme ou bascule
        try:
            run(["git","branch","-M", branch])
        except subprocess.CalledProcessError:
            run(["git","checkout", branch])

def assemble_url(env):
    # 1) si GIT_URL fourni, on l’utilise tel quel
    url = env.get("GIT_URL", "").strip()
    if url:
        return url, None, None, None
    # 2) sinon on construit depuis USER/TOKEN/REPO
    user  = env.get("GIT_USER", "").strip()
    token = env.get("GIT_TOKEN", "").strip()
    repo  = env.get("GIT_REPO", "").strip()
    if not (user and token and repo):
        echo("❌ Variables manquantes. Fournis soit GIT_URL, soit GIT_USER + GIT_TOKEN + GIT_REPO dans .env")
        sys.exit(1)
    # format recommandé (fiable) : USER:TOKEN@
    url = f"https://{user}:{token}@github.com/{user}/{repo}.git"
    return url, user, token, repo

def main():
    echo("🔧 Démarrage push auto (sans dépendances)")
    env = load_env(ENV_PATH)
    branch = env.get("GIT_BRANCH", DEFAULT_BRANCH)
    repo_path = env.get("REPO_PATH", ".")
    os.chdir(repo_path)

    url, user, token, repo = assemble_url(env)
    echo("\n📄 .env lu :")
    if user:
        echo(f"  GIT_USER   = {user}")
        echo(f"  GIT_TOKEN  = {mask_token(token)}")
        echo(f"  GIT_REPO   = {repo}")
    echo(f"  GIT_BRANCH = {branch}")
    echo(f"  REPO_PATH  = {os.path.abspath('.')}")
    echo(f"  URL        = {url.replace(token, mask_token(token)) if token else url}")

    # Vérifie que c’est bien un repo
    p = subprocess.run(["git","rev-parse","--is-inside-work-tree"], capture_output=True, text=True)
    if p.returncode != 0 or p.stdout.strip() != "true":
        echo("❌ Ce dossier n’est pas un dépôt git. Lance d’abord `git init` (ou place-toi dans le bon dossier).")
        sys.exit(1)

    # Branche
    echo("\n🌿 Préparation de la branche…")
    ensure_branch(branch)

    # Remote origin
    echo("\n🔗 Mise à jour du remote 'origin'…")
    # s’il n’existe pas, add; sinon set-url
    rem = subprocess.run(["git","remote"], capture_output=True, text=True)
    if "origin" in [r.strip() for r in rem.stdout.splitlines()]:
        run(["git","remote","set-url","origin", url])
    else:
        run(["git","remote","add","origin", url])

    # Add + commit (ignore si rien à committer)
    echo("\n📝 Commit…")
    run(["git","add","-A"])
    c = subprocess.run(["git","commit","-m","update"])
    if c.returncode != 0:
        echo("ℹ️ Aucun changement à committer (OK).")

    # Push (crée l’upstream si besoin)
    echo("\n⬆️  Push…")
    try:
        run(["git","push","-u","origin", branch])
        echo("\n✅ Push terminé avec succès.")
    except subprocess.CalledProcessError as e:
        echo("\n❌ Échec du push.")
        echo("   Causes courantes :")
        echo("   - TOKEN invalide ou expiré")
        echo("   - Scopes insuffisants (donne au moins `repo` ou `public_repo`)")
        echo("   - Nom de repo ou utilisateur incorrect")
        echo("\n   Vérifie aussi que l’URL suit bien ce format :")
        echo("   https://<USER>:<TOKEN>@github.com/<USER>/<REPO>.git")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()