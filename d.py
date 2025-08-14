#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, subprocess, sys, shlex
from pathlib import Path

ENV_PATH = Path(".") / ".env"
DEFAULTS = {
    "GIT_USER": "nicolasfoltzer77-tech",
    "GIT_REPO": "NicoMagicApp",
    "GIT_BRANCH": "main",
    "REPO_PATH": ".",
}

SSH_DIR = Path.home() / ".ssh"
KEY_PRIV = SSH_DIR / "id_ed25519"
KEY_PUB  = SSH_DIR / "id_ed25519.pub"
KNOWN    = SSH_DIR / "known_hosts"
CLE_PY   = Path("./cle.py")   # contiendra la clé publique

def echo(msg): print(msg, flush=True)

def run(cmd, check=True, capture=False, cwd=None):
    if isinstance(cmd, str):
        shell = True
        printable = cmd
    else:
        shell = False
        printable = " ".join(shlex.quote(x) for x in cmd)
    echo(f"$ {printable}")
    return subprocess.run(cmd, check=check, capture_output=capture, text=True, shell=shell, cwd=cwd)

def load_env():
    env = dict(DEFAULTS)
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k,v = line.split("=",1)
                env[k.strip()] = v.strip()
    return env

def ensure_ssh_dir():
    SSH_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    try: os.chmod(SSH_DIR, 0o700)
    except: pass

def ensure_known_hosts():
    try:
        # Ajoute l’empreinte GitHub pour éviter la question interactive
        run(["ssh-keyscan", "-t", "ed25519", "-H", "github.com"], check=True, capture=True)
        out = subprocess.check_output(["ssh-keyscan", "-t", "ed25519", "-H", "github.com"], text=True)
        with open(KNOWN, "a", encoding="utf-8") as f:
            f.write(out)
        try: os.chmod(KNOWN, 0o644)
        except: pass
    except Exception:
        # si ssh-keyscan absent, on ignore
        pass

def ensure_key(comment):
    if KEY_PRIV.exists() and KEY_PUB.exists():
        echo(f"🔐 Clé SSH déjà présente: {KEY_PRIV}")
        return
    echo("🔐 Génération d’une nouvelle clé SSH (ed25519)…")
    ensure_ssh_dir()
    run(["ssh-keygen", "-t", "ed25519", "-C", comment, "-f", str(KEY_PRIV), "-N", ""])
    try: os.chmod(KEY_PRIV, 0o600)
    except: pass

def ensure_agent_and_add():
    # Démarre un agent si pas déjà dispo
    if not os.environ.get("SSH_AUTH_SOCK"):
        res = run("ssh-agent -s", capture=True)
        txt = res.stdout or ""
        for line in txt.splitlines():
            if "SSH_AUTH_SOCK" in line:
                val = line.split(";")[0].split("=",1)[1]
                os.environ["SSH_AUTH_SOCK"] = val
            if "SSH_AGENT_PID" in line:
                val = line.split(";")[0].split("=",1)[1]
                os.environ["SSH_AGENT_PID"] = val
    # Ajoute la clé
    run(["ssh-add", str(KEY_PRIV)])

def write_cle_py():
    pub = KEY_PUB.read_text(encoding="utf-8").strip()
    CLE_PY.write_text(
        f'''# cle.py — contient la clé publique SSH à ajouter dans GitHub
PUBLIC_KEY = "{pub}"
print(PUBLIC_KEY)
print("\\nAjoute cette clé sur GitHub → Settings → SSH and GPG keys → New SSH key")'''
        , encoding="utf-8"
    )
    echo(f"🗝️  Fichier créé : {CLE_PY}  (exécute `python cle.py` pour afficher la clé)")

def git_is_repo(path):
    r = run(["git","rev-parse","--is-inside-work-tree"], check=False, capture=True, cwd=path)
    return r.returncode==0 and (r.stdout or "").strip()=="true"

def ensure_branch(path, branch):
    r = run(["git","rev-parse","--abbrev-ref","HEAD"], check=False, capture=True, cwd=path)
    cur = (r.stdout or "").strip()
    if cur in ("", "HEAD"):
        run(["git","checkout","-b",branch], cwd=path)
    elif cur != branch:
        try:
            run(["git","branch","-M",branch], cwd=path)
        except subprocess.CalledProcessError:
            run(["git","checkout",branch], cwd=path)

def set_remote_to_ssh(path, user, repo):
    ssh_url = f"git@github.com:{user}/{repo}.git"
    r = run(["git","remote"], check=False, capture=True, cwd=path)
    remotes = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
    if "origin" in remotes:
        run(["git","remote","set-url","origin",ssh_url], cwd=path)
    else:
        run(["git","remote","add","origin",ssh_url], cwd=path)
    echo(f"🔗 origin = {ssh_url}")

def main():
    env = load_env()
    user   = env["GIT_USER"]
    repo   = env["GIT_REPO"]
    branch = env["GIT_BRANCH"]
    repo_path = Path(env["REPO_PATH"]).resolve()

    echo(f"📄 .env lu : user={user} repo={repo} branch={branch} repo_path={repo_path}")

    if not git_is_repo(repo_path):
        echo("❌ Ce dossier n’est pas un dépôt git (git init manquant ?).")
        sys.exit(1)

    # SSH setup
    ensure_ssh_dir()
    ensure_key(comment=f"{user}@paperspace")
    ensure_agent_and_add()
    ensure_known_hosts()
    write_cle_py()

    # Git remote SSH + push
    echo("🌿 Préparation de la branche…")
    ensure_branch(repo_path, branch)

    echo("🔗 Configuration du remote SSH…")
    set_remote_to_ssh(repo_path, user, repo)

    echo("📝 Commit…")
    run(["git","add","-A"], cwd=repo_path)
    c = run(["git","commit","-m","update"], cwd=repo_path, check=False)
    if c.returncode != 0:
        echo("ℹ️ Aucun changement à committer (OK).")

    echo("⬆️  Push… (si GitHub refuse, ajoute la clé publique de cle.py dans ton compte)")
    try:
        run(["git","push","-u","origin",branch], cwd=repo_path)
        echo("✅ Push terminé.")
    except subprocess.CalledProcessError:
        echo("\n❌ Push refusé (probablement car la clé SSH n’est pas encore ajoutée sur GitHub).")
        echo("   1) Exécute :  python cle.py   → copie la clé")
        echo("   2) Va sur GitHub → Settings → SSH and GPG keys → New SSH key → colle-la → Save")
        echo("   3) Relance :     python d.py")
        sys.exit(1)

if __name__ == "__main__":
    main()