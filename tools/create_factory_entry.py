#!/usr/bin/env python3
# Copyright 2026 radium-wang
# SPDX-License-Identifier: Apache-2.0
"""Create the SD-card factory-menu entry files documented for one GR IV.

This writes two small files into an output directory. It does not access a
camera or SD card. The entry is firmware-specific and was verified on one
camera only.
"""

import argparse
from pathlib import Path


FILES = {
    "00078560.636": b"[OPEN_FACTORY_DEBUG_MENU]\r\n",
    "DEVELOP.MOD": bytes.fromhex("07 01 2c 1f 10 03 1e 16 05 2d"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("--force", action="store_true", help="replace existing files with the same names")
    args = parser.parse_args()

    args.output_directory.mkdir(parents=True, exist_ok=True)
    destinations = [args.output_directory / name for name in FILES]
    if not args.force:
        existing = [path for path in destinations if path.exists()]
        if existing:
            names = ", ".join(str(path) for path in existing)
            raise FileExistsError(f"refusing to replace existing files: {names}; use --force to replace them")
    for name, data in FILES.items():
        destination = args.output_directory / name
        destination.write_bytes(data)
        print(f"wrote {destination} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
