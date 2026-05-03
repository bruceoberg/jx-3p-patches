"""Tests for jx3p.formats: JSON and CSV I/O round-trips and schema validation."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from jx3p import codec, formats
from jx3p.patch import JX3PPatch


FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOLDEN_WAV = FIXTURES / "patchdump.wav"
GOLDEN_CSV = FIXTURES / "patchdump.csv"
GOLDEN_JSON = FIXTURES / "patchdump.json"


# --- CSV --------------------------------------------------------------------

def test_csv_writer_is_byte_identical_to_golden() -> None:
    """formats.write_csv reproduces the golden CSV byte-for-byte."""
    banks = formats.read_csv(GOLDEN_CSV)
    out = FIXTURES / "_tmp_csv.csv"
    try:
        formats.write_csv(out, banks)
        assert out.read_bytes() == GOLDEN_CSV.read_bytes()
    finally:
        out.unlink(missing_ok=True)


def test_csv_read_matches_wav_decoded(tmp_path: Path) -> None:
    """The CSV fixture and the WAV fixture decode to the same patches."""
    from_wav = codec.read_wav(GOLDEN_WAV)
    from_csv = formats.read_csv(GOLDEN_CSV)
    assert from_wav == from_csv


def test_csv_round_trip(tmp_path: Path) -> None:
    """csv -> patches -> csv preserves every byte of the file."""
    banks = formats.read_csv(GOLDEN_CSV)
    out = tmp_path / "rt.csv"
    formats.write_csv(out, banks)
    assert out.read_bytes() == GOLDEN_CSV.read_bytes()


# --- JSON -------------------------------------------------------------------

def test_json_round_trip(tmp_path: Path) -> None:
    """patches -> json -> patches preserves every field."""
    banks_in = codec.read_wav(GOLDEN_WAV)
    out = tmp_path / "rt.json"
    formats.write_json(out, banks_in)
    banks_out = formats.read_json(out)
    assert banks_in == banks_out


def test_json_csv_cross_round_trip(tmp_path: Path) -> None:
    """csv -> patches -> json -> patches -> csv stays byte-identical to the source CSV."""
    banks_a = formats.read_csv(GOLDEN_CSV)
    json_path = tmp_path / "via.json"
    formats.write_json(json_path, banks_a)
    banks_b = formats.read_json(json_path)
    csv_path = tmp_path / "rt.csv"
    formats.write_csv(csv_path, banks_b)
    assert csv_path.read_bytes() == GOLDEN_CSV.read_bytes()


def test_json_writer_matches_golden_fixture(tmp_path: Path) -> None:
    """formats.write_json from the WAV-decoded patches reproduces the committed golden JSON."""
    banks = codec.read_wav(GOLDEN_WAV)
    out = tmp_path / "rt.json"
    formats.write_json(out, banks)
    assert out.read_bytes() == GOLDEN_JSON.read_bytes()


def test_write_json_includes_format_version(tmp_path: Path) -> None:
    """Top-level JSON must declare format_version = 1.0."""
    banks = [[JX3PPatch() for _ in range(16)] for _ in range(2)]
    out = tmp_path / "fv.json"
    formats.write_json(out, banks)
    data = json.loads(out.read_text())
    assert data["format_version"] == "1.0"
    assert isinstance(data["banks"], list) and len(data["banks"]) == 2


# --- schema validation ------------------------------------------------------

def test_validate_accepts_default_bank() -> None:
    """A bank of default-constructed patches must validate."""
    banks = [[JX3PPatch() for _ in range(16)] for _ in range(2)]
    data = {
        "format_version": "1.0",
        "banks": [[p.to_dict() for p in bank] for bank in banks],
    }
    formats.validate_bank_json(data)


@pytest.mark.parametrize(
    "mutate, error_pattern",
    [
        (lambda d: d.__setitem__("format_version", "2.0"), "format_version"),
        (lambda d: d.__setitem__("banks", []), "banks"),
        (lambda d: d["banks"][0][0].__setitem__("dco2_tune", 300), "300"),
        (lambda d: d["banks"][0][0].__setitem__("lfo_waveform", "triangle"), "triangle"),
        (lambda d: d["banks"][0][0].__setitem__("chorus", "on"), "'on'"),
        (lambda d: d["banks"][0][0].__setitem__("mystery", 16), "16"),
    ],
)
def test_validate_rejects_invalid(mutate, error_pattern: str) -> None:
    """validate_bank_json must reject obvious schema violations."""
    banks = [[JX3PPatch() for _ in range(16)] for _ in range(2)]
    data = {
        "format_version": "1.0",
        "banks": [[p.to_dict() for p in bank] for bank in banks],
    }
    mutate(data)
    with pytest.raises(jsonschema.ValidationError, match=error_pattern):
        formats.validate_bank_json(data)
