"""Round-trip tests for the Python codec.

Cover the directions that don't depend on jx3p.formats yet:

  WAV -> patches -> WAV -> patches             (Python alone, lossless?)
  WAV -> patches -> WAV -> CSV (via C decoder) (Python encoder ↔ C decoder)

CSV/JSON round-trips via jx3p.formats live in tests/test_formats.py once
that module is implemented.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from jx3p import codec


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOLDEN_WAV = FIXTURES / "patchdump.wav"
GOLDEN_CSV = FIXTURES / "patchdump.csv"
DECODER_BIN = REPO_ROOT / "build" / "decoder" / "bin" / "decode_patches"


@pytest.fixture(scope="session")
def decoder_binary() -> Path:
    if not DECODER_BIN.exists():
        pytest.skip(f"decoder binary not built; run `make -C c` first ({DECODER_BIN})")
    return DECODER_BIN


def test_wav_patches_wav_patches_is_lossless(tmp_path: Path) -> None:
    """read_wav → write_wav → read_wav reproduces every patch field."""
    banks_in = codec.read_wav(GOLDEN_WAV)
    out_wav = tmp_path / "roundtrip.wav"
    codec.write_wav(out_wav, banks_in)
    banks_out = codec.read_wav(out_wav)

    for bank_idx in range(2):
        for slot in range(16):
            assert banks_in[bank_idx][slot] == banks_out[bank_idx][slot], (
                f"patch at bank {bank_idx}, slot {slot} changed across round-trip"
            )


def test_c_decoder_accepts_python_encoded_wav(decoder_binary: Path, tmp_path: Path) -> None:
    """A WAV the Python encoder produced must decode to the golden CSV via the C tool."""
    banks_in = codec.read_wav(GOLDEN_WAV)
    out_wav = tmp_path / "roundtrip.wav"
    codec.write_wav(out_wav, banks_in)

    out_csv = tmp_path / "roundtrip.csv"
    subprocess.run(
        [str(decoder_binary), str(out_wav), str(out_csv)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert out_csv.read_bytes() == GOLDEN_CSV.read_bytes(), (
        "C decoder produced different CSV from a Python-encoded WAV"
    )
