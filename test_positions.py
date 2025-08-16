"""Tests for the positions logging utilities."""

import json
from pathlib import Path

from positions import Position, log_positions


def test_log_positions(tmp_path: Path) -> None:
    log_file = tmp_path / "log.jsonl"
    positions = [Position(symbol="BTC", entry_price=10000.0, current_price=10500.0, quantity=0.1)]
    log_positions(positions, log_file=str(log_file))

    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["symbol"] == "BTC"
    assert entry["gain"] == 50.0
    assert round(entry["gain_percent"], 2) == 5.0
