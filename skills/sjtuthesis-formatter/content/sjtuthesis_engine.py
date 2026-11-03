#!/usr/bin/env python3
"""
SJTU Thesis Engine — CLI Entry Point
=====================================

Central command-line interface for SJTU thesis formatting.
Inspired by minimax-docx-pro's docx_engine.py layered architecture.

Usage:
    python sjtuthesis_engine.py {doctor|info|render-word|render-latex|interactive|validate} [options]

Commands:
    doctor              Environment check and dependency report
    info                Interactive progressive Q&A → saves thesis_info.json
    render-word         Generate .docx from thesis_info.json
    render-latex        Generate .tex from thesis_info.json
    interactive         Full guided mode: info → pick format → render
    validate            Check .docx or .tex for SJTU compliance
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Ensure modules are importable
SCRIPT_LOCATION = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_LOCATION))

from modules.thesis_info import ThesisInfo
from modules.word_renderer import render_docx, render_word_from_json
from modules.latex_renderer import render_latex_from_json, render_sjtuthesis_latex, render_standalone_latex
from modules.validator import validate
from modules.helpers import detect_heading_level, insert_cjk_spacing, has_cjk
from modules.semantic_parser import parse_document, document_to_json
from modules.style_mapper import StyleMapper, available_profiles, profile_description, infer_semantic_role
from modules.citation_handler import (
    detect_citation_format, extract_citations, validate_citations,
    extract_cross_references, validate_cross_references, citation_format_description
)
from modules.figure_handler import (
    extract_captions, generate_list_of_figures, generate_list_of_tables,
    check_number_continuity, suggest_float_placement
)
from modules.cleaning_engine import semantic_clean, clean_web_paste, detect_widows, detect_track_changes, detect_comments, strip_formatting_artifacts
from modules.change_log import ChangeLog, ChangeCategory, ChangeStatus, unified_diff, side_by_side_diff
from modules.user_preferences import UserPreferences, TemplateStrictness, PageDensity, analyze_template, UserTemplate
from modules.format_detector import detect_format, detect_batch, format_summary, FileFormat
from modules.document_merger import merge_documents, merge_simple, MergePlan
from modules.space_auditor import audit_spaces, quick_fix_spaces, SpaceAuditReport
from modules.pdf_bookmarks import bookmarks_from_tree, render_latex_bookmarks, render_word_outline, BookmarkHierarchy, PdfMetadata
from modules.math_typesetting import (
    classify_symbol, should_be_italic, format_math_expression, render_equation,
    SJTU_MATH_RULES, math_rules_summary, MathFormatProfile
)
from modules.citation_handler import (
    parse_reference_list, format_all_references, ReferenceItem, detect_reference_type
)


# ── Helpers ────────────────────────────────────────────────────────

def print_banner():
    """Print the SJTU thesis engine banner."""
    print()
    print("=" * 55)
    print("  SJTU 论文排版助手 — Thesis Formatter Engine")
    print("  上海交通大学学位论文排版引擎 v1.0")
    print("=" * 55)
    print()


def resolve_output_dir() -> Path:
    """Resolve output directory from env or cwd."""
    return Path(os.environ.get("OUTPUT_DIR", ".")).resolve()


# ── doctor ─────────────────────────────────────────────────────────

def action_doctor():
    """Check environment and report available dependencies."""
    print_banner()
    print("=== 环境诊断 ===")
    print()

    # Python version
    print(f"  Python: {sys.version.split()[0]}")

    # python-docx
    try:
        import docx
        from docx import Document
        print(f"  python-docx: {docx.__version__ if hasattr(docx, '__version__') else 'installed'}")
    except ImportError:
        print("  python-docx: ✗ 未安装 (pip install python-docx)")

    # tqdm
    try:
        import tqdm
        print(f"  tqdm: {tqdm.__version__ if hasattr(tqdm, '__version__') else 'installed'}")
    except ImportError:
        print("  tqdm: ○ 可选，进度显示")

    # Pandoc (optional)
    pandoc = shutil.which("pandoc")
    if pandoc:
        print(f"  pandoc: {pandoc}")
    else:
        print("  pandoc: ○ 可选，用于文档预览")

    # LibreOffice (optional)
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        print(f"  LibreOffice: {soffice}")
    else:
        print("  LibreOffice: ○ 可选，用于 .doc → .docx 转换")

    # LaTeX (optional)
    xelatex = shutil.which("xelatex")
    if xelatex:
        print(f"  XeLaTeX: {xelatex}")
        # Check for SJTUThesis
        kpsewhich = shutil.which("kpsewhich")
        if kpsewhich:
            try:
                result = subprocess.run([kpsewhich, "sjtuthesis.cls"],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    print(f"  SJTUThesis: 已安装 ({result.stdout.strip()})")
                else:
                    print("  SJTUThesis: ○ 未安装，将使用独立 LaTeX 模板")
            except Exception:
                print("  SJTUThesis: ○ 无法检查")
    else:
        print("  XeLaTeX: ○ 未安装 (LaTeX 输出仍可生成 .tex 源码)")

    print()
    print("=== 技能路径 ===")
    print(f"  技能目录: {SCRIPT_LOCATION}")
    print(f"  模块目录: {SCRIPT_LOCATION / 'modules'}")
    print()

    # Quick summary
    print("=== 快速使用 ===")
    print(f"  交互模式: python {Path(__file__).name} interactive")
    print(f"  信息收集: python {Path(__file__).name} info")
    print(f"  生成 Word: python {Path(__file__).name} render-word thesis_info.json output.docx")
    print(f"  生成 LaTeX: python {Path(__file__).name} render-latex thesis_info.json output.tex")
    print(f"  格式验证: python {Path(__file__).name} validate output.docx")
    print()

    print("Ready!")


# ── info ───────────────────────────────────────────────────────────

def action_info(output_json: Optional[str] = None):
    """Interactive progressive Q&A to collect thesis information."""
    print_banner()
    print("📋 上海交通大学学位论文排版助手")
    print("=" * 50)
    print("我将逐步收集您的论文信息。每轮输入后按 Enter 确认。")
    print("如不清楚某项，可直接按 Enter 跳过（后续可补充）。")
    print()

    info = ThesisInfo()

    # ── Round 1: Basic Info ─────────────────────────────────────────
    print(f"\n【第1轮】{ThesisInfo.get_round_description(1)}")
    print("-" * 50)

    raw_title = input("📌 论文标题（或粘贴草稿片段）: ").strip()
    if raw_title:
        info.title = raw_title
        info.title_cn = raw_title
        info.body_content = raw_title

    degree = input("🎓 学位类型（学士/硕士/博士）: ").strip()
    if degree:
        info.parse_degree_type(degree)
    else:
        print("  → 默认: 学士")

    college = input("🏫 所属学院: ").strip()
    if college:
        info.college = college
    else:
        print("  → 跳过，后续可补充")

    fmt = input("📄 输出格式（Word/LaTeX/Both）: ").strip()
    if fmt:
        info.parse_output_format(fmt)
    else:
        print("  → 默认: Word")

    info.advance_round()

    # ── Round 2: Personal Info ──────────────────────────────────────
    print(f"\n【第2轮】{ThesisInfo.get_round_description(2)}")
    print("-" * 50)

    name = input("👤 您的姓名: ").strip()
    if name:
        info.author = name

    sid = input("🆔 学号: ").strip()
    if sid:
        info.student_id = sid

    major = input("📚 专业: ").strip()
    if major:
        info.major = major

    supervisor = input("👨‍🏫 导师姓名: ").strip()
    if supervisor:
        info.supervisor = supervisor

    title_cn = input("📝 论文中文题目: ").strip()
    if title_cn:
        info.title_cn = title_cn
        if not info.title:
            info.title = title_cn

    title_en = input("🔤 论文英文题目: ").strip()
    if title_en:
        info.title_en = title_en

    info.advance_round()

    # ── Round 3: Refinements ────────────────────────────────────────
    print(f"\n【第3轮】{ThesisInfo.get_round_description(3)}")
    print("-" * 50)

    odd_header = input("📌 奇数页页眉（默认: 章名，直接 Enter 使用默认）: ").strip()
    if odd_header:
        info.header_odd = odd_header

    even_header = input("📌 偶数页页眉（默认: 上海交通大学XXX学位论文）: ").strip()
    if even_header:
        info.header_even = even_header

    numbering = input("🔢 编号体系（阿拉伯数字/中文序号）: ").strip()
    if numbering:
        info.parse_numbering_system(numbering)
    else:
        print("  → 默认: 阿拉伯数字")

    keywords_cn_raw = input("🏷️ 中文关键词（逗号分隔，3-5个）: ").strip()
    if keywords_cn_raw:
        info.parse_keywords_cn(keywords_cn_raw)

    keywords_en_raw = input("🏷️ English keywords (comma separated): ").strip()
    if keywords_en_raw:
        info.parse_keywords_en(keywords_en_raw)

    abstract_cn = input("📄 中文摘要（可为空，后续可补充）: ").strip()
    if abstract_cn:
        info.abstract_cn = abstract_cn

    abstract_en = input("📄 English abstract (optional): ").strip()
    if abstract_en:
        info.abstract_en = abstract_en

    toc = input("📑 是否生成目录？(Y/n): ").strip()
    info.include_toc = info.parse_bool(toc, True)

    ack = input("🙏 是否包含致谢？(Y/n): ").strip()
    info.include_acknowledgements = info.parse_bool(ack, True)

    appendix = input("📎 是否需要附录？(y/N): ").strip()
    info.include_appendix = info.parse_bool(appendix, False)

    info.advance_round()

    # ── Round 4: Confirm & Output ───────────────────────────────────
    print(f"\n【第4轮】{ThesisInfo.get_round_description(4)}")
    print("-" * 50)
    print(info.summary())

    # Ask to confirm
    confirm = input("\n✅ 以上信息是否正确？(Y/n): ").strip()
    if confirm.lower() in ("n", "no", "否"):
        print("\n⚠️ 已取消。您可以重新运行 python sjtuthesis_engine.py info")
        sys.exit(0)

    # Ask for body content (optional at this stage)
    print("\n📄 是否现在粘贴论文正文内容？（直接 Enter 跳过，或粘贴全文后按 Ctrl+Z 再 Enter）")
    print("   （提示：可先粘贴标题和章节结构，后续可在 AI 对话中补充）")
    body_lines = []
    print("   请输入（输入空行后按 Enter 结束）:")
    while True:
        try:
            line = input()
            if line.strip() == "" and body_lines and body_lines[-1] == "":
                break
            body_lines.append(line)
        except EOFError:
            break
    if body_lines:
        info.body_content = "\n".join(body_lines)

    # Ask for references
    print("\n📚 是否粘贴参考文献？（直接 Enter 跳过）")
    ref_lines = []
    print("   请输入（输入空行后按 Enter 结束）:")
    while True:
        try:
            line = input()
            if line.strip() == "" and ref_lines and ref_lines[-1] == "":
                break
            ref_lines.append(line)
        except EOFError:
            break
    if ref_lines:
        info.references_raw = "\n".join(ref_lines)

    info.advance_round()

    # ── Save ────────────────────────────────────────────────────────
    if output_json:
        output_path = Path(output_json)
    else:
        output_path = Path("thesis_info.json")

    info.save(output_path)
    print(f"\n✅ 信息已保存至: {output_path}")

    # Suggest next steps
    print(f"\n下一步:")
    print(f"  生成 Word:  python {Path(__file__).name} render-word {output_path} output.docx")
    print(f"  生成 LaTeX: python {Path(__file__).name} render-latex {output_path} output.tex")


# ── render-word ────────────────────────────────────────────────────

def action_render_word(json_path: str, output_path: str):
    """Generate Word document from thesis info JSON."""
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"✗ 找不到信息文件: {json_path}")
        print(f"  请先运行: python {Path(__file__).name} info")
        sys.exit(1)

    output_file = Path(output_path)
    print(f"📄 正在生成 Word 文档...")

    try:
        info = ThesisInfo.load(json_file)
        result = render_docx(info, output_file)

        if result.exists():
            size_kb = result.stat().st_size / 1024
            print(f"✅ Word 文档已生成: {result} ({size_kb:.1f} KB)")
            print(f"\n📋 验证建议:")
            print(f"  python {Path(__file__).name} validate {result}")
        else:
            print(f"✗ 生成失败: 输出文件未创建")
            sys.exit(1)

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ── render-latex ───────────────────────────────────────────────────

def action_render_latex(json_path: str, output_path: str, standalone: bool = False):
    """Generate LaTeX document from thesis info JSON."""
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"✗ 找不到信息文件: {json_path}")
        print(f"  请先运行: python {Path(__file__).name} info")
        sys.exit(1)

    output_file = Path(output_path)
    mode = "独立" if standalone else "SJTUThesis"
    print(f"📄 正在生成 LaTeX 文档 ({mode}模式)...")

    try:
        info = ThesisInfo.load(json_file)
        if standalone:
            result = render_standalone_latex(info, output_file)
        else:
            result = render_sjtuthesis_latex(info, output_file)

        if result.exists():
            size_kb = result.stat().st_size / 1024
            print(f"✅ LaTeX 文档已生成: {result} ({size_kb:.1f} KB)")
            print(f"\n📋 编译建议:")
            if standalone:
                print(f"  xelatex {result}")
                print(f"  xelatex {result}  (两次编译以确保目录和引用)")
            else:
                print(f"  确保已安装 SJTUThesis 模板，然后运行:")
                print(f"  xelatex {result}")
                print(f"  xelatex {result}")
        else:
            print(f"✗ 生成失败: 输出文件未创建")
            sys.exit(1)

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ── interactive ────────────────────────────────────────────────────

def action_interactive():
    """Full guided mode: progressive info → pick format → render."""
    print_banner()
    print("🎯 欢迎使用 SJTU 论文排版助手 — 全流程引导模式")
    print("我将引导您逐步完成论文排版的全过程。")
    print()

    # Step 1: Collect info
    json_path = Path("thesis_info.json")
    action_info(str(json_path) if json_path.exists() else None)

    # Reload info
    info = ThesisInfo.load(json_path)

    # Step 2: Render
    print(f"\n{'='*50}")
    print("🎯 开始生成文档")
    print("=" * 50)
    print()

    if info.output_format in ("word", "both"):
        word_output = Path("output/thesis.docx")
        action_render_word(str(json_path), str(word_output))

    if info.output_format in ("latex", "both"):
        latex_output = Path("output/thesis.tex")
        action_render_latex(str(json_path), str(latex_output), standalone=True)

    print(f"\n✅ 全部完成！文件保存在 output/ 目录下。")


# ── validate ───────────────────────────────────────────────────────

def action_validate(file_path: str):
    """Validate a document against SJTU formatting spec."""
    path = Path(file_path)
    if not path.exists():
        print(f"✗ 文件不存在: {file_path}")
        sys.exit(1)

    report = validate(path)
    report.print_report()
    if report.has_blockers():
        sys.exit(1)


# ── semantic-parse (NEW) ──────────────────────────────────────────

def action_semantic_parse(text_file: str, output_json: str = ""):
    """Parse document text into hierarchical semantic tree."""
    path = Path(text_file)
    if not path.exists():
        print(f"✗ 文件不存在: {text_file}")
        sys.exit(1)

    text = path.read_text("utf-8", errors="ignore")
    print(f"📖 正在解析: {text_file} ({len(text)} 字符)")

    tree = parse_document(text)

    if output_json:
        out_path = Path(output_json)
        import json
        data = document_to_json(tree)
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 解析结果已保存: {out_path}")

    # Print summary
    counts = tree.count_by_type()
    print(f"\n📊 文档结构分析:")
    for node_type, count in sorted(counts.items(), key=lambda x: -x[1]):
        if node_type.name not in ("DOCUMENT", "PARAGRAPH"):
            print(f"  {node_type.name}: {count}")

    # Show tree (first 3 levels)
    print(f"\n🌳 结构树预览:")
    lines = tree.to_text().split("\n")
    for line in lines[:30]:
        print(f"  {line}")
    if len(lines) > 30:
        print(f"  ... ({len(lines) - 30} more lines)")


# ── style-list (NEW) ──────────────────────────────────────────────

def action_style_list(profile: str = ""):
    """List available style profiles and their roles."""
    if profile:
        if profile not in available_profiles():
            print(f"✗ 未知配置: {profile}")
            print(f"  可用: {', '.join(available_profiles())}")
            sys.exit(1)
        mapper = StyleMapper(profile)
        print(f"\n📋 样式配置: {profile} — {profile_description(profile)}")
        print("=" * 50)
        for role in mapper.list_roles():
            style = mapper.map(role)
            print(f"\n  [{role}]")
            print(f"    字体(中): {style.font_cn}, 字体(英): {style.font_en}")
            print(f"    字号: {style.size_pt}pt, 加粗: {style.bold}")
            print(f"    对齐: {style.align}, 行距: {style.line_spacing_pt}pt")
            if style.first_line_indent_chars:
                print(f"    首行缩进: {style.first_line_indent_chars}字符")
    else:
        print("\n📋 可用样式配置:")
        print("=" * 50)
        for p in available_profiles():
            print(f"  {p}: {profile_description(p)}")
        print(f"\n查看详细: python {Path(__file__).name} style-list <profile>")


# ── clean (NEW) ───────────────────────────────────────────────────

def action_clean(input_file: str, output_file: str = ""):
    """Clean and normalize document text."""
    path = Path(input_file)
    if not path.exists():
        print(f"✗ 文件不存在: {input_file}")
        sys.exit(1)

    text = path.read_text("utf-8", errors="ignore")
    print(f"🧹 正在清洗: {input_file} ({len(text)} 字符)")

    cleaned, report = semantic_clean(text)

    if output_file:
        out_path = Path(output_file)
        out_path.write_text(cleaned, encoding="utf-8")
        print(f"✅ 清洗结果已保存: {out_path}")

    print(f"\n📋 清洗报告:")
    for action in report.actions:
        print(f"  • {action}")

    # Detect widows
    widows = detect_widows(cleaned)
    if widows:
        print(f"  ⚠ 检测到 {len(widows)} 处可能的孤行:")
        for w in widows[:10]:
            print(f"    第{w}行")


# ── citations (NEW) ───────────────────────────────────────────────

def action_citations(text_file: str):
    """Analyze citation format, validate references, check cross-refs."""
    path = Path(text_file)
    if not path.exists():
        print(f"✗ 文件不存在: {text_file}")
        sys.exit(1)

    text = path.read_text("utf-8", errors="ignore")
    print(f"📚 正在分析引用: {text_file}")

    # Detect citation format
    fmt = detect_citation_format(text)
    print(f"\n📌 引用格式: {citation_format_description(fmt)}")

    # Extract all citations
    citations = extract_citations(text)
    if citations:
        print(f"📎 检测到 {len(citations)} 处引用标记")
        for c in citations[:10]:
            print(f"    [{c}]")
        if len(citations) > 10:
            print(f"    ... 共{len(citations)}处")
    else:
        print("📎 未检测到引用标记")

    # Extract cross-references
    xrefs = extract_cross_references(text)
    if xrefs:
        print(f"\n🔗 检测到 {len(xrefs)} 处交叉引用:")
        for x in xrefs[:10]:
            print(f"    第{x.line_num}行: {x.context} → {x.ref_type} {x.target_num}")

    # Validate cross-references
    xref_issues = validate_cross_references(text)
    if xref_issues:
        print(f"\n⚠️ 交叉引用问题:")
        for iss in xref_issues:
            print(f"    {iss.location}: {iss.summary}")

    # Figure/table analysis
    from modules.figure_handler import check_number_continuity, match_as_shown_to_figure
    continuity_issues = check_number_continuity(text)
    if continuity_issues:
        print(f"\n⚠️ 图表编号问题:")
        for iss in continuity_issues:
            print(f"    {iss}")

    shown_matches = match_as_shown_to_figure(text)
    if shown_matches:
        print(f"\n🔗 '如下图所示' → 题注匹配: {len(shown_matches)} 处")


# ── figures (NEW) ─────────────────────────────────────────────────

def action_figures(text_file: str):
    """Analyze figures/tables, generate LoF/LoT, check placement."""
    path = Path(text_file)
    if not path.exists():
        print(f"✗ 文件不存在: {text_file}")
        sys.exit(1)

    text = path.read_text("utf-8", errors="ignore")
    print(f"🖼️ 正在分析图表: {text_file}")

    captions = extract_captions(text)
    if not captions:
        print("未检测到图表题注。")
        return

    figures = [c for c in captions if c.kind == "figure"]
    tables = [c for c in captions if c.kind == "table"]

    print(f"\n📊 图表统计:")
    print(f"  图: {len(figures)} 个")
    print(f"  表: {len(tables)} 个")

    if figures:
        print(f"\n📷 图目录:")
        for f in figures:
            print(f"  图 {f.number}: {f.title}")

    if tables:
        print(f"\n📋 表目录:")
        for t in tables:
            print(f"  表 {t.number}: {t.title}")

    # Check continuity
    issues = check_number_continuity(text)
    if issues:
        print(f"\n⚠️ 编号问题:")
        for iss in issues:
            print(f"  {iss}")

    # Float suggestions
    suggestions = suggest_float_placement(text)
    if suggestions:
        print(f"\n📐 浮动体放置建议:")
        for s in suggestions[:10]:
            mention = f"首次提及在第{s.first_mention_line}行" if s.first_mention_line else "未找到引用"
            print(f"  {s.kind} {s.caption_num}: {mention} → 建议: {s.placement}")

    # Generate LoF/LoT
    lof = generate_list_of_figures(text)
    if lof:
        print(f"\n📄 图目录内容:")
        for line in lof.split("\n"):
            print(f"  {line}")

    lot = generate_list_of_tables(text)
    if lot:
        print(f"\n📄 表目录内容:")
        for line in lot.split("\n"):
            print(f"  {line}")


# ── style-apply (NEW) ─────────────────────────────────────────────

def action_style_apply(input_file: str, profile: str):
    """Apply a named style profile to structured JSON document."""
    path = Path(input_file)
    if not path.exists():
        print(f"✗ 文件不存在: {input_file}")
        sys.exit(1)

    if profile not in available_profiles():
        print(f"✗ 未知配置: {profile}")
        print(f"  可用: {', '.join(available_profiles())}")
        sys.exit(1)

    import json
    data = json.loads(path.read_text("utf-8"))
    mapper = StyleMapper(profile)

    print(f"\n🎨 应用样式配置: {profile} — {profile_description(profile)}")

    def apply_to_tree(node: dict, depth: int = 0):
        if isinstance(node, dict) and "type" in node:
            role = infer_semantic_role(node["type"], depth)
            style = mapper.map(role)
            node["_style"] = {
                "role": role,
                "font_cn": style.font_cn,
                "font_en": style.font_en,
                "size_pt": style.size_pt,
                "bold": style.bold,
                "align": style.align,
            }
            if "children" in node:
                for child in node["children"]:
                    apply_to_tree(child, depth + (1 if node["type"] in ("SECTION", "CHAPTER") else 0))

    apply_to_tree(data)
    out_path = path.with_suffix(f".styled{path.suffix}")
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 样式已应用，结果保存至: {out_path}")


# ── format-detect (NEW) ──────────────────────────────────────────

def action_format_detect(file_path: str):
    """Auto-detect input file format and content summary."""
    info = detect_format(file_path)
    print(f"\n📄 格式检测结果:")
    print(format_summary(info))
    return info


# ── diff (NEW) ───────────────────────────────────────────────────

def action_diff(file_a: str, file_b: str, mode: str = "side"):
    """Show diff between two document versions."""
    path_a, path_b = Path(file_a), Path(file_b)
    if not path_a.exists() or not path_b.exists():
        print("✗ 文件不存在")
        sys.exit(1)

    text_a = path_a.read_text("utf-8", errors="ignore")
    text_b = path_b.read_text("utf-8", errors="ignore")

    if mode == "side":
        from modules.change_log import side_by_side_diff
        output = side_by_side_diff(text_a, text_b)
    else:
        from modules.change_log import unified_diff
        output = unified_diff(text_a, text_b)

    print(f"\n📊 差异对比 ({file_a} ↔ {file_b}):")
    print("=" * 60)
    print(output[:3000])  # limit output


# ── space-audit (NEW) ───────────────────────────────────────────

def action_space_audit(file_path: str, fix: bool = False):
    """Audit whitespace health and optionally fix."""
    path = Path(file_path)
    if not path.exists():
        print(f"✗ 文件不存在: {file_path}")
        sys.exit(1)

    text = path.read_text("utf-8", errors="ignore")
    print(f"\n🔍 空格健康检查: {file_path}")

    if fix:
        text, report = quick_fix_spaces(text)
        print(report.summary())
        out_path = path.with_suffix(f".fixed{path.suffix}")
        out_path.write_text(text, encoding="utf-8")
        print(f"✅ 已修复并保存至: {out_path}")
    else:
        report = audit_spaces(text)
        print(report.summary())
        for iss in report.issues[:20]:
            print(f"  第{iss.line_num}行 [{iss.issue_type}]: {iss.context[:50]}")
        if len(report.issues) > 20:
            print(f"  ... 共{len(report.issues)}个问题")

    return report


# ── merge (NEW) ─────────────────────────────────────────────────

def action_merge(file_paths: list[str], output: str = "merged.txt"):
    """Merge multiple documents into one."""
    if len(file_paths) < 2:
        print("✗ 请指定至少2个文件")
        sys.exit(1)

    print(f"\n🔗 合并文档: {', '.join(file_paths)}")
    plan = MergePlan(strategy="append", renumber_sections=True, renumber_figures=True)
    for fp in file_paths:
        plan.add_file(fp)

    merged_text, logs = merge_documents(plan)
    out_path = Path(output)
    out_path.write_text(merged_text, encoding="utf-8")

    print(f"合并日志:")
    for log in logs:
        print(f"  {log}")
    print(f"✅ 合并完成: {out_path} ({len(merged_text)} 字符)")


# ── track-changes (NEW) ─────────────────────────────────────────

def action_track_changes(file_path: str):
    """Detect track changes, comments, and formatting artifacts."""
    path = Path(file_path)
    if not path.exists():
        print(f"✗ 文件不存在: {file_path}")
        sys.exit(1)

    text = path.read_text("utf-8", errors="ignore")
    print(f"\n🔍 内容保护检查: {file_path}")

    # Track changes
    changes = detect_track_changes(text)
    if changes:
        print(f"\n📝 修订痕迹 ({len(changes)} 处):")
        for marker, line in changes[:10]:
            print(f"  第{line}行: {marker[:60]}")
    else:
        print(f"\n📝 修订痕迹: 未检测到")

    # Comments
    comments = detect_comments(text)
    if comments:
        print(f"\n💬 批注/标记 ({len(comments)} 处):")
        for comment, line in comments[:10]:
            print(f"  第{line}行: {comment[:60]}")
    else:
        print(f"\n💬 批注/标记: 未检测到")

    print(f"\n建议: 使用 'python {Path(__file__).name} clean {file_path}' 进行清洗")


# ── template-analyze (NEW) ──────────────────────────────────────

def action_template_analyze(file_path: str):
    """Analyze an uploaded template document for style rules."""
    path = Path(file_path)
    if not path.exists():
        print(f"✗ 文件不存在: {file_path}")
        sys.exit(1)

    print(f"\n📐 模板分析: {file_path}")
    template = analyze_template(path)
    print(f"  名称: {template.name}")
    print(f"  类型: {path.suffix}")
    if template.rules:
        print(f"\n  检测到的格式规则:")
        for rule in template.rules:
            print(f"    • {rule}")
    if template.page_margins:
        m = template.page_margins
        print(f"\n  页面设置:")
        print(f"    上: {m.get('top_cm')}cm  下: {m.get('bottom_cm')}cm")
        print(f"    左: {m.get('left_cm')}cm  右: {m.get('right_cm')}cm")


# ── preference (NEW) ────────────────────────────────────────────

def action_preference(from_instruction: str = ""):
    """Parse a natural language formatting instruction into preferences."""
    if not from_instruction:
        print("用法: python sjtuthesis_engine.py preference \"<自然语言指令>\"")
        print("示例: python sjtuthesis_engine.py preference \"严格遵循学校模板，紧凑排版\"")
        sys.exit(1)

    print(f"\n⚙️  解析排版偏好: \"{from_instruction}\"")
    prefs = UserPreferences.from_instruction(from_instruction)
    print(f"  严格度: {prefs.strictness.value}")
    print(f"  密度: {prefs.density.value}")
    if prefs.reference_format:
        print(f"  参考文献格式: {prefs.reference_format}")
    if prefs.extra_rules:
        for rule in prefs.extra_rules:
            print(f"  特殊规则: {rule}")
    print(f"  原始指令: {from_instruction}")


# ── change-log (NEW) ────────────────────────────────────────────

def action_change_log(file_path: str):
    """Display a saved change log from a formatting session."""
    path = Path(file_path)
    if not path.exists():
        print(f"✗ 文件不存在: {file_path}")
        sys.exit(1)

    import json
    data = json.loads(path.read_text("utf-8"))
    cl = ChangeLog(**data)
    print(cl.summary())


# ── Main ───────────────────────────────────────────────────────────

def show_usage():
    """Print usage information."""
    print_banner()
    print(f"用法: python {Path(__file__).name} <命令> [参数]")
    print()
    print("【基础命令】")
    print("  doctor                   环境诊断")
    print("  info [output.json]       交互式信息收集")
    print("  interactive              全流程引导模式")
    print("  render-word <json> <输出.docx>   生成 Word 文档")
    print("  render-latex <json> <输出.tex>   生成 LaTeX 文档")
    print("  render-latex --standalone <json> <输出.tex>   生成独立 LaTeX")
    print("  validate <文件>           格式合规验证 (.docx / .tex)")
    print()
    print("【智能分析】")
    print("  semantic-parse <输入.txt> [输出.json]   语义结构解析")
    print("  clean <输入.txt> [输出.txt]             语义清洗")
    print("  citations <输入.txt>                    引用格式分析")
    print("  figures <输入.txt>                      图表分析 (含LoF/LoT)")
    print("  space-audit <文件> [--fix]              空格健康检查")
    print("  format-detect <文件>                    格式自动检测")
    print("  track-changes <文件>                    修订痕迹与批注检测")
    print("  template-analyze <文件>                 模板样式分析")
    print()
    print("【文档处理】")
    print("  merge <文件1> <文件2> [文件3...] [-o 输出]   多文档合并")
    print("  diff <文件A> <文件B>                   文档差异对比")
    print("  preference \"<指令>\"                     自然语言→排版偏好")
    print("  change-log <changelog.json>             显示修改日志")
    print()
    print("【样式引擎】")
    print("  style-list [配置名]                     列出样式配置")
    print("  style-apply <树.json> <配置名>          应用样式到结构树")
    print()
    print("示例:")
    print(f"  python {Path(__file__).name} doctor")
    print(f"  python {Path(__file__).name} format-detect thesis.docx")
    print(f"  python {Path(__file__).name} merge ch1.md ch2.md ch3.md -o thesis.txt")
    print(f"  python {Path(__file__).name} space-audit draft.txt --fix")
    print(f"  python {Path(__file__).name} preference \"严格模板 紧凑排版\"")
    print(f"  python {Path(__file__).name} track-changes thesis.docx")
    print(f"  python {Path(__file__).name} diff original.txt formatted.txt")
    print(f"  python {Path(__file__).name} semantic-parse draft.txt structure.json")
    print(f"  python {Path(__file__).name} style-list sjtu")
    print(f"  python {Path(__file__).name} render-word thesis_info.json output.docx")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help", "--usage"):
        show_usage()
        sys.exit(0)

    command = sys.argv[1]

    if command == "doctor":
        action_doctor()

    elif command == "info":
        output = sys.argv[2] if len(sys.argv) > 2 else None
        action_info(output)

    elif command == "render-word":
        if len(sys.argv) < 4:
            print("用法: python sjtuthesis_engine.py render-word <thesis_info.json> <output.docx>")
            sys.exit(1)
        action_render_word(sys.argv[2], sys.argv[3])

    elif command == "render-latex":
        if len(sys.argv) < 4:
            print("用法: python sjtuthesis_engine.py render-latex [--standalone] <thesis_info.json> <output.tex>")
            sys.exit(1)
        standalone = False
        arg_idx = 2
        if sys.argv[2] == "--standalone":
            standalone = True
            arg_idx = 3
            if len(sys.argv) < 5:
                print("用法: python sjtuthesis_engine.py render-latex --standalone <thesis_info.json> <output.tex>")
                sys.exit(1)
        action_render_latex(sys.argv[arg_idx], sys.argv[arg_idx + 1], standalone=standalone)

    elif command == "interactive":
        action_interactive()

    elif command == "validate":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py validate <file.docx|file.tex>")
            sys.exit(1)
        action_validate(sys.argv[2])

    elif command == "semantic-parse":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py semantic-parse <input.txt> [output.json]")
            sys.exit(1)
        action_semantic_parse(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")

    elif command == "clean":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py clean <input.txt> [output.txt]")
            sys.exit(1)
        action_clean(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")

    elif command == "citations":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py citations <input.txt>")
            sys.exit(1)
        action_citations(sys.argv[2])

    elif command == "figures":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py figures <input.txt>")
            sys.exit(1)
        action_figures(sys.argv[2])

    elif command == "style-list":
        profile = sys.argv[2] if len(sys.argv) > 2 else ""
        action_style_list(profile)

    elif command == "style-apply":
        if len(sys.argv) < 4:
            print("用法: python sjtuthesis_engine.py style-apply <input.json> <profile>")
            sys.exit(1)
        action_style_apply(sys.argv[2], sys.argv[3])

    elif command == "format-detect":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py format-detect <file>")
            sys.exit(1)
        action_format_detect(sys.argv[2])

    elif command == "diff":
        if len(sys.argv) < 4:
            print("用法: python sjtuthesis_engine.py diff <fileA> <fileB>")
            sys.exit(1)
        action_diff(sys.argv[2], sys.argv[3],
                    mode=sys.argv[4] if len(sys.argv) > 4 else "side")

    elif command == "space-audit":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py space-audit <file> [--fix]")
            sys.exit(1)
        action_space_audit(sys.argv[2], fix="--fix" in sys.argv)

    elif command == "merge":
        if len(sys.argv) < 4:
            print("用法: python sjtuthesis_engine.py merge <file1> <file2> [file3...] [-o output]")
            sys.exit(1)
        # Collect files until -o flag
        files = []
        output = "merged.txt"
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "-o" and i + 1 < len(sys.argv):
                output = sys.argv[i + 1]
                i += 2
            else:
                files.append(sys.argv[i])
                i += 1
        action_merge(files, output)

    elif command == "track-changes":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py track-changes <file>")
            sys.exit(1)
        action_track_changes(sys.argv[2])

    elif command == "template-analyze":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py template-analyze <file>")
            sys.exit(1)
        action_template_analyze(sys.argv[2])

    elif command == "preference":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py preference \"<natural language instruction>\"")
            sys.exit(1)
        action_preference(sys.argv[2])

    elif command == "change-log":
        if len(sys.argv) < 3:
            print("用法: python sjtuthesis_engine.py change-log <changelog.json>")
            sys.exit(1)
        action_change_log(sys.argv[2])

    else:
        print(f"未知命令: {command}")
        print(f"运行 'python {Path(__file__).name} help' 查看帮助")
        sys.exit(1)


if __name__ == "__main__":
    main()
