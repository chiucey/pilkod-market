---
name: file-binary-converter
description: |
  Convert any file into a plain-text dump of its raw bytes in one of four
  radices — binary (0/1), base-4 (0-3), octal (0-7), or hex (0-9 a-f) —
  and decode such text back into the original file. Each input byte maps
  to a fixed-width digit string (binary 8, base-4 4, octal 3, hex 2 chars).
  Use this skill when the user says "转成二进制", "转成 0/1", "binary txt",
  "hex dump", "十六进制", "把文件变成 01 串", "01 txt", "hex view", "xxd",
  "八进制", "四进制", "octal", "base-4", or asks to revert a previously
  generated radix text back to the original file. The script is strictly
  streaming so even multi-GB inputs stay cheap. Do NOT use for: base64
  (different alphabet), file compression, image OCR, or character-encoding
  conversions like GBK ↔ UTF-8.
---

# File Binary Converter

A "binary viewer" with four radix modes. Backed by `scripts/convert.py`
— call it as a subprocess; **never** reimplement the conversion in
Python in-conversation, and **never** read the generated dump back into
context just to write it with the agent's file-write tool.

## The four radix modes

| Mode      | Chars/byte | Charset  | Example (one byte 0x5A) | Expansion |
|-----------|-----------:|----------|--------------------------|----------:|
| `binary`  | 8          | `0` `1`  | `01011010`               | ≈ 8×      |
| `base4`   | 4          | `0`–`3`  | `1122`                   | ≈ 4×      |
| `octal`   | 3          | `0`–`7`  | `132`                    | ≈ 3×      |
| `hex`     | 2          | `0`–`f`  | `5a`                     | ≈ 2×      |

All four round-trip cleanly: encode → decode gives the original bytes back.

## Inputs to collect

- **Input file path** — where the source file lives (or the text dump to decode).
- **Direction** — `encode` (file → radix text) or `decode` (radix text → file).
- **Mode** — one of `binary` / `base4` / `octal` / `hex`. The user almost
  always has a preference; if they said "二进制/0和1/01 串" → `binary`,
  "十六进制/hex/xxd" → `hex`, "八进制/octal" → `octal`, "四进制/base-4" → `base4`.
  If genuinely ambiguous, ask one short question — pick the cheapest one
  (hex) only as a last resort.
- **Layout knobs** (encode only, sensible defaults already set):
  - `--line-width` bytes per output line. `0` = single line. Default `16`
    for hex, `0` (one line) for the other three. Change if the user wants
    a specific N.
  - `--space` to separate bytes with a single space.
  - `--prefix` (hex only) to write `0xff` instead of `ff`.
  - `--upper` (hex only) to use `FF` instead of `ff`.
  - `--offset` (hex only) to prepend an 8-char hex address per line (xxd style).
- **For xxd-style text on decode**: also pass `--strip-offset`, otherwise the
  leading `00000000:` columns will be parsed as data and corrupt the output.

If the user did not specify layout, use the defaults. Confirm output path
before writing to a directory the user didn't name.

## Procedure

1. **Pick the radix from the request.** If the user explicitly said one of
   the four (binary / base-4 / octal / hex), use that. If they said nothing,
   ask before encoding — defaulting silently to hex usually surprises them
   for casual "转成 0/1"-style asks.

2. **Run the script as a subprocess. Do not write the dump yourself.** The
   script streams 1 MiB chunks and writes the output file directly; you
   should not paste the dump into a `write` / `edit` / `apply_patch`
   tool call. That would (a) blow up the context for any non-trivial
   file, and (b) duplicate work the script already does efficiently.

   Use `python3 <skill_dir>/scripts/convert.py ...`. The script is at
   `<skill_dir>/scripts/convert.py`. Always pass `--in` and `--out`
   explicitly.

   - Encode — most common shapes:
     ```bash
     # binary (0/1), 16 bytes per line
     python3 <skill_dir>/scripts/convert.py encode \
       --in <src> --out <src>.bin.txt \
       --format binary --line-width 16

     # base-4
     python3 <skill_dir>/scripts/convert.py encode \
       --in <src> --out <src>.b4.txt \
       --format base4 --line-width 16

     # octal
     python3 <skill_dir>/scripts/convert.py encode \
       --in <src> --out <src>.oct.txt \
       --format octal --line-width 16

     # hex (xxd style)
     python3 <skill_dir>/scripts/convert.py encode \
       --in <src> --out <src>.xxd \
       --format hex --line-width 16 --space --offset
     ```
   - Decode — `auto` picks the right radix by the dump's character set
     (a-f ⇒ hex, only 0/1 ⇒ binary, only 0-3 ⇒ base-4, only 0-7 ⇒ octal):
     ```bash
     python3 <skill_dir>/scripts/convert.py decode \
       --in <dump>.txt --out <restored> --format auto
     ```
     For xxd-style dumps add `--strip-offset`.

3. **Surface the script's stderr line.** Every run prints a one-line
   summary like
   `encoded X -> Y (5242880 bytes -> 41943040 chars, fmt=binary, expansion≈8x)`
   to stderr. Quote it back so the user sees the byte count, the dump
   size, the format, and the expansion factor. For files > 10 MB,
   mention the size and warn that the dump will be 2–8× the input.

4. **Verify when you can.** For round-trips where the original file
   checksum is known, or when the user asks "did it really preserve
   everything?", decode the dump back and `md5sum` both sides. The
   skill's `--format auto` already routes 0/1 to binary, 0-3 to base-4,
   0-7 to octal, anything with a-f to hex.

5. **Deliver the output file.** Use `<deliver-assets>` to hand the .txt
   back. Never tell the user the file exists without actually uploading
   it (see memory HOT rule).

## Output contract

- One text file the user can open in any editor or terminal.
- Format is one of:
  - Plain `0`/`1` stream (binary, 8 chars/byte).
  - Plain `0`-`3` stream (base-4, 4 chars/byte).
  - Plain `0`-`7` stream (octal, 3 chars/byte).
  - Plain hex `00 ff 7f ...` (hex, 2 chars/byte; with optional `0x`
    prefix, optional `XXXXXXXX:` offset per line, optional spaces).
- Line breaks are `\n` (LF). Final line ends with `\n` unless
  `--line-width 0` (single line) and the file has content, in which
  case the trailing newline is preserved.
- The script is **streaming** (1 MiB read chunks, line-buffered writes),
  so the process never holds the full file in memory. The text file
  will be 2–8× the input size — warn the user when input is large.

## Failure handling

- **Decode produces wrong byte count** → user likely fed xxd-style text
  without `--strip-offset`, or the input mixes radices. Re-run with
  the right flag; or, if the dump is genuinely mixed, ask the user to
  confirm the radix.
- **Auto-detect picks the wrong radix** → happens for hex dumps that
  contain only decimal digits (e.g. `00112233`). Tell the user to pass
  `--format hex` explicitly in that case.
- **Output file is huge** → binary is ~8× input. Suggest a denser radix
  (hex) instead, or trim the input range.
- **User wants base64 / URL-encoding instead** → not this skill; do the
  conversion with plain shell (`base64` / `python3 -c "import base64; ..."`).
- **User wants to inspect but not save the file** → encode to a temp
  path, then `head` / `tail` it; do not read the whole dump into context.
- **"Just show me the first 256 bytes as hex"** → still encode the full
  file if the user wants the artifact; for one-off previews, use
  `head -c 256 <file> | od -An -tx1` directly.
- **User asks for a "binary file" (an executable, not 0/1 text)** →
  wrong skill; that is regular file handling, no conversion needed.

## Examples

**Input:** "把这个 PDF 转成 0 和 1 的 txt 发我"
**Action:** `encode --format binary --line-width 16`. The script writes the
dump to disk; the agent never holds the bytes. Note the ~8× expansion
when relaying the size.

**Input:** "用 xxd 的格式给我 dump 一下"
**Action:** `encode --format hex --line-width 16 --space --offset`. The
output mimics `xxd` so the user can re-run it through this skill's
decode (with `--strip-offset`) to get the original back.

**Input:** "再给我一个八进制的版本"
**Action:** `encode --format octal --line-width 16`. Same source, different
radix — no need to re-upload the file.

**Input:** "把这份 hex 文本还原回 png"
**Action:** `decode --format auto` to a `.png` path. If the file came
from xxd or this skill's `--offset` mode, also pass `--strip-offset`.
Verify with `md5sum` if the original checksum is available.
