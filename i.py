#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

ENV_PATH = "/notebooks/.env"

def main():
    print("⚙️ Configuration GitHub")

    git_user = "nicolasfoltzer77-tech"
    git_token = "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" 
    git_repo = "NicoMagicApp"
    git_branch = "main"
    repo_path = "/notebooks"
  
    if not git_token:
        print("❌ Token obligatoire !")
        return
    
    env_content = f"""GIT_USER={git_user}
GIT_TOKEN={git_token}
GIT_REPO={git_repo}
GIT_BRANCH={git_branch}
REPO_PATH={repo_path}
"""
    with open(ENV_PATH, "w") as f:
        f.write(env_content)

    print(f"✅ Fichier .env mis à jour : {ENV_PATH}")
    print(env_content)

if __name__ == "__main__":
    main()

