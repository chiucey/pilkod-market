#!/usr/bin/env python3
"""
跨境电商选品技能 - 测试脚本
测试技能各个模块的功能
"""

import sys
import json
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from product_selector import ProductSelector

def test_data_initialization():
    """测试数据初始化"""
    print("测试数据初始化...")

    selector = ProductSelector()

    # 初始化数据
    selector.update_hot_topics()
    selector.update_best_sellers()
    selector.update_market_trends()
    selector.update_categories()

    # 验证数据
    topics = selector.get_hot_topics()
    products = selector.get_best_sellers()
    trends = selector.get_market_trends()
    categories = selector.get_categories()

    assert len(topics.get("topics", [])) > 0, "热点数据为空"
    assert len(products.get("products", [])) > 0, "爆品数据为空"
    assert len(trends.get("trends", [])) > 0, "趋势数据为空"
    assert len(categories.get("categories", [])) > 0, "品类数据为空"

    print("✓ 数据初始化测试通过")
    return True

def test_hot_topics_operations():
    """测试热点数据操作"""
    print("测试热点数据操作...")

    selector = ProductSelector()

    # 获取当前热点
    topics = selector.get_hot_topics()
    assert "topics" in topics

    # 添加自定义热点
    custom_topic = {
        "name": "测试品类",
        "trend": "上升",
        "heat_score": 90
    }
    selector.add_custom_topic(custom_topic)

    # 验证添加成功
    topics = selector.get_hot_topics()
    custom_found = any(t.get("name") == "测试品类" for t in topics.get("topics", []))
    assert custom_found, "自定义热点添加失败"

    print("✓ 热点数据操作测试通过")
    return True

def test_best_sellers_operations():
    """测试爆品数据操作"""
    print("测试爆品数据操作...")

    selector = ProductSelector()

    # 获取当前爆品
    products = selector.get_best_sellers()
    assert "products" in products

    # 添加自定义爆品
    custom_product = {
        "name": "测试爆品",
        "platform": "Amazon",
        "market": "北美",
        "price_range": "$20-30"
    }
    selector.add_custom_product(custom_product)

    # 验证添加成功
    products = selector.get_best_sellers()
    custom_found = any(p.get("name") == "测试爆品" for p in products.get("products", []))
    assert custom_found, "自定义爆品添加失败"

    print("✓ 爆品数据操作测试通过")
    return True

def test_product_analysis():
    """测试产品分析功能"""
    print("测试产品分析功能...")

    selector = ProductSelector()

    # 分析家居用品
    result = selector.analyze_product_opportunity("家居用品")

    assert "category" in result
    assert "opportunity_score" in result
    assert "recommendation" in result
    assert result["category"] == "家居用品"

    # 验证分数范围
    assert 0 <= result["opportunity_score"] <= 100

    print(f"✓ 产品分析测试通过 (机会评分: {result['opportunity_score']})")
    return True

def test_report_generation():
    """测试报告生成功能"""
    print("测试报告生成功能...")

    selector = ProductSelector()

    # 生成完整报告
    report = selector.generate_report("full")

    assert "选品热点" in report or "hot_topics" in report.lower() or len(report) > 0
    assert len(report) > 100, "报告内容过短"

    # 测试不同类型报告
    topics_report = selector.generate_report("hot_topics")
    products_report = selector.generate_report("best_sellers")
    trends_report = selector.generate_report("trends")

    assert len(topics_report) > 0
    assert len(products_report) > 0
    assert len(trends_report) > 0

    print("✓ 报告生成测试通过")
    return True

def test_data_persistence():
    """测试数据持久化"""
    print("测试数据持久化...")

    import tempfile
    import shutil

    # 使用临时目录
    temp_dir = Path(tempfile.mkdtemp())

    try:
        selector1 = ProductSelector(temp_dir)

        # 添加数据
        custom_topic = {"name": "持久化测试", "trend": "上升", "heat_score": 85}
        selector1.add_custom_topic(custom_topic)

        custom_product = {"name": "持久化产品", "platform": "Amazon", "market": "北美", "price_range": "$25"}
        selector1.add_custom_product(custom_product)

        # 创建新实例验证数据
        selector2 = ProductSelector(temp_dir)
        topics = selector2.get_hot_topics()
        products = selector2.get_best_sellers()

        topic_found = any(t.get("name") == "持久化测试" for t in topics.get("topics", []))
        product_found = any(p.get("name") == "持久化产品" for p in products.get("products", []))

        assert topic_found, "热点数据未持久化"
        assert product_found, "爆品数据未持久化"

        print("✓ 数据持久化测试通过")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return True

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("跨境电商选品技能 - 测试套件")
    print("=" * 60)
    print()

    tests = [
        test_data_initialization,
        test_hot_topics_operations,
        test_best_sellers_operations,
        test_product_analysis,
        test_report_generation,
        test_data_persistence,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 测试失败: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
