"""
SJTU Thesis — Format Compliance Validator
==========================================

Checks Word (.docx) or LaTeX (.tex) documents against the
SJTU 2022 thesis formatting specification and reports issues
with severity levels (borrowing minimax-docx-pro's approach).
"""

import re
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class Severity(Enum):
    """Issue severity levels, inspired by minimax-docx-pro's check pipeline."""
    BLOCKER = "BLOCKER"   # Must fix
    WARNING = "WARNING"   # Should fix
    HINT = "HINT"         # Nice to have


@dataclass
class ValidationIssue:
    """A single validation finding."""
    severity: Severity
    location: str
    summary: str
    detail: str = ""


@dataclass
class ValidationReport:
    """Complete validation result."""
    file_path: Path
    issues: List[ValidationIssue] = field(default_factory=list)
    passed: int = 0
    skipped: int = 0

    def has_blockers(self) -> bool:
        return any(i.severity == Severity.BLOCKER for i in self.issues)

    def has_warnings(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)

    def add(self, severity: Severity, location: str, summary: str, detail: str = ""):
        self.issues.append(ValidationIssue(severity, location, summary, detail))

    def add_blocker(self, location: str, summary: str, detail: str = ""):
        self.add(Severity.BLOCKER, location, summary, detail)

    def add_warning(self, location: str, summary: str, detail: str = ""):
        self.add(Severity.WARNING, location, summary, detail)

    def add_hint(self, location: str, summary: str, detail: str = ""):
        self.add(Severity.HINT, location, summary, detail)

    def print_report(self):
        """Print formatted validation report."""
        icon = {
            Severity.BLOCKER: "✗",
            Severity.WARNING: "!",
            Severity.HINT: "?",
        }
        print(f"\n{'='*60}")
        print(f"  验证报告: {self.file_path}")
        print(f"{'='*60}")
        if not self.issues:
            print("  ✓ 全部通过，未发现问题")
            return

        for issue in self.issues:
            print(f"  {icon.get(issue.severity, ' ')} [{issue.severity.value}] "
                  f"{issue.location}: {issue.summary}")
            if issue.detail:
                for line in issue.detail.split("\n"):
                    print(f"    {line}")

        blocker_count = sum(1 for i in self.issues if i.severity == Severity.BLOCKER)
        warning_count = sum(1 for i in self.issues if i.severity == Severity.WARNING)
        hint_count = sum(1 for i in self.issues if i.severity == Severity.HINT)
        print(f"\n  总计: {len(self.issues)} 个问题 "
              f"(阻塞: {blocker_count}, 警告: {warning_count}, 提示: {hint_count})")
        if self.has_blockers():
            print("  结论: ✗ 未通过 — 存在阻塞性问题")
        elif self.has_warnings():
            print("  结论: ⚠ 通过，但有警告")
        else:
            print("  结论: ✓ 通过")


# ── DOCX Validator ─────────────────────────────────────────────────

def validate_docx(file_path: Path) -> ValidationReport:
    """Validate a .docx file against SJTU 2022 formatting spec."""
    report = ValidationReport(file_path)

    if not file_path.exists():
        report.add_blocker("文件", f"文件不存在: {file_path}")
        return report

    if file_path.suffix.lower() not in (".docx",):
        report.add_blocker("文件", f"不是 .docx 文件: {file_path.suffix}")
        return report

    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            # Check for required parts
            namelist = zf.namelist()

            if "word/document.xml" not in namelist:
                report.add_blocker("结构", "缺少 word/document.xml")
            else:
                report.passed += 1

            if "word/styles.xml" in namelist:
                report.passed += 1
            else:
                report.add_warning("样式", "缺少 word/styles.xml，可能使用默认样式")

            # Check media
            media_files = [n for n in namelist if n.startswith("word/media/")]
            if media_files:
                report.passed += 1
                report.add_hint("图片", f"文档包含 {len(media_files)} 个媒体文件")

            # Check header/footer
            has_header = any("header" in n for n in namelist)
            has_footer = any("footer" in n for n in namelist)
            if not has_header:
                report.add_warning("页眉", "未找到页眉设置")
            if not has_footer:
                report.add_warning("页脚", "未找到页脚（页码）设置")

            # Check settings for odd/even headers
            if "word/settings.xml" in zf.namelist():
                settings_xml = zf.read("word/settings.xml").decode("utf-8", errors="ignore")
                if "evenAndOddHeaders" in settings_xml:
                    report.passed += 1
                else:
                    report.add_hint("页眉", "建议启用奇偶页不同页眉")

    except zipfile.BadZipFile:
        report.add_blocker("文件", "无效的 .docx 文件 (BadZipFile)")
    except Exception as e:
        report.add_blocker("异常", f"验证异常: {e}")

    return report


# ── LaTeX Validator ────────────────────────────────────────────────

def validate_latex(file_path: Path) -> ValidationReport:
    """Validate a .tex file for SJTU formatting compliance."""
    report = ValidationReport(file_path)

    if not file_path.exists():
        report.add_blocker("文件", f"文件不存在: {file_path}")
        return report

    try:
        content = file_path.read_text("utf-8", errors="ignore")
    except Exception as e:
        report.add_blocker("文件", f"无法读取文件: {e}")
        return report

    # ── Structure checks ────────────────────────────────────────────
    if "\\documentclass" in content:
        report.passed += 1
    else:
        report.add_blocker("结构", "缺少 \\documentclass 声明")

    if "\\begin{document}" in content:
        report.passed += 1
    else:
        report.add_blocker("结构", "缺少 \\begin{document}")

    if "\\end{document}" in content:
        report.passed += 1
    else:
        report.add_blocker("结构", "缺少 \\end{document}")

    # ── SJTU-specific checks ────────────────────────────────────────
    if "sjtuthesis" in content:
        report.passed += 1
    else:
        report.add_hint("模板", "未引用 sjtuthesis 模板；确认是否缺少 SJTUThesis 安装")

    if "\\title" in content:
        report.passed += 1
    else:
        report.add_blocker("信息", "缺少 \\title 命令")

    if "\\author" in content:
        report.passed += 1
    else:
        report.add_warning("信息", "缺少 \\author 命令")

    # ── Font checks ─────────────────────────────────────────────────
    if "SimSun" in content or "SimHei" in content or "\\song" in content or "\\hei" in content:
        report.passed += 1
    else:
        report.add_warning("字体", "未检测到中文字体设置（SimSun/SimHei）")

    if "Times New Roman" in content or "\\fontspec" in content:
        report.passed += 1
    else:
        report.add_hint("字体", "未检测到 Times New Roman 英文字体设置")

    # ── Section formatting ──────────────────────────────────────────
    if "\\section" in content:
        report.passed += 1
    if "\\subsection" in content:
        report.passed += 1
    if "\\tableofcontents" in content:
        report.passed += 1

    # ── Page layout ─────────────────────────────────────────────────
    if "geometry" in content:
        report.passed += 1
    else:
        report.add_hint("页面", "缺少 geometry 页面设置包")

    # ── References ──────────────────────────────────────────────────
    if "\\bibliography" in content or "\\begin{thebibliography}" in content:
        report.passed += 1
    else:
        report.add_warning("参考文献", "缺少参考文献部分")

    # ── Abstract ────────────────────────────────────────────────────
    if "abstract" in content.lower():
        report.passed += 1
    else:
        report.add_warning("摘要", "缺少 abstract 环境")

    # ── Line spacing ────────────────────────────────────────────────
    if "setspace" in content or "\\linespread" in content or "\\setlength{\\parskip}" in content:
        report.passed += 1
    else:
        report.add_hint("行距", "未检测到行距设置")

    return report


# ── Entry point ────────────────────────────────────────────────────

def validate(file_path: Path) -> ValidationReport:
    """Validate a file (auto-detect .docx vs .tex)."""
    suffix = file_path.suffix.lower()
    if suffix == ".docx":
        return validate_docx(file_path)
    elif suffix == ".tex":
        return validate_latex(file_path)
    else:
        report = ValidationReport(file_path)
        report.add_blocker("文件", f"不支持的文件格式: {suffix}（支持: .docx, .tex）")
        return report
