#!/usr/bin/env python3
"""
快速验证脚本 - 河洛同轴双螺旋干涉元模型
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from heluo_model import (
    HeLuoMetaModel, HeluoKernel, HeluoShell,
    HeluoInterferometer, HeluoObserver, SixDimensionState
)
import numpy as np


def test_basic_functionality():
    """测试基础功能"""
    print("测试1: 基础模型初始化...")

    model = HeLuoMetaModel()

    # 验证内核可加载数据
    model.kernel.unlock()
    model.kernel.load_static_data({"test": 1.0, "value": 0.5})
    model.kernel.lock()

    # 验证外壳可添加数据
    for i in range(10):
        model.shell.append_data(np.random.random())

    print("  ✓ 基础初始化通过")
    return True


def test_interference_calculation():
    """测试干涉计算"""
    print("测试2: 干涉计算...")

    model = HeLuoMetaModel()
    model.kernel.unlock()
    model.kernel.load_static_data({
        "a": 1.0, "b": 0.8, "c": 0.6,
        "d": 0.4, "e": 0.2, "f": 0.1
    })
    model.kernel.lock()

    # 喂入市场数据
    for i in range(50):
        model.feed_market_data(np.sin(i * 0.2) + 0.5)

    # 执行干涉
    result = model.run(10.0)

    assert "six_dimension" in result
    assert "hexagram_code" in result
    assert 1 <= result["hexagram_code"] <= 64

    print(f"  ✓ 干涉计算通过 - 卦象: {result['hexagram_name']}")
    return True


def test_six_dimension_state():
    """测试六维状态"""
    print("测试3: 六维状态映射...")

    state = SixDimensionState(
        dynamic=80.0, static=60.0, transform=50.0,
        harmony=70.0, clash=30.0, danger=20.0
    )

    arr = state.to_array()
    assert arr.shape == (6,)
    assert state.to_hexagram_code() in range(1, 65)

    print("  ✓ 六维状态映射通过")
    return True


def test_auto_calibrator():
    """测试自适应校准器"""
    print("测试4: 自适应校准...")

    model = HeLuoMetaModel()
    original_rate = model.shell.spiral_rate

    # 模拟校准
    new_rate = model.auto_calibrator.calibrate(
        predicted_phase=0.8,
        actual_outcome=0.6
    )

    assert new_rate != original_rate  # 应该有调整
    stats = model.auto_calibrator.get_calibration_stats()
    assert "current" in stats

    print(f"  ✓ 自适应校准通过 - 新螺旋率: {new_rate:.6f}")
    return True


def test_phase_variation():
    """测试相位变化检测"""
    print("测试5: 相位变化检测...")

    model = HeLuoMetaModel()
    model.kernel.unlock()
    model.kernel.load_static_data({"x": 1.0, "y": 1.0, "z": 1.0, "w": 1.0, "u": 1.0, "v": 1.0})
    model.kernel.lock()

    # 注入不同的市场状态
    results = []

    # 稳定市场
    for i in range(20):
        model.feed_market_data(0.5 + np.random.normal(0, 0.05))
    results.append(model.run(1.0))

    # 动荡市场
    for i in range(20):
        model.feed_market_data(np.random.random() * 2 - 1)
    results.append(model.run(2.0))

    # 验证结果有差异
    assert results[0]["six_dimension"]["danger"] != results[1]["six_dimension"]["danger"]

    print("  ✓ 相位变化检测通过")
    return True


def main():
    """运行所有验证"""
    print("=" * 50)
    print("河洛同轴双螺旋干涉元模型 - 验证测试")
    print("=" * 50)
    print()

    tests = [
        test_basic_functionality,
        test_interference_calculation,
        test_six_dimension_state,
        test_auto_calibrator,
        test_phase_variation,
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
            print(f"  ✗ 测试失败: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"验证结果: {passed} 通过, {failed} 失败")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
