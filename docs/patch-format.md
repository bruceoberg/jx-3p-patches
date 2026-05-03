# JX-3P patch byte format

A single JX-3P patch is **26 bytes** on the wire. The first 25 bytes hold the patch parameters; byte 25 is a checksum (the sum of bytes 0–24 mod 256).

A full tape dump contains **two banks of 16 patches** (32 patches total), with each patch transmitted twice for redundancy. Bank 0 is panel "C" (`bank_cd = 2`), bank 1 is panel "D" (`bank_cd = 3`).

The single source of truth for the byte layout is the C union in [c/include/jx3p_patch.h](../c/include/jx3p_patch.h). This document is a reference rendering of the same information.

## Byte-by-byte layout

Within each byte, **bit 0 is the LSB** (least significant). Multi-bit fields use the natural binary value.

| Byte | Bits | Field | Type | Notes |
|---|---|---|---|---|
| 0 | 0-5 | *(unused)* | | |
| 0 | 6-7 | `datatype` | uint2 | 2 = patch, 3 = sequence |
| 1 | 0-1 | `bank_ab` | uint2 | A/B bank (legacy) |
| 1 | 2-7 | *(unused)* | | |
| 2 | 0-1 | `bank_cd` | uint2 | C = 2, D = 3 |
| 2 | 2-7 | *(unused)* | | |
| 3 | 0-3 | `patch_num` | uint4 | 0..15 |
| 3 | 4-7 | *(unused)* | | |
| 4 | 0-1 | `dco1_range` | enum2 | A01: 0=`16'`, 1=`8'`, 2=`4'` |
| 4 | 2-3 | `dco1_waveform` | enum2 | A02: 0=saw, 1=pulse, 2=square |
| 4 | 4-5 | `dco2_range` | enum2 | A05: 0=`16'`, 1=`8'`, 2=`4'` |
| 4 | 6-7 | `dco2_waveform` | enum2 | A06: 0=saw, 1=pulse, 2=square, 3=noise |
| 5 | 0-1 | `dco2_crossmod` | enum2 | A07: 0=off, 1=sync, 2=metal |
| 5 | 2 | `vcf_env_polarity` | bit | B06: 0=neg, 1=pos *(see note)* |
| 5 | 3 | `vca_mode` | bit | B07: 0=gate, 1=env |
| 5 | 4 | `dco2_fmod_env` | bit | A11: DCO-2 ENV mod on/off |
| 5 | 5 | `dco2_fmod_lfo` | bit | A10: DCO-2 LFO mod on/off |
| 5 | 6 | `dco1_fmod_env` | bit | A04: DCO-1 ENV mod on/off |
| 5 | 7 | `dco1_fmod_lfo` | bit | A03: DCO-1 LFO mod on/off |
| 6 | 0-1 | `lfo_waveform` | enum2 | B10: 0=sine, 1=square, 2=random, 3=fast random |
| 6 | 2 | `dco_env_polarity` | bit | A14: 0=neg, 1=pos |
| 6 | 3 | `chorus` | bit | B09: 0=off, 1=on |
| 6 | 4-7 | `mystery` | uint4 | **Preserve verbatim.** See note below. |
| 7 | 0-7 | `dco2_fine_tune` | uint8 | A09 |
| 8 | 0-7 | `dco2_tune` | uint8 | A08 |
| 9 | 0-7 | `dco_env_amount` | uint8 | A13 |
| 10 | 0-7 | `dco_lfo_amount` | uint8 | A12 |
| 11 | 0-7 | `vcf_mix` | uint8 | A15 |
| 12 | 0-7 | `vcf_hpf` | uint8 | A16 |
| 13 | 0-7 | `vcf_resonance` | uint8 | B04 |
| 14 | 0-7 | `vcf_cutoff` | uint8 | B01 |
| 15 | 0-7 | `vcf_env_mod` | uint8 | B05 |
| 16 | 0-7 | `vcf_lfo_mod` | uint8 | B02 |
| 17 | 0-7 | `vcf_pitch_follow` | uint8 | B03 |
| 18 | 0-7 | `vca_level` | uint8 | B08 |
| 19 | 0-7 | `lfo_rate` | uint8 | B12 |
| 20 | 0-7 | `lfo_delay` | uint8 | B11 |
| 21 | 0-7 | `env_attack` | uint8 | B13 |
| 22 | 0-7 | `env_decay` | uint8 | B14 |
| 23 | 0-7 | `env_sustain` | uint8 | B15 |
| 24 | 0-7 | `env_release` | uint8 | B16 |
| 25 | 0-7 | `checksum` | uint8 | `(sum of bytes 0..24) mod 256` |

The "panel" column (`A01`, `B07`, etc.) refers to the parameter labels printed on the JX-3P front panel.

## Notes

### `mystery` (byte 6, bits 4-7)

These four bits have no documented purpose — jviikki noted that the JX-3P transmits them during a tape dump and that the synth's **verify** function fails if they are altered. Every conversion in this project (decoder → CSV, CSV → encoder, JSON → WAV, etc.) preserves them verbatim. When generating a patch from scratch, leave `mystery = 0`.

### `vcf_env_polarity` (byte 5, bit 2)

The original C header comment reads `0=positive, 1=negative?` — note the question mark. The CSV emitter, however, treats the bit identically to `dco_env_polarity` (`0 → "neg"`, `1 → "pos"`). This project follows the CSV convention. If hardware testing later contradicts this, the schema and CSV mapping will need to flip.

### `bank_ab` (byte 1, bits 0-1)

This is a legacy field from older synths in the same family. The JX-3P writes it but ignores it on read. The encoder stores `bank_num` (0 or 1) here.

### Bit and byte order on the wire

Each byte is transmitted as an **11-bit serial frame** over an FSK-modulated audio carrier:

```
0 d0 d1 d2 d3 d4 d5 d6 d7 1 1
^                          ^^
start bit                  two stop bits
```

Data bits go out **LSB first** (`d0` = bit 0). FSK frequencies: `882 Hz` cycle = a 1 bit, `3675 Hz` cycle = a 0 bit. Each patch record (26 bytes × 11 bits = 286 bits) is followed by ~48 bits of all-1s as a separator tone.

The full tape stream is a long pilot tone, then 32 patch records (each transmitted twice with separators between), then trailing silence.

## See also

- [c/include/jx3p_patch.h](../c/include/jx3p_patch.h) — the canonical struct layout
- [c/decoder/USAGE.txt](../c/decoder/USAGE.txt) — audio recording requirements for reliable decode
- [json-schema.md](json-schema.md) — JSON serialisation of the patch fields
