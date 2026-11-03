#!/usr/bin/env python3
"""股票自动盯盘技能验证脚本"""

import os
import re
import json
from pathlib import Path

def validate_skill():
    """验证技能文件结构和内容"""

    skill_dir = Path("/workspace/temp-skills/stock-auto-monitor")
    results = {
        "passed": [],
        "failed": []
    }

    # 1. 检查SKILL.md是否存在
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        results["failed"].append("SKILL.md文件不存在")
        return results
    results["passed"].append("SKILL.md文件存在")

    # 2. 读取SKILL.md内容
    content = skill_md.read_text(encoding="utf-8")

    # 3. 验证frontmatter
    frontmatter_pattern = r'^---\n(.*?)\n---'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        results["failed"].append("SKILL.md缺少frontmatter或格式错误")
        return results
    results["passed"].append("Frontmatter格式正确")

    # 解析frontmatter
    fm_content = match.group(1)
    fm_lines = fm_content.strip().split('\n')
    fm_dict = {}
    for line in fm_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            fm_dict[key.strip()] = value.strip()

    # 4. 验证必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in fm_dict:
            results["failed"].append(f"Frontmatter缺少必填字段: {field}")
        elif not fm_dict[field]:
            results["failed"].append(f"Frontmatter字段 {field} 为空")
        else:
            results["passed"].append(f"Frontmatter字段 {field} 存在且非空")

    # 5. 验证name格式
    if 'name' in fm_dict:
        if not re.match(r'^[a-z0-9-]+$', fm_dict['name']):
            results["failed"].append("name字段必须使用小写字母、数字、连字符")
        elif fm_dict['name'] != skill_dir.name:
            results["failed"].append(f"name字段({fm_dict['name']})应与文件夹名({skill_dir.name})一致")
        else:
            results["passed"].append("name字段格式正确")

    # 6. 验证description触发短语
    if 'description' in fm_dict:
        desc = fm_dict['description']
        trigger_keywords = ['触发关键词', '当用户需要', '使用当']
        has_trigger = any(kw in desc for kw in trigger_keywords)
        if has_trigger:
            results["passed"].append("description包含触发关键词")
        else:
            results["failed"].append("description缺少触发关键词")

    # 7. 验证_meta.json
    meta_file = skill_dir / "_meta.json"
    if not meta_file.exists():
        results["failed"].append("_meta.json文件不存在")
    else:
        results["passed"].append("_meta.json文件存在")
        try:
            meta_content = json.loads(meta_file.read_text(encoding="utf-8"))
            if 'id' not in meta_content:
                results["failed"].append("_meta.json缺少id字段")
            else:
                results["passed"].append("_meta.json包含id字段")
            if 'version' not in meta_content:
                results["failed"].append("_meta.json缺少version字段")
            else:
                results["passed"].append("_meta.json包含version字段")
        except json.JSONDecodeError:
            results["failed"].append("_meta.json格式错误，JSON解析失败")

    # 8. 验证内容完整性
    required_sections = [
        ('核心设置', r'核心设置'),
        ('买入信号', r'买入信号'),
        ('卖出信号', r'卖出信号'),
        ('止损规则', r'止损规则'),
        ('盯盘输出', r'输出格式|输出规范')
    ]

    for section_name, pattern in required_sections:
        if re.search(pattern, content):
            results["passed"].append(f"内容包含必含章节: {section_name}")
        else:
            results["failed"].append(f"内容缺少必含章节: {section_name}")

    # 9. 验证路径无中文
    for root, dirs, files in os.walk(skill_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            if any(ord(c) > 127 for c in filepath):
                results["failed"].append(f"文件路径包含非ASCII字符: {filepath}")
            else:
                results["passed"].append(f"路径验证通过: {filename}")

    return results

def print_results(results):
    """打印验证结果"""
    print("\n" + "="*50)
    print("验证结果汇总")
    print("="*50)

    print(f"\n✅ 通过项 ({len(results['passed'])}):")
    for item in results["passed"]:
        print(f"  ✓ {item}")

    if results["failed"]:
        print(f"\n❌ 失败项 ({len(results['failed'])}):")
        for item in results["failed"]:
            print(f"  ✗ {item}")
        print("\n⚠️ 验证未通过，请修复上述问题")
        return False
    else:
        print("\n🎉 所有验证项通过！技能结构正确")
        return True

if __name__ == "__main__":
    results = validate_skill()
    success = print_results(results)
    exit(0 if success else 1)
