#!/usr/bin/env python3
"""
提示词自动提升技能初始化脚本
用于创建必要的记忆存储目录和索引文件
"""

import os
import json
from datetime import datetime

def init_memory_structure():
    """初始化记忆存储结构"""
    base_path = "/memories/prompt-enhancements"

    # 创建目录结构
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(f"{base_path}/index", exist_ok=True)

    # 创建索引文件
    index_file = f"{base_path}/index/registry.json"
    if not os.path.exists(index_file):
        index = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "prompts": {}
        }
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"✓ 初始化完成: {base_path}")
    print(f"✓ 索引文件: {index_file}")

    return base_path

def add_prompt_mapping(original: str, enhanced: str, notes: str = "") -> str:
    """
    添加提示词映射关系

    Args:
        original: 原始提示词
        enhanced: 优化后的提示词
        notes: 优化说明

    Returns:
        映射ID
    """
    import hashlib

    base_path = "/memories/prompt-enhancements"

    # 生成唯一ID（基于原始提示词的哈希）
    prompt_hash = hashlib.md5(original.encode()).hexdigest()[:12]
    mapping_id = f"pmt_{prompt_hash}"

    # 创建映射文件
    mapping_data = {
        "id": mapping_id,
        "original_prompt": original,
        "enhanced_prompt": enhanced,
        "improvement_notes": notes,
        "created_at": datetime.now().isoformat(),
        "success_count": 0,
        "last_used": None
    }

    # 保存映射文件
    mapping_file = f"{base_path}/{mapping_id}.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, ensure_ascii=False, indent=2)

    # 更新索引
    index_file = f"{base_path}/index/registry.json"
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)

    index["prompts"][mapping_id] = {
        "original_hash": prompt_hash,
        "file": f"{mapping_id}.json",
        "added_at": datetime.now().isoformat()
    }

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return mapping_id

def find_similar_prompt(original: str) -> dict | None:
    """
    查找相似的已优化提示词

    Args:
        original: 用户输入的原始提示词

    Returns:
        匹配到的优化提示词数据，或None
    """
    import hashlib

    base_path = "/memories/prompt-enhancements"

    # 计算输入的哈希
    input_hash = hashlib.md5(original.encode()).hexdigest()[:12]
    input_id = f"pmt_{input_hash}"

    # 直接匹配
    direct_file = f"{base_path}/{input_id}.json"
    if os.path.exists(direct_file):
        with open(direct_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    # 模糊匹配 - 检查索引中的所有条目
    index_file = f"{base_path}/index/registry.json"
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)

        # 简单模糊匹配：检查原提示词的关键字重叠
        original_words = set(original.lower().split())

        for mapping_id, info in index["prompts"].items():
            mapping_file = f"{base_path}/{info['file']}"
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stored_words = set(data["original_prompt"].lower().split())

                    # 计算重叠率
                    if len(original_words) > 0:
                        overlap = len(original_words & stored_words) / len(original_words)
                        if overlap >= 0.7:  # 70%重叠率阈值
                            return data

    return None

def update_usage_stats(mapping_id: str, success: bool):
    """更新使用统计"""
    base_path = "/memories/prompt-enhancements"
    mapping_file = f"{base_path}/{mapping_id}.json"

    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data["success_count"] = data.get("success_count", 0) + (1 if success else 0)
        data["last_used"] = datetime.now().isoformat()

        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    init_memory_structure()
    print("\n使用方法：")
    print("  from init_skill import add_prompt_mapping, find_similar_prompt")
