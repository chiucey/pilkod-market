"""分类目录名解析：按规范映射到 SHARED_BASE_PATH 下的一级/二级文件夹。"""

import os
import re
from typing import Tuple

# 一级目录：{代码}_类_{中文名称}
LEVEL1: dict[str, str] = {
    "A": "A类_企业基础信息库",
    "B": "B类_财务与经营动态库",
    "C": "C类_战略规划与改革重组库",
    "D": "D类_项目与投资监管库",
    "E": "E类_内控合规与监督库",
    "F": "F类_国资监管政策法规库",
}

# 二级目录：{代码}_{中文名称}
LEVEL2: dict[str, dict[str, str]] = {
    "A": {
        "A01": "A01_组织架构",
        "A02": "A02_基础画像",
    },
    "B": {
        "B01": "B01_财务快报与决算",
        "B02": "B02_经营分析报告",
        "B03": "B03_预算与投资",
        "B04": "B04_考核分配",
    },
    "C": {
        "C01": "C01_五年规划",
        "C02": "C02_专项改革方案",
        "C03": "C03_重组整合与压减",
        "C04": "C04_科技创新",
    },
    "D": {
        "D01": "D01_固定资产股权投资项目",
        "D02": "D02_基金业务",
    },
    "E": {
        "E01": "E01_法治合规",
        "E02": "E02_社会责任与ESG",
    },
    "F": {
        "F01": "F01_国务院国资委规章",
        "F02": "F02_省国资委规范性文件",
        "F03": "F03_废止失效库",
    },
}

# 二级分类默认主题（模型 subject 不清晰时兜底）
TOPIC_FALLBACK: dict[str, str] = {
    "A01": "组织架构与职责清单",
    "A02": "企业基础画像报告",
    "B01": "年度财务决算审计报告",
    "B02": "主业经营分析报告",
    "B03": "年度预算与投资计划",
    "B04": "中长期激励方案",
    "C01": "十五五发展规划纲要",
    "C02": "专项改革实施方案",
    "C03": "重组整合与压减方案",
    "C04": "数字化转型规划评估",
    "D01": "固定资产股权投资项目",
    "D02": "基金年度运营报告",
    "E01": "法治合规管理报告",
    "E02": "社会责任ESG报告",
    "F01": "国资监管政策文件",
    "F02": "省国资委规范性文件",
    "F03": "废止失效政策文件",
}


def _first_level2_folder_name(category1: str) -> str:
    """category2 无法匹配时，使用该一级分类下的第一个二级目录名。"""
    sub = LEVEL2.get(category1, LEVEL2["F"])
    first_key = sorted(sub.keys())[0]
    return sub[first_key]


def level1_folder_name(category1: str) -> str:
    """一级目录文件夹名称。"""
    return LEVEL1.get(category1, LEVEL1["F"])


def level2_folder_name(category1: str, category2: str) -> str:
    """二级目录文件夹名称（与 category2 代码对应）。"""
    c1 = category1 if category1 in LEVEL1 else "F"
    sub = LEVEL2.get(c1, LEVEL2["F"])
    c2 = (category2 or "").strip().upper()
    if c2 in sub:
        return sub[c2]
    if not re.fullmatch(r"[A-F]\d{2}", c2):
        c2 = f"{c1}01"
    if c2 in sub:
        return sub[c2]
    return _first_level2_folder_name(c1)


def archive_subpath_parts(category1: str, category2: str) -> Tuple[str, str]:
    """返回 (一级目录名, 二级目录名)，用于拼接到 SHARED_BASE_PATH 下。"""
    c1 = category1 if category1 in LEVEL1 else "F"
    return level1_folder_name(c1), level2_folder_name(c1, category2)


def archive_target_directory(shared_base: str, category1: str, category2: str) -> str:
    """分类对应的完整目标目录（不含文件名）。"""
    l1, l2 = archive_subpath_parts(category1, category2)
    return os.path.join(os.path.abspath(shared_base), l1, l2)


def fallback_topic_by_category(category1: str, category2: str) -> str:
    """返回二级分类默认主题，用于文件命名兜底。"""
    c1 = category1 if category1 in LEVEL1 else "F"
    c2 = (category2 or "").strip().upper()
    if c2 not in LEVEL2.get(c1, {}):
        c2 = f"{c1}01"
    return TOPIC_FALLBACK.get(c2, "综合材料")
