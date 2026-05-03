"""JX3PPatch dataclass and conversion helpers.

A single JX-3P patch is 26 bytes on the wire (byte 25 is a checksum).
This module exposes the decoded fields as a flat dataclass with no I/O —
WAV/CSV/JSON conversion lives in jx3p.codec and jx3p.formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any


# String-enum tables for multi-bit fields. Values match the labels emitted by
# the C decoder (c/decoder/src/decoder_patch.c) and accepted by the C encoder
# (c/encoder/csv_parser.c). Keep these in lockstep with patch.schema.json.
# 1-bit fields are stored as plain bools; CSV serialization (in jx3p.formats)
# is responsible for mapping bools to the CSV labels (on/off, neg/pos, etc.).

DCO_RANGE = ["16'", "8'", "4'"]
DCO1_WAVEFORM = ["saw", "pulse", "square"]
DCO2_WAVEFORM = ["saw", "pulse", "square", "noise"]
DCO_CROSSMOD = ["off", "sync", "metal"]
LFO_WAVEFORM = ["sine", "square", "random", "fast random"]
ENV_POLARITY = ["neg", "pos"]
VCA_MODE = ["gate", "env"]


@dataclass
class JX3PPatch:
    """One JX-3P patch.

    All fields default to a zero-initialised state, matching what the C
    decoder produces from a freshly-zeroed 26-byte record.
    """

    # DCO-1 (panel A01-A04)
    dco1_range: str = "16'"
    dco1_waveform: str = "saw"
    dco1_fmod_lfo: bool = False
    dco1_fmod_env: bool = False

    # DCO-2 (panel A05-A11)
    dco2_range: str = "16'"
    dco2_waveform: str = "saw"
    dco2_crossmod: str = "off"
    dco2_tune: int = 0
    dco2_fine_tune: int = 0
    dco2_fmod_lfo: bool = False
    dco2_fmod_env: bool = False

    # DCO LFO/ENV amount and polarity (panel A12-A14)
    dco_lfo_amount: int = 0
    dco_env_amount: int = 0
    dco_env_polarity: str = "neg"

    # VCF (panel A15-A16, B01-B06)
    vcf_mix: int = 0
    vcf_hpf: int = 0
    vcf_cutoff: int = 0
    vcf_lfo_mod: int = 0
    vcf_pitch_follow: int = 0
    vcf_resonance: int = 0
    vcf_env_mod: int = 0
    vcf_env_polarity: str = "neg"

    # VCA, chorus (panel B07-B09)
    vca_mode: str = "gate"
    vca_level: int = 0
    chorus: bool = False

    # LFO (panel B10-B12)
    lfo_waveform: str = "sine"
    lfo_delay: int = 0
    lfo_rate: int = 0

    # ADSR (panel B13-B16)
    env_attack: int = 0
    env_decay: int = 0
    env_sustain: int = 0
    env_release: int = 0

    # Byte 6 bits 4-7. Purpose unknown; preserved for the JX-3P verify function.
    mystery: int = 0

    # Optional human-readable name (not part of the original JX-3P format).
    _patch_name: str | None = field(default=None)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict matching patch.schema.json."""
        out: dict[str, Any] = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if f.name == "_patch_name":
                if value is not None:
                    out[f.name] = value
            else:
                out[f.name] = value
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JX3PPatch":
        """Construct a patch from a dict (e.g. parsed from JSON).

        Unknown keys are rejected; missing required keys raise KeyError.
        """
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"unknown patch fields: {sorted(unknown)}")
        return cls(**data)

    @classmethod
    def from_bytes(cls, raw: bytes) -> "JX3PPatch":
        """Construct a patch from its 26-byte tape-dump representation.

        The wire-only fields (datatype, bank_ab, bank_cd, patch_num, checksum)
        are not part of JX3PPatch — they're recoverable from the bank/slot
        position and recomputed on encode. Out-of-range enum bits wrap
        modulo the enum size, matching the C decoder's behaviour.
        """
        if len(raw) != 26:
            raise ValueError(f"expected 26 bytes, got {len(raw)}")

        b4, b5, b6 = raw[4], raw[5], raw[6]
        return cls(
            dco1_range=DCO_RANGE[((b4 >> 0) & 0x3) % len(DCO_RANGE)],
            dco1_waveform=DCO1_WAVEFORM[((b4 >> 2) & 0x3) % len(DCO1_WAVEFORM)],
            dco2_range=DCO_RANGE[((b4 >> 4) & 0x3) % len(DCO_RANGE)],
            dco2_waveform=DCO2_WAVEFORM[((b4 >> 6) & 0x3) % len(DCO2_WAVEFORM)],
            dco2_crossmod=DCO_CROSSMOD[((b5 >> 0) & 0x3) % len(DCO_CROSSMOD)],
            vcf_env_polarity=ENV_POLARITY[(b5 >> 2) & 0x1],
            vca_mode=VCA_MODE[(b5 >> 3) & 0x1],
            dco2_fmod_env=bool((b5 >> 4) & 0x1),
            dco2_fmod_lfo=bool((b5 >> 5) & 0x1),
            dco1_fmod_env=bool((b5 >> 6) & 0x1),
            dco1_fmod_lfo=bool((b5 >> 7) & 0x1),
            lfo_waveform=LFO_WAVEFORM[((b6 >> 0) & 0x3) % len(LFO_WAVEFORM)],
            dco_env_polarity=ENV_POLARITY[(b6 >> 2) & 0x1],
            chorus=bool((b6 >> 3) & 0x1),
            mystery=(b6 >> 4) & 0xF,
            dco2_fine_tune=raw[7],
            dco2_tune=raw[8],
            dco_env_amount=raw[9],
            dco_lfo_amount=raw[10],
            vcf_mix=raw[11],
            vcf_hpf=raw[12],
            vcf_resonance=raw[13],
            vcf_cutoff=raw[14],
            vcf_env_mod=raw[15],
            vcf_lfo_mod=raw[16],
            vcf_pitch_follow=raw[17],
            vca_level=raw[18],
            lfo_rate=raw[19],
            lfo_delay=raw[20],
            env_attack=raw[21],
            env_decay=raw[22],
            env_sustain=raw[23],
            env_release=raw[24],
        )

    def to_bytes(self, bank_index: int, patch_num: int) -> bytes:
        """Serialise as the 26-byte tape-dump representation.

        bank_index is 0 (C bank) or 1 (D bank); patch_num is 0..15.
        The checksum byte is computed from the preceding 25 bytes.
        """
        if bank_index not in (0, 1):
            raise ValueError(f"bank_index must be 0 or 1, got {bank_index}")
        if not 0 <= patch_num <= 15:
            raise ValueError(f"patch_num must be 0..15, got {patch_num}")

        out = bytearray(26)
        out[0] = (2 << 6)  # datatype = 2 (patch)
        out[1] = bank_index & 0x3  # bank_ab (legacy field, mirrors bank index)
        out[2] = (bank_index + 2) & 0x3  # bank_cd: 2 = C, 3 = D
        out[3] = patch_num & 0xF
        out[4] = (
            (DCO_RANGE.index(self.dco1_range) & 0x3)
            | ((DCO1_WAVEFORM.index(self.dco1_waveform) & 0x3) << 2)
            | ((DCO_RANGE.index(self.dco2_range) & 0x3) << 4)
            | ((DCO2_WAVEFORM.index(self.dco2_waveform) & 0x3) << 6)
        )
        out[5] = (
            (DCO_CROSSMOD.index(self.dco2_crossmod) & 0x3)
            | ((ENV_POLARITY.index(self.vcf_env_polarity) & 0x1) << 2)
            | ((VCA_MODE.index(self.vca_mode) & 0x1) << 3)
            | ((int(self.dco2_fmod_env) & 0x1) << 4)
            | ((int(self.dco2_fmod_lfo) & 0x1) << 5)
            | ((int(self.dco1_fmod_env) & 0x1) << 6)
            | ((int(self.dco1_fmod_lfo) & 0x1) << 7)
        )
        out[6] = (
            (LFO_WAVEFORM.index(self.lfo_waveform) & 0x3)
            | ((ENV_POLARITY.index(self.dco_env_polarity) & 0x1) << 2)
            | ((int(self.chorus) & 0x1) << 3)
            | ((self.mystery & 0xF) << 4)
        )
        out[7] = self.dco2_fine_tune
        out[8] = self.dco2_tune
        out[9] = self.dco_env_amount
        out[10] = self.dco_lfo_amount
        out[11] = self.vcf_mix
        out[12] = self.vcf_hpf
        out[13] = self.vcf_resonance
        out[14] = self.vcf_cutoff
        out[15] = self.vcf_env_mod
        out[16] = self.vcf_lfo_mod
        out[17] = self.vcf_pitch_follow
        out[18] = self.vca_level
        out[19] = self.lfo_rate
        out[20] = self.lfo_delay
        out[21] = self.env_attack
        out[22] = self.env_decay
        out[23] = self.env_sustain
        out[24] = self.env_release
        out[25] = sum(out[:25]) & 0xFF
        return bytes(out)

    def validate(self) -> None:
        """Check enum membership and integer ranges. Raises ValueError on failure."""
        _check_enum("dco1_range", self.dco1_range, DCO_RANGE)
        _check_enum("dco1_waveform", self.dco1_waveform, DCO1_WAVEFORM)
        _check_bool("dco1_fmod_lfo", self.dco1_fmod_lfo)
        _check_bool("dco1_fmod_env", self.dco1_fmod_env)

        _check_enum("dco2_range", self.dco2_range, DCO_RANGE)
        _check_enum("dco2_waveform", self.dco2_waveform, DCO2_WAVEFORM)
        _check_enum("dco2_crossmod", self.dco2_crossmod, DCO_CROSSMOD)
        _check_uint8("dco2_tune", self.dco2_tune)
        _check_uint8("dco2_fine_tune", self.dco2_fine_tune)
        _check_bool("dco2_fmod_lfo", self.dco2_fmod_lfo)
        _check_bool("dco2_fmod_env", self.dco2_fmod_env)

        _check_uint8("dco_lfo_amount", self.dco_lfo_amount)
        _check_uint8("dco_env_amount", self.dco_env_amount)
        _check_enum("dco_env_polarity", self.dco_env_polarity, ENV_POLARITY)

        _check_uint8("vcf_mix", self.vcf_mix)
        _check_uint8("vcf_hpf", self.vcf_hpf)
        _check_uint8("vcf_cutoff", self.vcf_cutoff)
        _check_uint8("vcf_lfo_mod", self.vcf_lfo_mod)
        _check_uint8("vcf_pitch_follow", self.vcf_pitch_follow)
        _check_uint8("vcf_resonance", self.vcf_resonance)
        _check_uint8("vcf_env_mod", self.vcf_env_mod)
        _check_enum("vcf_env_polarity", self.vcf_env_polarity, ENV_POLARITY)

        _check_enum("vca_mode", self.vca_mode, VCA_MODE)
        _check_uint8("vca_level", self.vca_level)
        _check_bool("chorus", self.chorus)

        _check_enum("lfo_waveform", self.lfo_waveform, LFO_WAVEFORM)
        _check_uint8("lfo_delay", self.lfo_delay)
        _check_uint8("lfo_rate", self.lfo_rate)

        _check_uint8("env_attack", self.env_attack)
        _check_uint8("env_decay", self.env_decay)
        _check_uint8("env_sustain", self.env_sustain)
        _check_uint8("env_release", self.env_release)

        if not isinstance(self.mystery, int) or isinstance(self.mystery, bool) or not 0 <= self.mystery <= 15:
            raise ValueError(f"mystery must be int 0..15, got {self.mystery!r}")

        if self._patch_name is not None and not isinstance(self._patch_name, str):
            raise ValueError(f"_patch_name must be str or None, got {type(self._patch_name).__name__}")


def _check_enum(name: str, value: Any, allowed: list[str]) -> None:
    if value not in allowed:
        raise ValueError(f"{name} must be one of {allowed}, got {value!r}")


def _check_bool(name: str, value: Any) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be bool, got {value!r}")


def _check_uint8(name: str, value: Any) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 255:
        raise ValueError(f"{name} must be int 0..255, got {value!r}")
