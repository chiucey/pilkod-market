#!/usr/bin/env python3
"""
Finance Video Editor - 使用示例
Examples for Finance Video Editor Skill
"""

import asyncio
import json
from workflow import (
    main,
    main_async,
    run,
    FinanceVideoWorkflow,
    WorkflowConfig,
    FinanceVideoEditorSDK
)


# ============================================================================
# 示例 1: 基础使用
# ============================================================================

def basic_usage():
    """基础使用示例"""
    print("\n" + "=" * 50)
    print("示例 1: 基础使用")
    print("=" * 50)

    result = main("/path/to/finance_news.mp4")

    print(f"状态: {result['status']}")
    print(f"输出视频: {result['video_url']}")
    print(f"处理片段数: {result['segments_count']}")
    print(f"耗时: {result['processing_time']}秒")


# ============================================================================
# 示例 2: 自定义配置
# ============================================================================

def custom_config_usage():
    """自定义配置使用示例"""
    print("\n" + "=" * 50)
    print("示例 2: 自定义配置")
    print("=" * 50)

    config = {
        'video_duration': 6,        # 每个片段 6 秒
        'video_resolution': '4k',    # 4K 分辨率
        'max_parallel_generations': 5,  # 并行 5 个
        'enable_subtitle': True,      # 启用字幕
        'enable_finance_filter': True  # 启用财经滤镜
    }

    result = main("/path/to/market_analysis.mp4", config)

    print(json.dumps(result, indent=2, ensure_ascii=False))


# ============================================================================
# 示例 3: 使用 Workflow 类
# ============================================================================

def workflow_class_usage():
    """使用 Workflow 类示例"""
    print("\n" + "=" * 50)
    print("示例 3: 使用 Workflow 类")
    print("=" * 50)

    # 创建自定义配置
    config = WorkflowConfig(
        video_duration=8,
        video_resolution="1080p",
        max_parallel_generations=3,
        max_retries=5
    )

    # 创建工作流实例
    workflow = FinanceVideoWorkflow(config=config)

    # 设置进度回调
    def progress_callback(stage: str, current: int, total: int):
        print(f"[{current}/{total}] {stage}")

    workflow.set_progress_callback(progress_callback)

    # 执行工作流
    result = workflow.run("/path/to/investment_tutorial.mp4")

    print("\n最终结果:")
    print(f"状态: {result['status']}")
    print(f"视频地址: {result['video_url']}")


# ============================================================================
# 示例 4: 异步使用
# ============================================================================

async def async_usage():
    """异步使用示例"""
    print("\n" + "=" * 50)
    print("示例 4: 异步使用")
    print("=" * 50)

    result = await main_async("/path/to/stock_review.mp4")

    print(json.dumps(result, indent=2, ensure_ascii=False))


# ============================================================================
# 示例 5: SDK 封装使用
# ============================================================================

def sdk_usage():
    """SDK 封装使用示例"""
    print("\n" + "=" * 50)
    print("示例 5: SDK 封装使用")
    print("=" * 50)

    # 创建 SDK 实例
    sdk_instance = FinanceVideoEditorSDK({
        'video_duration': 5,
        'max_parallel_generations': 4
    })

    # 设置进度回调
    sdk_instance.set_progress_callback(
        lambda stage, current, total: print(f"进度: {stage} ({current}/{total})")
    )

    # 运行
    result = sdk_instance.run("/path/to/economic_report.mp4")

    print("\nSDK 执行结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ============================================================================
# 示例 6: 批量处理
# ============================================================================

def batch_processing():
    """批量处理示例"""
    print("\n" + "=" * 50)
    print("示例 6: 批量处理多个视频")
    print("=" * 50)

    video_list = [
        "/path/to/video1.mp4",
        "/path/to/video2.mp4",
        "/path/to/video3.mp4"
    ]

    results = []
    for video_path in video_list:
        print(f"\n处理: {video_path}")
        result = main(video_path)
        results.append(result)

    # 汇总结果
    print("\n" + "=" * 50)
    print("批量处理汇总")
    print("=" * 50)

    success_count = sum(1 for r in results if r['status'] == 'Success')
    total_segments = sum(r['segments_count'] for r in results)
    total_time = sum(r['processing_time'] for r in results)

    print(f"成功: {success_count}/{len(video_list)}")
    print(f"总片段数: {total_segments}")
    print(f"总耗时: {total_time:.2f}秒")


# ============================================================================
# 示例 7: 便捷函数使用
# ============================================================================

def convenience_function():
    """便捷函数使用示例"""
    print("\n" + "=" * 50)
    print("示例 7: 便捷函数")
    print("=" * 50)

    # 使用关键字参数
    result = run(
        "/path/to/finance_interview.mp4",
        video_duration=6,
        video_resolution="4k",
        max_parallel_generations=5,
        enable_subtitle=True
    )

    print(f"输出视频: {result['video_url']}")


# ============================================================================
# 示例 8: 错误处理
# ============================================================================

def error_handling():
    """错误处理示例"""
    print("\n" + "=" * 50)
    print("示例 8: 错误处理")
    print("=" * 50)

    try:
        result = main("/path/to/nonexistent_video.mp4")
        if result['status'] == 'Failed':
            print(f"处理失败!")
            print(f"错误信息: {result.get('errors', [])}")
    except Exception as e:
        print(f"异常: {e}")


# ============================================================================
# 主函数
# ============================================================================

def main_examples():
    """运行所有示例"""
    print("=" * 60)
    print("  Finance Video Editor - 使用示例")
    print("=" * 60)

    # 运行基础示例
    basic_usage()
    custom_config_usage()
    workflow_class_usage()
    convenience_function()
    error_handling()
    sdk_usage()
    batch_processing()

    print("\n" + "=" * 60)
    print("  所有示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    # 运行所有示例
    main_examples()

    # 或者单独运行异步示例
    # asyncio.run(async_usage())