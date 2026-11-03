"""
将人物描写词汇参考手册.md 和 提示词词母.md 转换为 JSON 格式
"""

import re
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "references"


def parse_vocab_md(filepath):
    """解析人物描写词汇参考手册.md，提取分类和词汇表"""
    text = filepath.read_text(encoding="utf-8")
    result = {}

    # 按 ## 分节
    sections = re.split(r"^##\s+", text, flags=re.MULTILINE)
    for sec in sections:
        if not sec.strip():
            continue
        lines = sec.strip().split("\n")
        title = lines[0].strip()
        # 去掉编号如 "1. 整体印象" 中的数字
        title = re.sub(r"^\d+\.\s*", "", title)

        # 处理子节（### 如 "### 眼睛", "### 瞳孔"）
        subsections = re.split(r"^###\s+", sec, flags=re.MULTILINE)
        if len(subsections) > 1:
            # 有子节
            sub_data = {}
            for sub in subsections:
                if not sub.strip():
                    continue
                sub_lines = sub.strip().split("\n")
                sub_title = sub_lines[0].strip()
                table_text = "\n".join(sub_lines[1:])
                entries = parse_table(table_text)
                if entries:
                    sub_data[sub_title] = entries
            if sub_data:
                result[title] = sub_data
        else:
            entries = parse_table(sec)
            if entries:
                result[title] = entries

    return result


def parse_table(text):
    """从 markdown 表格文本中提取 中文→英文 映射"""
    entries = {}
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            parts = [p.strip() for p in line.split("|")]
            # 过滤表头和分隔行
            if parts[1] in ("中文", "中文", "---") or "---" in parts[1]:
                continue
            if len(parts) >= 3 and parts[1] and parts[2]:
                cn = parts[1].strip()
                en = parts[2].strip()
                if cn and en:
                    # 多个英文用 / 分隔时取第一个为主
                    en_primary = en.split("/")[0].strip()
                    entries[cn] = en_primary
    return entries


def parse_mother_prompt_md(filepath):
    """解析提示词词母.md，提取模块和细节标签"""
    text = filepath.read_text(encoding="utf-8")
    result = {}
    modules = {}

    # 匹配功能模块标题，如 "## 🔧 功能模块：脸部细节极致描述"
    module_pattern = re.compile(
        r"^##\s+.*?(?:功能模块|模块[一二三四])(?::|：)?\s*(.*?)(?:（|$)", re.MULTILINE
    )

    # 查找所有模块
    sections = re.split(r"^(?=##\s)", text, flags=re.MULTILINE)
    current_module = None

    for sec in sections:
        if not sec.strip():
            continue
        header_match = re.match(
            r"^##\s+.*?(?:功能模块|模块[一二三四])(?::|：)?\s*(.*?)(?:（|\n|$)", sec
        )
        if header_match:
            current_module = header_match.group(1).strip()
            modules[current_module] = {
                "description": "",
                "details": [],
                "sd_tags": [],
                "mj_rule": "",
            }
            # 提取描述
            desc_match = re.search(r">\s*(.*?)(?:\n|$)", sec)
            if desc_match:
                modules[current_module]["description"] = desc_match.group(1).strip()
            # 提取细节项
            details = re.findall(r"\*\s*\(([^)]+)\)", sec)
            if details:
                modules[current_module]["details"] = details
            # 提取 SD 标签块
            sd_blocks = re.findall(
                r"```text\n(.*?)```", sec, re.DOTALL
            )
            for block in sd_blocks:
                tags = [t.strip() for t in block.strip().split(",") if t.strip()]
                modules[current_module]["sd_tags"].extend(tags)
            # 提取 MJ 描述
            mj_match = re.search(r">\s*(\.\.\.)", sec)
            mj_quotes = re.findall(r">\s*\"(.+?)\"", sec, re.DOTALL)
            if mj_quotes:
                modules[current_module]["mj_rule"] = mj_quotes[0].strip()

    result["模块"] = modules

    # 提取高级感光影组合预设
    preset_pattern = re.compile(r"\*\*(.*?)\*\*[：:]\s*(.*)")
    presets = preset_pattern.findall(text)
    if presets:
        result["光影预设"] = {k.strip(): v.strip() for k, v in presets}

    return result


def main():
    vocab_file = BASE / "人物描写词汇参考手册.md"
    mother_file = BASE / "提示词词母.md"

    print(f"📖 读取文件...")

    # 转换词汇手册
    if vocab_file.exists():
        vocab_data = parse_vocab_md(vocab_file)
        vocab_json = BASE / "词汇数据库.json"
        with open(vocab_json, "w", encoding="utf-8") as f:
            json.dump({"词汇": vocab_data}, f, ensure_ascii=False, indent=2)
        total_entries = sum(
            len(v) if isinstance(v, dict) else sum(len(sv) for sv in v.values())
            for v in vocab_data.values()
        )
        print(f"✅ 词汇数据库.json 已生成（{len(vocab_data)} 个分类）")

    # 转换提示词词母
    if mother_file.exists():
        mother_data = parse_mother_prompt_md(mother_file)
        mother_json = BASE / "母题数据库.json"
        with open(mother_json, "w", encoding="utf-8") as f:
            json.dump(mother_data, f, ensure_ascii=False, indent=2)
        print(
            f"✅ 母题数据库.json 已生成（{len(mother_data.get('模块', {}))} 个模块）"
        )

    print("\n🎉 转换完成！")


if __name__ == "__main__":
    main()
