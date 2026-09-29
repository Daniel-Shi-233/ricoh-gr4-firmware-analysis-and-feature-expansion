#!/usr/bin/env python3
# Copyright 2026 radium-wang
# SPDX-License-Identifier: Apache-2.0
"""Add a JPEG COM segment so a replacement matches an existing file size.

The image data is unchanged. This can avoid stale trailing bytes when a
camera-side file-copy operation overwrites a longer existing file without
truncating it. It does not check the camera's JPEG requirements.
"""

import argparse
from pathlib import Path


def pad_jpeg(source: bytes, target_size: int) -> bytes:
    if len(source) < 4 or not source.startswith(b"\xff\xd8") or not source.endswith(b"\xff\xd9"):
        raise ValueError("input must be a JPEG with SOI at the start and EOI at the end")
    difference = target_size - len(source)
    if difference == 0:
        return source
    if difference < 4:
        raise ValueError("target size must equal input size or be at least 4 bytes larger")
    if difference - 2 > 0xFFFF:
        raise ValueError("one JPEG COM segment cannot add more than 65,537 bytes")

    comment_length = difference - 2  # COM length includes its own two-byte length field
    comment = b"\xff\xfe" + comment_length.to_bytes(2, "big") + b" " * (difference - 4)
    return source[:-2] + comment + source[-2:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("target_size", type=int, help="required output length in bytes")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    result = pad_jpeg(args.input.read_bytes(), args.target_size)
    args.output.write_bytes(result)
    print(f"wrote {args.output} ({len(result)} bytes)")


if __name__ == "__main__":
    main()
