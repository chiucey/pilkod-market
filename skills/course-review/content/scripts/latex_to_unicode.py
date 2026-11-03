#!/usr/bin/env python3
"""Convert a LaTeX subset used in course cards into inline Unicode/HTML.

Removes the runtime KaTeX CDN dependency entirely, so the review panel opens
instantly and works offline. The subset below covers what actually shows up in
course review cards (no \frac, no matrices, no multi-line environments).

Usage:
    python3 latex_to_unicode.py topics.json -o topics.pretty.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

# LaTeX -> Unicode. Longest keys first so \rightarrow never eats \rightarrowarrow.
SYMBOLS = {
    r"\Leftrightarrow": "⟺", r"\leftrightarrow": "↔", r"\Rightarrow": "⇒", r"\rightarrow": "→",
    r"\longrightarrow": "⟶", r"\implies": "⟹", r"\xrightarrow": "⟶",
    r"\xleftarrow": "⟵", r"\longleftarrow": "⟵", r"\to": "→",
    r"\nRightarrow": "⇏", r"\notRightarrow": "⇏", r"\nLeftarrow": "⇍",
    r"\nleftrightarrow": "↮", r"\nmid": "∤", r"\ntop": "⊬", r"\nsubset": "⊄",
    r"\Leftrightarrow": "⟺", r"\iff": "⟺", r"\to": "→",
    r"\lor": "∨", r"\land": "∧", r"\vee": "∨", r"\wedge": "∧",
    r"\lnot": "¬", r"\neg": "¬", r"\sim": "∼", r"\approx": "≈", r"\neq": "≠",
    r"\forall": "∀", r"\exists": "∃", r"\subseteq": "⊆", r"\subset": "⊂",
    r"\supseteq": "⊇", r"\in": "∈", r"\notin": "∉", r"\cup": "∪", r"\cap": "∩",
    r"\emptyset": "∅", r"\Sigma": "Σ", r"\sigma": "σ", r"\Phi": "Φ", r"\phi": "φ",
    r"\theta": "θ", r"\alpha": "α", r"\beta": "β", r"\lambda": "λ", r"\mu": "μ",
    r"\times": "×", r"\cdot": "·", r"\equiv": "≡", r"\models": "⊨", r"\vdash": "⊢",
    r"\leq": "≤", r"\ge": "≥", r"\geq": "≥", r"\le": "≤", r"\ne": "≠",
    r"\ldots": "…", r"\dots": "…", r"\cdots": "…",
    r"\quad": "　", r"\qquad": "　　",
    r"\{": "{", r"\}": "}", r"\_": "_", r"\$": "$",
    # ch4 evidence-theory + reliability symbols
    r"\varnothing": "∅", r"\emptyset": "∅", r"\oplus": "⊕",
    r"\pm": "±", r"\propto": "∝", r"\perp": "⊥", r"\parallel": "∥",
    r"\bigcirc": "○", r"\bullet": "•", r"\circ": "∘",
    r"\prime": "′", r"\infty": "∞", r"\partial": "∂",
    # operators -> keep them as plain readable names (min/max read better than ⋀)
    r"\max": "max", r"\min": "min", r"\log": "log", r"\exp": "exp",
    r"\sin": "sin", r"\cos": "cos", r"\tan": "tan", r"\arg": "arg",
    r"\sum": "Σ", r"\prod": "Π", r"\int": "∫",
    r"\lim": "lim", r"\gcd": "gcd", r"\deg": "deg", r"\det": "det",
    r"\not=": "≠", r"\dotsb": "…", r"\dotsc": "…", r"\cdots": "…",
    r"\bigcirc": "○", r"\circ": "∘", r"\bullet": "•", r"\star": "★",
    r"\checkmark": "✓", r"\dagger": "†", r"\ell": "ℓ",
    # arg-style spacing commands -> plain space
    r"\,": " ", r"\;": " ", r"\!": "", r"\:": " ", r"\; ": " ",
    # size / decoration wrappers: drop them, keep contents
    r"\bigl": "", r"\bigr": "", r"\Bigl": "", r"\Bigr": "",
    r"\bigl|": "|", r"\bigr|": "|", r"\big|": "|",
    r"\left": "", r"\right": "", r"\bigl(": "(", r"\bigr)": ")",
    r"\displaystyle": "",
    # NOTE: deliberately NOT mapping , and ; — a full-width comma inside a
    # predicate like LIKE(x,y) reads as a typo when transcribed in an exam.
}
# bare LaTeX that is really just a variable name -> keep as-is
SAFE_WORD = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_()\s,.'\"-]*$")
BARE_SYMBOLS = {
    r"\forall": "∀", r"\exists": "∃", r"\neg": "¬", r"\land": "∧", r"\lor": "∨",
    r"\to": "→", r"\Rightarrow": "⇒", r"\iff": "⟺", r"\leq": "≤", r"\geq": "≥",
    r"\subseteq": "⊆", r"\in": "∈", r"\cup": "∪", r"\cap": "∩", r"\times": "×",
    r"\neq": "≠", r"\approx": "≈", r"\sim": "∼", r"\emptyset": "∅",
}

SUBSCRIPT = {"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆",
             "7": "₇", "8": "₈", "9": "₉", "a": "ₐ", "b": "ᵦ", "c": "꜀", "d": "ᵈ",
             "e": "ₑ", "f": "ꜰ", "g": "ᵍ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
             "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "q": "q", "r": "ᵣ",
             "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "w": "𝓌", "x": "ₓ", "y": "ᵧ", "z": "𝓏"}


def _strip_braced(s, cmd):
    """Replace \\cmd{...} with the inner text, honouring nested braces."""
    marker = "\\" + cmd + "{"
    out, i = [], 0
    while True:
        j = s.find(marker, i)
        if j < 0:
            out.append(s[i:])
            return "".join(out)
        out.append(s[i:j])
        depth, k = 1, j + len(marker)
        while k < len(s) and depth:
            if s[k] == "{":
                depth += 1
            elif s[k] == "}":
                depth -= 1
            k += 1
        out.append(s[j + len(marker):k - 1])
        i = k


def convert_math(expr):
    """Convert one LaTeX expression body to Unicode/HTML."""
    s = expr.strip()

    # \frac{a}{b} -> (a)/(b)  (kept simple; nothing in these cards nests)
    def frac(m):
        return f"({m.group(1)})/({m.group(2)})"
    for _ in range(3):
        s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", frac, s)

    # \xrightarrow{label} / \xleftarrow{label}: keep the arrow, drop the label.
    # Must run BEFORE symbol replacement, or \xrightarrow{...} is already gone.
    s = re.sub(r"\\x?(?:rightarrow|leftarrow)\{[^{}]*\}", "→", s)

    # \text{...} / \mathrm{...} -> contents. Must run BEFORE the generic
    # command stripper below, or \text{foo} degrades to "textfoo".
    s = re.sub(r"\\(?:text|mathrm|mathbf|mathit|operatorname)\{([^{}]*)\}", r"\1", s)

    # \boxed{...} -> contents, brace-balanced. A single-level regex fails on
    # \boxed{\{a\} \lor \{b\}} which is exactly what clause-set answers use.
    for _ in range(4):
        new = _strip_braced(s, "boxed")
        if new == s:
            break
        s = new
    s = re.sub(r"\\boxed\s+([A-Za-z0-9])", r"\1", s)   # \boxed X (no braces)


    # escaped chars
    s = re.sub(r"\\([%&#_{}])", r"\1", s)

    # symbols, longest-first
    for k in sorted(SYMBOLS, key=len, reverse=True):
        s = s.replace(k, SYMBOLS[k])

    # safety: nothing dangerous survived. Escape BEFORE the sub/sup tags are
    # emitted, otherwise this would mangle the very <sub>/<sup> we just built.
    s = s.replace("<", "&lt;").replace(">", "&gt;")

    # subscripts  X_{ab}  ->  <sub>ab</sub>   (emitted after escaping)
    s = re.sub(r"_\{([^{}]*)\}", lambda m: f"<sub>{m.group(1)}</sub>", s)
    # superscripts X^{2}  ->  <sup>2</sup>
    s = re.sub(r"\^\{([^{}]*)\}", lambda m: f"<sup>{m.group(1)}</sup>", s)
    return s

    # \, \; \! \  thin space commands
    s = re.sub(r"\\[,;:!> ]", " ", s)

    # \ (backslash-space) and \quad leftovers
    s = s.replace("\\ ", " ")

    # any remaining backslash command -> drop the backslash, keep the name readable
    s = LOOKALIKE.sub("\\\\n", s)   # protect "\nCF(E)" style function names
    s = re.sub(r"\\([A-Za-z]+)", r"\1", s)

    # collapse whitespace
    s = re.sub(r"[ \t]{2,}", " ", s).strip()

    # Tidy spacing around converted symbols: "P→ Q" -> "P→Q",
    # "¬ P" -> "¬P" (a stray space reads as a different token when dictating
    # the formula out loud while writing it on an exam paper).
    s = re.sub(r"([→⇒⟺↔∧∨¬⊆⊂⊇∈∉∪∩×≈∼≠≡⊨⊢≤≥])\s+", r"\1", s)
    s = re.sub(r"\s+([)\]])", r"\1", s)
    s = re.sub(r"([(\[])\s+", r"\1", s)
    return s


def convert_text(text):
    """Convert every $...$ / $$...$$ block inside a string, then bare subscripts."""
    if not isinstance(text, str):
        return text

    if "$" in text:
        def block(m):
            return convert_math(m.group(1))

        # display math first
        text = re.sub(r"\$\$([\s\S]*?)\$\$", block, text)
        text = re.sub(r"\$([^\$\n]+?)\$", block, text)
        # if any $ survived (malformed), strip them so no raw LaTeX leaks
        text = text.replace("$", "")

    # Bare subscripts written outside math, e.g. "C_1", "L_2", "F_3", "C_{12}".
    # Runs even when there was no $ at all — otherwise "C_1" stays literal.
    # Fill-card blanks are 3+ underscores, so this never eats a blank.
    text = re.sub(r"_\{([^{}]*)\}", r"<sub>\1</sub>", text)
    text = re.sub(r"(?<![A-Za-z0-9_])([A-Za-z])_(\d{1,2})(?![0-9A-Za-z_])",
                  r"\1<sub>\2</sub>", text)

    return text


# Commands the stripper must never touch. In course material these are
# function names written as "\nCF(E)" or "\nM(\{h\})" — a real newline
# followed by an identifier, NOT a LaTeX command. Mangling them to "nCF(E)"
# silently corrupts every formula that uses them.
LOOKALIKE = re.compile(r"\\n(?=[A-Za-z]+[\(\{\[])")


def walk(obj, key=None):
    if isinstance(obj, str):
        return convert_text(obj)
    if isinstance(obj, dict):
        return {k: walk(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v, key) for v in obj]
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topics_json")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    topics = json.loads(Path(args.topics_json).read_text(encoding="utf-8"))
    out = walk(topics)
    Path(args.output).write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    before = json.dumps(topics, ensure_ascii=False)
    after = json.dumps(out, ensure_ascii=False)
    print(f"✓ converted: {before.count('$')//2} math blocks")
    print(f"✓ remaining '$' chars: {after.count('$')}")
    print(f"✓ wrote {args.output} ({len(after)//1024} KB)")


if __name__ == "__main__":
    main()
