#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
协作学习协议使用示例

作者: MiniMax Agent
版本: 1.0.0
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collaborative_protocol import (
    CollaborativeProtocol,
    ExperienceRecorder,
    ExperiencePublisher,
    ExperienceRetriever,
    ExperienceIntegrator,
    Experience,
    ExperienceContent,
    ExperienceContext,
    ExperienceMetadata,
    ExperienceType,
    PrivacyLevel,
    create_protocol
)


def example_basic_recording():
    """基础经验记录示例"""
    print("=" * 60)
    print("基础经验记录示例")
    print("=" * 60)

    # 创建协议实例
    protocol = create_protocol(
        instance_id="example-instance-001",
        knowledge_base_path="data/knowledge_base"
    )

    # 使用记录器
    recorder = protocol.recorder

    # 开始记录会话
    with recorder.session(task_type="code_optimization") as session:
        # 记录执行步骤
        session.record_step(
            step_name="analysis",
            input_data={"code": "def foo(): pass"},
            output_data={"analysis": "Simple function, optimization not needed"},
            success=True,
            metadata={"important": True}
        )

        session.record_step(
            step_name="benchmark",
            input_data={"iterations": 1000},
            output_data={"time_ms": 5.2, "memory_mb": 10},
            success=True
        )

        # 完成记录
        session.finalize(
            success=True,
            metrics={
                "execution_time_ms": 5200,
                "memory_usage_mb": 10,
                "optimization_gain": 0.0
            }
        )

    # 从记录中提取经验
    experience = session.extract_experience(
        type=ExperienceType.LESSON_LEARNED.value,
        title="代码优化评估技巧",
        description="记录了如何评估代码是否需要优化的方法"
    )

    print(f"\n提取的经验:")
    print(f"  ID: {experience.experience_id}")
    print(f"  标题: {experience.title}")
    print(f"  类型: {experience.experience_type}")
    print(f"  摘要: {experience.content.summary}")

    return experience


def example_publishing_experience(experience: Experience):
    """发布经验示例"""
    print("\n" + "=" * 60)
    print("发布经验示例")
    print("=" * 60)

    protocol = create_protocol(
        instance_id="example-instance-001",
        knowledge_base_path="data/knowledge_base"
    )

    publisher = protocol.publisher

    # 发布经验
    result = publisher.publish(
        experience=experience,
        privacy_level=PrivacyLevel.PUBLIC.value,
        tags=["optimization", "code-review"]
    )

    print(f"\n发布结果:")
    print(f"  状态: {result['status']}")
    print(f"  经验ID: {result.get('experience_id', 'N/A')}")
    print(f"  隐私级别: {result.get('privacy_level', 'N/A')}")

    if result["status"] == "failed":
        print(f"  错误: {result.get('errors', [])}")

    return result


def example_searching_experiences():
    """搜索经验示例"""
    print("\n" + "=" * 60)
    print("搜索经验示例")
    print("=" * 60)

    protocol = create_protocol(
        instance_id="example-instance-001",
        knowledge_base_path="data/knowledge_base"
    )

    retriever = protocol.retriever

    # 搜索相关经验
    results = retriever.search(
        query="优化",
        filters={
            "type": [ExperienceType.LESSON_LEARNED.value, ExperienceType.BEST_PRACTICE.value],
            "privacy_level": PrivacyLevel.PUBLIC.value
        },
        limit=5
    )

    print(f"\n搜索到 {len(results)} 条相关经验:")

    for i, result in enumerate(results, 1):
        exp = result["experience"]
        print(f"\n{i}. {exp.title}")
        print(f"   类型: {exp.experience_type}")
        print(f"   相关性: {result['relevance_score']:.2f}")
        print(f"   置信度: {exp.metadata.confidence:.2f}")
        print(f"   摘要: {exp.content.summary[:50]}...")

    return results


def example_creating_skill_template():
    """创建技能模板示例"""
    print("\n" + "=" * 60)
    print("创建技能模板示例")
    print("=" * 60)

    # 创建技能模板经验
    template = Experience(
        experience_type=ExperienceType.SKILL_TEMPLATE.value,
        title="代码审查最佳实践",
        description="分享代码审查过程中发现的问题和解决方案",
        content=ExperienceContent(
            summary="总结了代码审查中常见的问题类型和解决方法",
            steps=[
                "1. 检查代码结构和命名规范",
                "2. 验证边界条件和错误处理",
                "3. 评估性能和资源使用",
                "4. 检查安全漏洞和潜在风险",
                "5. 验证测试覆盖率和代码质量"
            ],
            examples=[
                {
                    "scenario": "发现空指针风险",
                    "problem": "变量可能为 None",
                    "solution": "添加 null 检查或使用 Optional"
                }
            ],
            key_points=[
                "审查时注意代码的可读性和可维护性",
                "不要忽视边界条件的处理",
                "安全问题需要优先处理"
            ]
        ),
        context=ExperienceContext(
            applicability=["代码审查", "代码质量检查"],
            prerequisites=["了解基本的编程规范"],
            limitations=["不同语言可能有不同的最佳实践"]
        ),
        metadata=ExperienceMetadata(
            source_instance="example-instance-001",
            confidence=0.85,
            times_validated=5,
            tags=["code-review", "best-practice", "quality"]
        ),
        privacy_level=PrivacyLevel.PUBLIC.value,
        status="verified"
    )

    print(f"\n创建的技能模板:")
    print(f"  标题: {template.title}")
    print(f"  类型: {template.experience_type}")
    print(f"  步骤数: {len(template.content.steps)}")
    print(f"  置信度: {template.metadata.confidence}")

    return template


def example_creating_avoidance_guide():
    """创建避坑指南示例"""
    print("\n" + "=" * 60)
    print("创建避坑指南示例")
    print("=" * 60)

    guide = Experience(
        experience_type=ExperienceType.AVOIDANCE_GUIDE.value,
        title="避免在循环中进行字符串拼接",
        description="记录了在大数据量场景下字符串拼接的性能问题",
        content=ExperienceContent(
            summary="使用 + 运算符进行字符串拼接在大循环中会导致 O(n²) 的时间复杂度",
            steps=[
                "问题：每次拼接都会创建新的字符串对象",
                "影响：数据量大时性能急剧下降",
                "解决方案1：使用 list + join",
                "解决方案2：使用 StringBuilder",
                "解决方案3：考虑使用字符串模板"
            ],
            examples=[
                {
                    "wrong": "for i in range(10000): s += str(i)",
                    "right": "parts = [str(i) for i in range(10000)]; s = ''.join(parts)"
                }
            ],
            key_points=[
                "循环中的字符串拼接要谨慎",
                "优先使用 join 方法",
                "大字符串操作要注意内存使用"
            ]
        ),
        context=ExperienceContext(
            applicability=["大数据处理", "性能优化"],
            prerequisites=["了解时间复杂度概念"],
            limitations=[]
        ),
        metadata=ExperienceMetadata(
            source_instance="example-instance-001",
            confidence=0.95,
            times_validated=10,
            tags=["performance", "string", "optimization"]
        ),
        privacy_level=PrivacyLevel.PUBLIC.value,
        status="verified"
    )

    print(f"\n创建的避坑指南:")
    print(f"  标题: {guide.title}")
    print(f"  类型: {guide.experience_type}")
    print(f"  摘要: {guide.content.summary}")
    print(f"  置信度: {guide.metadata.confidence}")

    return guide


def example_integrating_experiences():
    """整合经验示例"""
    print("\n" + "=" * 60)
    print("整合经验示例")
    print("=" * 60)

    protocol = create_protocol(
        instance_id="example-instance-001",
        knowledge_base_path="data/knowledge_base"
    )

    integrator = protocol.integrator

    # 先发布一些经验
    experiences = []

    exp1 = Experience(
        experience_type=ExperienceType.BEST_PRACTICE.value,
        title="使用类型提示提高代码质量",
        description="Python 类型提示可以提高代码可读性和可维护性"
    )
    experiences.append(exp1)

    exp2 = Experience(
        experience_type=ExperienceType.BEST_PRACTICE.value,
        title="编写清晰的文档字符串",
        description="好的文档字符串帮助其他开发者理解代码"
    )
    experiences.append(exp2)

    exp3 = Experience(
        experience_type=ExperienceType.LESSON_LEARNED.value,
        title="测试覆盖率的重要性",
        description="低测试覆盖率导致的问题"
    )
    experiences.append(exp3)

    # 发布这些经验
    publisher = protocol.publisher
    for exp in experiences:
        publisher.publish(exp, privacy_level=PrivacyLevel.PUBLIC.value)

    # 整合所有经验
    all_experiences = []
    for exp_id in os.listdir(protocol.knowledge_base_path):
        if exp_id.endswith('.json') and not exp_id.startswith('.'):
            filepath = os.path.join(protocol.knowledge_base_path, exp_id)
            with open(filepath, "r", encoding="utf-8") as f:
                exp_dict = json.load(f)
            all_experiences.append(Experience.from_dict(exp_dict))

    result = integrator.integrate(
        experiences=all_experiences,
        strategy="merge_and_prioritize",
        conflict_resolution="keep_both"
    )

    print(f"\n整合结果:")
    print(f"  状态: {result['status']}")
    print(f"  经验数: {result['experiences_count']}")
    print(f"  冲突数: {result['conflicts_count']}")

    graph = result['knowledge_graph']
    print(f"\n知识图谱:")
    print(f"  节点数: {len(graph['nodes'])}")
    print(f"  边数: {len(graph['edges'])}")
    print(f"  类型分布: {dict(graph['metadata']['types'])}")


def example_sensitive_info_detection():
    """敏感信息检测示例"""
    print("\n" + "=" * 60)
    print("敏感信息检测示例")
    print("=" * 60)

    from collaborative_protocol import SensitiveInfoDetector

    test_texts = [
        "请联系 support@example.com 获取帮助",
        "我的API密钥是 sk-abc123def456xyz789",
        "密码是 my_secret_password123",
        "调用方需要在 Header 中传递 Bearer eyJhbGciOiJIUzI1NiIs..."
    ]

    print("\n敏感信息检测结果:")

    for text in test_texts:
        findings = SensitiveInfoDetector.detect(text)
        sanitized = SensitiveInfoDetector.sanitize(text)

        print(f"\n原文: {text[:50]}...")
        print(f"检测到: {[f['type'] for f in findings]}")
        print(f"脱敏后: {sanitized[:50]}...")


import json


def main():
    """主函数"""
    print("\n协作学习协议使用示例")
    print("=" * 60)

    try:
        # 基础示例
        experience = example_basic_recording()
        example_publishing_experience(experience)

        # 创建模板和指南
        template = example_creating_skill_template()
        guide = example_creating_avoidance_guide()

        # 发布模板和指南
        protocol = create_protocol(
            instance_id="example-instance-001",
            knowledge_base_path="data/knowledge_base"
        )
        protocol.publisher.publish(template, privacy_level=PrivacyLevel.PUBLIC.value)
        protocol.publisher.publish(guide, privacy_level=PrivacyLevel.PUBLIC.value)

        # 搜索
        example_searching_experiences()

        # 整合
        example_integrating_experiences()

        # 敏感信息检测
        example_sensitive_info_detection()

        # 获取统计
        stats = protocol.get_statistics()
        print("\n" + "=" * 60)
        print("知识库统计")
        print("=" * 60)
        print(f"总经验数: {stats['total_experiences']}")
        print(f"按类型分布: {dict(stats['by_type'])}")
        print(f"按隐私级别分布: {dict(stats['by_privacy'])}")
        print(f"平均置信度: {stats['average_confidence']:.2f}")

        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
