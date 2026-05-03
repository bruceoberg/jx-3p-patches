# JX-3P JSON patch format

This is the human- and machine-friendly serialisation used by the Python `jx3p` tool. It is the canonical interchange format for this project — CSV exists for historical compatibility with the C tools, WAV is the format the JX-3P itself speaks, but JSON is what people should edit by hand or programmatically.

The format is described by two JSON Schemas:

- [schemas/patch.schema.json](../schemas/patch.schema.json) — a single patch object
- [schemas/bank.schema.json](../schemas/bank.schema.json) — a full 2-bank, 32-patch collection

Both validate as JSON Schema 2020-12.

## Top-level shape

```json
{
  "format_version": "1.0",
  "banks": [
    [ /* 16 patch objects, bank C, slots C01..C16 */ ],
    [ /* 16 patch objects, bank D, slots D01..D16 */ ]
  ]
}
```

Bank order is fixed: `banks[0]` = panel C, `banks[1]` = panel D, matching the CSV row order produced by the C decoder.

## Patch object

Every patch carries every field from the byte format ([patch-format.md](patch-format.md)) except for the wire-only fields (`datatype`, `bank_ab`, `bank_cd`, `patch_num`, `checksum`), which are derived from the bank/slot position and from the data itself when re-encoding.

```json
{
  "dco1_range": "16'",
  "dco1_waveform": "saw",
  "dco1_fmod_lfo": false,
  "dco1_fmod_env": false,
  "dco2_range": "8'",
  "dco2_waveform": "pulse",
  "dco2_crossmod": "off",
  "dco2_tune": 127,
  "dco2_fine_tune": 177,
  "dco2_fmod_lfo": true,
  "dco2_fmod_env": false,
  "dco_lfo_amount": 44,
  "dco_env_amount": 89,
  "dco_env_polarity": "pos",
  "vcf_mix": 71,
  "vcf_hpf": 17,
  "vcf_cutoff": 162,
  "vcf_lfo_mod": 0,
  "vcf_pitch_follow": 195,
  "vcf_resonance": 67,
  "vcf_env_mod": 22,
  "vcf_env_polarity": "pos",
  "vca_mode": "env",
  "vca_level": 76,
  "chorus": true,
  "lfo_waveform": "sine",
  "lfo_delay": 99,
  "lfo_rate": 254,
  "env_attack": 11,
  "env_decay": 73,
  "env_sustain": 215,
  "env_release": 146,
  "mystery": 0,
  "_patch_name": "Brass 1"
}
```

`_patch_name` is the only optional field. It does not exist in the original JX-3P format — the synth has no notion of a patch name. It is included here so users can label patches in JSON.

## Field type rules

The Python dataclass [jx3p/patch.py](../jx3p/patch.py) is the source of truth for what type each field has in JSON.

### Multi-value enums → strings

Fields that have three or four discrete values are stored as strings, using the same labels the C decoder writes to CSV:

| Field | Allowed values |
|---|---|
| `dco1_range`, `dco2_range` | `"16'"`, `"8'"`, `"4'"` |
| `dco1_waveform` | `"saw"`, `"pulse"`, `"square"` |
| `dco2_waveform` | `"saw"`, `"pulse"`, `"square"`, `"noise"` |
| `dco2_crossmod` | `"off"`, `"sync"`, `"metal"` |
| `lfo_waveform` | `"sine"`, `"square"`, `"random"`, `"fast random"` |

### Two-value enums → strings (for readability)

Three of the 1-bit fields are also stored as strings, even though they only have two values, because the labels are more readable than booleans for these particular fields:

| Field | Allowed values |
|---|---|
| `dco_env_polarity`, `vcf_env_polarity` | `"neg"`, `"pos"` |
| `vca_mode` | `"gate"`, `"env"` |

### Other 1-bit fields → booleans

Modulation enables and chorus are JSON booleans:

| Field | `true` means |
|---|---|
| `dco1_fmod_lfo`, `dco1_fmod_env` | DCO-1 modulation source enabled |
| `dco2_fmod_lfo`, `dco2_fmod_env` | DCO-2 modulation source enabled |
| `chorus` | chorus on |

In CSV these are written as `0` / `1` and `off` / `on`.

### Integer fields → integers

| Field | Range |
|---|---|
| All `*_tune`, `*_amount`, `*_mix`, `*_hpf`, `*_cutoff`, `*_mod`, `*_follow`, `*_resonance`, `*_level`, `*_delay`, `*_rate`, `env_*` | `0..255` |
| `mystery` | `0..15` |

## Format versioning

`format_version` is `"1.0"` and is required at the top level. The schema rejects any other value. Any breaking change (renamed field, type change, new required field) bumps the major version.

## Round-trip guarantees

When implemented end-to-end, the following operations are intended to be lossless:

- `WAV → JSON → WAV` reproduces a byte-identical WAV (modulo the FSK encoder's deterministic timing).
- `JSON → CSV → JSON` reproduces the same JSON, except `_patch_name` is dropped (CSV has no column for it).
- `CSV → JSON → CSV` reproduces the same CSV byte-for-byte.

The `mystery` field is preserved by every conversion. See [patch-format.md](patch-format.md#mystery-byte-6-bits-4-7) for why this matters.

## Status

The schemas, the in-memory dataclass ([jx3p/patch.py](../jx3p/patch.py)), the WAV codec ([jx3p/codec.py](../jx3p/codec.py)), and the CSV/JSON readers and writers ([jx3p/formats.py](../jx3p/formats.py)) are all implemented and covered by the test suite. The CLI subcommands `jx3p wav-to-json`, `json-to-wav`, `csv-to-json`, and `json-to-csv` are fully wired up and exercised against the golden fixtures.
