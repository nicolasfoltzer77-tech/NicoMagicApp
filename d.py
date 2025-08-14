with open("/notebooks/.env", "r") as f:
    data = f.read()

data = data.replace("NicoMagicAp.git", "NicoMagicApp.git")

with open("/notebooks/.env", "w") as f:
    f.write(data)

print("✅ URL corrigée dans .env")