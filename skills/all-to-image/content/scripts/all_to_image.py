#!/usr/bin/env python3
"""
all-to-image: turn any file into one or more PNG images.

Algorithm
---------
- Read the input file as raw bytes.
- Split the byte stream into chunks of `--chunk-bytes` (default 1 MiB).
- For each chunk, every 3 consecutive bytes become one pixel's (R, G, B).
  If the last group has <3 bytes, the missing tail is filled with random
  bytes drawn from a seeded RNG so the output is reproducible for the
  same input length.
- The number of pixels N is known exactly. Two output aspect ratios are
  produced per chunk (4:3 and 16:9). Width is picked as
    w = round(sqrt(N * ratio))
  and clamped so w >= 1 and w*h >= N. If the last pixel row is short,
  the trailing cells are padded with (0, 0, 0) (black).
- A `.meta.json` sidecar records the original file size, chunk size,
  per-chunk pixel count, image width / height, and the exact number of
  random padding bytes appended per chunk. With that sidecar the source
  bytes can be recovered losslessly from the images.

Usage
-----
    python all_to_image.py INPUT [-o OUTPUT_DIR] [--chunk-bytes 1048576]

OUTPUT_DIR defaults to "INPUT.to_images/" beside the input file.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Tuple

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "ERROR: Pillow is required. Install with: pip install pillow\n"
    )
    raise


CHUNK_BYTES_DEFAULT = 1_048_576  # 1 MiB
RANDOM_SEED = 0xA110_CE11  # deterministic padding across runs
ASPECT_RATIOS = {
    "4x3": 4 / 3,
    "16x9": 16 / 9,
}


def split_bytes_into_pixels(data: bytes, rng: random.Random) -> Tuple[bytes, int]:
    """Return (pixel_bytes, random_tail_len).

    Every 3 source bytes -> 3 pixel bytes (R, G, B). If len(data) % 3 != 0,
    the tail is padded with random bytes so the result length is a
    multiple of 3. The number of random padding bytes is returned so the
    caller can record it for lossless reverse mapping.
    """
    pad = (-len(data)) % 3
    if pad:
        data = data + bytes(rng.getrandbits(8) for _ in range(pad))
    return data, pad


def pick_dimensions(n_pixels: int, ratio: float) -> Tuple[int, int]:
    """Pick (width, height) for `n_pixels` such that the image is close
    to the given aspect ratio (w/h) and the grid holds every pixel.

    The exact ratio is impossible for arbitrary n, so we round
    w = round(sqrt(n * ratio)) and derive h = ceil(n / w). If w*h is
    still < n we add one more row. The result is always w*h >= n.
    """
    if n_pixels <= 0:
        return 1, 1
    w = max(1, round(math.sqrt(n_pixels * ratio)))
    h = max(1, math.ceil(n_pixels / w))
    # guarantee capacity even when w*h < n due to integer arithmetic
    while w * h < n_pixels:
        h += 1
    return w, h


def render_chunk(pixel_bytes: bytes, w: int, h: int) -> Image.Image:
    """Build an RGB image from a multiple-of-3 byte buffer. The buffer
    is padded with (0,0,0) up to w*h*3 bytes if shorter."""
    needed = w * h * 3
    if len(pixel_bytes) < needed:
        pixel_bytes = pixel_bytes + b"\x00" * (needed - len(pixel_bytes))
    elif len(pixel_bytes) > needed:
        # should never happen given the math above, but be safe
        pixel_bytes = pixel_bytes[:needed]
    return Image.frombytes("RGB", (w, h), pixel_bytes)


def process_file(
    input_path: Path,
    output_dir: Path,
    chunk_bytes: int,
) -> dict:
    """Process the whole input file and write the resulting images.

    Returns the meta dict that is also written to `<input>.meta.json`.
    """
    file_size = input_path.stat().st_size
    base = input_path.name
    output_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "input": str(input_path),
        "input_size_bytes": file_size,
        "chunk_bytes": chunk_bytes,
        "chunks": [],
    }

    with input_path.open("rb") as fh:
        idx = 0
        while True:
            raw = fh.read(chunk_bytes)
            if not raw:
                break
            idx += 1
            rng = random.Random(RANDOM_SEED ^ len(raw) ^ (idx * 0x9E37_79B9_7F4A_7C15))
            pixel_buf, pad = split_bytes_into_pixels(raw, rng)
            n_pixels = len(pixel_buf) // 3

            chunk_record = {
                "index": idx,
                "source_bytes": len(raw),
                "random_padding_bytes": pad,
                "n_pixels": n_pixels,
                "images": [],
            }

            for ratio_name, ratio_value in ASPECT_RATIOS.items():
                w, h = pick_dimensions(n_pixels, ratio_value)
                img = render_chunk(pixel_buf, w, h)
                out_name = f"{base}_part{idx:04d}_{ratio_name}.png"
                out_path = output_dir / out_name
                # optimize=False keeps encode fast; PNG is already lossless
                img.save(out_path, format="PNG", optimize=False)
                chunk_record["images"].append(
                    {
                        "ratio": ratio_name,
                        "path": str(out_path),
                        "width": w,
                        "height": h,
                        "png_size_bytes": out_path.stat().st_size,
                    }
                )
                print(
                    f"  [{idx:04d}] {ratio_name}: {w}x{h} "
                    f"({n_pixels} px from {len(raw)} B, "
                    f"+{pad} random) -> {out_name}",
                    flush=True,
                )

            meta["chunks"].append(chunk_record)

    sidecar = output_dir / f"{base}.meta.json"
    sidecar.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return meta


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Encode any file as RGB pixel images (4:3 + 16:9).",
    )
    ap.add_argument("input", type=Path, help="path to the file to encode")
    ap.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="output directory (default: <input>.to_images)",
    )
    ap.add_argument(
        "--chunk-bytes",
        type=int,
        default=CHUNK_BYTES_DEFAULT,
        help=f"source bytes per chunk (default: {CHUNK_BYTES_DEFAULT} = 1 MiB)",
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    input_path: Path = args.input.resolve()
    if not input_path.is_file():
        sys.stderr.write(f"ERROR: {input_path} is not a file\n")
        return 2

    output_dir = args.output_dir or input_path.with_suffix(
        input_path.suffix + ".to_images"
    )
    output_dir = output_dir.resolve()

    print(
        f"Encoding {input_path} ({input_path.stat().st_size} B) "
        f"-> {output_dir} (chunk={args.chunk_bytes} B)"
    )

    meta = process_file(input_path, output_dir, args.chunk_bytes)

    n_chunks = len(meta["chunks"])
    n_images = sum(len(c["images"]) for c in meta["chunks"])
    print(
        f"Done: {n_chunks} chunk(s), {n_images} image(s) "
        f"(4:3 + 16:9 each). Sidecar: {output_dir / (input_path.name + '.meta.json')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
