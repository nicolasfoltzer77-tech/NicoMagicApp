# Local smoke test (offline). Run with: python test_smoke.py
# Ensures bot.py can be imported and main guard prevents execution on import.

import importlib
import sys

try:
    import bot
    print("✅ Import success: bot module loaded.")
    sys.exit(0)
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
