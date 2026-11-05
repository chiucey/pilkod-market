---
name: unicode-special-chars
description: Generate, inspect, encode, and decode Unicode characters — including invisible / zero-width / variation-selector / tag characters used as hidden markers, watermarks, anti-spam tokens, or steganography. Use when the user asks to "生成不可见字符", "zero-width text", "ZWJ/ZWNJ 文本", "零宽水印", "Unicode 转码", "HTML 实体", "URL 编码", "escape Unicode", "生成特殊符号", "tag character", "variation selector", "copy invisible char", or any task that needs encoding/decoding between UTF-8 bytes, code points, HTML/XML entities, URL percent-encoding, Java/Python/JS string escapes, CSS \NNNN, and visual inspection. Do NOT use for emoji rendering questions (route to image-creator) or for general "what does this symbol mean" lookups (route to web_search).
---

# Unicode Special Characters

A working toolkit for the two requests that actually show up: **(a) round-trip a character through every encoding layer** and **(b) emit invisible / tag / variation-selector strings that survive copy-paste but look empty**.

## Core toolkit (run in Python)

Always-available. No external deps. Use this as the source of truth for conversions and for inspecting unknown strings.

```python
def inspect(s: str) -> dict:
    """Decompose a string into every layer another system might see it as."""
    out = {"repr": repr(s), "length": len(s), "codepoints": []}
    for i, ch in enumerate(s):
        cp = ord(ch)
        out["codepoints"].append({
            "i": i, "ch": ch, "U+": f"U+{cp:04X}",
            "name": _name(cp),  # see _name below; may be None
            "cat": _cat(cp),    # see _cat below
            "utf8": ch.encode("utf-8").hex(),
            "html": f"&#{cp};" or f"&#x{cp:X};",
            "url":  "".join(f"%{b:02X}" for b in ch.encode("utf-8")),
            "py":   _py_escape(ch),
        })
    return out
```

`_name` and `_cat`: try `unicodedata.name(ch)` / `unicodedata.category(ch)`; on lookup failure fall back to a small built-in table for the common invisible chars (see `references/invisible-table.md`).

`inspect` is the single most useful function in this skill. When the user pastes a weird-looking-but-empty string, **run this first** — it tells you exactly what they actually have.

## Invisible & boundary characters (the actual toolbox)

| Codepoint | Name | Use case |
|---|---|---|
| `U+200B` | ZERO WIDTH SPACE (ZWSP) | word break without glyph; classic invisible watermark char |
| `U+200C` | ZERO WIDTH NON-JOINER (ZWNJ) | force ligature break (Persian/Arabic) |
| `U+200D` | ZERO WIDTH JOINER (ZWJ) | force ligature / join emoji sequences |
| `U+2060` | WORD JOINER | invisible non-breaking; preferred over ZWNBSP |
| `U+FEFF` | ZERO WIDTH NO-BREAK SPACE / BOM | file BOM; sticky when pasted mid-string |
| `U+200E` / `U+200F` | LRM / RLM | direction control; survive in many "plain text" fields |
| `U+2061`–`U+2064` | invisible math operators | math-mode spacing; copy-paste invisible |
| `U+115F` / `U+1160` / `U+17B4` / `U+17B5` | Hangul fillers / Khmer inherent vowels | count as "letters" but render zero-width in many fonts |
| `U+2062` | INVISIBLE TIMES | mathematical "×" with no glyph |
| `U+E0001`–`U+E007F` | LANGUAGE TAG | invisible ASCII-mirrorable (each stores a printable letter); ideal for hidden markers / steganography |
| `U+FE00`–`U+FE0F` | VARIATION SELECTORS (VS1–VS16) | select glyph variant (most famously `‍` + `️` = monochrome emoji) |
| `U+E0100`–`U+E01EF` | VARIATION SELECTORS SUPPLEMENT | extended variants for CJK / historical scripts |
| `U+FFF9`–`U+FFFB` | INTERLINEAR ANNOTATION | embed hidden metadata, often ignored by renderers |
| `U+2028` / `U+2029` | LINE / PARAGRAPH SEPARATOR | more "newline-like" than `\n`; bypass naive line filters |
| `U+0085` | NEL | another "newline" that isn't `\n` |
| `U+202E` | RIGHT-TO-LEFT OVERRIDE | can flip display order — handle with care, security-relevant |
| `U+180E` | MONGOLIAN VOWEL SEPARATOR | width-zero in most fonts; **deprecated in Unicode 12** but still works in many editors |

Full list with category, UTF-8 bytes, render-behavior notes → `references/invisible-table.md`.

### Generation snippets

```python
# 1) Zero-width watermark (looks like "secret" but is "se\u200bcret")
def zwsp_text(s): return "\u200b".join(s)

# 2) Tag-character ASCII mirror (invisible, but readable in `inspect`)
def tag_text(s): return "".join(chr(0xE0001 + ord(c)) for c in s)

# 3) Variation-selector flood (used to defeat naive dedup)
def vs_flood(s, n=4): return s + "".join(chr(0xFE00 + i) for i in range(n))

# 4) "Looks empty but has length 5"
empty_looking = "\u200B\u200C\u200D\u2060\uFEFF"

# 5) Newline-lookalike that bypasses `\n` filters
not_a_newline = "line1\u2028line2"   # also: \u0085, \u2029
```

## Encoding round-trips (cheat sheet)

When the user asks for **"escape this for X"**, use the right tool — don't hand-roll:

| Target | Python one-liner |
|---|---|
| UTF-8 hex bytes | `s.encode("utf-8").hex()` |
| HTML numeric | `''.join(f'&#{ord(c)};' for c in s)` |
| HTML hex | `''.join(f'&#x{ord(c):X};' for c in s)` |
| URL percent-encoded | `urllib.parse.quote(s)` |
| Python `\u` escape | `s.encode("unicode_escape").decode("ascii")` |
| JSON `\u` escape | `json.dumps(s, ensure_ascii=False)` |
| JS `\u` / `\xNN` | same as Python; for non-BMP use `\u{1F600}` |
| CSS `\NNNN ` | `''.join(f'\\{ord(c):X} ' for c in s)` (trailing space = hex terminator) |
| Java `\uXXXX` | only for BMP; for supplementary use surrogate pair `\uD83D\uDE00` |
| Base64 of UTF-8 | `base64.b64encode(s.encode("utf-8")).decode()` |
| Punycode (for IDN) | `s.encode("punycode").decode("ascii")` |

For the **reverse direction** (user pastes an escape and wants the char), apply the matching decode and show the result with `inspect()`.

## Common requests → recipe

1. **"Hide a secret message inside normal text"** → emit `zwsp_text` (or `tag_text` for ASCII-mirrorable). Tell the user the trade-off: ZWSP-based marks survive most platforms but break on Twitter/X and some old forums; tag characters are more robust but bigger.
2. **"Make a string that looks empty"** → emit `empty_looking` (above) and show `len()` + `inspect()` so they see it's not actually empty.
3. **"This string breaks the parser, what's in it?"** → run `inspect()` on the user's input. 90% of the time it's a BOM, a ZWJ, an RTL override, or a Mongolian vowel sep.
4. **"Generate a bullet / arrow / math symbol"** → reach for the **Enclosed Alphanumerics** (①②③…), **Arrows** (←→↑↓⇒⇔…), **Mathematical Alphanumeric Symbols** (𝐀-𝐙, 𝑎-𝑧), or **Miscellaneous Symbols and Arrows** block. Reference: `references/symbol-blocks.md`.
5. **"Encode a username so the platform can't see it"** → warn that this is platform-policy-fragile; offer ZWSP watermarking as a low-risk option.

## Failure modes / pitfalls

- **Invisible chars in source code → silent bugs.** `len("\u200B") == 1` and `"a" == "a\u200B"` is `False`. Always normalize with `s.replace("\u200B", "")` before comparison unless invisibility is the point.
- **RTL override (`U+202E`) is a phishing vector.** Filenames, URLs, terminal output. Surface it in `inspect()` and warn the user; do not emit it silently.
- **Variation selectors stack.** The 16 VS in the BMP + 240 in the Supp VS are designed to combine with the *preceding* code point. A bare `VS16` does nothing; you need `char + VS16`.
- **Tag chars (`U+E0001`+) are technically CJK Compatibility Tags, not "private use".** Some normalizers strip them. Test on the target system.
- **Python `len()` counts code points, not graphemes.** `len("👨‍👩‍👧") == 5` (man + ZWJ + woman + ZWJ + girl). Use `grapheme` library or manually walk if you need visual length.
- **Mongolian Vowel Separator (U+180E)** is deprecated; some platforms now render it as a visible glyph. Prefer `U+2060` Word Joiner for "modern invisible space".
- **"Plain text" is a lie.** Almost every "plain text" field (CSV cells, JSON strings, form inputs) preserves every Unicode code point. The "invisible" guarantee only holds against human eyes, not against any program that calls `inspect()`.

## Output contract

When invoked, this skill should produce (pick what's relevant):

1. **For "convert X"** — the target-encoding string, plus the round-trip-verified original for confirmation.
2. **For "make invisible"** — the string + a `inspect()` dump so the user sees it really is there.
3. **For "what is this"** — the `inspect()` table, called out for any security-relevant code points (RTL override, homoglyphs, etc.).

Never just hand the user bytes/hax without telling them what those bytes will look like on screen.
