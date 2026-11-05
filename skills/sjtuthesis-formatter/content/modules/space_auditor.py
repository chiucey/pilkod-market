"""
Space Auditor — Smart Whitespace Health Check
==============================================

Performs a comprehensive whitespace audit on document text:
1. Identifies protected regions (code blocks, URLs, formulas) where
   spaces should NOT be modified
2. Runs whitespace health checks on unprotected regions
3. Corrects punctuation-adjacent spacing
4. Removes redundant spaces while preserving intentional indentation
5. Reports all changes with context
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple


# ── Protected patterns (never modify spaces here) ─────────────────

PROTECTED_PATTERNS = [
    # Code blocks (Markdown)
    (re.compile(r'```.*?```', re.DOTALL), "code block"),
    (re.compile(r'`[^`]+`'), "inline code"),
    # URLs and DOIs
    (re.compile(r'https?://\S+'), "URL"),
    (re.compile(r'10\.\d{4,}/[-._;()/:A-Za-z0-9]+'), "DOI"),
    # LaTeX math
    (re.compile(r'\$[^$]+\$'), "inline math"),
    (re.compile(r'\$\$[^$]+\$\$', re.DOTALL), "display math"),
    (re.compile(r'\\\(.*?\\\)', re.DOTALL), "LaTeX inline math"),
    (re.compile(r'\\\[.*?\\\]', re.DOTALL), "LaTeX display math"),
    # LaTeX commands
    (re.compile(r'\\[a-zA-Z]+(\{[^}]*\})?'), "LaTeX command"),
    # Email addresses
    (re.compile(r'\S+@\S+\.\S+'), "email"),
]


@dataclass
class SpaceIssue:
    """A whitespace issue found during auditing."""
    position: int           # Character offset
    context: str            # Surrounding text snippet
    issue_type: str         # extra_space / missing_space / punctuation_space
    severity: str           # error / warning / hint
    original: str = ""
    corrected: str = ""
    line_num: int = 0


@dataclass
class SpaceAuditReport:
    """Complete whitespace audit report."""
    total_issues: int = 0
    issues: List[SpaceIssue] = field(default_factory=list)
    fixes_applied: int = 0
    protected_zones: int = 0

    def add(self, issue: SpaceIssue):
        self.issues.append(issue)
        self.total_issues = len(self.issues)

    def summary(self) -> str:
        by_type = {}
        for iss in self.issues:
            by_type[iss.issue_type] = by_type.get(iss.issue_type, 0) + 1
        lines = [f"  空格审计: {len(self.issues)} 个问题, {self.fixes_applied} 个已修复"]
        for t, c in sorted(by_type.items()):
            lines.append(f"    {t}: {c} 处")
        return "\n".join(lines)


# ── Pattern compilation ───────────────────────────────────────────

# CJK / Latin boundary: missing space
CJK_LATIN_SPACE_RE = re.compile(r'([一-鿿㐀-䶿豈-﫿])([A-Za-z0-9])')
LATIN_CJK_SPACE_RE = re.compile(r'([A-Za-z0-9])([一-鿿㐀-䶿豈-﫿])')

# Multiple consecutive spaces (not at line start = indentation)
MULTI_SPACE_RE = re.compile(r'(?<!\n) {3,}')

# Space before punctuation (Chinese)
SPACE_BEFORE_CH_PUNCT = re.compile(r' ([，。、；：！？）】」』】])')

# Space after opening punctuation
SPACE_AFTER_OPEN_PUNCT = re.compile(r'([（【「『【])\s+')

# Trailing whitespace
TRAILING_WS_RE = re.compile(r'[ \t]+$', re.MULTILINE)

# Space between Chinese punctuation and CJK
CH_PUNCT_CJK_SPACE = re.compile(r'([，。、；：！？）】」』])\s+([一-鿿])')

# Double punctuation
DOUBLE_PUNCT_RE = re.compile(r'([，。、；：！？])\1+')


# ── Core audit function ───────────────────────────────────────────

def find_protected_zones(text: str) -> List[Tuple[int, int, str]]:
    """Find regions where spaces should not be modified."""
    zones: List[Tuple[int, int, str]] = []
    for pattern, label in PROTECTED_PATTERNS:
        for match in pattern.finditer(text):
            zones.append((match.start(), match.end(), label))
    # Merge overlapping zones
    zones.sort()
    merged: List[Tuple[int, int, str]] = []
    for start, end, label in zones:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end), merged[-1][2])
        else:
            merged.append((start, end, label))
    return merged


def is_in_protected_zone(pos: int, zones: List[Tuple[int, int, str]]) -> bool:
    """Check if a position falls within a protected zone."""
    return any(start <= pos <= end for start, end, _ in zones)


def get_line_number(text: str, pos: int) -> int:
    """Get 1-indexed line number for a character position."""
    return text[:pos].count("\n") + 1


def get_context(text: str, pos: int, width: int = 20) -> str:
    """Get surrounding context for an issue."""
    start = max(0, pos - width)
    end = min(len(text), pos + width)
    ctx = text[start:end].replace("\n", "¶")
    if start > 0:
        ctx = "..." + ctx
    if end < len(text):
        ctx = ctx + "..."
    return ctx


# ── Audit pipeline ────────────────────────────────────────────────

def audit_spaces(text: str, fix: bool = False) -> SpaceAuditReport:
    """Run a full whitespace health check.

    Args:
        text: The document text to audit.
        fix: If True, apply fixes automatically.

    Returns:
        SpaceAuditReport with issues found and fixes applied.
    """
    report = SpaceAuditReport()
    protected = find_protected_zones(text)
    report.protected_zones = len(protected)
    lines = []

    # Check 1: CJK/Latin missing spaces
    for pattern, issue_type in [
        (CJK_LATIN_SPACE_RE, "CJK后缺空格"),
        (LATIN_CJK_SPACE_RE, "CJK前缺空格"),
    ]:
        for match in pattern.finditer(text):
            pos = match.start() + len(match.group(1))
            if is_in_protected_zone(pos, protected):
                continue
            report.add(SpaceIssue(
                position=pos,
                context=get_context(text, pos),
                issue_type=issue_type,
                severity="warning",
                original=match.group(0),
                corrected=match.group(1) + " " + match.group(2),
                line_num=get_line_number(text, pos),
            ))

    # Check 2: Redundant multiple spaces (not indentation)
    for match in MULTI_SPACE_RE.finditer(text):
        pos = match.start()
        if is_in_protected_zone(pos, protected):
            continue
        report.add(SpaceIssue(
            position=pos,
            context=get_context(text, pos),
            issue_type="多余空格",
            severity="warning",
            original=match.group(0),
            corrected=" ",
            line_num=get_line_number(text, pos),
        ))

    # Check 3: Space before Chinese punctuation
    for match in SPACE_BEFORE_CH_PUNCT.finditer(text):
        pos = match.start()
        if is_in_protected_zone(pos, protected):
            continue
        report.add(SpaceIssue(
            position=pos,
            context=get_context(text, pos),
            issue_type="标点前多余空格",
            severity="error",
            original=match.group(0),
            corrected=match.group(1),
            line_num=get_line_number(text, pos),
        ))

    # Check 4: Space after opening punctuation
    for match in SPACE_AFTER_OPEN_PUNCT.finditer(text):
        pos = match.start()
        if is_in_protected_zone(pos, protected):
            continue
        report.add(SpaceIssue(
            position=pos,
            context=get_context(text, pos),
            issue_type="左引号后多余空格",
            severity="warning",
            original=match.group(0),
            corrected=match.group(1),
            line_num=get_line_number(text, pos),
        ))

    # Check 5: Trailing whitespace
    for match in TRAILING_WS_RE.finditer(text):
        pos = match.start()
        if is_in_protected_zone(pos, protected):
            continue
        report.add(SpaceIssue(
            position=pos,
            context=get_context(text, pos),
            issue_type="行尾多余空格",
            severity="hint",
            original=repr(match.group(0)),
            corrected="",
            line_num=get_line_number(text, pos),
        ))

    # Apply fixes if requested
    if fix:
        text = apply_space_fixes(text, report, protected)

    return report


def apply_space_fixes(text: str, report: SpaceAuditReport,
                      protected: List[Tuple[int, int, str]]) -> str:
    """Apply all whitespace fixes safely.

    Works from right to left to preserve positions.
    """
    # Collect all fixes, sorted by position (reversed)
    fixes = []
    for iss in report.issues:
        if iss.original and iss.corrected:
            fixes.append((iss.position, iss.original, iss.corrected))

    # Sort by position descending (right to left)
    fixes.sort(key=lambda x: x[0], reverse=True)

    for pos, original, corrected in fixes:
        # Double-check protected
        if not is_in_protected_zone(pos, protected):
            # Find the actual text at this position
            actual = text[pos:pos + len(original)]
            if actual == original or actual[:1] == original[:1]:
                text = text[:pos] + corrected + text[pos + len(original):]
                report.fixes_applied += 1

    return text


# ── Convenience ───────────────────────────────────────────────────

def quick_fix_spaces(text: str) -> Tuple[str, SpaceAuditReport]:
    """One-step audit + fix."""
    report = audit_spaces(text, fix=True)
    # Apply CJK spacing
    text = CJK_LATIN_SPACE_RE.sub(r'\1 \2', text)
    text = LATIN_CJK_SPACE_RE.sub(r'\1 \2', text)
    # Remove space before Chinese punctuation
    text = SPACE_BEFORE_CH_PUNCT.sub(r'\1', text)
    # Remove trailing whitespace
    text = TRAILING_WS_RE.sub('', text)
    # Collapse multiple spaces
    text = MULTI_SPACE_RE.sub(' ', text)
    return text, report
