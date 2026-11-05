#!/usr/bin/env python3
"""
用户记忆初始化脚本
创建用户术语库和实体白名单的初始模板
"""

import json
import os

def create_user_glossary_template():
    """创建用户术语库模板"""
    template = {
        "version": "1.0",
        "last_updated": "2026-03-26",
        "description": "用户自定义翻译术语库 - 优先于内置术语",
        "terms": {},
        "entities": {},
        "corrections": {},
        "stats": {
            "total_terms": 0,
            "total_entities": 0,
            "total_corrections": 0
        }
    }
    return template

def create_entity_list_template():
    """创建实体名称白名单模板"""
    template = {
        "version": "1.0",
        "last_updated": "2026-03-26",
        "description": "实体名称白名单 - 翻译时原样保留",
        "categories": {
            "law": {},
            "game": {},
            "company": {},
            "platform": {},
            "country": {},
            "other": {}
        },
        "stats": {
            "total_entities": 0,
            "by_category": {}
        }
    }
    return template

def main():
    output_dir = "/memories"

    # 创建用户术语库
    glossary = create_user_glossary_template()
    glossary_path = os.path.join(output_dir, "literal-translator-user-glossary.json")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(glossary_path, 'w', encoding='utf-8') as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)

    print(f"✓ 用户术语库已创建: {glossary_path}")

    # 创建实体白名单
    entity_list = create_entity_list_template()
    entity_path = os.path.join(output_dir, "literal-translator-entity-list.json")

    with open(entity_path, 'w', encoding='utf-8') as f:
        json.dump(entity_list, f, ensure_ascii=False, indent=2)

    print(f"✓ 实体白名单已创建: {entity_path}")

if __name__ == "__main__":
    main()
