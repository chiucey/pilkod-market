#!/usr/bin/env python3
"""
Brand Commercial Negotiation - 加密加载器
Version: 1.0.0
Author: MiniMax Agent

此文件为加密加载器，用于在运行时解密并执行加密的核心代码。
用户无法直接查看或修改源代码。
"""

import base64
import os
import sys
from types import ModuleType

# 尝试多个可能的路径
POSSIBLE_PATHS = [
    os.path.join(os.path.dirname(__file__), 'brand_negotiation_core.py.enc'),
    os.path.join(os.path.dirname(__file__), 'scripts', 'brand_negotiation_core.py.enc'),
]

def _load_encoded_module():
    """加载并解密编码的模块"""
    encoded_code = None

    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                encoded_code = f.read()
            break

    if encoded_code is None:
        # 尝试从字符串常量加载（打包时内嵌）
        raise ImportError("无法找到加密模块")

    # Base64解码
    decoded_bytes = base64.b64decode(encoded_code.encode('ascii'))
    decoded_code = decoded_bytes.decode('utf-8')

    # 创建模块
    module = ModuleType('brand_negotiation_core')
    exec(decoded_code, module.__dict__)

    return module

# 加载加密模块
try:
    _module = _load_encoded_module()
    globals().update({
        k: getattr(_module, k)
        for k in dir(_module)
        if not k.startswith('_')
    })
except ImportError as e:
    print(f"警告: {e}")
    print("请确保 .enc 文件存在于正确位置")

# 导出公开接口
__all__ = [
    'BrandNegotiationEngine',
    'BrandHubService',
    'GEOAdvisor',
    'ContentFactory',
    'PricingStrategyService',
    'DistributionOrchestrator',
    'NegotiationMasterKit',
    'SkillInput',
    'BrandInput',
    'GoalInput',
    'PartnerInput',
    'ConstraintsInput',
    'AssetsInput',
    'ChannelsInput',
    'PricingPreferenceInput',
    'OpportunityGrade',
    'PrimaryGoal',
    'quick_execute',
]

# 模块元数据
__version__ = "1.0.0"
__author__ = "MiniMax Agent"
__description__ = "品牌商务谈判核心引擎 (闭源代码)"
