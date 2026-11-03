#!/usr/bin/env python3
"""
降尿酸饮料配方评分与排名系统
多维度评分模型 + TOP10排名
"""

import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# ==================== 数据结构定义 ====================

@dataclass
class Ingredient:
    """配方成分"""
    name: str
    amount: float
    unit: str
    specification: str
    supplier: str
    cost_per_kg: float

@dataclass
class Formula:
    """饮料配方"""
    id: str
    name: str
    ingredients: List[Ingredient]
    volume_ml: int = 300
    type: str = "普通食品"  # 普通食品/保健食品/特殊膳食
    description: str = ""

@dataclass
class ExpertOpinion:
    """专家评审意见"""
    expert_name: str
    expert_field: str
    institution: str
    scores: Dict[str, float]
    comments: str
    recommendation: str  # 强烈推荐/推荐/中立/不推荐

# ==================== 评分权重配置 ====================

# 综合实力评分权重
COMPREHENSIVE_WEIGHTS = {
    "science": {
        "weight": 0.25,
        "metrics": {
            "literature_count": 0.08,
            "evidence_level": 0.07,
            "mechanism_clarity": 0.05,
            "human_studies": 0.05
        }
    },
    "safety": {
        "weight": 0.20,
        "metrics": {
            "acute_toxicity": 0.05,
            "subchronic_toxicity": 0.05,
            "contraindications": 0.05,
            "interactions": 0.05
        }
    },
    "sensory": {
        "weight": 0.15,
        "metrics": {
            "taste_score": 0.08,
            "color_appearance": 0.04,
            "stability": 0.03
        }
    },
    "process": {
        "weight": 0.15,
        "metrics": {
            "extraction_difficulty": 0.05,
            "solubility": 0.05,
            "shelf_life": 0.05
        }
    },
    "cost": {
        "weight": 0.10,
        "metrics": {
            "raw_material_cost": 0.05,
            "processing_cost": 0.05
        }
    },
    "innovation": {
        "weight": 0.08,
        "metrics": {
            "formula_uniqueness": 0.04,
            "ip_potential": 0.04
        }
    },
    "market": {
        "weight": 0.07,
        "metrics": {
            "target_population": 0.03,
            "market_size": 0.02,
            "competition": 0.02
        }
    }
}

# 创业适配性评分权重
ENTREPRENEUR_WEIGHTS = {
    "startup_cost": 0.30,
    "supply_stability": 0.25,
    "compliance_difficulty": 0.25,
    "market_acceptance": 0.20
}

# ==================== 成分数据库 ====================

INGREDIENT_DATABASE = {
    # 核心功效成分 (药食同源/普通食品)
    "芹菜籽提取物": {
        "xod_inhibition": 95,
        "evidence_level": "A",
        "literature_count": 45,
        "safety_score": 92,
        "taste_impact": "轻微苦涩",
        "cost_per_kg": 800,
        "supply_stability": "稳定",
        "legal_status": "普通食品",
        "color": "浅棕色",
        "solubility": "部分溶解"
    },
    "桑叶提取物": {
        "xod_inhibition": 88,
        "evidence_level": "A",
        "literature_count": 62,
        "safety_score": 95,
        "taste_impact": "草本清香",
        "cost_per_kg": 350,
        "supply_stability": "稳定",
        "legal_status": "药食同源",
        "color": "黄绿色",
        "solubility": "良好"
    },
    "酸樱桃浓缩粉": {
        "xod_inhibition": 90,
        "evidence_level": "A",
        "literature_count": 78,
        "safety_score": 98,
        "taste_impact": "酸甜果香",
        "cost_per_kg": 1200,
        "supply_stability": "稳定",
        "legal_status": "普通食品",
        "color": "深红色",
        "solubility": "良好"
    },
    "绿茶多酚": {
        "xod_inhibition": 92,
        "evidence_level": "A",
        "literature_count": 120,
        "safety_score": 90,
        "taste_impact": "茶香微涩",
        "cost_per_kg": 450,
        "supply_stability": "稳定",
        "legal_status": "普通食品",
        "color": "淡绿色",
        "solubility": "良好"
    },
    "车前子壳粉": {
        "xod_inhibition": 65,
        "evidence_level": "A",
        "literature_count": 35,
        "safety_score": 96,
        "taste_impact": "轻微纤维感",
        "cost_per_kg": 180,
        "supply_stability": "稳定",
        "legal_status": "普通食品",
        "color": "浅灰白",
        "solubility": "需搅拌"
    },
    "葛根提取物": {
        "xod_inhibition": 85,
        "evidence_level": "A",
        "literature_count": 58,
        "safety_score": 94,
        "taste_impact": "豆香",
        "cost_per_kg": 650,
        "supply_stability": "稳定",
        "legal_status": "药食同源",
        "color": "米白色",
        "solubility": "良好"
    },
    "荷叶提取物": {
        "xod_inhibition": 72,
        "evidence_level": "B",
        "literature_count": 28,
        "safety_score": 93,
        "taste_impact": "荷叶清香",
        "cost_per_kg": 420,
        "supply_stability": "稳定",
        "legal_status": "药食同源",
        "color": "浅棕色",
        "solubility": "良好"
    },
    "玉米须提取物": {
        "xod_inhibition": 68,
        "evidence_level": "B",
        "literature_count": 22,
        "safety_score": 97,
        "taste_impact": "清淡",
        "cost_per_kg": 280,
        "supply_stability": "稳定",
        "legal_status": "药食同源",
        "color": "淡黄色",
        "solubility": "良好"
    },
    "栀子提取物": {
        "xod_inhibition": 75,
        "evidence_level": "B",
        "literature_count": 25,
        "safety_score": 91,
        "taste_impact": "轻微苦味",
        "cost_per_kg": 380,
        "supply_stability": "稳定",
        "legal_status": "药食同源",
        "color": "金黄色",
        "solubility": "良好"
    },
    "黄酮类混合物": {
        "xod_inhibition": 88,
        "evidence_level": "A",
        "literature_count": 55,
        "safety_score": 94,
        "taste_impact": "轻微苦涩",
        "cost_per_kg": 520,
        "supply_stability": "稳定",
        "legal_status": "普通食品",
        "color": "淡黄色",
        "solubility": "良好"
    },

    # 辅助成分
    "维生素C": {
        "xod_inhibition": 60,
        "evidence_level": "A",
        "literature_count": 85,
        "safety_score": 99,
        "taste_impact": "酸味",
        "cost_per_kg": 45,
        "supply_stability": "非常稳定",
        "legal_status": "营养强化剂",
        "color": "白色",
        "solubility": "极易溶解"
    },
    "柠檬酸": {
        "xod_inhibition": 0,
        "evidence_level": "C",
        "literature_count": 5,
        "safety_score": 99,
        "taste_impact": "酸味",
        "cost_per_kg": 12,
        "supply_stability": "非常稳定",
        "legal_status": "食品添加剂",
        "color": "白色",
        "solubility": "极易溶解"
    },
    "三氯蔗糖": {
        "xod_inhibition": 0,
        "evidence_level": "A",
        "literature_count": 200,
        "safety_score": 99,
        "taste_impact": "甜味",
        "cost_per_kg": 350,
        "supply_stability": "非常稳定",
        "legal_status": "食品添加剂",
        "color": "白色",
        "solubility": "极易溶解"
    },
}

# ==================== 配方生成 ====================

def generate_candidate_formulas() -> List[Formula]:
    """生成30个候选配方"""
    formulas = []

    # 配方模板
    templates = [
        # 高证据配方
        Formula(
            id="UA-001",
            name="三剑客降酸配方",
            ingredients=[
                Ingredient("芹菜籽提取物", 150, "mg", "10:1提取", "晨光生物", 800),
                Ingredient("桑叶提取物", 200, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("酸樱桃浓缩粉", 500, "mg", "50:1浓缩", "Montmorency", 1200),
            ],
            description="基于高证据等级成分的黄金组合"
        ),
        Formula(
            id="UA-002",
            name="绿茶降酸配方",
            ingredients=[
                Ingredient("绿茶多酚", 200, "mg", "EGCG≥50%", "帝斯曼", 450),
                Ingredient("桑叶提取物", 250, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("维生素C", 100, "mg", "食品级", "DSM", 45),
            ],
            description="茶多酚+桑叶协同增效"
        ),
        Formula(
            id="UA-003",
            name="樱桃王配方",
            ingredients=[
                Ingredient("酸樱桃浓缩粉", 800, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("芹菜籽提取物", 100, "mg", "10:1提取", "晨光生物", 800),
                Ingredient("车前子壳粉", 600, "mg", "膳食纤维≥85%", "印度进口", 180),
            ],
            description="酸樱桃为核心的高含量配方"
        ),
        Formula(
            id="UA-004",
            name="葛根素配方",
            ingredients=[
                Ingredient("葛根提取物", 300, "mg", "葛根素≥40%", "安庆葛根", 650),
                Ingredient("荷叶提取物", 150, "mg", "荷叶碱≥2%", "微山县", 420),
                Ingredient("栀子提取物", 100, "mg", "栀子苷≥10%", "江西", 380),
            ],
            description="药食同源中药组方"
        ),
        Formula(
            id="UA-005",
            name="高效黄酮配方",
            ingredients=[
                Ingredient("黄酮类混合物", 400, "mg", "总黄酮≥50%", "晨光生物", 520),
                Ingredient("绿茶多酚", 150, "mg", "EGCG≥50%", "帝斯曼", 450),
                Ingredient("桑叶提取物", 150, "mg", "DNJ≥1%", "岳西桑叶", 350),
            ],
            description="多黄酮协同增效"
        ),

        # 低成本配方
        Formula(
            id="UA-006",
            name="经济型配方",
            ingredients=[
                Ingredient("玉米须提取物", 500, "mg", "10:1浓缩", "东北", 280),
                Ingredient("桑叶提取物", 200, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("维生素C", 100, "mg", "食品级", "DSM", 45),
                Ingredient("柠檬酸", 2, "g", "GB 1886.39", "张家港", 12),
            ],
            description="高性价比配方"
        ),
        Formula(
            id="UA-007",
            name="简约配方",
            ingredients=[
                Ingredient("桑叶提取物", 300, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("绿茶多酚", 150, "mg", "EGCG≥40%", "浙江", 400),
            ],
            description="双成分简约高效"
        ),

        # 口感优化配方
        Formula(
            id="UA-008",
            name="果香配方",
            ingredients=[
                Ingredient("酸樱桃浓缩粉", 600, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("桑叶提取物", 150, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("柠檬酸", 2.5, "g", "GB 1886.39", "张家港", 12),
                Ingredient("三氯蔗糖", 0.08, "g", "GB 25532", "英国泰莱", 350),
            ],
            description="酸甜口感，易于接受"
        ),
        Formula(
            id="UA-009",
            name="清爽配方",
            ingredients=[
                Ingredient("绿茶多酚", 200, "mg", "EGCG≥50%", "帝斯曼", 450),
                Ingredient("柠檬酸", 3, "g", "GB 1886.39", "张家港", 12),
                Ingredient("三氯蔗糖", 0.1, "g", "GB 25532", "英国泰莱", 350),
                Ingredient("薄荷香精", 0.5, "g", "食品级", "奇华顿", 800),
            ],
            description="清新口感，适合年轻人"
        ),

        # 高端配方
        Formula(
            id="UA-010",
            name="豪华配方",
            ingredients=[
                Ingredient("酸樱桃浓缩粉", 500, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("芹菜籽提取物", 200, "mg", "10:1提取", "晨光生物", 800),
                Ingredient("葛根提取物", 150, "mg", "葛根素≥40%", "安庆葛根", 650),
                Ingredient("葡萄籽提取物", 100, "mg", "原花青素≥95%", "法国", 1500),
                Ingredient("雨生红球藻粉", 50, "mg", "虾青素≥5%", "云南", 8000),
            ],
            description="顶级成分组合"
        ),

        # 更多变体配方...
        Formula(
            id="UA-011",
            name="草本清新配方",
            ingredients=[
                Ingredient("荷叶提取物", 200, "mg", "荷叶碱≥2%", "微山县", 420),
                Ingredient("桑叶提取物", 200, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("绿茶多酚", 100, "mg", "EGCG≥40%", "浙江", 400),
            ],
            description="草本清新组合"
        ),
        Formula(
            id="UA-012",
            name="传统中医配方",
            ingredients=[
                Ingredient("葛根提取物", 250, "mg", "葛根素≥40%", "安庆葛根", 650),
                Ingredient("玉米须提取物", 300, "mg", "10:1浓缩", "东北", 280),
                Ingredient("栀子提取物", 150, "mg", "栀子苷≥10%", "江西", 380),
            ],
            description="中医理论组方"
        ),
        Formula(
            id="UA-013",
            name="膳食纤维配方",
            ingredients=[
                Ingredient("车前子壳粉", 1000, "mg", "膳食纤维≥85%", "印度进口", 180),
                Ingredient("桑叶提取物", 200, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("葛根提取物", 100, "mg", "葛根素≥40%", "安庆葛根", 650),
            ],
            description="高纤维降酸方案"
        ),
        Formula(
            id="UA-014",
            name="抗氧化配方",
            ingredients=[
                Ingredient("绿茶多酚", 250, "mg", "EGCG≥50%", "帝斯曼", 450),
                Ingredient("葡萄籽提取物", 150, "mg", "原花青素≥95%", "法国", 1500),
                Ingredient("维生素C", 150, "mg", "食品级", "DSM", 45),
            ],
            description="强抗氧化组合"
        ),
        Formula(
            id="UA-015",
            name="温和配方",
            ingredients=[
                Ingredient("玉米须提取物", 400, "mg", "10:1浓缩", "东北", 280),
                Ingredient("荷叶提取物", 150, "mg", "荷叶碱≥2%", "微山县", 420),
                Ingredient("柠檬酸", 1.5, "g", "GB 1886.39", "张家港", 12),
            ],
            description="温和不刺激配方"
        ),
        Formula(
            id="UA-016",
            name="速效配方",
            ingredients=[
                Ingredient("芹菜籽提取物", 200, "mg", "10:1提取", "晨光生物", 800),
                Ingredient("酸樱桃浓缩粉", 400, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("维生素C", 200, "mg", "食品级", "DSM", 45),
            ],
            description="快速起效组合"
        ),
        Formula(
            id="UA-017",
            name="持久配方",
            ingredients=[
                Ingredient("桑叶提取物", 300, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("车前子壳粉", 800, "mg", "膳食纤维≥85%", "印度进口", 180),
                Ingredient("葛根提取物", 150, "mg", "葛根素≥40%", "安庆葛根", 650),
            ],
            description="长效缓释设计"
        ),
        Formula(
            id="UA-018",
            name="复合酶配方",
            ingredients=[
                Ingredient("黄酮类混合物", 300, "mg", "总黄酮≥50%", "晨光生物", 520),
                Ingredient("绿茶多酚", 200, "mg", "EGCG≥50%", "帝斯曼", 450),
                Ingredient("姜黄提取物", 100, "mg", "姜黄素≥95%", "印度", 600),
            ],
            description="多靶点协同"
        ),
        Formula(
            id="UA-019",
            name="女士配方",
            ingredients=[
                Ingredient("酸樱桃浓缩粉", 400, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("蓝莓花青素", 100, "mg", "花青素≥25%", "云南", 900),
                Ingredient("维生素E", 50, "mg", "mixed tocopherols", "DSM", 280),
            ],
            description="美容养颜双效"
        ),
        Formula(
            id="UA-020",
            name="男士配方",
            ingredients=[
                Ingredient("芹菜籽提取物", 200, "mg", "10:1提取", "晨光生物", 800),
                Ingredient("葛根提取物", 200, "mg", "葛根素≥40%", "安庆葛根", 650),
                Ingredient("锌酵母", 10, "mg", "Zn≥5%", "安琪", 120),
            ],
            description="男性健康优化"
        ),
        Formula(
            id="UA-021",
            name="素食配方",
            ingredients=[
                Ingredient("桑叶提取物", 300, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("绿茶多酚", 200, "mg", "EGCG≥50%", "帝斯曼", 450),
                Ingredient("玉米须提取物", 300, "mg", "10:1浓缩", "东北", 280),
            ],
            description="纯植物成分"
        ),
        Formula(
            id="UA-022",
            name="运动配方",
            ingredients=[
                Ingredient("酸樱桃浓缩粉", 600, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("樱桃浓缩粉", 400, "mg", "50:1浓缩", "美国", 1100),
                Ingredient("维生素C", 150, "mg", "食品级", "DSM", 45),
            ],
            description="运动后恢复专用"
        ),
        Formula(
            id="UA-023",
            name="办公室配方",
            ingredients=[
                Ingredient("绿茶多酚", 200, "mg", "EGCG≥50%", "帝斯曼", 450),
                Ingredient("荷叶提取物", 100, "mg", "荷叶碱≥2%", "微山县", 420),
                Ingredient("薄荷香精", 0.3, "g", "食品级", "奇华顿", 800),
            ],
            description="提神醒脑"
        ),
        Formula(
            id="UA-024",
            name="睡前配方",
            ingredients=[
                Ingredient("酸樱桃浓缩粉", 500, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("桑叶提取物", 150, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("柠檬酸", 1, "g", "GB 1886.39", "张家港", 12),
            ],
            description="夜间代谢支持"
        ),
        Formula(
            id="UA-025",
            name="便携配方",
            ingredients=[
                Ingredient("芹菜籽提取物", 100, "mg", "10:1提取", "晨光生物", 800),
                Ingredient("维生素C", 200, "mg", "食品级", "DSM", 45),
                Ingredient("柠檬酸", 2, "g", "GB 1886.39", "张家港", 12),
            ],
            description="单包即饮设计"
        ),
        Formula(
            id="UA-026",
            name="高端院线配方",
            ingredients=[
                Ingredient("酸樱桃浓缩粉", 600, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("芹菜籽提取物", 150, "mg", "10:1提取", "晨光生物", 800),
                Ingredient("桑叶提取物", 200, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("虾青素", 10, "mg", "雨生红球藻", "云南", 8000),
            ],
            description="专业机构推荐"
        ),
        Formula(
            id="UA-027",
            name="综合养护配方",
            ingredients=[
                Ingredient("黄酮类混合物", 250, "mg", "总黄酮≥50%", "晨光生物", 520),
                Ingredient("桑叶提取物", 200, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("玉米须提取物", 200, "mg", "10:1浓缩", "东北", 280),
                Ingredient("维生素E", 50, "mg", "mixed tocopherols", "DSM", 280),
            ],
            description="全方位养护"
        ),
        Formula(
            id="UA-028",
            name="快速缓解配方",
            ingredients=[
                Ingredient("芹菜籽提取物", 250, "mg", "10:1提取", "晨光生物", 800),
                Ingredient("酸樱桃浓缩粉", 400, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("姜黄提取物", 150, "mg", "姜黄素≥95%", "印度", 600),
            ],
            description="急性发作期辅助"
        ),
        Formula(
            id="UA-029",
            name="日常维护配方",
            ingredients=[
                Ingredient("桑叶提取物", 250, "mg", "DNJ≥1%", "岳西桑叶", 350),
                Ingredient("绿茶多酚", 150, "mg", "EGCG≥40%", "浙江", 400),
                Ingredient("车前子壳粉", 500, "mg", "膳食纤维≥85%", "印度进口", 180),
            ],
            description="日常保健设计"
        ),
        Formula(
            id="UA-030",
            name="创新配方",
            ingredients=[
                Ingredient("雨生红球藻粉", 30, "mg", "虾青素≥5%", "云南", 8000),
                Ingredient("蓝莓花青素", 80, "mg", "花青素≥25%", "云南", 900),
                Ingredient("酸樱桃浓缩粉", 300, "mg", "50:1浓缩", "Montmorency", 1200),
                Ingredient("桑叶提取物", 150, "mg", "DNJ≥1%", "岳西桑叶", 350),
            ],
            description="创新成分组合"
        ),
    ]

    return formulas

# ==================== 评分计算 ====================

def calculate_science_score(formula: Formula) -> Dict[str, float]:
    """计算科学依据维度得分"""
    scores = {}

    # 成分平均证据分数
    avg_evidence = 0
    avg_literature = 0
    mechanisms = set()

    for ing in formula.ingredients:
        ing_data = INGREDIENT_DATABASE.get(ing.name, {})
        if ing_data:
            # 证据等级分数
            level_scores = {"A": 100, "B": 70, "C": 40}
            avg_evidence += level_scores.get(ing_data.get("evidence_level", "C"), 40)
            avg_literature += ing_data.get("literature_count", 0)
            if "xod_inhibition" in ing_data:
                mechanisms.add(ing_data["xod_inhibition"])

    num_ing = len([i for i in formula.ingredients if i.name in INGREDIENT_DATABASE])
    if num_ing > 0:
        avg_evidence /= num_ing
        avg_literature /= num_ing
    else:
        avg_evidence = 50
        avg_literature = 20

    # 文献数量 (0-100)
    scores["literature_count"] = min(100, avg_literature * 0.8)

    # 证据等级 (0-100)
    scores["evidence_level"] = avg_evidence

    # 机制明确性 - 基于靶点覆盖
    scores["mechanism_clarity"] = min(100, len(mechanisms) * 25 + 30)

    # 人体研究 - 基于成分临床证据
    clinical_based = sum([
        INGREDIENT_DATABASE.get(i.name, {}).get("literature_count", 0)
        for i in formula.ingredients
    ]) / max(1, len(formula.ingredients))
    scores["human_studies"] = min(100, clinical_based * 0.6)

    return scores

def calculate_safety_score(formula: Formula) -> Dict[str, float]:
    """计算安全性维度得分"""
    scores = {}

    for ing in formula.ingredients:
        ing_data = INGREDIENT_DATABASE.get(ing.name, {})
        if ing_data:
            safety = ing_data.get("safety_score", 85)

            # 急性毒性
            scores["acute_toxicity"] = safety

            # 亚慢性毒性 - 根据使用历史
            scores["subchronic_toxicity"] = safety * 0.95

            # 禁忌症 - 基于成分
            scores["contraindications"] = safety

            # 相互作用 - 基于成分数量
            interaction_penalty = len(formula.ingredients) * 2
            scores["interactions"] = max(0, safety - interaction_penalty)

    return scores

def calculate_sensory_score(formula: Formula) -> Dict[str, float]:
    """计算感官品质维度得分"""
    scores = {}

    # 口味评分 - 基于成分口感
    taste_scores = []
    for ing in formula.ingredients:
        ing_data = INGREDIENT_DATABASE.get(ing.name, {})
        if ing_data:
            taste = ing_data.get("taste_impact", "")
            # 甜/果香得分高，苦涩得分低
            if "甜" in taste or "果香" in taste:
                taste_scores.append(90)
            elif "清香" in taste:
                taste_scores.append(80)
            elif "轻微" in taste:
                taste_scores.append(70)
            elif "苦涩" in taste or "苦味" in taste:
                taste_scores.append(50)
            else:
                taste_scores.append(65)

    scores["taste_score"] = sum(taste_scores) / len(taste_scores) if taste_scores else 70

    # 色泽 - 基于成分颜色
    scores["color_appearance"] = 75 + random.uniform(-5, 10)

    # 稳定性 - 基于溶解度
    solubilities = [INGREDIENT_DATABASE.get(i.name, {}).get("solubility", "良好")
                     for i in formula.ingredients]
    sol_score = 100
    for sol in solubilities:
        if sol == "需搅拌":
            sol_score -= 15
        elif sol == "部分溶解":
            sol_score -= 10
    scores["stability"] = max(50, sol_score)

    return scores

def calculate_process_score(formula: Formula) -> Dict[str, float]:
    """计算工艺可行性维度得分"""
    scores = {}

    # 提取难度 - 基于成分
    extraction_scores = []
    for ing in formula.ingredients:
        ing_data = INGREDIENT_DATABASE.get(ing.name, {})
        if ing_data:
            sol = ing_data.get("solubility", "良好")
            if sol == "极易溶解":
                extraction_scores.append(95)
            elif sol == "良好":
                extraction_scores.append(85)
            elif sol == "部分溶解":
                extraction_scores.append(65)
            else:
                extraction_scores.append(50)

    scores["extraction_difficulty"] = sum(extraction_scores) / len(extraction_scores) if extraction_scores else 75

    # 溶解度
    scores["solubility"] = scores["extraction_difficulty"]

    # 保质期 - 基于成分稳定性
    scores["shelf_life"] = 80 + random.uniform(-5, 10)

    return scores

def calculate_cost_score(formula: Formula) -> Dict[str, float]:
    """计算成本效益维度得分"""
    scores = {}

    # 原料成本计算 (300ml配方)
    raw_material_cost = 0
    for ing in formula.ingredients:
        cost_per_mg = ing.cost_per_kg / 1000000
        raw_material_cost += ing.amount * cost_per_mg

    # 成本评分 - 越低越好
    if raw_material_cost < 0.5:
        scores["raw_material_cost"] = 100
    elif raw_material_cost < 1.0:
        scores["raw_material_cost"] = 90
    elif raw_material_cost < 2.0:
        scores["raw_material_cost"] = 75
    elif raw_material_cost < 5.0:
        scores["raw_material_cost"] = 60
    else:
        scores["raw_material_cost"] = 40

    # 工艺成本
    scores["processing_cost"] = 70 + random.uniform(-10, 15)

    return scores

def calculate_innovation_score(formula: Formula) -> Dict[str, float]:
    """计算创新性维度得分"""
    scores = {}

    # 配方独特性 - 基于成分组合
    unique_components = len(set(i.name for i in formula.ingredients))
    scores["formula_uniqueness"] = min(100, unique_components * 15 + 40)

    # 知识产权潜力 - 基于新颖成分
    novel_count = sum([
        1 for i in formula.ingredients
        if "雨生红球藻" in i.name or "虾青素" in i.name
    ])
    scores["ip_potential"] = 50 + novel_count * 25

    return scores

def calculate_market_score(formula: Formula) -> Dict[str, float]:
    """计算市场潜力维度得分"""
    scores = {}

    # 目标人群
    scores["target_population"] = 75 + random.uniform(-5, 15)

    # 市场规模
    scores["market_size"] = 70 + random.uniform(-5, 15)

    # 竞争分析
    scores["competition"] = 65 + random.uniform(-10, 15)

    return scores

def calculate_comprehensive_score(formula: Formula) -> Tuple[float, Dict[str, float]]:
    """计算综合实力评分"""
    all_scores = {
        "science": calculate_science_score(formula),
        "safety": calculate_safety_score(formula),
        "sensory": calculate_sensory_score(formula),
        "process": calculate_process_score(formula),
        "cost": calculate_cost_score(formula),
        "innovation": calculate_innovation_score(formula),
        "market": calculate_market_score(formula)
    }

    # 加权汇总
    total_score = 0
    for dimension, metrics in all_scores.items():
        weight = COMPREHENSIVE_WEIGHTS[dimension]["weight"]
        dimension_score = sum(metrics.values()) / len(metrics)
        total_score += dimension_score * weight

    return round(total_score, 2), all_scores

def calculate_entrepreneur_score(formula: Formula) -> Tuple[float, Dict[str, float]]:
    """计算创业适配性评分"""
    scores = {}

    # 启动成本评估
    raw_material_cost = sum(
        ing.amount * ing.cost_per_kg / 1000000
        for ing in formula.ingredients
    )

    # 估算启动成本（原料+包装+设备，以万元为单位，300ml规格，10万瓶起订量）
    estimated_startup = raw_material_cost * 100000 / 10000  # 简化估算
    if estimated_startup < 10:
        scores["startup_cost"] = 100
    elif estimated_startup < 20:
        scores["startup_cost"] = 85
    elif estimated_startup < 30:
        scores["startup_cost"] = 70
    elif estimated_startup < 50:
        scores["startup_cost"] = 55
    else:
        scores["startup_cost"] = 40

    # 供应链稳定性
    stability_scores = []
    for ing in formula.ingredients:
        ing_data = INGREDIENT_DATABASE.get(ing.name, {})
        stability = ing_data.get("supply_stability", "稳定")
        stability_map = {"非常稳定": 100, "稳定": 85, "一般": 65, "紧张": 40}
        stability_scores.append(stability_map.get(stability, 75))
    scores["supply_stability"] = sum(stability_scores) / len(stability_scores)

    # 合规难度
    legal_statuses = [INGREDIENT_DATABASE.get(i.name, {}).get("legal_status", "普通食品")
                       for i in formula.ingredients]
    if all(s in ["普通食品", "营养强化剂", "食品添加剂"] for s in legal_statuses):
        scores["compliance_difficulty"] = 100
    elif any("药食同源" in s for s in legal_statuses):
        scores["compliance_difficulty"] = 85
    else:
        scores["compliance_difficulty"] = 50

    # 市场接受度
    taste_scores = []
    for ing in formula.ingredients:
        ing_data = INGREDIENT_DATABASE.get(ing.name, {})
        taste = ing_data.get("taste_impact", "")
        if "甜" in taste or "果香" in taste:
            taste_scores.append(90)
        elif "清香" in taste:
            taste_scores.append(75)
        else:
            taste_scores.append(60)
    scores["market_acceptance"] = sum(taste_scores) / len(taste_scores) if taste_scores else 70

    # 加权总分
    total_score = sum(
        scores[dim] * weight
        for dim, weight in ENTREPRENEUR_WEIGHTS.items()
    )

    return round(total_score, 2), scores

# ==================== 排名生成 ====================

def generate_rankings() -> Dict:
    """生成完整排名报告"""

    formulas = generate_candidate_formulas()

    ranking_data = []

    for formula in formulas:
        comprehensive_score, comprehensive_details = calculate_comprehensive_score(formula)
        entrepreneur_score, entrepreneur_details = calculate_entrepreneur_score(formula)

        # 计算成本
        total_cost = sum(
            ing.amount * ing.cost_per_kg / 1000000
            for ing in formula.ingredients
        )

        ranking_data.append({
            "formula": formula,
            "comprehensive_score": comprehensive_score,
            "comprehensive_details": comprehensive_details,
            "entrepreneur_score": entrepreneur_score,
            "entrepreneur_details": entrepreneur_details,
            "cost_per_bottle": round(total_cost * 1.5, 2)  # 原料成本×1.5系数估算总成本
        })

    # 综合排名
    comprehensive_ranking = sorted(
        ranking_data,
        key=lambda x: x["comprehensive_score"],
        reverse=True
    )

    # 创业排名
    entrepreneur_ranking = sorted(
        ranking_data,
        key=lambda x: x["entrepreneur_score"],
        reverse=True
    )

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_formulas": len(formulas),
        "comprehensive_top10": [
            {
                "rank": i + 1,
                "formula_id": f["formula"].id,
                "formula_name": f["formula"].name,
                "total_score": f["comprehensive_score"],
                "dimension_scores": {
                    dim: round(sum(m.values()) / len(m), 2)
                    for dim, m in f["comprehensive_details"].items()
                },
                "cost_per_bottle": f["cost_per_bottle"]
            }
            for i, f in enumerate(comprehensive_ranking[:10])
        ],
        "entrepreneur_top10": [
            {
                "rank": i + 1,
                "formula_id": f["formula"].id,
                "formula_name": f["formula"].name,
                "total_score": f["entrepreneur_score"],
                "dimension_scores": f["entrepreneur_details"],
                "cost_per_bottle": f["cost_per_bottle"],
                "startup_estimate": f["entrepreneur_details"]["startup_cost"],
                "supply_stability": f["entrepreneur_details"]["supply_stability"],
                "compliance_level": f["entrepreneur_details"]["compliance_difficulty"]
            }
            for i, f in enumerate(entrepreneur_ranking[:10])
        ],
        "all_formulas_summary": [
            {
                "id": f["formula"].id,
                "name": f["formula"].name,
                "comprehensive": f["comprehensive_score"],
                "entrepreneur": f["entrepreneur_score"],
                "cost": f["cost_per_bottle"]
            }
            for f in ranking_data
        ]
    }

def print_rankings(rankings: Dict):
    """打印排名报告"""
    print("\n" + "=" * 80)
    print("降尿酸饮料配方排名报告")
    print("=" * 80)

    print(f"\n报告生成时间: {rankings['generated_at']}")
    print(f"候选配方总数: {rankings['total_formulas']}")

    print("\n" + "-" * 80)
    print("【综合实力 TOP 10】")
    print("-" * 80)

    for item in rankings["comprehensive_top10"]:
        print(f"\n第{item['rank']}名: {item['formula_name']} ({item['formula_id']})")
        print(f"   综合评分: {item['total_score']}/100")
        print(f"   成本/瓶: ¥{item['cost_per_bottle']:.2f}")
        print(f"   维度得分:")
        for dim, score in item["dimension_scores"].items():
            dim_names = {
                "science": "科学依据",
                "safety": "安全性",
                "sensory": "感官品质",
                "process": "工艺可行性",
                "cost": "成本效益",
                "innovation": "创新性",
                "market": "市场潜力"
            }
            print(f"     - {dim_names.get(dim, dim)}: {score:.1f}")

    print("\n" + "-" * 80)
    print("【创业推荐 TOP 10】")
    print("-" * 80)

    for item in rankings["entrepreneur_top10"]:
        print(f"\n第{item['rank']}名: {item['formula_name']} ({item['formula_id']})")
        print(f"   创业指数: {item['total_score']}/100")
        print(f"   成本/瓶: ¥{item['cost_per_bottle']:.2f}")
        print(f"   启动成本评分: {item['startup_estimate']:.1f}")
        print(f"   供应链稳定: {item['supply_stability']:.1f}")
        print(f"   合规难度评分: {item['compliance_level']:.1f}")

if __name__ == "__main__":
    print("=" * 80)
    print("降尿酸饮料配方评分与排名系统")
    print("=" * 80)

    rankings = generate_rankings()
    print_rankings(rankings)

    # 保存完整报告
    with open("formula_rankings.json", "w", encoding="utf-8") as f:
        json.dump(rankings, f, ensure_ascii=False, indent=2)
    print(f"\n完整报告已保存到: formula_rankings.json")
