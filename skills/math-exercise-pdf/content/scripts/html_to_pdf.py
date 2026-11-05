# -*- coding: utf-8 -*-
"""
HTML转PDF生成器
将HTML文件通过Edge浏览器headless模式转换为PDF

用法:
    python html_to_pdf.py <输入html文件路径> [输出pdf路径] [--force]
    
示例:
    python html_to_pdf.py test.html
    python html_to_pdf.py test.html output.pdf
    python html_to_pdf.py test.html --force
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

SUSPICIOUS_COMMANDS = (
    "frac",
    "dfrac",
    "tfrac",
    "sum",
    "prod",
    "lim",
    "epsilon",
    "varepsilon",
    "to",
    "infty",
    "cdots",
    "ldots",
    "sqrt",
    "left",
    "right",
    "underline",
    "overline",
    "mathbb",
    "vec",
    "forall",
    "exists",
    "ge",
    "le",
    "neq",
    "quad",
    "qquad",
)

MATH_REGION_PATTERN = re.compile(
    r"(?s)"
    r"(\$\$.*?(?<!\\)\$\$"
    r"|(?<!\\)\$(?!\$).*?(?<!\\)\$"
    r"|\\\[.*?\\\]"
    r"|\\\(.*?\\\))"
)


def _blank_keep_newlines(match: re.Match) -> str:
    """将匹配区域替换为空白，保留换行，便于后续定位行号。"""
    return re.sub(r"[^\r\n]", " ", match.group(0))


def _console_safe(text: str) -> str:
    """避免Windows控制台编码导致的打印异常。"""
    encoding = sys.stdout.encoding or "utf-8"
    try:
        text.encode(encoding)
        return text
    except UnicodeEncodeError:
        return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def find_suspicious_latex_outside_math(html_text: str) -> List[Tuple[int, str, str]]:
    """
    在非数学区域查找可疑LaTeX命令（如 \\underline 未放在 $...$ 中）。

    Returns:
        [(行号, 命令, 行内容), ...]
    """
    sanitized = html_text

    # 先屏蔽 script/style 区域，避免误报
    sanitized = re.sub(r"(?is)<script.*?>.*?</script>", _blank_keep_newlines, sanitized)
    sanitized = re.sub(r"(?is)<style.*?>.*?</style>", _blank_keep_newlines, sanitized)

    # 屏蔽常见数学定界符内部内容
    sanitized = MATH_REGION_PATTERN.sub(_blank_keep_newlines, sanitized)

    cmd_pattern = re.compile(r"\\(" + "|".join(SUSPICIOUS_COMMANDS) + r")\b")
    lines = html_text.splitlines()
    issues: List[Tuple[int, str, str]] = []

    for match in cmd_pattern.finditer(sanitized):
        line_no = sanitized.count("\n", 0, match.start()) + 1
        cmd = "\\" + match.group(1)
        line_content = lines[line_no - 1].strip() if 1 <= line_no <= len(lines) else ""
        issues.append((line_no, cmd, line_content))

    # 去重（同一行同一命令保留一次）
    seen = set()
    deduped: List[Tuple[int, str, str]] = []
    for item in issues:
        key = (item[0], item[1])
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def find_raw_angle_in_math(html_text: str) -> List[Tuple[int, str, str]]:
    """
    检测数学定界符内的裸 < / >。
    这类字符在HTML里可能被当作标签起始，导致公式截断或显示不全。
    """
    lines = html_text.splitlines()
    issues: List[Tuple[int, str, str]] = []

    for match in MATH_REGION_PATTERN.finditer(html_text):
        segment = match.group(0)
        if "<" not in segment and ">" not in segment:
            continue
        line_no = html_text.count("\n", 0, match.start()) + 1
        line_content = lines[line_no - 1].strip() if 1 <= line_no <= len(lines) else ""
        snippet = re.sub(r"\s+", " ", segment).strip()
        issues.append((line_no, line_content, snippet[:120]))
    return issues


def sanitize_raw_angle_in_math(html_text: str) -> Tuple[str, int]:
    """
    将数学定界符内的裸 < / > 转义为 &lt; / &gt;，避免被HTML解析器吞掉。
    返回: (修复后的文本, 替换数量)
    """
    replaced_count = 0

    def repl(match: re.Match) -> str:
        nonlocal replaced_count
        segment = match.group(0)
        count = segment.count("<") + segment.count(">")
        if count == 0:
            return segment
        replaced_count += count
        return segment.replace("<", "&lt;").replace(">", "&gt;")

    fixed = MATH_REGION_PATTERN.sub(repl, html_text)
    return fixed, replaced_count


def detect_edge_path() -> str | None:
    edge_candidates = [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    return next((p for p in edge_candidates if os.path.exists(p)), None)


def html_to_pdf(input_html: str, output_pdf: str | None = None, force: bool = False) -> bool:
    """
    将HTML文件转换为PDF
    
    Args:
        input_html: 输入HTML文件路径
        output_pdf: 输出PDF路径（可选，默认与HTML同名）
        force: 发现可疑LaTeX语法时是否强制导出
    """
    if not os.path.exists(input_html):
        print(f"错误: 文件不存在: {input_html}")
        return False
    
    if output_pdf is None:
        base_name = os.path.splitext(input_html)[0]
        output_pdf = base_name + ".pdf"
    
    abs_input = os.path.abspath(input_html)
    abs_output = os.path.abspath(output_pdf)

    try:
        html_text = Path(abs_input).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("警告: HTML不是UTF-8编码，已尝试忽略非法字符继续检查。")
        html_text = Path(abs_input).read_text(encoding="utf-8", errors="ignore")

    issues = find_suspicious_latex_outside_math(html_text)
    if issues:
        print(f"警告: 检测到 {len(issues)} 处可能未放在数学定界符中的LaTeX命令。")
        for line_no, cmd, line_content in issues[:10]:
            print(f"  行{line_no}: {cmd} -> {_console_safe(line_content)}")
        if len(issues) > 10:
            print(f"  ... 其余 {len(issues) - 10} 处已省略")
        if not force:
            print("错误: 已停止导出。请将命令包裹在 $...$ 或 $$...$$ 中，或使用 --force 强制导出。")
            return False
        print("已启用 --force，继续导出。")

    angle_issues = find_raw_angle_in_math(html_text)
    fixed_html, replaced_count = sanitize_raw_angle_in_math(html_text)

    temp_input_path: Path | None = None
    export_input_path = Path(abs_input)
    if replaced_count > 0:
        print(f"提示: 检测到 {len(angle_issues)} 处数学区包含裸 < 或 >，将自动转义后导出。")
        for line_no, line_content, snippet in angle_issues[:8]:
            print(f"  行{line_no}: {_console_safe(line_content)}")
            print(f"    片段: {_console_safe(snippet)}")
        if len(angle_issues) > 8:
            print(f"  ... 其余 {len(angle_issues) - 8} 处已省略")

        temp_input_path = Path(abs_input).with_name(Path(abs_input).stem + ".__katex_safe__.html")
        temp_input_path.write_text(fixed_html, encoding="utf-8")
        export_input_path = temp_input_path
        print(f"已生成临时安全副本: {temp_input_path}（替换 {replaced_count} 个符号）")

    edge_path = detect_edge_path()

    if edge_path is None:
        print("错误: 未找到Microsoft Edge浏览器")
        return False

    input_uri = export_input_path.as_uri()
    
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        # 给予JS足够时间渲染KaTeX，避免打印过早
        "--virtual-time-budget=15000",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={abs_output}",
        "--enable-features=UseSkiaRenderer",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--mute-audio",
        "--no-first-run",
        "--safebrowsing-disable-auto-update",
        input_uri,
    ]
    
    print(f"正在生成PDF: {output_pdf}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

        if result.returncode != 0:
            print(f"警告: Edge返回码 {result.returncode}")
            if result.stderr:
                print(f"Edge stderr: {result.stderr.strip()}")
        elif result.stderr:
            print(f"Edge stderr: {result.stderr.strip()}")

        time.sleep(2)

        if os.path.exists(abs_output):
            size = os.path.getsize(abs_output)
            print(f"PDF生成成功: {abs_output} ({size/1024:.1f} KB)")
            return True
        else:
            print("错误: PDF生成失败")
            return False
    finally:
        if temp_input_path is not None and temp_input_path.exists():
            try:
                temp_input_path.unlink()
            except OSError:
                print(f"警告: 临时文件未能删除: {temp_input_path}")

if __name__ == "__main__":
    args = [arg for arg in sys.argv[1:] if arg != "--force"]
    force = "--force" in sys.argv[1:]

    if len(args) < 1:
        print(__doc__)
        sys.exit(1)
    
    input_file = args[0]
    output_file = args[1] if len(args) > 1 else None
    
    success = html_to_pdf(input_file, output_file, force=force)
    sys.exit(0 if success else 1)
