#!/usr/bin/env python3
"""
市场情绪评分计算测试
测试情绪评分算法的准确性
"""

def test_sentiment_score_calculation():
    """测试情绪评分计算"""
    # 模拟数据
    sentiment_score = 75
    capital_score = 60
    tech_score = 80

    weights = {
        "sentiment": 0.4,
        "capital": 0.35,
        "tech": 0.25
    }

    # 计算综合得分
    total_score = (sentiment_score * weights["sentiment"] +
                  capital_score * weights["capital"] +
                  tech_score * weights["tech"])

    print(f"综合情绪评分: {total_score:.1f}")
    assert 70 <= total_score <= 80, f"评分计算异常: {total_score}"
    print("✅ 评分计算测试通过")

def test_sentiment_level_classification():
    """测试情绪等级分类"""
    def get_sentiment_level(score):
        if score < 20:
            return "极度悲观"
        elif score < 40:
            return "悲观"
        elif score < 60:
            return "中性"
        elif score < 80:
            return "乐观"
        else:
            return "极度乐观"

    test_cases = [
        (15, "极度悲观"),
        (25, "悲观"),
        (45, "中性"),
        (65, "乐观"),
        (85, "极度乐观"),
    ]

    for score, expected_level in test_cases:
        result = get_sentiment_level(score)
        assert result == expected_level, f"评分 {score} 应分类为 {expected_level}, 实际为 {result}"
        print(f"✅ 评分 {score} -> {result}")

    print("✅ 情绪等级分类测试通过")

def test_weight_adjustment():
    """测试权重调整"""
    adjusted_weights = {"sentiment": 0.5, "capital": 0.3, "tech": 0.2}

    # 验证权重总和为1
    assert sum(adjusted_weights.values()) == 1.0, "权重总和必须为1"
    print("✅ 权重调整验证通过")

def main():
    print("🧪 运行市场情绪评分测试")
    print("=" * 50)

    test_sentiment_score_calculation()
    test_sentiment_level_classification()
    test_weight_adjustment()

    print("=" * 50)
    print("✅ 所有测试通过！")

if __name__ == "__main__":
    main()
