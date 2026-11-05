"""
Math Typesetting — Fine-Grained Mathematical Formatting Rules
=============================================================

Defines precise mathematical typography rules following:
- SJTU 2022 thesis specification
- GB 3100-3102 (quantities and units)
- ISO 80000-2 (mathematical notation)
- LaTeX / MathML best practices

Covers:
1. Variable italic vs. constant upright
2. Matrix/vector bold (bold italic for vectors, bold upright for matrices)
3. Subscript/superscript rules (physical → italic, descriptive → upright)
4. Equation numbering and alignment
5. Function names (sin, cos, log, etc. → upright)
6. Parentheses, brackets, and delimiter sizing
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


# ── Font classification for math symbols ──────────────────────────

# Mathematical functions that should be upright (not italic)
MATH_FUNCTIONS = {
    "sin", "cos", "tan", "cot", "sec", "csc",
    "sinh", "cosh", "tanh", "coth", "sech", "csch",
    "arcsin", "arccos", "arctan", "arccot", "arcsec", "arccsc",
    "exp", "log", "ln", "lg", "lb",
    "max", "min", "sup", "inf", "lim", "limsup", "liminf",
    "det", "dim", "hom", "ker", "im", "Re", "Im",
    "arg", "deg", "Pr", "gcd", "lcm",
    "mod", "bmod", "pmod",
    "tr", "diag", "rank", "rref",
    "sgn", "erf", "erfc",
}

# Named constants (upright)
MATH_CONSTANTS = {
    "π", "pi",      # pi (when used as constant name in text)
    "e",            # Euler's number (upright in some styles)
    "i",            # imaginary unit (upright in some styles)
    "∞", "inf",     # infinity
}

# Greek letters (variable → italic by default)
GREEK_LETTERS = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon",
    "zeta", "eta", "theta", "vartheta", "iota", "kappa",
    "lambda", "mu", "nu", "xi", "omicron", "pi", "varpi",
    "rho", "varrho", "sigma", "varsigma", "tau", "upsilon",
    "phi", "varphi", "chi", "psi", "omega",
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon",
    "Zeta", "Eta", "Theta", "Iota", "Kappa",
    "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi",
    "Rho", "Sigma", "Tau", "Upsilon",
    "Phi", "Chi", "Psi", "Omega",
}

# Well-known operators (upright)
OPERATORS = {
    "+", "-", "±", "∓", "×", "÷", "*",
    "=", "≈", "≠", "<", ">", "≤", "≥", "≡", "≅", "∼", "∝",
    "∈", "∉", "⊂", "⊃", "⊆", "⊇", "∪", "∩", "∖",
    "→", "←", "↔", "⇒", "⇐", "⇔", "↦",
    "∇", "∂", "∆", "∏", "∑", "∫", "∮", "∬",
    "∀", "∃", "∧", "∨", "¬",
}


# ── Data types ────────────────────────────────────────────────────

@dataclass
class MathSymbolRule:
    """Formatting rule for a mathematical symbol."""
    symbol: str
    category: str                # variable, constant, function, operator, greek
    font_shape: str              # italic, upright, bold-italic, bold-upright
    description: str = ""


@dataclass
class MathFormatProfile:
    """Complete math formatting rules for a venue."""
    name: str = "sjtu"
    variables_italic: bool = True
    constants_upright: bool = True
    functions_upright: bool = True
    vectors_bold_italic: bool = True
    matrices_bold_upright: bool = True
    physical_quantities_italic: bool = True
    descriptive_subscripts_upright: bool = True
    greek_variables_italic: bool = True
    layout: str = "align"        # align, gather, flalign
    numbering: str = "right"     # right, left, center


# ── Classification functions ──────────────────────────────────────

def classify_symbol(symbol: str) -> str:
    """Classify a math symbol into a category.

    Returns one of:
        'variable', 'constant', 'function', 'operator', 'greek', 'number', 'unknown'
    """
    if symbol.lower() in MATH_FUNCTIONS:
        return "function"
    if symbol.lower() in MATH_CONSTANTS:
        return "constant"
    if symbol in OPERATORS:
        return "operator"
    if symbol.lower() in GREEK_LETTERS:
        return "greek"
    if re.match(r'^[a-zA-Z]$', symbol):
        return "variable"   # Single letter → variable (italic)
    if re.match(r'^[0-9]+(\.[0-9]+)?$', symbol):
        return "number"
    return "unknown"


def should_be_italic(symbol: str, profile: MathFormatProfile = None) -> bool:
    """Determine if a symbol should be italic.

    Follows standard mathematical typography:
    - Variables (x, y, z, a, b, c...) → italic
    - Constants (π, e, i...) → upright
    - Functions (sin, cos, log...) → upright
    - Greek letters (α, β, γ...) → italic (variables)
    - Numbers → upright
    - Operators → upright
    """
    if profile is None:
        profile = MathFormatProfile()

    cat = classify_symbol(symbol)

    if cat == "variable":
        return profile.variables_italic
    if cat == "greek":
        return profile.greek_variables_italic
    if cat == "constant":
        return not profile.constants_upright
    if cat == "function":
        return not profile.functions_upright
    # operators and numbers are always upright
    return False


def subscript_should_be_italic(subscript: str) -> bool:
    """Determine if a subscript should be italic.

    Physical quantity subscripts → italic (C_p, T_c)
    Descriptive/abbreviation subscripts → upright (E_max, R_min)
    """
    # Single letter subscripts → likely physical quantity → italic
    if re.match(r'^[a-zA-Z]$', subscript):
        return True
    # Multi-letter subscripts → likely descriptive → upright
    if re.match(r'^[a-zA-Z]{2,}$', subscript):
        return False
    return False


# ── LaTeX math formatting ─────────────────────────────────────────

def format_math_expression(latex_expr: str, profile: MathFormatProfile = None) -> str:
    """Format a LaTeX math expression according to typographic rules.

    Applies \\mathrm{} to functions/constants that should be upright,
    \\mathbf{} or \\boldsymbol{} for vectors/matrices.

    Args:
        latex_expr: Raw LaTeX math expression.
        profile: Formatting profile.

    Returns:
        Formatted LaTeX expression with correct font commands.
    """
    if profile is None:
        profile = MathFormatProfile()

    # 1. Wrap functions (sin, cos, etc.) with \\mathrm{} if not already
    for func in sorted(MATH_FUNCTIONS, key=len, reverse=True):
        # Only match standalone function names (not inside \\something)
        latex_expr = re.sub(
            r'(?<![\\a-zA-Z])' + re.escape(func) + r'\b(?!\s*\\|})',
            r'\\mathrm{' + func + r'}',
            latex_expr,
        )

    # 2. Handle common patterns
    # Subscript formatting
    latex_expr = re.sub(
        r'_{([a-zA-Z]+)}',
        lambda m: f'_{{\\mathrm{{{m.group(1)}}}}}' if not subscript_should_be_italic(m.group(1))
                  else f'_{{{m.group(1)}}}',
        latex_expr,
    )

    # 3. Bold for vectors (\\vec{} → \\boldsymbol{})
    if profile.vectors_bold_italic:
        latex_expr = re.sub(
            r'\\vec\{([^}]+)\}',
            r'\\boldsymbol{\1}',
            latex_expr,
        )

    return latex_expr


def render_equation(content: str, number: str = "",
                    profile: MathFormatProfile = None) -> str:
    """Generate a complete LaTeX equation environment.

    Args:
        content: The equation body (formatted).
        number: Optional equation number like "(1-1)".
        profile: Formatting profile.

    Returns:
        Complete LaTeX equation block.
    """
    if profile is None:
        profile = MathFormatProfile()

    if number:
        if profile.layout == "align":
            return (
                f"\\begin{{equation}}\n"
                f"  {content}\n"
                f"  \\label{{eq:{number}}}\n"
                f"\\end{{equation}}\n"
            )
        else:
            return (
                f"\\begin{{equation}}\n"
                f"  {content}\n"
                f"  \\tag{{{number}}}\n"
                f"\\end{{equation}}\n"
            )
    else:
        return (
            f"\\begin{{equation*}}\n"
            f"  {content}\n"
            f"\\end{{equation*}}\n"
        )


def render_multiline_equation(lines: List[str], profile: MathFormatProfile = None) -> str:
    """Generate a multi-line aligned equation environment."""
    if profile is None:
        profile = MathFormatProfile()

    joined = " \\\\\n  ".join(lines)
    return (
        f"\\begin{{align}}\n"
        f"  {joined}\n"
        f"\\end{{align}}\n"
    )


# ── MathML generation ─────────────────────────────────────────────

def latex_to_mathml_basic(latex: str) -> str:
    """Very basic LaTeX → MathML conversion.

    This is a simplified converter for common patterns.
    For production use, employ a dedicated library.
    """
    # This is a placeholder — full LaTeX→MathML requires a parser.
    # We wrap the LaTeX in a MathML sematics element for tool compatibility.
    import html
    escaped = html.escape(latex)
    return (
        f'<math xmlns="http://www.w3.org/1998/Math/MathML">\n'
        f'  <semantics>\n'
        f'    <annotation encoding="application/x-tex">{escaped}</annotation>\n'
        f'  </semantics>\n'
        f'</math>'
    )


# ── Format validation ─────────────────────────────────────────────

def validate_math_formatting(text: str) -> List[str]:
    """Check math formatting in text for common issues.

    Returns:
        List of issue descriptions.
    """
    issues: List[str] = []
    # Check for known function names used as variables (should be upright)
    for func in MATH_FUNCTIONS:
        # Look for the function appearing as a standalone variable
        pattern = r'(?<![\\a-zA-Z])' + re.escape(func) + r'(?![a-zA-Z])'
        for match in re.finditer(pattern, text):
            pos = match.start()
            context = text[max(0, pos - 10):pos + len(func) + 10]
            # Skip if inside \mathrm or already formatted
            before = text[max(0, pos - 20):pos]
            if '\\mathrm' in before:
                continue
            issues.append(f"Function '{func}' should be upright (not italic): ...{context}...")

    return issues


# ── SJTU-specific rules ──────────────────────────────────────────

SJTU_MATH_RULES = MathFormatProfile(
    name="sjtu",
    variables_italic=True,
    constants_upright=True,
    functions_upright=True,
    vectors_bold_italic=True,
    matrices_bold_upright=True,
    physical_quantities_italic=True,
    descriptive_subscripts_upright=True,
    greek_variables_italic=True,
    layout="align",
    numbering="right",
)

IEEE_MATH_RULES = MathFormatProfile(
    name="ieee",
    variables_italic=True,
    constants_upright=True,
    functions_upright=True,
    vectors_bold_italic=True,
    matrices_bold_upright=True,
    physical_quantities_italic=True,
    descriptive_subscripts_upright=True,
    greek_variables_italic=True,
    layout="align",
    numbering="right",
)


def math_rules_summary(profile: MathFormatProfile = None) -> str:
    """Generate a human-readable summary of math formatting rules."""
    if profile is None:
        profile = SJTU_MATH_RULES

    lines = [
        f"📐 数学排版规则 ({profile.name})",
        "=" * 40,
        "",
        "【变量与常量】",
        f"  变量 (x, y, z): {'斜体' if profile.variables_italic else '正体'}",
        f"  常量 (π, e, i): {'正体' if profile.constants_upright else '斜体'}",
        f"  函数名 (sin, cos): {'正体' if profile.functions_upright else '斜体'}",
        "",
        "【向量与矩阵】",
        f"  向量: {'粗斜体' if profile.vectors_bold_italic else '普通'}",
        f"  矩阵: {'粗正体' if profile.matrices_bold_upright else '普通'}",
        "",
        "【上下标】",
        f"  物理量下标 (C_p): 斜体",
        f"  说明性下标 (E_max): 正体",
        "",
        "【公式编号】",
        f"  编号位置: {profile.numbering}",
        f"  布局: {profile.layout}",
        "",
        "【参考规范】",
        "  GB 3100~3102-1993 量和单位",
        "  ISO 80000-2  数学符号",
        "  SJTU 学位论文撰写规范 2022",
    ]
    return "\n".join(lines)
