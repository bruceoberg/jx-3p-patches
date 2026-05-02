"""CSV and JSON readers/writers for JX-3P patch banks.

JSON is the canonical interchange format (see schemas/). CSV matches the
columns emitted by the C decoder so existing fixtures keep working.
"""

from __future__ import annotations

from pathlib import Path

from jx3p.patch import JX3PPatch


def read_json(path: str | Path) -> list[list[JX3PPatch]]:
    """Read a 2x16 patch collection from a JSON file conforming to bank.schema.json."""
    raise NotImplementedError


def write_json(path: str | Path, banks: list[list[JX3PPatch]]) -> None:
    """Write a 2x16 patch collection to a JSON file conforming to bank.schema.json."""
    raise NotImplementedError


def read_csv(path: str | Path) -> list[list[JX3PPatch]]:
    """Read a 2x16 patch collection from a CSV file matching the C decoder's output."""
    raise NotImplementedError


def write_csv(path: str | Path, banks: list[list[JX3PPatch]]) -> None:
    """Write a 2x16 patch collection to a CSV file matching the C decoder's output."""
    raise NotImplementedError


def validate_bank_json(data: dict) -> None:
    """Validate a parsed JSON dict against bank.schema.json. Raises on failure."""
    raise NotImplementedError
