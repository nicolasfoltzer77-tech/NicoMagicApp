"""Smoke test for importing the :mod:`bot` module.

This file acts both as a pytest test and as a standalone script.  When run
directly (``python test_smoke.py``) it prints whether the import succeeded.
When collected by pytest, the ``test_import_bot`` function is executed and will
fail if the import raises an exception.
"""

import importlib


def test_import_bot() -> None:
    """Ensure that the ``bot`` module can be imported."""
    importlib.import_module("bot")


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    try:
        importlib.import_module("bot")
        print("\u2705 Import success: bot module loaded.")
    except Exception as exc:  # pragma: no cover - informational output
        print(f"\u274c Import failed: {exc}")

