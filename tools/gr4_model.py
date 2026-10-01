# License: see LICENSE
"""Exact GR IV product-header decoding; no camera access."""
import struct

MODELS = {
    0x132E0: ("STANDARD", r"A:\Resource\Jpeg\GoodBye.jpg"),
    0x132E1: ("HDF", r"A:\Resource\Jpeg\GB_HDF.jpg"),
    0x13330: ("MONO", r"A:\Resource\Jpeg\GB_Mono.jpg"),
}


def identify_header(header: bytes) -> tuple[str, str] | None:
    """Decode exactly eight bytes; reject bad magic, length or unknown IDs.

    Identifies a product, not firmware version or script compatibility.
    """
    if len(header) != 8:
        return None
    magic, product = struct.unpack("<II", header)
    return MODELS.get(product) if magic == 0xA55A5AA5 else None
