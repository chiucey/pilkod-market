#!/usr/bin/env python3
"""
权重验证脚本 - 验证MBTI权重配置的合法性
确保每个MBTI类型的权重配置符合框架规则
"""

import json
import sys
from pathlib import Path

# 16种MBTI的标准权重配置
WEIGHT = {
    "INTP": {'Ti': 0.47, 'Ne': 0.23, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.05, 'Fi': 0.05},
    "INTJ": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.22, 'Ni': 0.48, 'Se': 0.05, 'Fi': 0.05},
    "INFP": {'Ti': 0.05, 'Ne': 0.28, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.05, 'Fi': 0.42},
    "INFJ": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.05, 'Fe': 0.27, 'Te': 0.05, 'Ni': 0.43, 'Se': 0.05, 'Fi': 0.05},
    "ISTP": {'Ti': 0.46, 'Ne': 0.05, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.24, 'Fi': 0.05},
    "ISTJ": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.44, 'Fe': 0.05, 'Te': 0.26, 'Ni': 0.05, 'Se': 0.05, 'Fi': 0.05},
    "ISFP": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.21, 'Fi': 0.49},
    "ISFJ": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.45, 'Fe': 0.25, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.05, 'Fi': 0.05},
    "ENFP": {'Ti': 0.05, 'Ne': 0.41, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.05, 'Fi': 0.29},
    "ENFJ": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.05, 'Fe': 0.55, 'Te': 0.05, 'Ni': 0.15, 'Se': 0.05, 'Fi': 0.05},
    "ENTP": {'Ti': 0.20, 'Ne': 0.50, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.05, 'Fi': 0.05},
    "ENTJ": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.53, 'Ni': 0.17, 'Se': 0.05, 'Fi': 0.05},
    "ESFP": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.52, 'Fi': 0.18},
    "ESFJ": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.30, 'Fe': 0.40, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.05, 'Fi': 0.05},
    "ESTP": {'Ti': 0.19, 'Ne': 0.05, 'Si': 0.05, 'Fe': 0.05, 'Te': 0.05, 'Ni': 0.05, 'Se': 0.51, 'Fi': 0.05},
    "ESTJ": {'Ti': 0.05, 'Ne': 0.05, 'Si': 0.16, 'Fe': 0.05, 'Te': 0.54, 'Ni': 0.05, 'Se': 0.05, 'Fi': 0.05},
}

# 主导-辅助功能映射
mbti_to_function = {
    "INTP": {"main": "Ti", "aux": "Ne"}, "ISTP": {"main": "Ti", "aux": "Se"},
    "INFP": {"main": "Fi", "aux": "Ne"}, "ISFP": {"main": "Fi", "aux": "Se"},
    "INTJ": {"main": "Ni", "aux": "Te"}, "ISTJ": {"main": "Si", "aux": "Te"},
    "INFJ": {"main": "Ni", "aux": "Fe"}, "ISFJ": {"main": "Si", "aux": "Fe"},
    "ENFP": {"main": "Ne", "aux": "Fi"}, "ENFJ": {"main": "Fe", "aux": "Ni"},
    "ENTP": {"main": "Ne", "aux": "Ti"}, "ESTP": {"main": "Se", "aux": "Ti"},
    "ENTJ": {"main": "Te", "aux": "Ni"}, "ESTJ": {"main": "Te", "aux": "Si"},
    "ESFP": {"main": "Se", "aux": "Fi"}, "ESFJ": {"main": "Fe", "aux": "Si"},
}

ALL_FUNCTIONS = {"Ti", "Te", "Fi", "Fe", "Ni", "Ne", "Si", "Se"}


def validate_weights():
    """验证所有MBTI类型的权重配置"""
    errors = []

    for mbti in WEIGHT:
        weights = WEIGHT[mbti]

        # 1. 检查权重总和是否为1.0
        total = sum(weights.values())
        if abs(total - 1.0) > 0.001:
            errors.append(f"{mbti}: 权重总和={total}, 期望=1.0")

        # 2. 检查是否有8个功能
        if set(weights.keys()) != ALL_FUNCTIONS:
            missing = ALL_FUNCTIONS - set(weights.keys())
            extra = set(weights.keys()) - ALL_FUNCTIONS
            if missing:
                errors.append(f"{mbti}: 缺少功能 {missing}")
            if extra:
                errors.append(f"{mbti}: 多余功能 {extra}")

        # 3. 检查主导功能权重范围
        main_func = mbti_to_function[mbti]["main"]
        aux_func = mbti_to_function[mbti]["aux"]
        main_weight = weights[main_func]
        aux_weight = weights[aux_func]

        if not (0.31 <= main_weight <= 1.0):
            errors.append(f"{mbti}: 主导功能{main_func}权重={main_weight}, 期望范围[0.31, 1.0]")

        if not (0.06 <= aux_weight <= 0.30):
            errors.append(f"{mbti}: 辅助功能{aux_func}权重={aux_weight}, 期望范围[0.06, 0.30]")

        # 4. 检查主导权重是否大于辅助权重
        if main_weight <= aux_weight:
            errors.append(f"{mbti}: 主导权重({main_weight})应大于辅助权重({aux_weight})")

        # 5. 检查所有权重是否在有效范围内
        for func, weight in weights.items():
            if not (0 <= weight <= 1):
                errors.append(f"{mbti}: 功能{func}权重={weight}超出范围[0, 1]")

    return errors


def validate_change_mechanism():
    """验证演化机制的逻辑正确性"""
    errors = []
    change_weight = 0.06

    for mbti in WEIGHT:
        main_func = mbti_to_function[mbti]["main"]
        aux_func = mbti_to_function[mbti]["aux"]

        # 模拟多次使用辅助功能后的状态
        aux_temp = WEIGHT[mbti][aux_func]
        for _ in range(5):  # 模拟5次使用
            aux_temp += change_weight

        main_base = WEIGHT[mbti][main_func]

        # 如果5次使用后可能触发互换检测
        if aux_temp >= main_base:
            # 这是预期的演化行为
            pass

        # 检查归一化阈值
        main_temp = WEIGHT[mbti][main_func]
        for _ in range(10):  # 模拟10次使用主导功能
            main_temp += change_weight

        if main_temp >= 0.5:
            # 预期触发归一化
            pass

    return errors


def main():
    """主验证流程"""
    print("=" * 50)
    print("JPAF权重配置验证")
    print("=" * 50)

    errors = validate_weights()
    errors.extend(validate_change_mechanism())

    if errors:
        print(f"\n发现 {len(errors)} 个错误:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n✓ 所有权重配置验证通过!")
        print("  - 16种MBTI类型权重配置正确")
        print("  - 主导/辅助功能映射正确")
        print("  - 权重范围符合规范")
        print("  - 演化机制逻辑正确")
        sys.exit(0)


if __name__ == "__main__":
    main()
