"""Numeric-contract tests for delphi/1.0-win16/pak_extract.py.

Pins the arithmetic the Quantum decoder depends on: bit-reader word
assembly and overrun accounting, adaptive-model frequency invariants,
arithmetic-decoder symbol selection intervals, archive field parsing
bounds, DOS timestamp field extraction and match-copy window math.
The end-to-end coder path is covered by byte-for-byte validation against
real archives (see module docstring there); these tests pin the pieces
that refactors of the hot loops most easily break silently.
"""

import importlib.util
import struct
import sys
import unittest
from itertools import pairwise
from pathlib import Path
from types import ModuleType

_REPO = Path(__file__).resolve().parents[1]
_PAK = _REPO / "delphi" / "1.0-win16" / "pak_extract.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pak_extract", _PAK)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load pak_extract from {_PAK}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["pak_extract"] = module
    spec.loader.exec_module(module)
    return module


pak = _load_module()


def _is_strictly_decreasing(values: list[int]) -> bool:
    return all(a > b for a, b in pairwise(values))


class ModelTests(unittest.TestCase):
    def test_init_uniform_frequencies(self) -> None:
        m = pak.Model(64, 8)
        self.assertEqual(m.frq[0], 8)
        self.assertTrue(_is_strictly_decreasing(m.frq))
        self.assertEqual(m.frq[-1], 0)
        self.assertEqual(m.sym[:8], [64, 65, 66, 67, 68, 69, 70, 71])
        self.assertEqual(m.entries, 8)

    def test_decode_symbol_low_c_selects_last_symbol(self) -> None:
        # symf = ((c - lo + 1) * total - 1) // range: c == lo gives symf 0,
        # which lands in the last (smallest) cumulative interval.
        m = pak.Model(192, 8)
        bits = pak.BitReader(bytes(8))
        sym, h, lo, _c = pak.decode_symbol(m, bits, 0xFFFF, 0, 0)
        self.assertEqual(sym, 199)
        # Every cumulative entry at or above the decoded interval gains one
        # +8 step; the sentinel below it stays 0.
        self.assertEqual(m.frq, [16, 15, 14, 13, 12, 11, 10, 9, 0])
        self.assertEqual((h, lo), (0xFFFF, 0x0000))

    def test_decode_symbol_high_c_selects_first_symbol(self) -> None:
        # symf == total - 1 falls into the first symbol's interval.
        m = pak.Model(0, 8)
        bits = pak.BitReader(bytes(8))
        sym, _h, _lo, _c = pak.decode_symbol(m, bits, 0xFFFF, 0, 0xFFFF)
        self.assertEqual(sym, 0)
        self.assertEqual(m.frq[0], 16)

    def test_decode_symbol_mid_interval_boundaries(self) -> None:
        # With the uniform 8-symbol model, symf 4 selects the 4th interval;
        # h moves to the interval top and lo to its base, then renormalizes.
        m = pak.Model(0, 8)
        bits = pak.BitReader(bytes(8))
        c = 40000  # ((40000) * 8 - 1) // 65536 == 4
        sym, h, lo, _c = pak.decode_symbol(m, bits, 0xFFFF, 0, c)
        self.assertEqual(sym, 3)
        self.assertEqual((h, lo), (0xFFFF, 0x0000))
        # Intervals at or above the decoded one (indices 0..3) gain +8 once.
        self.assertEqual(m.frq[:4], [16, 15, 14, 13])
        self.assertEqual(m.frq[4], 4)  # below: untouched

    def test_halving_update_keeps_frequencies_strict_and_positive(self) -> None:
        m = pak.Model(0, 42)
        for _ in range(3):  # shift_left 4 -> 3 -> 2 -> 1, all halving passes
            m.update()
            self.assertTrue(_is_strictly_decreasing(m.frq))
            self.assertTrue(all(f >= 1 for f in m.frq[:-1]))
            self.assertEqual(m.frq[-1], 0)

    def test_halving_update_reduces_skewed_totals(self) -> None:
        m = pak.Model(0, 8)
        m.frq = [4000, 3200, 2400, 1600, 800, 400, 200, 100, 0]
        m.update()
        self.assertTrue(_is_strictly_decreasing(m.frq))
        self.assertEqual(m.frq[0], 2000)  # halved from 4000

    def test_full_rescale_sorts_symbols_by_frequency(self) -> None:
        m = pak.Model(0, 7)
        m.shift_left = 1  # next update() takes the full-rescale branch
        # Cumulative layout whose individual frequencies come out as six 1s
        # plus a 50 on the LAST symbol: (frq[i] - frq[i+1] + 1) >> 1.
        cum = []
        nxt = 0
        indiv = [1, 1, 1, 1, 1, 1, 50]
        for f in reversed(indiv):
            nxt = 2 * f - 1 + nxt
            cum.append(nxt)
        m.frq = [*reversed(cum), 0]
        m.update()
        self.assertEqual(m.sym[0], 6)  # heaviest symbol moved to the front
        self.assertTrue(_is_strictly_decreasing(m.frq))
        self.assertEqual(m.frq[0], 56)  # 50 + six 1s
        self.assertEqual(m.frq[-1], 0)


class BitReaderTests(unittest.TestCase):
    def test_reads_msb_first_big_endian_words(self) -> None:
        br = pak.BitReader(b"\xab\xcd")
        self.assertEqual(br.read_bits(16), 0xABCD)
        self.assertEqual(br.pos, 2)
        self.assertEqual(br.bits_left, 0)

    def test_bit_order_inside_a_word(self) -> None:
        br = pak.BitReader(b"\xb4\xb4")
        self.assertEqual(br.read_bits(3), 0b101)
        self.assertEqual(br.read_bits(3), 0b101)
        self.assertEqual(br.read_bits(3), 0b001)  # crosses into the second word

    def test_read_many_bits_spans_words(self) -> None:
        data = b"\xde\xad\xbe\xef"
        br = pak.BitReader(data)
        expected = int.from_bytes(data, "big") >> (32 - 19)
        self.assertEqual(br.read_many_bits(19), expected)
        self.assertEqual(br.pos, 4)  # whole words are pulled in 16 bits at a time

    def test_overrun_zero_fills_and_is_counted(self) -> None:
        br = pak.BitReader(b"")
        self.assertEqual(br.read_bits(16), 0)
        self.assertEqual(br.overrun, 2)
        br.read_bits(1)
        self.assertEqual(br.overrun, 4)


class VarFieldTests(unittest.TestCase):
    def test_var_length_short_and_extended_forms(self) -> None:
        self.assertEqual(pak.read_var_length(b"\x05xyz", 0), (5, 1))
        self.assertEqual(pak.read_var_length(b"\x81\x02", 0), ((1 << 8) | 2, 2))
        self.assertEqual(pak.read_var_length(b"\xff\xff", 0), (32767, 2))

    def test_var_length_truncation_raises(self) -> None:
        with self.assertRaises(ValueError):
            pak.read_var_length(b"", 0)
        with self.assertRaises(ValueError):
            pak.read_var_length(b"\x80", 0)

    def test_var_string_overrun_raises(self) -> None:
        with self.assertRaises(ValueError):
            pak.read_var_string(b"\x05ab", 0)


class ParseArchiveTests(unittest.TestCase):
    @staticmethod
    def _archive_bytes() -> bytes:
        out = bytearray(b"DS\x01\x00")
        out += struct.pack("<H", 2)  # file count
        out += bytes([16, 0])  # table size, flags
        out += bytes([7]) + b"A\\T.PAS"  # varstring name
        out += bytes([0])  # empty comment
        out += struct.pack("<IHH", 10, 0x1234, 0x5678)
        out += bytes([5]) + b"B.DCU"
        out += bytes([0])
        out += struct.pack("<IHH", 5, 0xABCD, 0x0246)
        return bytes(out)

    def test_parse_header_and_entries(self) -> None:
        header, files, stream_off = pak.parse_archive(self._archive_bytes())
        self.assertEqual(header, (1, 0, 2, 16, 0))
        self.assertEqual([(f.name, f.size) for f in files], [("A\\T.PAS", 10), ("B.DCU", 5)])
        # Little-endian time/date fields survive the round trip.
        self.assertEqual([f.time for f in files], [0x1234, 0xABCD])
        self.assertEqual([f.date for f in files], [0x5678, 0x0246])
        self.assertEqual(stream_off, len(self._archive_bytes()))

    def test_truncated_entry_raises(self) -> None:
        data = bytearray(self._archive_bytes())
        del data[-6:]  # cut into the last entry's time/date fields
        with self.assertRaises(ValueError):
            pak.parse_archive(bytes(data))

    def test_bad_magic_and_table_size_raise(self) -> None:
        with self.assertRaises(ValueError):
            pak.parse_archive(b"XX" + self._archive_bytes()[2:])
        bad_table = bytearray(self._archive_bytes())
        bad_table[6] = 22
        with self.assertRaises(ValueError):
            pak.parse_archive(bytes(bad_table))


class DosDatetimeTests(unittest.TestCase):
    def test_field_extraction(self) -> None:
        date = (44 << 9) | (1 << 5) | 31  # 2024-01-31
        time = (23 << 11) | (59 << 5) | 29  # 23:59:58 (2-second units)
        self.assertEqual(pak.dos_datetime(time, date), "2024-01-31 23:59:58")

    def test_zero_fields_render_raw_values(self) -> None:
        # Display-only: unpacked fields are rendered as-is, no clamping.
        self.assertEqual(pak.dos_datetime(0, 0), "1980-00-00 00:00:00")


class NameSafetyTests(unittest.TestCase):
    def test_member_name_flattens_dos_paths(self) -> None:
        self.assertEqual(pak.member_name("LIB\\X.DCU"), "X.DCU")
        self.assertEqual(pak.member_name("X.DCU"), "X.DCU")

    def test_member_name_rejects_traversals(self) -> None:
        for bad in ("", ".", "..", "LIB\\..", "LIB\\..\\.."):
            with self.assertRaises(ValueError):
                pak.member_name(bad)

    def test_display_name_masks_control_characters(self) -> None:
        self.assertEqual(pak.display_name("A\x1b[0mB"), "A?[0mB")
        self.assertEqual(pak.display_name("plain.pas"), "plain.pas")


class DecompressBoundaryTests(unittest.TestCase):
    def test_no_files_yields_empty_output(self) -> None:
        self.assertEqual(pak.quantum_decompress(b"", [], 16), b"")

    def test_zero_size_files_still_consume_inter_file_checksum(self) -> None:
        # One 16-bit raw checksum sits between the two zero-byte members.
        self.assertEqual(pak.quantum_decompress(b"\x12\x34", [0, 0], 16), b"")

    def test_small_declared_size_fabricates_output_from_padding(self) -> None:
        # A declared size small enough to be met by matches against the
        # zero-filled pre-history completes without tripping the guard.
        self.assertEqual(len(pak.quantum_decompress(b"", [100], 16)), 100)

    def test_exhausted_stream_raises_instead_of_hanging(self) -> None:
        with self.assertRaises(ValueError):
            pak.quantum_decompress(b"", [10**6], 16)


if __name__ == "__main__":
    unittest.main()
