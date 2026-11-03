"""标签生成模块：仅保留业务标签与内容关键词标签。"""

import re
from typing import Dict, List

import jieba.analyse

# 停用词用于过滤过泛关键词，保留主题相关词。
_STOPWORDS = {
    "公司",
    "集团",
    "文件",
    "报告",
    "方案",
    "规划",
    "工作",
    "推进",
    "实施",
    "相关",
    "年度",
    "发展",
}


def _sanitize_tag_text(text: str) -> str:
    value = (text or "").strip()
    value = re.sub(r"[\s\r\n]+", "", value)
    value = re.sub(r"^[#]+", "", value)
    value = re.sub(r"[^\w\u4e00-\u9fff]", "", value)
    return value


def _extract_keywords(content: str, top_k: int = 8) -> List[str]:
    source = (content or "").strip()
    if not source:
        return []
    raw_keywords = jieba.analyse.textrank(
        source[:3000],
        topK=top_k,
        withWeight=False,
        allowPOS=("n", "nz", "vn", "v"),
    )
    keywords: List[str] = []
    for kw in raw_keywords:
        clean_kw = _sanitize_tag_text(kw)
        if len(clean_kw) < 2:
            continue
        if clean_kw in _STOPWORDS:
            continue
        if clean_kw in keywords:
            continue
        keywords.append(clean_kw)
    return keywords


def generate_tags(metadata: Dict[str, str], content: str) -> List[str]:
    """生成标签（3-8个）：单位/年份/版本 + 内容关键词。"""
    tags: List[str] = []
    company = _sanitize_tag_text(str(metadata.get("company", "")))
    year = re.sub(r"\D", "", str(metadata.get("file_date", "")))[:4]
    version = _sanitize_tag_text(str(metadata.get("version", "")))

    if company:
        tags.append(f"#{company}")
    if len(year) == 4:
        tags.append(f"#{year}")
    if version:
        tags.append(f"#{version}")

    keyword_tags = [f"#{kw}" for kw in _extract_keywords(content, top_k=10)]

    # 内容关键词保持 3-5 个，整体标签控制在 3-8 个。
    for tag in keyword_tags:
        if tag not in tags:
            tags.append(tag)
        content_count = len([t for t in tags if t not in {f"#{company}", f"#{year}", f"#{version}"}])
        if content_count >= 5:
            break

    if len(tags) < 3:
        subject = _sanitize_tag_text(str(metadata.get("subject", "")))
        if subject and f"#{subject}" not in tags:
            tags.append(f"#{subject}")

    # 最终去重并截断，保证标签数量适中。
    result: List[str] = []
    for t in tags:
        if t and t not in result:
            result.append(t)
        if len(result) >= 8:
            break
    return result[:8]

