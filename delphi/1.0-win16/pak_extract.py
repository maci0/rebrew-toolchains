#!/usr/bin/env python3
"""pak_extract.py — Quantum archive (.PAK) extractor, reverse-engineered.

Delphi 1.0 / Borland installer archives (CMDLINE.PAK, UNITS.PAK, LIB.PAK,
BIN.CA1/CA2, ...) use the "Quantum" compression format created by David
Stafford (Cinematronics, 1993-1995) and licensed to Borland, Microsoft and
Novell. Quantum is also one of the Microsoft CAB compression methods.

This file is a from-scratch Python implementation of the format, produced by
reverse-engineering the archives on the Borland Delphi 1.0 Desktop Edition
floppy (September 1995). It reads the same header layout and arithmetic-coded
LZ77 stream that the original UNPAQ.EXE (Quantum 0.92) produces.

Algorithm
---------
- Header:  "DS" magic, major/minor version, file count (u16 LE), table size
  (window = 2^N), compression flags.
- Per-file entry: varstring name, varstring comment, expanded size (u32 LE),
  DOS time (u16), DOS date (u16).
- Data: all files form ONE continuous stream of arithmetic-coded LZ77.
  Between files a 16-bit checksum is embedded in the raw bit stream (not
  passed through the arithmetic decoder); coder state and adaptive models
  persist across file boundaries.
- Coder: 16-bit range coder (H/L/C), MSB-first bit reader feeding 16-bit
  big-endian words. 9 adaptive frequency models (4 literal bands of 64,
  3 position-slot models, 1 length-slot model, 1 selector model) with
  cumulative frequencies, +8 update per decoded symbol and rescaling when
  the total exceeds 3800.
- Matches: selector 4 = 3-byte match, 5 = 4-byte match, 6 = variable length
  (length slots 0..26 with 0-5 extra bits, then position slot). Offsets use
  42 position slots with 0-19 extra bits.

Reference implementations used for cross-validation (all public domain /
MIT / LGPL lineage):
- QUANTUM.DOC (official spec, Cinematronics)
- libmspack QTM decoder by Stuart Caie (LGPL 2.1)
- Matthew Russotto's Quantum research
- unquantum by David Carrero Fernandez-Baillo (MIT) — used to validate
  this port byte-for-byte against real archives.

Usage:
    python3 pak_extract.py -lo ARCHIVE.PAK        # list contents
    python3 pak_extract.py -x -o OUTDIR ARCHIVE.PAK   # extract
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Static tables (from QUANTUM.DOC / libmspack)
# ---------------------------------------------------------------------------

# 42 position slots -> base match offsets
POSITION_BASE: list[int] = [
    0,
    1,
    2,
    3,
    4,
    6,
    8,
    12,
    16,
    24,
    32,
    48,
    64,
    96,
    128,
    192,
    256,
    384,
    512,
    768,
    1024,
    1536,
    2048,
    3072,
    4096,
    6144,
    8192,
    12288,
    16384,
    24576,
    32768,
    49152,
    65536,
    98304,
    131072,
    196608,
    262144,
    393216,
    524288,
    786432,
    1048576,
    1572864,
]

# extra bits per position slot
EXTRA_BITS: list[int] = [
    0,
    0,
    0,
    0,
    1,
    1,
    2,
    2,
    3,
    3,
    4,
    4,
    5,
    5,
    6,
    6,
    7,
    7,
    8,
    8,
    9,
    9,
    10,
    10,
    11,
    11,
    12,
    12,
    13,
    13,
    14,
    14,
    15,
    15,
    16,
    16,
    17,
    17,
    18,
    18,
    19,
    19,
]

# 27 length slots -> base lengths (selector 6, variable-length matches)
LENGTH_BASE: list[int] = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    8,
    10,
    12,
    14,
    18,
    22,
    26,
    30,
    38,
    46,
    54,
    62,
    78,
    94,
    110,
    126,
    158,
    190,
    222,
    254,
]

# extra bits per length slot
LENGTH_EXTRA: list[int] = [
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    1,
    1,
    1,
    2,
    2,
    2,
    2,
    3,
    3,
    3,
    3,
    4,
    4,
    4,
    4,
    5,
    5,
    5,
    5,
    0,
]

# ---------------------------------------------------------------------------
# Adaptive frequency model (cumulative frequencies, descending)
# ---------------------------------------------------------------------------


class Model:
    """Adaptive frequency model over symbols [start, start+length)."""

    def __init__(self, start: int, length: int) -> None:
        # syms[i] = (symbol, cumulative frequency); syms[length] is the
        # sentinel with cumulative frequency 0.
        self.syms: list[tuple[int, int]] = [(start + i, length - i) for i in range(length + 1)]
        self.entries = length
        self.shift_left = 4

    def update(self) -> None:
        """Rescale model frequencies when the total exceeds 3800."""
        self.shift_left -= 1
        if self.shift_left > 0:
            # Halve cumulative frequencies, maintaining monotonicity.
            for i in range(self.entries - 1, -1, -1):
                sym, freq = self.syms[i]
                freq >>= 1
                if freq <= self.syms[i + 1][1]:
                    freq = self.syms[i + 1][1] + 1
                self.syms[i] = (sym, freq)
        else:
            self.shift_left = 50
            # Convert cumulative -> individual frequencies.
            for i in range(self.entries):
                sym, freq = self.syms[i]
                freq = (freq - self.syms[i + 1][1] + 1) >> 1  # +1: no zeros
                self.syms[i] = (sym, freq)
            # Selection sort by individual frequency, descending.
            for i in range(self.entries - 1):
                for j in range(i + 1, self.entries):
                    if self.syms[i][1] < self.syms[j][1]:
                        self.syms[i], self.syms[j] = self.syms[j], self.syms[i]
            # Convert back to cumulative frequencies.
            for i in range(self.entries - 1, -1, -1):
                sym, freq = self.syms[i]
                self.syms[i] = (sym, freq + self.syms[i + 1][1])


# ---------------------------------------------------------------------------
# Bit reader — MSB-first, big-endian 16-bit words
# ---------------------------------------------------------------------------


class BitReader:
    """Reads an MSB-first bit stream from a byte buffer.

    Bits are injected 16 at a time as big-endian words; after the real input
    is exhausted, zero bytes are served (``overrun`` counts how many), which
    lets the decoder finish the final renormalization.
    """

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0
        self.bit_buffer = 0
        self.bits_left = 0
        self.overrun = 0

    def fill(self) -> None:
        if self.pos < len(self.data):
            b0 = self.data[self.pos]
            self.pos += 1
        else:
            self.overrun += 1
            b0 = 0
        if self.pos < len(self.data):
            b1 = self.data[self.pos]
            self.pos += 1
        else:
            self.overrun += 1
            b1 = 0
        word = (b0 << 8) | b1
        self.bit_buffer |= word << (32 - 16 - self.bits_left)
        self.bits_left += 16

    def ensure_bits(self, n: int) -> None:
        while self.bits_left < n:
            self.fill()

    def peek_bits(self, n: int) -> int:
        return self.bit_buffer >> (32 - n)

    def remove_bits(self, n: int) -> None:
        self.bit_buffer = (self.bit_buffer << n) & 0xFFFFFFFF
        self.bits_left -= n

    def read_bits(self, n: int) -> int:
        if n == 0:
            return 0
        self.ensure_bits(n)
        val = self.peek_bits(n)
        self.remove_bits(n)
        return val

    def read_many_bits(self, n: int) -> int:
        """Read n bits, handling n > 16 in chunks."""
        if n == 0:
            return 0
        val = 0
        while n > 0:
            if self.bits_left <= 16:
                self.fill()
            bitrun = min(self.bits_left, n)
            val = (val << bitrun) | self.peek_bits(bitrun)
            self.remove_bits(bitrun)
            n -= bitrun
        return val


# ---------------------------------------------------------------------------
# Arithmetic decoder
# ---------------------------------------------------------------------------


def decode_symbol(
    model: Model, bits: BitReader, h: int, lo: int, c: int
) -> tuple[int, int, int, int]:
    """Decode one symbol; returns (symbol, new_h, new_l, new_c)."""
    range_ = ((h - lo) & 0xFFFF) + 1
    total_freq = model.syms[0][1]
    if total_freq == 0 or range_ == 0:
        raise ValueError("Decompression error: zero frequency or range")

    symf = ((((c - lo + 1) * total_freq - 1) % (1 << 32)) // range_) & 0xFFFF

    i = 1
    while i < model.entries:
        if model.syms[i][1] <= symf:
            break
        i += 1

    sym = model.syms[i - 1][0]

    range2 = ((h - lo) & 0xFFFF) + 1
    h = (lo + (model.syms[i - 1][1] * range2) // total_freq - 1) & 0xFFFF
    lo = (lo + (model.syms[i][1] * range2) // total_freq) & 0xFFFF

    # Increase the frequency of the decoded symbol and everything above it.
    j = i
    while True:
        j -= 1
        s, f = model.syms[j]
        model.syms[j] = (s, f + 8)
        if j == 0:
            break

    if model.syms[0][1] > 3800:
        model.update()

    # Renormalization.
    while True:
        if (lo & 0x8000) != (h & 0x8000):
            if (lo & 0x4000) != 0 and (h & 0x4000) == 0:
                c ^= 0x4000
                lo &= 0x3FFF
                h |= 0x4000
            else:
                break
        lo = (lo << 1) & 0xFFFF
        h = ((h << 1) | 1) & 0xFFFF
        c = ((c << 1) | bits.read_bits(1)) & 0xFFFF

    return sym, h, lo, c


# ---------------------------------------------------------------------------
# Stream decompressor
# ---------------------------------------------------------------------------

MAX_PADDING_SLACK = 64


def quantum_decompress(compressed: bytes, file_sizes: list[int], window_bits: int) -> bytes:
    """Decompress a Quantum stream covering all files back-to-back."""
    window_size = 1 << window_bits
    window = bytearray(window_size)
    window_posn = 0
    output = bytearray()

    bits = BitReader(compressed)

    i = window_bits * 2
    model0 = Model(0, 64)
    model1 = Model(64, 64)
    model2 = Model(128, 64)
    model3 = Model(192, 64)
    model4 = Model(0, min(i, 24))  # position slots, 3-byte matches
    model5 = Model(0, min(i, 36))  # position slots, 4-byte matches
    model6 = Model(0, i)  # position slots, variable matches
    model6len = Model(0, 27)  # length slots
    model7 = Model(0, 7)  # selector

    h = 0xFFFF
    lo = 0
    c = bits.read_bits(16)

    for file_idx, file_size in enumerate(file_sizes):
        file_end = len(output) + file_size
        while len(output) < file_end:
            if bits.overrun > MAX_PADDING_SLACK:
                raise ValueError("Compressed stream exhausted; declared size cannot be produced")

            selector, h, lo, c = decode_symbol(model7, bits, h, lo, c)

            if selector < 4:
                model = (model0, model1, model2, model3)[selector]
                byte, h, lo, c = decode_symbol(model, bits, h, lo, c)
                window[window_posn] = byte
                window_posn = (window_posn + 1) & (window_size - 1)
                output.append(byte)
                continue

            if selector == 4:
                pos_sym, h, lo, c = decode_symbol(model4, bits, h, lo, c)
                extra = bits.read_many_bits(EXTRA_BITS[pos_sym])
                offset = POSITION_BASE[pos_sym] + extra + 1
                length = 3
            elif selector == 5:
                pos_sym, h, lo, c = decode_symbol(model5, bits, h, lo, c)
                extra = bits.read_many_bits(EXTRA_BITS[pos_sym])
                offset = POSITION_BASE[pos_sym] + extra + 1
                length = 4
            else:  # selector == 6
                len_sym, h, lo, c = decode_symbol(model6len, bits, h, lo, c)
                len_extra = bits.read_many_bits(LENGTH_EXTRA[len_sym])
                length = LENGTH_BASE[len_sym] + len_extra + 5
                pos_sym, h, lo, c = decode_symbol(model6, bits, h, lo, c)
                pos_extra = bits.read_many_bits(EXTRA_BITS[pos_sym])
                offset = POSITION_BASE[pos_sym] + pos_extra + 1

            src = (window_posn + window_size - offset) & (window_size - 1)
            for _ in range(min(length, file_end - len(output))):
                byte = window[src]
                window[window_posn] = byte
                output.append(byte)
                src = (src + 1) & (window_size - 1)
                window_posn = (window_posn + 1) & (window_size - 1)

        # Between files: consume the 16-bit raw checksum (not arithmetic-coded).
        if file_idx < len(file_sizes) - 1:
            bits.read_bits(16)

    return bytes(output)


# ---------------------------------------------------------------------------
# Archive parsing
# ---------------------------------------------------------------------------


def read_var_length(data: bytes, pos: int) -> tuple[int, int]:
    if pos >= len(data):
        raise ValueError("Truncated archive: missing string length")
    first = data[pos]
    pos += 1
    if first < 128:
        return first, pos
    if pos >= len(data):
        raise ValueError("Truncated archive: missing extended string length")
    second = data[pos]
    pos += 1
    return ((first & 0x7F) << 8) | second, pos


def read_var_string(data: bytes, pos: int) -> tuple[str, int]:
    length, pos = read_var_length(data, pos)
    if pos + length > len(data):
        raise ValueError(f"Truncated archive: string of {length} bytes overruns the file")
    s = data[pos : pos + length].decode("latin-1")
    return s, pos + length


def _read_u16(data: bytes, pos: int) -> int:
    if pos + 2 > len(data):
        raise ValueError("Truncated archive: u16 field overruns the file")
    return struct.unpack_from("<H", data, pos)[0]


def _read_u32(data: bytes, pos: int) -> int:
    if pos + 4 > len(data):
        raise ValueError("Truncated archive: u32 field overruns the file")
    return struct.unpack_from("<I", data, pos)[0]


def parse_archive(
    data: bytes,
) -> tuple[tuple[int, int, int, int, int], list[dict[str, object]], int]:
    """Parse a Quantum archive; returns (header, file_entries, stream_offset)."""
    if len(data) < 8 or data[:2] != b"DS":
        raise ValueError("Invalid Quantum archive signature (expected 'DS')")

    pos = 2
    major = data[pos]
    pos += 1
    minor = data[pos]
    pos += 1
    num_files = _read_u16(data, pos)
    pos += 2
    table_size = data[pos]
    pos += 1
    flags = data[pos]
    pos += 1

    if not 10 <= table_size <= 21:
        raise ValueError(f"Invalid table size {table_size} (must be 10..21)")

    header = (major, minor, num_files, table_size, flags)

    files: list[dict[str, object]] = []
    for _ in range(num_files):
        name, pos = read_var_string(data, pos)
        comment, pos = read_var_string(data, pos)
        size = _read_u32(data, pos)
        pos += 4
        time_ = _read_u16(data, pos)
        pos += 2
        date_ = _read_u16(data, pos)
        pos += 2
        files.append(
            {
                "name": name,
                "comment": comment,
                "size": size,
                "time": time_,
                "date": date_,
            }
        )

    return header, files, pos


def dos_datetime(time_: int, date_: int) -> str:
    day = date_ & 0x1F
    month = (date_ >> 5) & 0x0F
    year = ((date_ >> 9) & 0x7F) + 1980
    secs = (time_ & 0x1F) * 2
    mins = (time_ >> 5) & 0x3F
    hours = (time_ >> 11) & 0x1F
    return f"{year:04d}-{month:02d}-{day:02d} {hours:02d}:{mins:02d}:{secs:02d}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Quantum archive (.PAK) extractor")
    ap.add_argument("archive", help="path to the .PAK archive")
    ap.add_argument("-lo", "--list", action="store_true", help="list contents")
    ap.add_argument("-x", "--extract", action="store_true", help="extract files")
    ap.add_argument("-o", "--output", default=".", help="output directory (extract)")
    args = ap.parse_args(argv)

    path = Path(args.archive)
    data = path.read_bytes()
    header, files, stream_off = parse_archive(data)
    major, minor, num_files, table_size, flags = header

    print(
        f"Quantum {major}.{minor:02d} archive — {num_files} file(s), "
        f"window {1 << table_size} bytes, flags 0x{flags:02X}"
    )
    total = sum(int(f["size"]) for f in files)

    if args.list or not args.extract:
        print(f"{'size':>12}  {'date':<19}  name")
        for f in files:
            dt = dos_datetime(int(f["time"]), int(f["date"]))
            print(f"{f['size']:>12}  {dt}  {f['name']}")
        print(f"{total:>12}  {'':<19} {len(files)} file(s)")
        return 0

    if not args.extract:
        return 0

    compressed = data[stream_off:]
    out = quantum_decompress(compressed, [int(f["size"]) for f in files], table_size)

    if len(out) != total:
        raise ValueError(f"Decompression size mismatch: expected {total}, got {len(out)}")

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    pos = 0
    for f in files:
        size = int(f["size"])
        name = Path(f["name"]).name  # flat extraction, no path traversal
        (out_dir / name).write_bytes(out[pos : pos + size])
        pos += size
    print(f"Extracted {len(files)} file(s), {total} bytes -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
