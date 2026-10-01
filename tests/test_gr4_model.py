"""Synthetic fixtures only; not camera emulation."""
import struct
import unittest
from tools.gr4_model import identify_header


class ModelTests(unittest.TestCase):
    def test_products_and_paths(self):
        for product, label, filename in [(0x132E0, "STANDARD", "GoodBye.jpg"), (0x132E1, "HDF", "GB_HDF.jpg"), (0x13330, "MONO", "GB_Mono.jpg")]:
            self.assertEqual(identify_header(struct.pack("<II", 0xA55A5AA5, product)), (label, "A:\\Resource\\Jpeg\\" + filename))

    def test_fail_closed(self):
        for header in [b"", b"\0" * 7, b"\0" * 9, struct.pack("<II", 0, 0x132E0), struct.pack("<II", 0xA55A5AA5, 0x132E2), struct.pack(">II", 0xA55A5AA5, 0x132E0)]:
            self.assertIsNone(identify_header(header))
