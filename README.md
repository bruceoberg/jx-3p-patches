# jx-3p-patches

Tools for reading and writing patch files for the **Roland JX-3P** synthesiser.

The JX-3P has no MIDI patch dump capability — the only way to back up its patches is to record a tape dump (FSK-encoded audio) via the cassette out jack. This project provides:

- A **C decoder** that converts a tape-dump WAV file into CSV
- A **C encoder** that converts a CSV back into a tape-dump WAV file
- A Python package (`jx3p`) — *in progress* — that mirrors the C tools and adds JSON ↔ WAV/CSV conversion
- **JSON Schemas** describing the patch and bank formats

End-user musician install instructions are in [docs/install.md](docs/install.md). The rest of this README is for people building from source.

## Credits

This project bundles work from several authors:

- The **tape decoder** (`c/decoder/`) was originally written by **Shawn Thomas (phaysis)** in 2013. See <http://www.phaysis.com/projects/roland-jx-3p-tape-dump-patch-decoder/>. Released by the author to the public domain.
- The **tape encoder** (`c/encoder/`) was written by **Jarkko Viikki (jviikki)** in 2019. MIT-licensed.
- The reorganisation, Python port, JSON format, and build/test infrastructure are by **bruce oberg**, 2026. MIT-licensed.

See [LICENSE](LICENSE) for the project-wide license.

## Project layout

```
c/
  decoder/        — C decoder (phaysis):  WAV → CSV
  encoder/        — C encoder (jviikki):  CSV → WAV
  Makefile        — orchestrates the C build
jx3p/             — Python package (in progress)
schemas/          — JSON Schemas (single patch + 2-bank collection)
tests/            — pytest suite (parity tests against the C decoder)
testdata/         — original sample WAV/CSV from upstream
docs/             — documentation
build/            — C build artifacts (gitignored)
Makefile          — root: delegates `make c`, `make test`, `make install`
pyproject.toml    — Python package metadata (uv-managed)
shell.nix         — Nix dev environment
shell.zsh         — Homebrew-based installer for non-Nix macOS users
```

## Building from source

The toolchain you need:

- A C compiler (`clang` on macOS, `gcc` on Linux)
- GNU `make`
- `libsndfile` (the only non-stdlib C dependency)
- `uv` (drives Python package management and tests)

Pick whichever section below matches your setup.

### macOS / Linux with Nix (recommended for developers)

[shell.nix](shell.nix) declares the full toolchain. With direnv:

```sh
direnv allow
make
```

Without direnv:

```sh
nix-shell
make
```

### macOS without Nix (musician-friendly)

Run the bundled installer once. It installs Xcode Command Line Tools (clang + make), Homebrew, libsndfile, and uv:

```sh
./shell.zsh
```

The script is idempotent — safe to re-run. Then build:

```sh
make
```

### Linux without Nix

On Debian / Ubuntu:

```sh
sudo apt install build-essential libsndfile1-dev
curl -LsSf https://astral.sh/uv/install.sh | sh
make
```

On other distros, install equivalent packages (`libsndfile-devel` on Fedora, `libsndfile-dev` on Arch, etc.).

### Build targets

From the repo root:

| Target | Effect |
|---|---|
| `make` / `make all` | Build C tools and run Python tests |
| `make c` | Build the C tools only |
| `make test` | Run `pytest tests/` via `uv` |
| `make install` | `uv tool install .` (puts `jx3p` on your PATH) |
| `make clean` | Remove `build/` |

After `make c`, all binaries live under `build/decoder/bin/` and `build/encoder/bin/`.

## CLI tools

### C decoder — WAV → CSV

| Tool | Description |
|---|---|
| `build/decoder/bin/decode_patches WAV` | Decode a tape-dump WAV. Writes `patchdump.csv` in the current directory. |
| `build/decoder/bin/analyzer WAV` | *(diagnostic)* Emit zero-crossing lengths from a WAV. |
| `build/decoder/bin/bitstream WAV` | *(diagnostic)* Emit the raw FSK bitstream from a WAV. |
| `build/decoder/bin/c1diff WAV1 WAV2` | *(diagnostic)* Compare patch C01 between two tape dumps. |

For best decode results, see the audio-preparation notes in [c/decoder/USAGE.txt](c/decoder/USAGE.txt) — short version: 16-bit mono, 44.1 kHz, normalised between -12 dB and -1 dB, recorded directly from the JX-3P tape jack.

### C encoder — CSV → WAV

| Tool | Description |
|---|---|
| `build/encoder/bin/writer INPUT.csv OUTPUT.wav` | Encode a CSV patch bank into a tape-dump WAV. |
| `build/encoder/bin/reader WAV` | *(diagnostic)* Dump WAV samples as integers, one per line. |

### Python — JSON ↔ WAV/CSV

After `make install` (or `uv tool install .`), the `jx3p` command is on your PATH:

| Subcommand | Description |
|---|---|
| `jx3p wav-to-json IN.wav OUT.json` | Decode a tape-dump WAV into JSON. |
| `jx3p json-to-wav IN.json OUT.wav` | Encode a JSON patch bank into a tape-dump WAV. |
| `jx3p csv-to-json IN.csv OUT.json` | Convert a CSV patch bank to JSON. |
| `jx3p json-to-csv IN.json OUT.csv` | Convert a JSON patch bank to CSV. |

> **Status:** the dataclass and JSON schemas are complete; codec and formats I/O are still stubs. Use the C tools for actual conversions today.

## License

MIT for the encoder, Python package, schemas, and infrastructure (see [LICENSE](LICENSE)). The decoder code was released to the public domain by its original author.
