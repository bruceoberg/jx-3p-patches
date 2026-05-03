"""Parity tests: C decoder output must equal Python decoder output, field-by-field.

This file is a skeleton. The Python decoder lives in jx3p.codec and is not yet
implemented; the corresponding assertion is marked xfail until codec.read_wav
is wired up.
"""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOLDEN_WAV = FIXTURES / "patchdump.wav"
GOLDEN_CSV = FIXTURES / "patchdump.csv"
DECODER_BIN = REPO_ROOT / "build" / "decoder" / "bin" / "decode_patches"


def _read_csv_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    """Return (header, rows) with each cell stripped."""
    with path.open() as fh:
        reader = csv.reader(fh)
        rows = [[cell.strip() for cell in row] for row in reader]
    if not rows:
        return [], []
    return rows[0], rows[1:]


@pytest.fixture(scope="session")
def decoder_binary() -> Path:
    if not DECODER_BIN.exists():
        pytest.skip(f"decoder binary not built; run `make -C c` first ({DECODER_BIN})")
    return DECODER_BIN


def test_c_decoder_matches_golden_csv(decoder_binary: Path, tmp_path: Path) -> None:
    """Run the C decoder against the golden WAV and diff its output vs the golden CSV."""
    out_csv = tmp_path / "decoded.csv"
    subprocess.run(
        [str(decoder_binary), str(GOLDEN_WAV), str(out_csv)],
        capture_output=True,
        text=True,
        check=True,
    )

    expected_header, expected_rows = _read_csv_rows(GOLDEN_CSV)
    actual_header, actual_rows = _read_csv_rows(out_csv)

    assert actual_header == expected_header, "CSV header differs"
    assert len(actual_rows) == len(expected_rows), (
        f"row count mismatch: got {len(actual_rows)}, expected {len(expected_rows)}"
    )

    for row_idx, (expected_row, actual_row) in enumerate(zip(expected_rows, actual_rows)):
        assert len(actual_row) == len(expected_row), (
            f"row {row_idx} ({expected_row[0]}): "
            f"got {len(actual_row)} cols, expected {len(expected_row)}"
        )
        for col_idx, (expected_cell, actual_cell) in enumerate(zip(expected_row, actual_row)):
            assert actual_cell == expected_cell, (
                f"row {row_idx} ({expected_row[0]}), column {col_idx} "
                f"({expected_header[col_idx]}): "
                f"got {actual_cell!r}, expected {expected_cell!r}"
            )


@pytest.mark.xfail(reason="jx3p.codec.read_wav not yet implemented", strict=True)
def test_python_decoder_matches_c_decoder(decoder_binary: Path, tmp_path: Path) -> None:
    """The Python codec.read_wav output must match the C decoder field-by-field."""
    from jx3p import codec

    banks = codec.read_wav(GOLDEN_WAV)

    c_csv = tmp_path / "decoded.csv"
    subprocess.run(
        [str(decoder_binary), str(GOLDEN_WAV), str(c_csv)],
        capture_output=True,
        text=True,
        check=True,
    )
    expected_header, expected_rows = _read_csv_rows(c_csv)
    _ = expected_header, expected_rows, banks
    raise NotImplementedError("comparison harness pending codec implementation")
