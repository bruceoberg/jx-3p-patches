"""Parity tests: C decoder output must equal Python decoder output, field-by-field."""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import pytest

from jx3p.patch import JX3PPatch


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOLDEN_WAV = FIXTURES / "patchdump.wav"
GOLDEN_CSV = FIXTURES / "patchdump.csv"
DECODER_BIN = REPO_ROOT / "build" / "decoder" / "bin" / "decode_patches"

# CSV column → JX3PPatch attribute (None for the first "patch" label column).
# The "true"/"false" rendering for boolean columns matches the C decoder's
# 0/1 / on/off / neg/pos / gate/env conventions; see _patch_to_csv_row below.
_CSV_FIELD_ORDER = (
    None,                       # patch label (e.g. "C01")
    "dco1_range",
    "dco1_waveform",
    "dco1_fmod_lfo",
    "dco1_fmod_env",
    "dco2_range",
    "dco2_waveform",
    "dco2_crossmod",
    "dco2_tune",
    "dco2_fine_tune",
    "dco2_fmod_lfo",
    "dco2_fmod_env",
    "dco_lfo_amount",
    "dco_env_amount",
    "dco_env_polarity",
    "vcf_mix",
    "vcf_hpf",
    "vcf_cutoff",
    "vcf_lfo_mod",
    "vcf_pitch_follow",
    "vcf_resonance",
    "vcf_env_mod",
    "vcf_env_polarity",
    "vca_mode",
    "vca_level",
    "chorus",
    "lfo_waveform",
    "lfo_delay",
    "lfo_rate",
    "env_attack",
    "env_decay",
    "env_sustain",
    "env_release",
    "mystery",
)


def _read_csv_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    """Return (header, rows) with each cell stripped."""
    with path.open() as fh:
        reader = csv.reader(fh)
        rows = [[cell.strip() for cell in row] for row in reader]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def _patch_label(bank_idx: int, slot: int) -> str:
    return f"{'CD'[bank_idx]}{slot + 1:02d}"


def _patch_to_csv_row(bank_idx: int, slot: int, patch: JX3PPatch) -> list[str]:
    """Render one patch as the same string list the C decoder emits in CSV."""
    bool_chorus = "on" if patch.chorus else "off"
    cells: list[str] = [_patch_label(bank_idx, slot)]
    for attr in _CSV_FIELD_ORDER[1:]:
        value = getattr(patch, attr)
        if attr == "chorus":
            cells.append(bool_chorus)
        elif isinstance(value, bool):
            cells.append("1" if value else "0")
        else:
            cells.append(str(value))
    return cells


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


def test_python_decoder_matches_golden_csv() -> None:
    """jx3p.codec.read_wav output must equal the golden CSV field-by-field."""
    from jx3p import codec

    banks = codec.read_wav(GOLDEN_WAV)

    expected_header, expected_rows = _read_csv_rows(GOLDEN_CSV)
    assert len(expected_rows) == 32

    for row_idx, expected_row in enumerate(expected_rows):
        bank_idx = row_idx // 16
        slot = row_idx % 16
        actual_row = _patch_to_csv_row(bank_idx, slot, banks[bank_idx][slot])
        for col_idx, (expected_cell, actual_cell) in enumerate(zip(expected_row, actual_row)):
            assert actual_cell == expected_cell, (
                f"row {row_idx} ({expected_row[0]}), column {col_idx} "
                f"({expected_header[col_idx]}): "
                f"Python got {actual_cell!r}, C wrote {expected_cell!r}"
            )
