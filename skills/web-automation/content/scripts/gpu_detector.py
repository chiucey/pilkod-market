#!/usr/bin/env python3
"""
GPU 检测工具脚本
自动检测系统 GPU 状态，提供智能的 GPU 使用建议

核心功能：
1. 检测 GPU 是否可用
2. 检测 GPU 数量和类型
3. 测试 GPU 性能
4. 提供使用建议

版本：1.0.0
"""

import sys
import json
from typing import Dict, Any, Optional


def detect_paddle_gpu() -> Dict[str, Any]:
    """
    检测 PaddlePaddle GPU 支持

    返回：
        GPU 检测结果
    """
    result = {
        "framework": "paddlepaddle",
        "gpu_available": False,
        "gpu_count": 0,
        "gpu_devices": [],
        "error": None
    }

    try:
        import paddle
    except ImportError:
        result["error"] = "PaddlePaddle 未安装"
        return result

    try:
        # 检测 GPU 可用性
        result["gpu_available"] = paddle.is_compiled_with_cuda()

        if result["gpu_available"]:
            # 获取 GPU 数量
            result["gpu_count"] = paddle.device.cuda.device_count()

            # 获取 GPU 设备信息
            for i in range(result["gpu_count"]):
                try:
                    device = paddle.CUDAPlace(i)
                    result["gpu_devices"].append({
                        "id": i,
                        "name": f"cuda:{i}",
                        "available": True
                    })
                except Exception as e:
                    result["gpu_devices"].append({
                        "id": i,
                        "name": f"cuda:{i}",
                        "available": False,
                        "error": str(e)
                    })
    except Exception as e:
        result["error"] = f"GPU 检测失败: {str(e)}"

    return result


def detect_pytorch_gpu() -> Dict[str, Any]:
    """
    检测 PyTorch GPU 支持

    返回：
        GPU 检测结果
    """
    result = {
        "framework": "pytorch",
        "gpu_available": False,
        "gpu_count": 0,
        "gpu_devices": [],
        "error": None
    }

    try:
        import torch
    except ImportError:
        result["error"] = "PyTorch 未安装"
        return result

    try:
        # 检测 CUDA 可用性
        result["gpu_available"] = torch.cuda.is_available()

        if result["gpu_available"]:
            # 获取 GPU 数量
            result["gpu_count"] = torch.cuda.device_count()

            # 获取 GPU 设备信息
            for i in range(result["gpu_count"]):
                try:
                    device_name = torch.cuda.get_device_name(i)
                    device_capability = torch.cuda.get_device_capability(i)
                    device_memory = torch.cuda.get_device_properties(i).total_memory

                    result["gpu_devices"].append({
                        "id": i,
                        "name": device_name,
                        "capability": device_capability,
                        "memory_mb": device_memory // (1024 * 1024),
                        "available": True
                    })
                except Exception as e:
                    result["gpu_devices"].append({
                        "id": i,
                        "name": f"cuda:{i}",
                        "available": False,
                        "error": str(e)
                    })
    except Exception as e:
        result["error"] = f"GPU 检测失败: {str(e)}"

    return result


def test_gpu_performance(framework: str = "paddlepaddle") -> Dict[str, Any]:
    """
    测试 GPU 性能

    参数：
        framework: 框架类型（paddlepaddle 或 pytorch）

    返回：
        性能测试结果
    """
    result = {
        "framework": framework,
        "test_passed": False,
        "cpu_time_ms": None,
        "gpu_time_ms": None,
        "speedup": None,
        "error": None
    }

    try:
        import time
        import numpy as np

        # 创建测试数据
        size = 1000
        a = np.random.rand(size, size).astype('float32')
        b = np.random.rand(size, size).astype('float32')

        # CPU 测试
        if framework == "paddlepaddle":
            import paddle
            a_cpu = paddle.to_tensor(a, place=paddle.CPUPlace())
            b_cpu = paddle.to_tensor(b, place=paddle.CPUPlace())

            start_time = time.time()
            for _ in range(10):
                c_cpu = paddle.matmul(a_cpu, b_cpu)
            result["cpu_time_ms"] = (time.time() - start_time) * 100

            # GPU 测试
            if paddle.is_compiled_with_cuda():
                a_gpu = paddle.to_tensor(a, place=paddle.CUDAPlace(0))
                b_gpu = paddle.to_tensor(b, place=paddle.CUDAPlace(0))

                start_time = time.time()
                for _ in range(10):
                    c_gpu = paddle.matmul(a_gpu, b_gpu)
                result["gpu_time_ms"] = (time.time() - start_time) * 100

                result["speedup"] = result["cpu_time_ms"] / result["gpu_time_ms"]
                result["test_passed"] = True

        elif framework == "pytorch":
            import torch

            a_cpu = torch.from_numpy(a)
            b_cpu = torch.from_numpy(b)

            start_time = time.time()
            for _ in range(10):
                c_cpu = torch.matmul(a_cpu, b_cpu)
            result["cpu_time_ms"] = (time.time() - start_time) * 100

            # GPU 测试
            if torch.cuda.is_available():
                a_gpu = a_cpu.cuda()
                b_gpu = b_cpu.cuda()

                start_time = time.time()
                for _ in range(10):
                    c_gpu = torch.matmul(a_gpu, b_gpu)
                result["gpu_time_ms"] = (time.time() - start_time) * 100

                result["speedup"] = result["cpu_time_ms"] / result["gpu_time_ms"]
                result["test_passed"] = True

    except Exception as e:
        result["error"] = f"性能测试失败: {str(e)}"

    return result


def get_recommendation() -> Dict[str, Any]:
    """
    获取 GPU 使用建议

    返回：
        使用建议
    """
    recommendation = {
        "use_gpu": False,
        "gpu_framework": None,
        "reason": "",
        "fallback_to_cpu": True
    }

    # 检测 PaddlePaddle GPU
    paddle_result = detect_paddle_gpu()
    if paddle_result["gpu_available"] and paddle_result["gpu_count"] > 0:
        recommendation["use_gpu"] = True
        recommendation["gpu_framework"] = "paddlepaddle"
        recommendation["reason"] = f"检测到 {paddle_result['gpu_count']} 个 PaddlePaddle GPU 设备"
        return recommendation

    # 检测 PyTorch GPU
    pytorch_result = detect_pytorch_gpu()
    if pytorch_result["gpu_available"] and pytorch_result["gpu_count"] > 0:
        recommendation["use_gpu"] = True
        recommendation["gpu_framework"] = "pytorch"
        recommendation["reason"] = f"检测到 {pytorch_result['gpu_count']} 个 PyTorch GPU 设备"
        return recommendation

    # 无 GPU
    recommendation["reason"] = "未检测到 GPU，使用 CPU 模式"
    return recommendation


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="GPU 检测工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 检测 GPU：
  python gpu_detector.py

2. 检测 PaddlePaddle GPU：
  python gpu_detector.py --framework paddlepaddle

3. 检测 PyTorch GPU：
  python gpu_detector.py --framework pytorch

4. 测试 GPU 性能：
  python gpu_detector.py --test-performance

5. 获取使用建议：
  python gpu_detector.py --recommendation
        """
    )

    parser.add_argument(
        "--framework",
        choices=["paddlepaddle", "pytorch", "all"],
        default="all",
        help="框架类型"
    )

    parser.add_argument(
        "--test-performance",
        action="store_true",
        help="测试 GPU 性能"
    )

    parser.add_argument(
        "--recommendation",
        action="store_true",
        help="获取使用建议"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 格式输出"
    )

    args = parser.parse_args()

    results = {}

    # 检测 GPU
    if args.framework in ["paddlepaddle", "all"]:
        results["paddlepaddle"] = detect_paddle_gpu()

    if args.framework in ["pytorch", "all"]:
        results["pytorch"] = detect_pytorch_gpu()

    # 性能测试
    if args.test_performance:
        if args.framework in ["paddlepaddle", "all"]:
            results["paddlepaddle_performance"] = test_gpu_performance("paddlepaddle")

        if args.framework in ["pytorch", "all"]:
            results["pytorch_performance"] = test_gpu_performance("pytorch")

    # 使用建议
    if args.recommendation:
        results["recommendation"] = get_recommendation()

    # 输出结果
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # 格式化输出
        print("=" * 60)
        print("GPU 检测结果")
        print("=" * 60)

        for framework, result in results.items():
            if "performance" in framework or framework == "recommendation":
                continue

            framework_name = framework.upper()
            print(f"\n{framework_name}:")
            print(f"  GPU 可用: {result['gpu_available']}")

            if result["gpu_available"]:
                print(f"  GPU 数量: {result['gpu_count']}")
                print(f"  GPU 设备:")
                for device in result.get("gpu_devices", []):
                    if device["available"]:
                        print(f"    - {device['name']}")
                    else:
                        print(f"    - {device['name']} (不可用)")
            elif result["error"]:
                print(f"  错误: {result['error']}")

        # 性能测试结果
        if args.test_performance:
            print("\n" + "=" * 60)
            print("性能测试结果")
            print("=" * 60)

            for key, result in results.items():
                if "performance" in key:
                    framework = key.replace("_performance", "").upper()
                    print(f"\n{framework}:")
                    if result["test_passed"]:
                        print(f"  CPU 时间: {result['cpu_time_ms']:.2f} ms")
                        print(f"  GPU 时间: {result['gpu_time_ms']:.2f} ms")
                        print(f"  加速比: {result['speedup']:.2f}x")
                    else:
                        print(f"  测试失败: {result.get('error', '未知错误')}")

        # 使用建议
        if args.recommendation:
            print("\n" + "=" * 60)
            print("使用建议")
            print("=" * 60)
            rec = results["recommendation"]
            print(f"\n使用 GPU: {rec['use_gpu']}")
            print(f"GPU 框架: {rec.get('gpu_framework', '无')}")
            print(f"原因: {rec['reason']}")
            print(f"回退到 CPU: {rec['fallback_to_cpu']}")


if __name__ == "__main__":
    main()
