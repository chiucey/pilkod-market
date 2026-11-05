# Invisible / Zero-Width Character Reference

Complete table of the code points that look empty (or near-empty) in most fonts but **still take up a position in the string**. Each entry: codepoint, official name, category, UTF-8 bytes, common use, and a render-behavior note.

> The Python `unicodedata` module covers most of these. For the few that return `None` (deprecated chars, CJK tags), use the fallback `_name` table in `SKILL.md`.

## Zero-width "spacing" characters

| Codepoint | Name | Cat | UTF-8 | Common use | Render note |
|---|---|---|---|---|---|
| `U+200B` | ZERO WIDTH SPACE | Cf | `E2 80 8B` | word break, invisible watermark | Truly zero-width in nearly all fonts |
| `U+200C` | ZERO WIDTH NON-JOINER | Cf | `E2 80 8C` | prevent ligature | Zero-width; essential for Persian/Arabic |
| `U+200D` | ZERO WIDTH JOINER | Cf | `E2 80 8D` | force ligature / join emoji | Zero-width; required for ZWJ-emoji like 👨‍👩‍👧 |
| `U+FEFF` | ZERO WIDTH NO-BREAK SPACE / BOM | Cf | `EF BB BF` | file BOM, also used as invisible marker | Often auto-stripped at file boundaries; **sticky when pasted mid-string** |
| `U+2060` | WORD JOINER | Cf | `E2 81 A0` | modern replacement for `U+FEFF` mid-string | Truly zero-width; preferred over ZWNBSP |
| `U+180E` | MONGOLIAN VOWEL SEPARATOR | Cf | `E1 A0 8E` | legacy zero-width separator | **Deprecated in Unicode 12**; some renderers now show it as a visible thin glyph. Avoid for new work. |
| `U+034F` | COMBINING GRAPHEME JOINER | Mn | `CD 8F` | rare; sequence boundary marker | Zero-width; very rarely used |
| `U+115F` | HANGUL CHOSEONG FILLER | Lo | `E1 85 9F` | counts as letter, renders empty | Width-zero in most fonts |
| `U+1160` | HANGUL JUNGSEONG FILLER | Lo | `E1 85 A0` | counts as letter, renders empty | Width-zero in most fonts |
| `U+17B4` | KHMER VOWEL INHERENT AQ | Mn | `E1 9E B4` | visual invisible in non-Khmer | Zero-width outside Khmer fonts |
| `U+17B5` | KHMER VOWEL INHERENT AA | Mn | `E1 9E B5` | visual invisible in non-Khmer | Zero-width outside Khmer fonts |
| `U+2061` | FUNCTION APPLICATION | Cf | `E2 81 A1` | math invisible × | Zero-width |
| `U+2062` | INVISIBLE TIMES | Cf | `E2 81 A2` | math invisible × | Zero-width |
| `U+2063` | INVISIBLE SEPARATOR | Cf | `E2 81 A3` | math invisible separator | Zero-width |
| `U+2064` | INVISIBLE PLUS | Cf | `E2 81 A4` | math invisible + | Zero-width |

## Direction / formatting (carry behavior, not just rendering)

| Codepoint | Name | Cat | UTF-8 | Behavior |
|---|---|---|---|---|
| `U+200E` | LEFT-TO-RIGHT MARK | Cf | `E2 80 8E` | invisible; flips bidi context to LTR |
| `U+200F` | RIGHT-TO-LEFT MARK | Cf | `E2 80 8F` | invisible; flips bidi context to RTL |
| `U+202A` | LEFT-TO-RIGHT EMBEDDING | Cf | `E2 80 AA` | starts LTR run |
| `U+202B` | RIGHT-TO-LEFT EMBEDDING | Cf | `E2 80 AB` | starts RTL run |
| `U+202C` | POP DIRECTIONAL FORMATTING | Cf | `E2 80 AC` | ends run |
| `U+202D` | LEFT-TO-RIGHT OVERRIDE | Cf | `E2 80 AD` | force LTR (display-order override) |
| `U+202E` | RIGHT-TO-LEFT OVERRIDE | Cf | `E2 80 AE` | **force RTL — security-relevant** (filename spoofing) |
| `U+2066`–`U+2069` | LRI/RLI/FSI/PDI | Cf | `E2 81 A6`–`E2 81 A9` | isolate runs (safer than overrides) |

## Annotation / metadata slots (often ignored by renderers)

| Codepoint | Name | Cat | UTF-8 | Use |
|---|---|---|---|---|
| `U+FFF9` | INTERLINEAR ANNOTATION ANCHOR | Cf | `EF BF B9` | embed hidden annotation |
| `U+FFFA` | INTERLINEAR ANNOTATION SEPARATOR | Cf | `EF BF BA` | ditto |
| `U+FFFB` | INTERLINEAR ANNOTATION TERMINATOR | Cf | `EF BF BB` | ditto |
| `U+E0001`–`U+E007F` | LANGUAGE TAG | Cf | `F3 A0 80 81`–`F3 A0 81 BF` | **invisible ASCII mirror** — each `U+E00XX` = ASCII char `XX`. Tag is invisible, ASCII-mirrorable. **Watch for normalization**: NFKC may strip. |

## Variation selectors (combine with preceding char)

| Codepoint block | Name | Range | Use |
|---|---|---|---|
| `U+FE00`–`U+FE0F` | VARIATION SELECTOR-1..16 (VS1–VS16) | 16 chars | glyph variant; `VS15` = text, `VS16` = emoji |
| `U+E0100`–`U+E01EF` | VARIATION SELECTORS SUPPLEMENT | 240 chars | extended variants for CJK, Tangut, etc. |

VS **must follow a base character**; alone they do nothing. `U+2764` + `U+FE0F` = red heart emoji; `U+2764` + `U+FE0E` = text heart (monochrome).

## "Newline-like" that aren't `\n`

| Codepoint | Name | Cat | UTF-8 | Where it acts as newline |
|---|---|---|---|---|
| `U+0085` | NEXT LINE (NEL) | Cc | `C2 85` | legacy Unix, some terminals |
| `U+2028` | LINE SEPARATOR | Zl | `E2 80 A8` | formal line break; ECMA-48, JS `String.split` |
| `U+2029` | PARAGRAPH SEPARATOR | Zp | `E2 80 A9` | formal paragraph break; same as above |
| `U+2028` vs `\n` | — | — | — | `U+2028` is its own line break in JS; `\n` is not. Useful for "bypass naive line filters" |

## Soft / controllable characters

| Codepoint | Name | Cat | UTF-8 | Behavior |
|---|---|---|---|---|
| `U+00AD` | SOFT HYPHEN | Cf | `C2 AD` | invisible; appears as `-` only at line break |
| `U+034F` | COMBINING GRAPHEME JOINER | Mn | `CD 8F` | grapheme cluster boundary marker |
| `U+061C` | ARABIC LETTER MARK | Cf | `D8 9C` | Arabic shaping context |
| `U+206A`–`U+206F` | Deprecated formatting | Cf | varies | **deprecated; avoid** |

## Quick generation script

```python
def is_invisible(cp: int) -> bool:
    """Returns True for chars that are zero-width in most fonts."""
    return (
        0x200B <= cp <= 0x200F       # ZWSP / ZWNJ / ZWJ / LRM / RLM
        or cp == 0x202A <= cp <= 0x202E
        or 0x202A <= cp <= 0x202E     # directional embedding/override
        or 0x2060 <= cp <= 0x2064     # WJ, math invisibles
        or 0x2066 <= cp <= 0x2069     # isolate runs
        or cp in (0xFEFF, 0x180E, 0x00AD, 0x034F, 0x061C, 0x0085, 0x115F, 0x1160, 0x17B4, 0x17B5)
        or 0xFFF9 <= cp <= 0xFFFB
        or 0xE0001 <= cp <= 0xE007F
        or 0xFE00 <= cp <= 0xFE0F
        or 0xE0100 <= cp <= 0xE01EF
        or 0x2028 <= cp <= 0x2029
    )
```

## Platform gotchas (live data, may shift)

- **Twitter/X** strips `U+200B`, `U+200C`, `U+200D` in some surfaces (it normalizes). Tag chars (`U+E0001`+) survive.
- **Discord** keeps all ZW chars in display; counts toward the 2000-char limit even when invisible.
- **GitHub** (commit messages, comments) keeps ZWSP/ZWNJ/ZWJ. Tag chars preserved in raw view, may render as boxes in web.
- **Windows Notepad** historically stripped ZW chars on save; modern Notepad keeps them.
- **Many "plain text" sanitizers** (HTML form validators, SQL escape routines) treat them as zero-length — **but they aren't.** Always re-validate after sanitization.
