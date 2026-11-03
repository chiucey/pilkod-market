#!/usr/bin/env python3
"""
自然语言 → paper-review 配置转换器
用法: python3 nl2config.py "我想调研量子计算硬件最近进展，关注arxiv和Nature，评估创新性和实用性，每篇给3个改进方向"
"""
import json
import re
import sys

DEFAULT_WEIGHTS = {
    "创新性": 0.25,
    "可复现性": 0.25,
    "可拓展性": 0.20,
    "优化潜力": 0.20,
    "影响力": 0.10,
}

DEFAULT_DOMAINS = {
    "ai4bio": ["arxiv", "nature", "ccf", "biorxiv", "pwcb"],
    "cs": ["arxiv", "ccf", "pwcb"],
    "quantum": ["arxiv", "nature", "ccf", "pwcb"],
    "medical": ["pubmed", "nature", "biorxiv", "arxiv"],
    "finance": ["arxiv", "ccf", "nature"],
    "default": ["arxiv", "nature", "ccf", "biorxiv", "pwcb"],
}

PLATFORM_KEYWORDS = {
    "arxiv": ["arxiv", "预印本"],
    "nature": ["nature", "自然", "nature子刊"],
    "ccf": ["ccf", "顶会", "icml", "neurips", "iclr", "cvpr", "aaai", "acl", "kdd", "sigkdd", "sigir", "emnlp"],
    "science": ["science", "科学"],
    "cell": ["cell", "细胞"],
    "biorxiv": ["biorxiv", "预印本"],
    "pwcb": ["papers with code", "pwc"],
    "pubmed": ["pubmed", "生物医学"],
}

DIMENSION_KEYWORDS = {
    "创新性": ["创新", "novelty", "新方法", "新框架", "突破", "突破性"],
    "可复现性": ["可复现", "代码", "开源", "reproducibil", "开源"],
    "可拓展性": ["可拓展", "scalab", "迁移", "泛化", "拓展"],
    "优化潜力": ["优化", "瓶颈", "改进空间", "optimiz"],
    "影响力": ["影响力", "impact", "重要", "价值", "应用"],
    "理论创新性": ["理论", "新理论", "分析框架", "数学贡献"],
    "实验完整性": ["实验", "验证", "充分性", "benchmark"],
    "写作质量": ["写作", "清晰", "逻辑"],
    "部署可行性": ["部署", "推理速度", "延迟", "硬件", "落地"],
    "任务匹配度": ["匹配", "场景", "业务", "实际问题"],
    "数据依赖": ["数据", "数据需求", "私有数据"],
    "可维护性": ["可维护", "代码质量", "文档", "社区"],
    "商业价值": ["商业", "价值", "成本", "业务价值"],
    "技术新颖度": ["技术新", "范式", "新思路"],
    "热度关注度": ["热度", "关注", "stars", "引用", "讨论"],
    "可跟进性": ["跟进", "可行性", "我方能力", "落地"],
}

def detect_platforms(text):
    platforms = []
    text_lower = text.lower()
    for platform, keywords in PLATFORM_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in keywords):
            platforms.append(platform)
    return platforms if platforms else DEFAULT_DOMAINS["default"]

def detect_dimensions(text):
    detected = []
    text_lower = text.lower()
    for dim, keywords in DIMENSION_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in keywords):
            detected.append(dim)
    return detected if detected else list(DEFAULT_WEIGHTS.keys())

def normalize_dimensions(dimensions, weights_map):
    total = sum(weights_map.get(d, 0.20) for d in dimensions)
    return [
        {"name": d, "weight": round(weights_map.get(d, 0.20) / total, 4), "question": ""}
        for d in dimensions
    ]

def extract_topic(text):
    # 提取用户描述的核心主题
    text = re.sub(r'(调研|搜索|论文|我想要|能不能|请帮我|能不能|看看)', '', text)
    text = re.sub(r'(最近|进展|最新|2024|2025|2026)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.strip('，,。:：')

def generate_keywords(topic, text):
    keywords = [topic]
    year_match = re.findall(r'202[4-6]', text)
    years = list(set(year_match)) if year_match else ["2024", "2025"]
    for kw in topic.split():
        for year in years:
            keywords.append(f"{kw} {year}")
    keywords.append(topic + " survey review")
    keywords.append(topic + " SOTA")
    keywords.append(topic + " github code")
    return list(dict.fromkeys(keywords))[:12]

def parse_natural_language(text):
    topic = extract_topic(text)
    platforms = detect_platforms(text)
    raw_dims = detect_dimensions(text)
    
    # 推断领域
    topic_lower = topic.lower()
    if any(k in topic_lower for k in ["rna", "蛋白", "生物", "alphafold", "biorxiv"]):
        domain = "ai4bio"
    elif any(k in topic_lower for k in ["量子", "quantum"]):
        domain = "quantum"
    elif any(k in topic_lower for k in ["医学", "医疗", "clinical", "biomedical"]):
        domain = "medical"
    elif any(k in topic_lower for k in ["金融", "finance", "量化", "trading"]):
        domain = "finance"
    else:
        domain = "cs"
    
    # 提取权重（如果有明确的权重描述）
    weights_map = dict(DEFAULT_WEIGHTS)
    weight_patterns = [
        (r'创新性[^\d]*?(\d+)%?', '创新性', 0.01),
        (r'可复现性[^\d]*?(\d+)%?', '可复现性', 0.01),
        (r'可拓展性[^\d]*?(\d+)%?', '可拓展性', 0.01),
        (r'优化潜力[^\d]*?(\d+)%?', '优化潜力', 0.01),
        (r'影响力[^\d]*?(\d+)%?', '影响力', 0.01),
        (r'理论[^\d]*?(\d+)%?', '理论创新性', 0.01),
        (r'实验[^\d]*?(\d+)%?', '实验完整性', 0.01),
        (r'部署[^\d]*?(\d+)%?', '部署可行性', 0.01),
    ]
    for pattern, key, multiplier in weight_patterns:
        m = re.search(pattern, text)
        if m:
            weights_map[key] = int(m.group(1)) * multiplier

    # 判断输出格式
    output_format = "standard"
    if any(k in text for k in ["简洁", "简短", "简单", "compact", "只要"]):
        output_format = "compact"
    if any(k in text for k in ["表格", "excel", "table", "平铺"]):
        output_format = "table"

    dims = normalize_dimensions(raw_dims, weights_map)
    topic_keywords = generate_keywords(topic, text)

    return {
        "name": topic.replace(" ", "-")[:30],
        "topic": topic,
        "topic_keywords": topic_keywords,
        "platforms": platforms,
        "evaluation": {
            "dimensions": dims,
            "min_papers": 5,
            "max_papers": 20
        },
        "output": {
            "format": output_format,
            "include_summary_table": True,
            "include_improvements": True,
            "improvement_count": 3
        }
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("用法: python3 nl2config.py <自然语言描述>")
        print("示例: python3 nl2config.py \"我想调研量子计算硬件最近进展，关注arxiv和Nature，评估创新性和实用性\"")
        sys.exit(1)
    
    config = parse_natural_language(text)
    print(json.dumps(config, ensure_ascii=False, indent=2))
