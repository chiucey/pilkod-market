#!/usr/bin/env python3
"""校验标签 OCR 输出 JSON 是否符合 part-label-to-json 的约定结构。

用法: python3 validate_json.py output/零件标签-1.json [更多文件...]
退出码: 0 = 无 ERROR(可能有 WARN), 1 = 有 ERROR

只做**结构**校验（类型、键、顺序、空值），刻意不做内容猜测：
品号/件号没有固定格式，任何"像不像日期""像不像批次号"的启发式都会误报，
把 WARN 训练成噪声后，真正的错就看不见了。内容质量由 `parse_note` 承担。
"""
import json
import re
import sys

TOP_KEYS = ["label_type", "fields", "parse_note"]

# 含空格 / 括号 / 长破折号——可能是未归一化，也可能是识别破损，提示人工看一眼
SUSPECT_CHARS = re.compile(r"[()\[\]（）【】—–−─]|\s")
# ASCII 字母形式的 key（应改成中文语义名）
LATIN_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,24}$")

REVIEW_HINTS = ("人工核对", "建议核对", "存疑", "待确认", "不确定", "留空", "模糊", "反光", "看不清")


def check_one(path):
    errors, warns = [], []

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return ["文件不存在"], []
    except json.JSONDecodeError as e:
        return [f"JSON 解析失败: {e}"], []

    if not isinstance(data, dict):
        return ["顶层不是对象（单图输出应为单个 JSON 对象，不要套数组）"], []

    for k in TOP_KEYS:
        if k not in data:
            errors.append(f"缺少顶层 key: {k}")
    extra = [k for k in data if k not in TOP_KEYS]
    if extra:
        warns.append(f"顶层出现约定外 key: {extra}")
    if [k for k in data if k in TOP_KEYS] != TOP_KEYS:
        warns.append(f"顶层 key 顺序应为 {TOP_KEYS}")

    lt = data.get("label_type")
    if "label_type" in data:
        if not isinstance(lt, str) or not lt.strip():
            errors.append("label_type 必须是非空字符串")

    fields = data.get("fields")
    if "fields" in data:
        if not isinstance(fields, dict):
            errors.append("fields 必须是对象")
        elif not fields:
            warns.append("fields 为空对象——确认是不是整张都没识别出来")
        else:
            for name, val in fields.items():
                if LATIN_KEY.match(str(name)):
                    warns.append(f"字段名 '{name}' 是英文，建议改用中文语义名")
                if not isinstance(val, str):
                    errors.append(f"字段 '{name}' 值不是字符串（是 {type(val).__name__}）")
                    continue
                if not val.strip():
                    warns.append(f"字段 '{name}' 为空字符串——parse_note 里要说明原因")
                    continue
                if SUSPECT_CHARS.search(val):
                    warns.append(f"字段 '{name}' 含空格/括号/长破折号: {val!r}——确认是原样字符还是识别破损")

    note = data.get("parse_note")
    if "parse_note" in data:
        if not isinstance(note, str):
            errors.append("parse_note 必须是字符串")
        elif not note.strip():
            errors.append("parse_note 为空——必须写明质量情况或'无明显异常'")

    needs_review = isinstance(note, str) and any(h in note for h in REVIEW_HINTS)
    return errors, warns, needs_review


def main(argv):
    if not argv:
        print("usage: validate_json.py <file.json> [...]")
        return 1

    failed = False
    for path in argv:
        errors, warns = [], []
        result = check_one(path)
        if len(result) == 2:  # early return 分支
            errors, warns = result
            needs_review = False
        else:
            errors, warns, needs_review = result

        status = "ERROR" if errors else ("WARN" if warns else "OK")
        print(f"[{status}] {path}")
        for e in errors:
            print(f"  ERROR  {e}")
        for w in warns:
            print(f"  WARN   {w}")
        if needs_review:
            print("  NOTE   parse_note 标记了需人工核对")
        if errors:
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
