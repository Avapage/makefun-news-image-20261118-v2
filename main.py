"""Deliver this entry's picture to the grader.

The whole entry is a single picture, entry.png, sitting next to this
file in the bot directory. The grader expects that same picture, byte
for byte, inside the output directory. This program checks the source
is a real 1024x1024 PNG, copies it across, and proves the copy matches
before it calls the job done.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_EDGE = 1024
PICTURE_NAME = "entry.png"


def complain(message: str) -> SystemExit:
    print(f"main.py: {message}", file=sys.stderr)
    return SystemExit(1)


def picture_dimensions(path: Path) -> tuple[int, int]:
    """Read the width and height out of the PNG's IHDR header."""
    with path.open("rb") as handle:
        head = handle.read(24)
    if len(head) < 24 or not head.startswith(PNG_MAGIC):
        raise complain(f"{path} does not start with a PNG signature")
    if head[12:16] != b"IHDR":
        raise complain(f"{path} has no IHDR chunk where one belongs")
    return struct.unpack(">II", head[16:24])


def checked_source(bot_dir: Path) -> Path:
    source = bot_dir / PICTURE_NAME
    if not source.is_file():
        raise complain(f"no {PICTURE_NAME} found in {bot_dir}")
    width, height = picture_dimensions(source)
    if (width, height) != (EXPECTED_EDGE, EXPECTED_EDGE):
        raise complain(
            f"{PICTURE_NAME} is {width}x{height}, "
            f"not the required {EXPECTED_EDGE}x{EXPECTED_EDGE}"
        )
    return source


def deliver(source: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / PICTURE_NAME
    shutil.copyfile(source, target)
    if target.read_bytes() != source.read_bytes():
        raise complain("the delivered copy differs from the source picture")
    return target


def main() -> int:
    bot_dir = Path(os.environ.get("MAKEFUN_BOT_DIR", "/bot"))
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    source = checked_source(bot_dir)
    deliver(source, output_dir)
    width, height = picture_dimensions(source)
    size = source.stat().st_size
    print(
        f"{PICTURE_NAME} delivered to {output_dir}: "
        f"{width}x{height}, {size} bytes, copy verified byte for byte."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
