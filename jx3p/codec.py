"""WAV ↔ patch struct codec.

The JX-3P encodes patches as FSK audio: 882 Hz cycles represent a 1 bit and
3675 Hz cycles represent a 0 bit. Each patch record is 26 bytes, transmitted
as 26 11-bit serial frames (start bit 0, 8 data bits LSB-first, two stop bits).
A bank holds 16 patches; both banks of 32 patches are dumped, with each patch
transmitted twice for redundancy.

This module mirrors the C decoder (c/decoder/) and encoder (c/encoder/).
"""

from __future__ import annotations

from pathlib import Path

from jx3p.patch import JX3PPatch


def read_wav(path: str | Path) -> list[list[JX3PPatch]]:
    """Decode a JX-3P tape-dump WAV file into a 2x16 list of patches.

    Returned shape: ``[bank][patch_num]``, with bank 0 = C bank and bank 1 = D
    bank, matching the C decoder's CSV row order.
    """
    raise NotImplementedError


def write_wav(path: str | Path, banks: list[list[JX3PPatch]]) -> None:
    """Encode a 2x16 list of patches back into a JX-3P tape-dump WAV file."""
    raise NotImplementedError
