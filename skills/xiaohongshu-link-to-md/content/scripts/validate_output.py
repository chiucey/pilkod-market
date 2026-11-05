"""
validate_output.py — 验证 xiaohongshu-link-to-md 输出的 Markdown 文件质量。

检查项:
1. 文件存在且非空
2. 无残留未替换占位符（{{xxx}}）
3. 本地图片引用路径实际存在（link/embed 模式）
4. Markdown 基本语法有效（可选）

Usage:
    python scripts/validate_output.py ./xiaohongshu-notes/2026-06-02-xxx.md
    python scripts/validate_output.py ./xiaohongshu-notes/2026-06-02-xxx.md --check-images
"""

import os
import re
import sys
from pathlib import Path


class ValidationError(Exception):
    """验证错误，附带行号和上下文。"""
    def __init__(self, message, line=None, context=None):
        self.line = line
        self.context = context
        super().__init__(message)


def validate_file_exists(filepath):
    """检查输出文件是否存在且非空。"""
    path = Path(filepath)
    if not path.exists():
        raise ValidationError(f"文件不存在: {filepath}")
    if not path.is_file():
        raise ValidationError(f"路径不是文件: {filepath}")
    if path.stat().st_size == 0:
        raise ValidationError(f"文件为空: {filepath}")
    return path


def validate_no_unfilled_placeholders(filepath):
    """检查无残留占位符 {{xxx}}。"""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    pattern = re.compile(r"\{\{.*?\}\}")

    unfilled = []
    in_code_block = False
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        matches = pattern.findall(line)
        for match in matches:
            if match in ("{{URL}}", "{{原文链接}}"):
                continue
            unfilled.append((i, match.strip()))

    if unfilled:
        details = "\n".join(
            f"  行 {ln}: {placeholder}" for ln, placeholder in unfilled
        )
        raise ValidationError(
            f"发现 {len(unfilled)} 个未替换占位符:\n{details}"
        )
    return True


def validate_image_refs(filepath, base_dir=None):
    """检查本地图片引用路径是否实际存在。"""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")

    img_pattern = re.compile(r"!\[.*?\]\(([^)]+)\)")

    if base_dir is None:
        base_dir = path.parent

    missing = []
    for i, line in enumerate(content.split("\n"), start=1):
        matches = img_pattern.findall(line)
        for src in matches:
            if src.startswith(("http://", "https://", "data:")):
                continue
            img_path = Path(base_dir) / src
            if not img_path.exists():
                missing.append((i, src, str(img_path)))

    if missing:
        details = "\n".join(
            f"  行 {ln}: {src} → {resolved}"
            for ln, src, resolved in missing
        )
        raise ValidationError(
            f"发现 {len(missing)} 个缺失的本地图片:\n{details}"
        )
    return True


def validate_markdown_syntax(filepath):
    """基本 Markdown 语法检查。只检查真正的语法问题，避免误报。"""
    import re

    path = Path(filepath)
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    issues = []
    in_code_block = False

    valid_heading = re.compile(r"^#{1,6}\s")
    suspicious_heading = re.compile(r"^#{1,6}(?=\S)")

    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        if in_code_block:
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if re.match(r"^#[a-zA-Z0-9_\u4e00-\u9fff]+", stripped):
            continue

        if suspicious_heading.match(stripped) and not valid_heading.match(stripped):
            issues.append((i, f"Heading 缺少空格: '{stripped[:30]}'"))

    if issues:
        details = "\n".join(
            f"  行 {ln}: {desc}" for ln, desc in issues
        )
        raise ValidationError(
            f"发现 {len(issues)} 个语法问题:\n{details}"
        )
    return True


def validate(filepath, check_images=False, check_syntax=False):
    """运行所有验证项，返回 (passed, errors)。"""
    errors = []

    try:
        validate_file_exists(filepath)
        print(f"✅ 文件存在且非空: {filepath}")
    except ValidationError as e:
        errors.append(e)

    try:
        validate_no_unfilled_placeholders(filepath)
        print(f"✅ 无残留占位符: {filepath}")
    except ValidationError as e:
        errors.append(e)

    if check_images:
        try:
            validate_image_refs(filepath)
            print(f"✅ 本地图片引用有效: {filepath}")
        except ValidationError as e:
            errors.append(e)

    if check_syntax:
        try:
            validate_markdown_syntax(filepath)
            print(f"✅ Markdown 语法基本正常: {filepath}")
        except ValidationError as e:
            errors.append(e)

    if errors:
        print(f"\n❌ 验证失败！发现 {len(errors)} 个问题:\n")
        for err in errors:
            print(f"  [{type(err).__name__}] {err}")
        return False

    print(f"\n✅ 全部验证通过！")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="验证 xiaohongshu-link-to-md 输出的 Markdown 文件"
    )
    parser.add_argument("file", help="要验证的 .md 文件路径")
    parser.add_argument(
        "--check-images",
        action="store_true",
        help="同时检查本地图片引用路径是否实际存在",
    )
    parser.add_argument(
        "--check-syntax",
        action="store_true",
        help="同时检查 Markdown 基本语法",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="严格模式：等同于 --check-images --check-syntax",
    )

    args = parser.parse_args()

    check_images = args.check_images or args.strict
    check_syntax = args.check_syntax or args.strict

    success = validate(args.file, check_images=check_images, check_syntax=check_syntax)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
