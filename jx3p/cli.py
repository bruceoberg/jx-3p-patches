"""Command-line entry point for the jx3p tool.

Usage examples for end users (musicians):

    jx3p wav-to-json mydump.wav patches.json
    jx3p json-to-wav patches.json mydump.wav
    jx3p csv-to-json patches.csv patches.json
    jx3p json-to-csv patches.json patches.csv

Run ``jx3p --help`` for the full list of commands.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jx3p",
        description=(
            "Read and write Roland JX-3P patch files. "
            "Convert between tape-dump WAV files, CSV, and JSON."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    p_w2j = sub.add_parser(
        "wav-to-json",
        help="Decode a JX-3P tape-dump WAV file into a JSON patch bank.",
    )
    p_w2j.add_argument("wav", type=Path, help="Input .wav file from your tape recorder.")
    p_w2j.add_argument("json", type=Path, help="Output .json file to create.")

    p_j2w = sub.add_parser(
        "json-to-wav",
        help="Encode a JSON patch bank into a JX-3P tape-dump WAV file.",
    )
    p_j2w.add_argument("json", type=Path, help="Input .json file with your patches.")
    p_j2w.add_argument("wav", type=Path, help="Output .wav file to create (play this into your JX-3P).")

    p_c2j = sub.add_parser(
        "csv-to-json",
        help="Convert a CSV patch bank into JSON.",
    )
    p_c2j.add_argument("csv", type=Path, help="Input .csv file.")
    p_c2j.add_argument("json", type=Path, help="Output .json file to create.")

    p_j2c = sub.add_parser(
        "json-to-csv",
        help="Convert a JSON patch bank into CSV.",
    )
    p_j2c.add_argument("json", type=Path, help="Input .json file.")
    p_j2c.add_argument("csv", type=Path, help="Output .csv file to create.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    from jx3p import codec, formats

    if args.command == "wav-to-json":
        banks = codec.read_wav(args.wav)
        formats.write_json(args.json, banks)
    elif args.command == "json-to-wav":
        banks = formats.read_json(args.json)
        codec.write_wav(args.wav, banks)
    elif args.command == "csv-to-json":
        banks = formats.read_csv(args.csv)
        formats.write_json(args.json, banks)
    elif args.command == "json-to-csv":
        banks = formats.read_json(args.json)
        formats.write_csv(args.csv, banks)
    else:
        parser.error(f"unknown command: {args.command}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
