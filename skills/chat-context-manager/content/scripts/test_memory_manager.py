#!/usr/bin/env python3
"""
测试脚本 - 测试记忆管理器的核心功能
"""

import sys
import tempfile
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.memory_manager import MemoryManager

def test_identity_extraction():
    """测试身份信息提取"""
    manager = MemoryManager()

    test_cases = [
        ("我叫小明", "name", "小明"),
        ("叫我Nova", "name", "Nova"),
        ("我的头像是月光下的男孩", "avatar", "月光下的男孩"),
        ("My name is Nova", "name", "Nova"),
    ]

    print("测试身份信息提取...")
    all_passed = True
    for text, expected_key, expected_value in test_cases:
        result = manager.identify_identity_info(text)
        if result and expected_key in result:
            print(f"   ✓ '{text}' -> {result}")
        else:
            print(f"   ✗ '{text}' 未能正确提取 (结果: {result})")
            all_passed = False

    return all_passed

def test_preference_extraction():
    """测试偏好信息提取"""
    manager = MemoryManager()

    test_cases = [
        ("叫我小明吧", "nickname", "小明"),
        ("希望对话轻松一些", "preference", "对话轻松一些"),
    ]

    print("\n测试偏好信息提取...")
    all_passed = True
    for text, expected_key, expected_value in test_cases:
        result = manager.identify_preference_info(text)
        if result and expected_key in result:
            print(f"   ✓ '{text}' -> {result}")
        else:
            print(f"   ✗ '{text}' 未能正确提取 (结果: {result})")
            all_passed = False

    return all_passed

def test_save_and_load():
    """测试保存和加载功能"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MemoryManager(tmpdir)

        # 保存测试
        print("\n测试保存功能...")
        if manager.save_identity("name", "TestUser", "测试用户"):
            print("   ✓ 保存身份信息成功")
        else:
            print("   ✗ 保存身份信息失败")
            return False

        if manager.save_preference("nickname", "Test", "测试昵称"):
            print("   ✓ 保存偏好信息成功")
        else:
            print("   ✗ 保存偏好信息失败")
            return False

        # 加载测试
        print("\n测试加载功能...")
        identity = manager.load_identity()
        if "TestUser" in identity:
            print("   ✓ 加载身份信息成功")
        else:
            print("   ✗ 加载身份信息失败")
            return False

        return True

def test_process_message():
    """测试消息处理"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MemoryManager(tmpdir)

        message = "我叫小明，头像是月光下的男孩，以后叫我明哥"
        results = manager.process_message(message)

        print("\n测试消息处理...")
        print(f"   输入: {message}")
        print(f"   结果: {results}")

        if len(results) >= 2:
            print(f"   ✓ 成功提取 {len(results)} 条信息")
            return True
        else:
            print(f"   ✗ 仅提取了 {len(results)} 条信息 (预期 >= 2)")
            return False

def main():
    print("=" * 50)
    print("记忆管理器测试")
    print("=" * 50)

    tests = [
        test_identity_extraction,
        test_preference_extraction,
        test_save_and_load,
        test_process_message,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n   ✗ 测试异常: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    if all(results):
        print("✓ 所有测试通过!")
        return 0
    else:
        print("✗ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
