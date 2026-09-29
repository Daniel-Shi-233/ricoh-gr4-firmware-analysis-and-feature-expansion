#!/usr/bin/env python3
# Copyright 2026 radium-wang
# SPDX-License-Identifier: Apache-2.0
"""Offline inspection of a GR IV firmware container.

The frame decoder follows the format documented by yeahnope/gr_unpack.
No output is suitable for installing on a camera.
"""

import argparse
import struct
from pathlib import Path


def checksum(path):
    total = 0
    with path.open("rb") as stream:
        while data := stream.read(1024 * 1024):
            for (word,) in struct.iter_unpack("<I", data):
                total = (total + word) & 0xFFFFFFFF
    return total


def unpack_frames(source):
    output = bytearray()
    frames = []
    pos = 0x80
    while pos + 2 <= len(source):
        frame_start = pos
        output_start = len(output)
        prefix = int.from_bytes(source[pos : pos + 2], "big")
        pos += 2
        if prefix == 0:
            break
        length = prefix & 0x7FFF
        end = pos + length
        if end > len(source):
            raise ValueError(f"frame exceeds input at 0x{pos-2:x}")
        if prefix & 0x8000:
            output.extend(source[pos:end])
            pos = end
            frames.append((frame_start, pos, output_start, len(output)))
            continue
        while pos < end:
            if pos + 2 > end:
                raise ValueError(f"short block at 0x{pos:x}")
            flags = int.from_bytes(source[pos : pos + 2], "big")
            pos += 2
            for bit in range(15, -1, -1):
                if pos >= end:
                    break
                if not flags & (1 << bit):
                    output.append(source[pos])
                    pos += 1
                    continue
                if pos + 2 > end:
                    raise ValueError(f"short reference at 0x{pos:x}")
                first, second = source[pos : pos + 2]
                pos += 2
                distance = ((first & 0xF8) << 5) + second
                count = first & 7
                if count == 7:
                    extension = source[pos]
                    pos += 1
                    count += extension
                    while extension == 255:
                        extension = source[pos]
                        pos += 1
                        count += extension
                if not distance:
                    break
                if distance > len(output):
                    raise ValueError(f"invalid back reference at 0x{pos:x}")
                for _ in range(count + 3):
                    output.append(output[-distance])
        pos = end
        frames.append((frame_start, pos, output_start, len(output)))
    return output, pos, frames


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("firmware", type=Path)
    parser.add_argument("--unpack", type=Path, help="write decoded payload for offline analysis")
    args = parser.parse_args()
    data = args.firmware.read_bytes()
    print("model:", data[8:20].split(b"\0")[0].decode("ascii"))
    for offset in (0x38, 0x4C, 0x50):
        print(f"version-like field @ 0x{offset:02x}:", data[offset : offset + 4].hex(" "))
    version = tuple(data[0x38:0x3C])
    print("four-component version in header:", ".".join(map(str, version)))
    print("little-endian word @ 0x4C:", f"0x{int.from_bytes(data[0x4C:0x50], 'little'):08x}")
    print("length:", len(data))
    print("stored trailing checksum:", data[-4:].hex(" "))
    print("sum of all little-endian 32-bit words modulo 2^32:", f"0x{checksum(args.firmware):08x}")
    if args.unpack:
        output, consumed, frames = unpack_frames(data)
        args.unpack.write_bytes(output)
        print("decoded bytes:", len(output), "consumed:", consumed, "frames:", len(frames))


if __name__ == "__main__":
    main()
