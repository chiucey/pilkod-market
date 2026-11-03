#!/usr/bin/env python3
"""File ↔ radix-text converter (binary / base-4 / octal / hex).

Each input byte is rendered as a fixed-width digit string:

    binary  -> 8 chars '0'/'1'   (1 byte = 8 binary digits)
    base4   -> 4 chars '0'..'3'   (1 byte = 4 base-4 digits, 4**4 == 256)
    octal   -> 3 chars '0'..'7'   (1 byte = 3 octal digits,  8**3 >  256)
    hex     -> 2 chars '0'..'f'   (1 byte = 2 hex digits)

Usage:
    # Encode a file to 0/1 text
    convert.py encode --in FILE --out OUT.txt --format binary

    # Encode to xxd-style hex
    convert.py encode --in FILE --out OUT.txt --format hex \\
        --line-width 16 --prefix --offset

    # Encode to base-4 / octal
    convert.py encode --in FILE --out OUT.txt --format base4 --line-width 16
    convert.py encode --in FILE --out OUT.txt --format octal --line-width 16

    # Decode any of the four back to a file
    convert.py decode --in FILE.txt --out OUT --format auto

The script is strictly streaming: 1 MiB raw read chunks, line-buffered
output, never holds the full file in memory. Callers (LLM or human) should
invoke it as a subprocess and hand the output path back; do NOT slurp the
generated text into context.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable, Iterable, Iterator

CHUNK_SIZE = 1 << 20  # 1 MiB raw read chunks


# ---------- format registry ----------
#
# Each entry: (chars_per_byte, base, digit_pattern, formatter, parse_token)
# - chars_per_byte: how many output chars each input byte produces
# - base:           numeric base (2/4/8/16)
# - digit_pattern:  regex of one token's allowed character class
# - formatter:      byte -> N-char digit string
# - parse_token:    N-char token -> byte (0..255)

def _fmt_binary(b: int) -> str:
    return f"{b:08b}"


def _fmt_base4(b: int) -> str:
    # 0..255 -> exactly 4 base-4 digits, MSB first
    return (
        f"{(b >> 6) & 0x3}"
        f"{(b >> 4) & 0x3}"
        f"{(b >> 2) & 0x3}"
        f"{b & 0x3}"
    )


def _fmt_octal(b: int) -> str:
    return f"{b:03o}"


def _fmt_hex(b: int) -> str:
    return f"{b:02x}"


def _parse_hex(t: bytes) -> int:
    return int(t, 16)


FORMATS: dict[str, dict] = {
    "binary": {
        "chars_per_byte": 8,
        "base": 2,
        "token_pattern": re.compile(rb"[01]{8}"),
        "formatter": _fmt_binary,
        "token_byte": 8,  # pattern matches 8-char tokens
    },
    "base4": {
        "chars_per_byte": 4,
        "base": 4,
        "token_pattern": re.compile(rb"[0-3]{4}"),
        "formatter": _fmt_base4,
        "token_byte": 4,
    },
    "octal": {
        "chars_per_byte": 3,
        "base": 8,
        "token_pattern": re.compile(rb"[0-7]{3}"),
        "formatter": _fmt_octal,
        "token_byte": 3,
    },
    "hex": {
        "chars_per_byte": 2,
        "base": 16,
        "token_pattern": re.compile(rb"[0-9a-fA-F]{2}"),
        "formatter": _fmt_hex,
        "token_byte": 2,
    },
}


# ---------- encoding ----------

def _encode_stream(
    src: Iterable[int],
    *,
    fmt: str,
    line_width: int,
    separator: str,
    prefix: bool = False,
    upper: bool = False,
    with_offset: bool = False,
) -> Iterator[str]:
    """Generic radix encoder. line_width = 0 means single line."""
    spec = FORMATS[fmt]
    formatter: Callable[[int], str] = spec["formatter"]
    if fmt == "hex" and upper:
        formatter = lambda b: f"{b:02X}"  # noqa: E731

    def _render(b: int) -> str:
        token = formatter(b)
        if fmt == "hex" and prefix:
            return "0x" + token
        return token

    line: list[str] = []
    line_count = 0
    offset = 0
    for byte in src:
        line.append(_render(byte))
        line_count += 1
        if line_width and line_count >= line_width:
            joined = separator.join(line)
            if fmt == "hex" and with_offset:
                yield f"{offset:08x}: {joined}\n"
            else:
                yield joined + "\n"
            offset += line_count
            line = []
            line_count = 0
    if line:
        joined = separator.join(line)
        if fmt == "hex" and with_offset:
            yield f"{offset:08x}: {joined}\n"
        else:
            yield joined + ("\n" if line_width else "")


# ---------- decoding ----------

def _iter_tokens(text: bytes, fmt: str) -> Iterator[int]:
    spec = FORMATS[fmt]
    base = spec["base"]
    for tok in spec["token_pattern"].findall(text):
        v = int(tok, base)
        if 0 <= v <= 255:
            yield v


OFFSET_PREFIX = re.compile(rb"^\s*[0-9a-fA-F]{1,16}\s*:\s*")


def _strip_offsets(text: bytes) -> bytes:
    return b"\n".join(OFFSET_PREFIX.sub(b"", line) for line in text.splitlines())


def _detect_format(text: bytes) -> str:
    """Heuristic: pick the radix whose digit alphabet fully covers the sample.

    Order of resolution:
      1. If sample contains a-f (any case) -> hex (only hex uses a-f).
      2. If unique digits are subset of {0,1}    -> binary
      3. If unique digits are subset of {0..3}    -> base4
      4. If unique digits are subset of {0..7}    -> octal
      5. Otherwise (digits include 8/9 but no a-f) -> hex fallback
    """
    cleaned = re.sub(rb"[^0-9a-fA-F]", b"", text[:4096])
    if not cleaned:
        return "hex"
    unique = set(cleaned)
    if unique & set(b"abcdefABCDEF"):
        return "hex"
    if unique <= {b"0"[0], b"1"[0]}:
        return "binary"
    if not (unique & set(b"456789")):
        return "base4"
    if not (unique & set(b"89")):
        return "octal"
    return "hex"


def decode_stream(text: bytes, fmt: str, dst, *, strip_offset: bool = False) -> int:
    """Stream decoded bytes into dst. Returns byte count."""
    if fmt == "auto":
        fmt = _detect_format(text)
    if fmt == "hex" and strip_offset:
        text = _strip_offsets(text)

    n = 0
    buf = bytearray()
    for byte in _iter_tokens(text, fmt):
        buf.append(byte)
        n += 1
        if len(buf) >= CHUNK_SIZE:
            dst.write(buf)
            buf.clear()
    if buf:
        dst.write(buf)
    return n


# ---------- CLI ----------

def _iter_bytes(path: Path) -> Iterator[int]:
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                return
            yield from chunk


def cmd_encode(args: argparse.Namespace) -> int:
    src_path = Path(args.input)
    if not src_path.is_file():
        print(f"error: not a file: {src_path}", file=sys.stderr)
        return 2
    if args.format not in FORMATS:
        print(f"error: unknown format '{args.format}'", file=sys.stderr)
        return 2

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Sensible defaults per format
    if args.line_width is None:
        line_width = 16 if args.format == "hex" else 0
    else:
        line_width = max(0, args.line_width)
    sep = " " if args.space else ""

    written = 0
    with out_path.open("w", encoding="utf-8", newline="") as out:
        for piece in _encode_stream(
            _iter_bytes(src_path),
            fmt=args.format,
            line_width=line_width,
            separator=sep,
            prefix=args.prefix,
            upper=args.upper,
            with_offset=args.offset,
        ):
            out.write(piece)
            written += len(piece.encode("utf-8"))

    spec = FORMATS[args.format]
    print(
        f"encoded {src_path} -> {out_path} "
        f"({src_path.stat().st_size} bytes -> {written} chars, "
        f"fmt={args.format}, expansion≈{spec['chars_per_byte']}x)",
        file=sys.stderr,
    )
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    in_path = Path(args.input)
    if not in_path.is_file():
        print(f"error: not a file: {in_path}", file=sys.stderr)
        return 2

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with in_path.open("rb") as f:
        text = f.read()
    fmt = args.format
    detected = None
    if fmt == "auto":
        detected = _detect_format(text)
        fmt = detected

    if fmt not in FORMATS:
        print(f"error: unknown format '{fmt}'", file=sys.stderr)
        return 2

    with out_path.open("wb") as out:
        n = decode_stream(text, fmt, out, strip_offset=args.strip_offset)

    print(
        f"decoded {in_path} -> {out_path} "
        f"({len(text)} chars -> {n} bytes, fmt={fmt})",
        file=sys.stderr,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="convert.py",
        description="Convert files to/from radix text (binary/base4/octal/hex).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--in", dest="input", required=True, help="input file path")
    common.add_argument("--out", dest="output", required=True, help="output path")

    enc = sub.add_parser("encode", parents=[common], help="file -> radix text")
    enc.add_argument(
        "--format",
        choices=list(FORMATS.keys()),
        default="hex",
        help="output radix (default: hex)",
    )
    enc.add_argument(
        "--line-width", type=int, default=None,
        help="bytes per output line; 0 = single line. Default: 16 (hex) or 0 (others).",
    )
    enc.add_argument(
        "--space", action="store_true",
        help="separate bytes with a single space (e.g. 'ff 00' or '01010101 10101010')",
    )
    enc.add_argument(
        "--prefix", action="store_true",
        help="hex only: prefix each byte with '0x' (e.g. '0xff 0x00')",
    )
    enc.add_argument(
        "--upper", action="store_true",
        help="hex only: use uppercase letters (FF instead of ff)",
    )
    enc.add_argument(
        "--offset", action="store_true",
        help="hex only: prepend an 8-char hex address per line (xxd style)",
    )

    dec = sub.add_parser("decode", parents=[common], help="radix text -> file")
    dec.add_argument(
        "--format",
        choices=list(FORMATS.keys()) + ["auto"],
        default="auto",
        help="input radix (default: auto-detect)",
    )
    dec.add_argument(
        "--strip-offset", action="store_true",
        help="hex only: ignore an optional '<hex>: ' address prefix per line (xxd / hexdump style)",
    )

    enc.set_defaults(func=cmd_encode)
    dec.set_defaults(func=cmd_decode)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
