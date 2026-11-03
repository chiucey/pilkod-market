# Unicode Symbol Block Quick Reference

When the user asks for a bullet / arrow / box / math / decorative symbol, you usually want a code point from one of these blocks. Each block has a range and a one-line "best for" tag.

## Most useful blocks (cite range, not full table)

| Block | Range | What lives here | Common asks |
|---|---|---|---|
| Arrows | `U+2190`–`U+21FF` | ←→↑↓ ⇒⇔ ↦↩↪ | "arrow", "implies", "right arrow" |
| Supplemental Arrows | `U+2900`–`U+297F` | ⇄⇆ ⇋ ⇎ | "long arrow", "mapping" |
| Miscellaneous Symbols | `U+2600`–`U+26FF` | ★☆ ☀☁☂☃ ☮☯ ☠ ☢☣ | "star", "weather", "warning" |
| Misc Symbols and Pictographs | `U+1F300`–`U+1F5FF` | 🌍🌎🌏 🌵🌲 🌊 🐌🐛 | emoji, weather, animals, plants |
| Emoticons | `U+1F600`–`U+1F64F` | 😀😁😂🤣😃😄😅 | classic emoji faces |
| Geometric Shapes | `U+25A0`–`U+25FF` | ■□▢▣ ▪▫ ▲△▴▵ ▶▷▸▹ ▼▽▾▿ ◀◁◂◃ | "box", "triangle", "diamond" |
| Box Drawing | `U+2500`–`U+257F` | ─━ │┃ ┏┓┗┛ ┣┫┳┻╋ | "table", "border", "TUI art" |
| Block Elements | `U+2580`–`U+259F` | ▀▁▂▃▄▅▆▇█ ▔▕▖▗▘▙▚▛▜▝▞▟ | "shade", "progress bar" |
| Mathematical Operators | `U+2200`–`U+22FF` | ∀∃∄ ∈∉∋ ⊂⊃⊆⊇ ∩∪∧∨ ¬ ⇒⇔ | "math", "set" |
| Misc Mathematical Symbols-A | `U+27C0`–`U+27EF` | ⟀⟂⟃⟄ ⟜⟝⟞⟟ ⟁ ⟢⟣ | "math" |
| Misc Mathematical Symbols-B | `U+2980`–`U+29FF` | ⦀⦁⦂⦃⦄ ⦰⦱⦲⦳ | "math brackets" |
| Supplemental Math Ops | `U+2A00`–`U+2AFF` | ⨀⨁⨂⨃⨄ ⨅⨆ | "tensor", "large ops" |
| Math Alphanumeric Symbols | `U+1D400`–`U+1D7FF` | 𝐀-𝐙 𝑎-𝑧 𝛼-𝜔 𝟎-𝟗 𝔄-𝔜 | "fancy letters", "blackboard" |
| Enclosed Alphanumerics | `U+2460`–`U+24FF` | ① ② ③ Ⓐ Ⓑ ⓐ ⓑ ㊀ ㊁ | "numbered list", "circled" |
| Enclosed CJK Letters | `U+3200`–`U+32FF` | ㊗㊙ ㊠-㊿ ㈝㈞㈠-㉇ | "circled CJK" |
| Enclosed Ideographic Supplement | `U+1F100`–`U+1F1FF` | 🈁🈂 🈚🈯🈲🈳🈴🈵🈶🈷🈸🈹🈺 | "squared CJK" |
| Number Forms | `U+2150`–`U+218F` | ⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞⅟ | "fractions" |
| Roman Numerals | `U+2160`–`U+2188` | Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ Ⅵ Ⅶ Ⅷ Ⅸ Ⅹ Ⅺ Ⅻ | "roman" |
| Currency Symbols | `U+20A0`–`U+20CF` | € £ ¥ ₹ ₽ ₿ ¢ ₩ ₪ ₫ ₴ ₦ | "currency" |
| Letterlike Symbols | `U+2100`–`U+214F` | ℂ ℕ ℚ ℝ ℤ ℋ ℘ ℐ ℒ ℳ ⅍ ℀ ℁ | "math" |
| Superscripts and Subscripts | `U+2070`–`U+209F` | ⁰¹²³⁴⁵⁶⁷⁸⁹ ⁺⁻⁼⁽⁾ ₀₁₂₃₄₅ | "exponent", "subscript" |
| Combining Diacritical Marks | `U+0300`–`U+036F` | combining acute/grave/tilde/caret/etc. | "diacritics" |
| Combining Diacritical Marks Extended | `U+1AB0`–`U+1AFF` | more combining marks | "rare diacritics" |
| Combining Diacritical Marks Supplement | `U+1DC0`–`U+1DFF` | more combining marks | "rare diacritics" |
| Combining Marks for Symbols | `U+20D0`–`U+20FF` | combining arrows/circles over/under | "diacritic on symbol" |
| Phonetic Extensions | `U+1D00`–`U+1D7F` | small caps, phonetic | "phonetic" |
| CJK Symbols and Punctuation | `U+3000`–`U+303F` | 、。〃〄 〇々〆〇 | "CJK punctuation" |
| CJK Compatibility Forms | `U+FE30`–`U+FE4F` | ︰︱︲︳︴︵︶︷︸ | "vertical CJK" |
| Fullwidth Forms | `U+FF00`–`U+FFEF` | Ａ-Ｚ ａ-ｚ ０-９ ！＠＃ | "fullwidth ASCII" |
| Halfwidth and Fullwidth Forms | `U+FF00`–`U+FFEF` | same as above | "fullwidth" |
| Private Use Area (BMP) | `U+E000`–`U+F8FF` | platform-specific glyphs (Apple Symbols, etc.) | platform-specific |
| Supplementary Private Use Area-A | `U+F0000`–`U+FFFFF` | app-defined | "custom font" |
| Supplementary Private Use Area-B | `U+100000`–`U+10FFFF` | app-defined | "custom font" |
| Tags | `U+E0000`–`U+E007F` | **deprecated** (was for tag-ranges); see `U+E0001`+ | — |
| Variation Selectors | `U+FE00`–`U+FE0F` and `U+E0100`–`U+E01EF` | variant selection | see invisible-table.md |

## Quick generation patterns

```python
def block_range(start, end):
    return [chr(c) for c in range(start, end + 1)]

arrows = block_range(0x2190, 0x21FF)
box_drawing = block_range(0x2500, 0x257F)
circled_digits = [chr(c) for c in range(0x2460, 0x2473)]  # ①..⑳
circled_letters = [chr(c) for c in range(0x24B6, 0x24CF)]  # Ⓐ..Ⓩ
math_bold = [chr(c) for c in range(0x1D400, 0x1D41A)]  # 𝐀..𝐙
fractions = [chr(c) for c in range(0x2150, 0x215F)]
```

## Matching "what I want" → block

- "I need a triangle" → `U+25B2` `U+25B3` `U+25B4` `U+25B5` etc. (Geometric Shapes `U+25A0`–`U+25FF`)
- "I need a star" → ★ `U+2605`, ☆ `U+2606`, ✶ `U+2736`, ✱ `U+2731` (Misc Symbols)
- "I need a check mark" → ✓ `U+2713`, ✔ `U+2714`, ✅ `U+2705`
- "I need a cross" → ✗ `U+2717`, ✘ `U+2718`, ❌ `U+274C`
- "I need a smiley" → 😀 `U+1F600` (Emoticons) or ✅/❌ (Misc Symbols/Pictographs)
- "I need a table border" → Box Drawing `U+2500`–`U+257F`
- "I need math letters" → Math Alphanumeric Symbols `U+1D400`–`U+1D7FF`
- "I need fancy numbers" → Enclosed Alphanumerics `U+2460`–`U+24FF` or Roman `U+2160`–`U+217F`
- "I need a subscript" → Superscripts/Subscripts `U+2070`–`U+209F`
- "I need a Greek letter" → Greek and Coptic `U+0370`–`U+03FF` (α β γ) or Math italic `U+1D6FC`–`U+1D71F` (𝛼 𝛽 𝛾)
- "I need playing-card suits" → ♠ `U+2660` ♥ `U+2665` ♦ `U+2666` ♣ `U+2663` (Misc Symbols)
- "I need a mahjong tile" → 🀀 `U+1F000`–`U+1F02F` (Mahjong Tiles)
- "I need a chess piece" → ♔ `U+2654`–`U+265F` (Misc Symbols)
- "I need a dice" → ⚀ `U+2680`–`U+2685` (Misc Symbols)

## Emoji skin-tone and ZWJ sequences

For "make a family emoji" or "rainbow flag", use **ZWJ sequences** (combining emoji with `U+200D`):

| Sequence | Result |
|---|---|
| 👨 + ZWJ + 👩 + ZWJ + 👧 + ZWJ + 👦 | 👨‍👩‍👧‍👦 family |
| 🏳 + ZWJ + 🌈 | 🏳️‍🌈 rainbow flag |
| 👩 + ZWJ + 💻 | 👩‍💻 woman technologist |
| ⌨ + VS16 | ⌨️ keyboard (forces emoji style) |

Skin tones: 🏻 `U+1F3FB` 🏼 `U+1F3FC` 🏽 `U+1F3FD` 🏾 `U+1F3FE` 🏿 `U+1F3FF`. Append after the base emoji.

For monochrome vs emoji style, append `U+FE0E` (text) or `U+FE0F` (emoji) after the base. Example: `❤` + `U+FE0F` = ❤️.
