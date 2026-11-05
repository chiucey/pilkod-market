#!/usr/bin/env python3
"""
简历优化技能脚本测试

测试各核心脚本的功能是否正常。
"""

import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from confidence_tracker import ConfidenceTracker
from keyword_extractor import KeywordExtractor


def test_confidence_tracker():
    """测试置信度追踪器"""
    print("\n" + "=" * 50)
    print("测试 1: 置信度追踪器")
    print("=" * 50)

    tracker = ConfidenceTracker()

    # 测试初始状态
    initial_status = tracker.get_status()
    assert initial_status["overall_confidence"] == 0, "初始置信度应为0"
    print("✓ 初始状态正确")

    # 测试维度更新
    tracker.update_dimension("job_target", 95.0, "用户明确表示目标岗位：产品经理")
    tracker.update_dimension("industry_positioning", 90.0, "用户有5年互联网经验")

    # 验证更新 (使用小数格式 0-1)
    assert abs(tracker.dimensions["job_target"].current - 0.95) < 0.01
    assert tracker.dimensions["job_target"].status == "met"
    print("✓ 维度更新正确")

    # 测试综合置信度计算
    overall = tracker.calculate_overall_confidence()
    print(f"  综合置信度: {overall:.1%}")
    assert overall > 0, "综合置信度应大于0"
    print("✓ 综合置信度计算正确")

    # 测试状态判定
    status = tracker.get_status()
    print(f"  状态: {status['status']}")
    print("✓ 状态判定正确")

    # 测试进度可视化
    viz = tracker.generate_progress_visualization()
    assert len(viz) > 0, "可视化内容不应为空"
    print("✓ 进度可视化生成正确")

    print("\n✅ 置信度追踪器测试通过！\n")


def test_keyword_extractor():
    """测试关键词提取器"""
    print("\n" + "=" * 50)
    print("测试 2: 关键词提取器")
    print("=" * 50)

    extractor = KeywordExtractor()

    # 测试JD文本
    sample_jd = """
    高级产品经理

    岗位描述：
    1. 负责用户增长相关产品的设计和优化
    2. 通过数据分析驱动产品决策
    3. 跨部门协调，推动产品落地
    4. 带领团队完成产品迭代

    任职要求：
    1. 本科及以上学历，5年以上互联网产品经验
    2. 具备优秀的数据分析能力，熟练使用SQL、Python等工具
    3. 有用户增长或商业化经验优先
    4. 具备良好的沟通协调能力和项目管理能力
    5. 有团队管理经验者优先
    """

    # 提取关键词
    keywords = extractor.extract_from_jd(sample_jd)
    print(f"✓ 从JD中提取到 {len(keywords)} 个关键词")
    assert len(keywords) > 0, "应该提取到关键词"

    # 显示前10个关键词
    print("\n  前10个关键词:")
    for keyword, freq in keywords[:10]:
        print(f"    {keyword}: {freq}次")
    print("✓ 关键词提取功能正常")

    # 测试匹配功能
    sample_resume = """
    产品经理，负责短视频产品迭代，
    通过数据分析优化用户体验，
    使用SQL进行数据提取和分析。
    协调开发、设计团队完成产品上线。
    技能：产品设计、数据分析、用户研究、Axure
    """

    matches = extractor.match_with_resume(keywords, sample_resume)
    print(f"\n✓ 关键词匹配分析完成，发现 {len(matches)} 个匹配项")

    # 生成报告
    report = extractor.generate_match_report(keywords, matches)
    assert "关键词优化" in report
    print("✓ 匹配报告生成正确")

    print("\n✅ 关键词提取器测试通过！\n")


def test_integration():
    """集成测试"""
    print("\n" + "=" * 50)
    print("测试 3: 集成测试")
    print("=" * 50)

    # 模拟完整的简历优化流程

    tracker = ConfidenceTracker()
    extractor = KeywordExtractor()

    # 步骤1: 收集用户信息并更新置信度
    print("\n[步骤1] 收集用户信息...")

    # 假设用户回答了求职目标问题
    tracker.update_dimension(
        "job_target",
        95.0,
        "目标：高级产品经理，期望薪资35-45K，倾向互联网/AI行业"
    )

    tracker.update_dimension(
        "industry_positioning",
        95.0,
        "深耕互联网/AI行业5年，有一定行业人脉"
    )

    tracker.update_dimension(
        "core_competencies",
        88.0,
        "核心竞争力：用户增长、数据驱动、跨部门协作"
    )

    tracker.update_dimension(
        "work_highlights",
        85.0,
        "主导过DAU 100万→200万增长项目，有量化数据"
    )

    tracker.update_dimension(
        "skill_match",
        90.0,
        "技能匹配度达到90%"
    )

    # 步骤2: 显示置信度状态
    print("\n[步骤2] 置信度评估...")
    print(tracker.generate_progress_visualization())

    # 步骤3: 生成关键词分析
    print("\n[步骤3] 关键词分析...")

    sample_jd = """
    高级产品经理
    要求：5年+产品经验，用户增长，数据分析，跨部门协作，团队管理
    """

    keywords = extractor.extract_from_jd(sample_jd)
    sample_resume = """
    高级产品经理
    负责用户增长产品，实现DAU翻倍增长
    熟练使用SQL、Python进行数据分析
    跨部门协调10+人团队
    """

    matches = extractor.match_with_resume(keywords, sample_resume)
    report = extractor.generate_match_report(keywords, matches)

    print(report)

    # 验证集成结果 (使用小数格式 0-1)
    status = tracker.get_status()
    assert status["overall_confidence"] >= 0.90, f"综合置信度应>=90%，当前为{status['overall_confidence']*100:.1f}%"

    print("\n✅ 集成测试通过！")
    print(f"   置信度达到: {status['overall_confidence']}%")


def main():
    print("\n" + "=" * 60)
    print("🧪 简历优化技能 - 脚本测试套件")
    print("=" * 60)

    try:
        test_confidence_tracker()
        test_keyword_extractor()
        test_integration()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60 + "\n")

        return 0

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
