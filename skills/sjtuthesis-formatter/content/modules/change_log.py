"""
Change Log — Structured Modification Tracking & Diff Preview
=============================================================

Records every formatting change made to a document so the user
can see what was modified, accept/reject individual changes,
and understand the rationale behind each edit.

Supports:
- Structured operation records (WHAT, WHERE, WHY, old→new)
- Before/after text diffing
- Change categorization (formatting, content, reference, etc.)
- Accept/reject per-change tracking
- Change Log summary generation
"""

import difflib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional


# ── Severity / Category ───────────────────────────────────────────

class ChangeCategory(Enum):
    FORMATTING = "formatting"       # Font, size, spacing, alignment
    STRUCTURE = "structure"         # Heading level, section reorg
    PUNCTUATION = "punctuation"     # Full/half-width, spacing
    REFERENCE = "reference"         # Citation format, reference order
    CROSS_REF = "cross_reference"   # Figure/table cross-reference
    CAPTION = "caption"             # Figure/table caption
    CLEANING = "cleaning"           # Whitespace, annotation removal
    TRANSLATION = "translation"     # Language translation
    CONTENT = "content"             # Actual content (rare, flagged)
    OTHER = "other"


class ChangeStatus(Enum):
    PENDING = "pending"         # Awaiting user decision
    ACCEPTED = "accepted"       # User accepted
    REJECTED = "rejected"       # User rejected
    AUTO = "auto"               # Applied automatically


# ── Change record ─────────────────────────────────────────────────

@dataclass
class ChangeRecord:
    """A single modification made to the document."""
    category: ChangeCategory
    location: str                # Section/chapter/line reference
    summary: str                 # Brief human-readable description
    old_value: str = ""
    new_value: str = ""
    detail: str = ""             # Extended explanation
    rule_reference: str = ""     # Which formatting rule was applied
    status: ChangeStatus = ChangeStatus.AUTO
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

    def diff_text(self) -> str:
        """Generate a side-by-side diff snippet."""
        if not self.old_value or not self.new_value:
            return ""
        diff = difflib.unified_diff(
            self.old_value.splitlines(keepends=True),
            self.new_value.splitlines(keepends=True),
            fromfile="before", tofile="after", lineterm=""
        )
        return "".join(list(diff)[:10])  # limit to 10 lines

    def brief(self) -> str:
        """One-line summary for the change log."""
        icon = {
            ChangeCategory.FORMATTING: "🎨",
            ChangeCategory.STRUCTURE: "🏗️",
            ChangeCategory.PUNCTUATION: "✏️",
            ChangeCategory.REFERENCE: "📚",
            ChangeCategory.CROSS_REF: "🔗",
            ChangeCategory.CAPTION: "🖼️",
            ChangeCategory.CLEANING: "🧹",
            ChangeCategory.TRANSLATION: "🌐",
            ChangeCategory.CONTENT: "⚠️",
        }.get(self.category, "•")
        status_mark = "✓" if self.status == ChangeStatus.ACCEPTED else "⏳"
        return f"  {icon} [{status_mark}] {self.location}: {self.summary}"


# ── Change Log ────────────────────────────────────────────────────

@dataclass
class ChangeLog:
    """Collection of changes made during a formatting session."""
    source_file: str = ""
    output_file: str = ""
    profile_used: str = ""
    changes: List[ChangeRecord] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    end_time: str = ""

    def record(self, category: ChangeCategory, location: str, summary: str,
               old_value: str = "", new_value: str = "",
               detail: str = "", rule_reference: str = "",
               status: ChangeStatus = ChangeStatus.AUTO):
        """Add a change record."""
        self.changes.append(ChangeRecord(
            category=category, location=location, summary=summary,
            old_value=old_value, new_value=new_value, detail=detail,
            rule_reference=rule_reference, status=status,
        ))

    def by_category(self, category: ChangeCategory) -> List[ChangeRecord]:
        return [c for c in self.changes if c.category == category]

    def count_by_category(self) -> dict:
        counts = {}
        for c in self.changes:
            counts[c.category] = counts.get(c.category, 0) + 1
        return counts

    def summary(self) -> str:
        """Generate a human-readable change log summary."""
        total = len(self.changes)
        if total == 0:
            return "✅ 未作任何修改。"

        lines = [
            "=" * 55,
            "  📋 排版修改日志 (Change Log)",
            f"  文件: {self.source_file}",
            f"  配置: {self.profile_used or '默认'}",
            f"  时间: {self.start_time}",
            f"  总计: {total} 处修改",
            "=" * 55,
            "",
        ]

        # Group by category
        for cat in ChangeCategory:
            cat_changes = self.by_category(cat)
            if not cat_changes:
                continue
            cat_name = {
                ChangeCategory.FORMATTING: "🎨 格式修改",
                ChangeCategory.STRUCTURE: "🏗️ 结构调整",
                ChangeCategory.PUNCTUATION: "✏️ 标点修正",
                ChangeCategory.REFERENCE: "📚 参考文献",
                ChangeCategory.CROSS_REF: "🔗 交叉引用",
                ChangeCategory.CAPTION: "🖼️ 图表题注",
                ChangeCategory.CLEANING: "🧹 文本清洗",
                ChangeCategory.CONTENT: "⚠️ 内容变更",
            }.get(cat, cat.value)
            lines.append(f"▸ {cat_name} ({len(cat_changes)} 处):")
            for c in cat_changes:
                lines.append(f"  • {c.location}: {c.summary}")
                if c.old_value and c.new_value:
                    old_short = c.old_value[:40].replace("\n", " ")
                    new_short = c.new_value[:40].replace("\n", " ")
                    if old_short != new_short:
                        lines.append(f"    - 原来: {old_short}")
                        lines.append(f"    + 现在: {new_short}")
                if c.rule_reference:
                    lines.append(f"    依据: {c.rule_reference}")
            lines.append("")

        lines.append("=" * 55)
        return "\n".join(lines)

    def markdown_summary(self) -> str:
        """Markdown version for embedding in reports."""
        text = self.summary()
        return f"```\n{text}\n```"

    def has_content_changes(self) -> bool:
        """Check if any changes modify actual content (not just formatting)."""
        return any(c.category == ChangeCategory.CONTENT for c in self.changes)

    def total_changes(self) -> int:
        return len(self.changes)

    def total_pending(self) -> int:
        return sum(1 for c in self.changes if c.status == ChangeStatus.PENDING)


# ── Text diff utilities ───────────────────────────────────────────

def unified_diff(text_a: str, text_b: str, context: int = 3) -> str:
    """Generate a unified diff between two text versions."""
    diff = difflib.unified_diff(
        text_a.splitlines(keepends=True),
        text_b.splitlines(keepends=True),
        fromfile="original", tofile="formatted",
        n=context, lineterm=""
    )
    return "".join(diff)


def side_by_side_diff(text_a: str, text_b: str, width: int = 50) -> str:
    """Generate a side-by-side diff suitable for console display."""
    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()
    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    output: List[str] = []

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            for k in range(i1, i2):
                if k < len(lines_a) and k < len(lines_b):
                    left = lines_a[k][:width].ljust(width)
                    right = lines_b[k][:width].ljust(width)
                    output.append(f"  {left}  {right}")
        elif op == "replace":
            for k in range(i1, i2):
                left = lines_a[k][:width].ljust(width) if k < len(lines_a) else "".ljust(width)
                right = ""
                right_idx = j1 + (k - i1)
                if right_idx < len(lines_b):
                    right = lines_b[right_idx][:width].ljust(width)
                output.append(f"- {left}  {right}")
            for k in range(j1, j2):
                left_idx = i1 + (k - j1)
                if left_idx >= i2:  # extra lines in B
                    right = lines_b[k][:width].ljust(width) if k < len(lines_b) else "".ljust(width)
                    output.append(f"+ {"".ljust(width)}  {right}")
        elif op == "delete":
            for k in range(i1, i2):
                left = lines_a[k][:width].ljust(width) if k < len(lines_a) else "".ljust(width)
                output.append(f"- {left}")
        elif op == "insert":
            for k in range(j1, j2):
                right = lines_b[k][:width].ljust(width) if k < len(lines_b) else "".ljust(width)
                output.append(f"+ {"".ljust(width)}  {right}")

    return "\n".join(output[:60])  # limit output
