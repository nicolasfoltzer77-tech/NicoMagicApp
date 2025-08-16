from __future__ import annotations

"""Utilities for logging open trading positions and computing gains.

This module provides a :class:`Position` data class representing an open
position and a :func:`log_positions` helper to append those positions to a
log file.  Each log entry includes the absolute gain and the percentage gain
relative to the entry price, which allows simple tracking of the performance
of open trades.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Iterable


@dataclass
class Position:
    """Represents an open trading position."""

    symbol: str
    entry_price: float
    current_price: float
    quantity: float

    @property
    def gain(self) -> float:
        """Return the absolute gain for the position."""
        return (self.current_price - self.entry_price) * self.quantity

    @property
    def gain_percent(self) -> float:
        """Return the percentage gain relative to the entry price."""
        if self.entry_price == 0:
            return 0.0
        return (self.current_price - self.entry_price) / self.entry_price * 100


def log_positions(positions: Iterable[Position], log_file: str = "open_positions.log") -> None:
    """Append a list of positions to ``log_file``.

    Each position is written as a JSON line containing its details, the
    computed gain and percentage gain, and a timestamp.
    """
    entries = []
    for pos in positions:
        entry = asdict(pos)
        entry["gain"] = pos.gain
        entry["gain_percent"] = pos.gain_percent
        entry["timestamp"] = datetime.now().isoformat()
        entries.append(entry)

    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
