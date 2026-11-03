---
name: all-to-image
description: Encode any file (any bytes) as one or more PNG images, by treating every 3 source bytes as the R, G, B of one pixel. Produces both 4:3 and 16:9 versions of each chunk and splits at 1 MiB source-bytes per chunk. The output is reversible (with the .meta.json sidecar) so it doubles as a "wrap a file in PNGs" tool. Triggers: "把任意文件转成图片", "file to image", "bytes to png", "all to image", "RGB stream image", "把文件塞进图片", "data to picture". Do NOT use for: visual byte inspection / entropy heatmaps / Hilbert-curve rendering (use force-picture-type), binary/hex/octal text dumps (use file-binary-converter), OCR or image content extraction.
---

# all-to-image

Wrap any file as one or more RGB PNG images. Every 3 source bytes become
the R, G, B channels of one pixel, in left-to-right top-to-bottom order.
The last group of a chunk, if shorter than 3 bytes, is padded with
random bytes drawn from a deterministic RNG. Two aspect ratios (4:3 and
16:9) are produced for each chunk. Input is split into 1 MiB chunks of
source bytes, so a 50 MiB blob becomes 100 chunks → 200 PNGs (4:3 + 16:9
each), plus one `.meta.json` sidecar.

The encoding is **lossless and reversible** when the `.meta.json`
sidecar is kept: re-read the pixels, drop the recorded
`random_padding_bytes` from the tail of each chunk, concatenate the
chunks in `index` order, and you get the original file back byte-for-byte.

## When to use

- A user wants to send a file as an image (e.g. through a chat channel
  that strips attachments, or to evade "no binaries" filters).
- A user wants a deterministic visual fingerprint of a file in two
  common aspect ratios, with a clean path back to the source bytes.
- Bulk "wrap every file in this folder" jobs where the 1 MiB-per-chunk
  rule keeps the per-image dimension predictable.

Do **not** use when the user wants:

- A *visualization* of byte distribution / entropy / Hilbert curve —
  `force-picture-type` is built for that.
- A *text dump* of bytes in binary / base-4 / octal / hex —
  `file-binary-converter`.
- A *decompression / extraction* of an image archive — wrong direction.

## How to call

```bash
python /workspace/.skills/all-to-image/scripts/all_to_image.py \
    INPUT_FILE \
    [-o OUTPUT_DIR] \
    [--chunk-bytes 1048576]
```

- `INPUT_FILE` — any readable file (binary or text).
- `-o / --output-dir` — where to put the PNGs. Default:
  `INPUT_FILE.to_images/` next to the input.
- `--chunk-bytes` — source-bytes per chunk, default `1048576` (1 MiB).

The script prints one line per generated image with the actual
`width x height`, the pixel count, the source-byte count and the
random-padding byte count for that chunk.

## Output naming

For a chunk index `N` and a basename `foo.bin`, the script writes:

```
foo.bin_part0001_4x3.png
foo.bin_part0001_16x9.png
foo.bin_part0002_4x3.png
foo.bin_part0002_16x9.png
...
foo.bin.meta.json
```

The sidecar records per chunk: `index`, `source_bytes`,
`random_padding_bytes`, `n_pixels`, and for each ratio: `width`,
`height`, `path`, `png_size_bytes`.

## How dimensions are chosen

For `N` pixels and a target ratio `r = w/h`:

```
w = max(1, round(sqrt(N * r)))
h = max(1, ceil(N / w))
# grow h if w*h < N
```

So the actual image is always close to the target ratio, and is always
large enough to hold every pixel. The very last pixel row may be
shorter than `w`; those cells are filled with black (0, 0, 0). Source
bytes (the actual payload) are never affected — only visual padding.

## Round-trip example

```python
# decode (assumes you kept the sidecar)
import json
from PIL import Image

with open("foo.bin.meta.json") as f:
    meta = json.load(f)

buf = bytearray()
for chunk in meta["chunks"]:
    img = Image.open(chunk["images"][0]["path"])  # 4x3 is fine
    raw = img.tobytes()                            # RGB, length = w*h*3
    pixels = chunk["n_pixels"]
    src = chunk["source_bytes"]
    buf += raw[: pixels * 3][:src]                # trim to source size
open("foo.bin.recovered", "wb").write(bytes(buf))
assert bytes(buf) == open("foo.bin", "rb").read()
```

## Limits and gotchas

- **Pillow required.** `pip install pillow` if missing. The script
  exits with a clear message otherwise.
- **No streaming input.** The script reads one chunk at a time, so
  memory is bounded by `chunk_bytes + 3 * w * h` per chunk. A 1 MiB
  chunk produces a PNG of ~700x525 (4:3) or ~787x444 (16:9).
- **The 1 MiB is source-bytes, not output PNG-bytes.** PNG size on
  disk varies with image content; the script does not re-split based
  on PNG size.
- **Random padding is deterministic.** Same `index + source_bytes`
  gives the same pad bytes, so the same input always produces
  byte-identical PNGs.
- **Tail padding in the image grid is black, not random.** Only the
  source-byte tail (last 1–2 bytes of a chunk) uses random padding;
  the visual padding in the last pixel row is `(0, 0, 0)` so chunk
  boundaries are obvious on inspection.
