#!/usr/bin/env python3
"""
户型图装修预算费用表生成脚本
功能：根据户型信息生成详细的装修预算费用表，支持三种方案等级
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BudgetItem:
    """预算项目"""
    category: str          # 费用类别
    subcategory: str       # 子类别
    item_name: str         # 项目名称
    unit: str              # 单位
    quantity: float        # 数量
    unit_price: float      # 单价
    total_price: float     # 总价
    brand: str = ""        # 品牌建议
    notes: str = ""        # 备注


@dataclass
class BudgetPlan:
    """装修预算方案"""
    plan_name: str                    # 方案名称
    plan_type: str                    # 方案类型：economy/standard/luxury
    total_area: float                 # 装修面积（平方米）
    base_cost: float = 0              # 基础装修总价
    main_material_cost: float = 0     # 主材总价
    furniture_cost: float = 0         # 家具总价
    appliance_cost: float = 0         # 家电总价
    soft_decor_cost: float = 0        # 软装总价
    other_cost: float = 0             # 其他费用
    total_cost: float = 0             # 总价
    items: List[BudgetItem] = field(default_factory=list)  # 明细项目

    def calculate_total(self) -> float:
        """计算总费用"""
        self.total_cost = (
            self.base_cost +
            self.main_material_cost +
            self.furniture_cost +
            self.appliance_cost +
            self.soft_decor_cost +
            self.other_cost
        )
        return self.total_cost


class BudgetGenerator:
    """预算生成器"""

    # 基础装修单价（元/平米）- 根据方案类型
    BASE_PRICE_PER_SQM = {
        "economy": 400,      # 经济型：400-600元/平米
        "standard": 700,     # 标准型：700-1000元/平米
        "luxury": 1200       # 豪华型：1200+元/平米
    }

    # 主材单价参考（元/平米）
    MAIN_MATERIAL_PRICES = {
        "floor": {           # 地板
            "economy": 80,
            "standard": 150,
            "luxury": 300
        },
        "tile": {            # 瓷砖
            "economy": 60,
            "standard": 120,
            "luxury": 250
        },
        "paint": {           # 油漆
            "economy": 35,
            "standard": 60,
            "luxury": 120
        },
        "ceiling": {         # 吊顶
            "economy": 80,
            "standard": 150,
            "luxury": 300
        },
        "door": {            # 门
            "economy": 800,
            "standard": 1500,
            "luxury": 3500
        },
        "cabinet": {         # 橱柜
            "economy": 800,
            "standard": 1500,
            "luxury": 3000
        },
        "bathroom": {        # 卫浴
            "economy": 3000,
            "standard": 8000,
            "luxury": 20000
        }
    }

    # 家具单价参考（元）
    FURNITURE_PRICES = {
        "sofa": {            # 沙发
            "economy": 3000,
            "standard": 8000,
            "luxury": 20000
        },
        "bed": {             # 床
            "economy": 2000,
            "standard": 5000,
            "luxury": 15000
        },
        "dining_table": {    # 餐桌
            "economy": 1500,
            "standard": 4000,
            "luxury": 12000
        },
        "wardrobe": {        # 衣柜
            "economy": 2000,
            "standard": 5000,
            "luxury": 15000
        },
        "desk": {            # 书桌
            "economy": 500,
            "standard": 1500,
            "luxury": 5000
        },
        "tv_stand": {        # 电视柜
            "economy": 800,
            "standard": 2000,
            "luxury": 6000
        }
    }

    # 家电单价参考（元）
    APPLIANCE_PRICES = {
        "air_conditioner": 3000,      # 空调
        "refrigerator": 4000,         # 冰箱
        "washing_machine": 2500,      # 洗衣机
        "tv": 4000,                    # 电视
        "water_heater": 2000,         # 热水器
        "range_hood": 1500,           # 油烟机
        "gas_stove": 1500,            # 燃气灶
        "microwave": 800,             # 微波炉
        "dishwasher": 3000,          # 洗碗机
        "air_purifier": 2000          # 空气净化器
    }

    # 软装单价参考（元）
    SOFT_DECOR_PRICES = {
        "curtain": 1500,               # 窗帘
        "lamp": 800,                   # 灯具
        "carpet": 500,                 # 地毯
        "painting": 300,               # 装饰画
        "plant": 200,                 # 绿植
        "cushion": 150,                # 抱枕
        "mirror": 300,                # 镜子
        "clock": 150                   # 挂钟
    }

    def __init__(self):
        self.plans: List[BudgetPlan] = []

    def generate_budget(
        self,
        total_area: float,
        room_count: int = 2,
        bathroom_count: int = 1,
        kitchen_type: str = "closed",
        has_balcony: bool = True,
        has_study: bool = False
    ) -> List[BudgetPlan]:
        """
        生成三种预算方案

        Args:
            total_area: 装修总面积（平方米）
            room_count: 卧室数量
            bathroom_count: 卫生间数量
            kitchen_type: 厨房类型（open/closed）
            has_balcony: 是否有阳台
            has_study: 是否有书房

        Returns:
            List[BudgetPlan]: 三种预算方案
        """
        plan_types = ["economy", "standard", "luxury"]
        plan_names = ["经济实用型", "品质舒适型", "高端豪华型"]

        for plan_type, plan_name in zip(plan_types, plan_names):
            plan = BudgetPlan(
                plan_name=plan_name,
                plan_type=plan_type,
                total_area=total_area
            )

            # 计算各部分费用
            self._calculate_base_cost(plan, room_count, bathroom_count, kitchen_type, has_balcony)
            self._calculate_main_material_cost(plan, room_count, bathroom_count, has_balcony)
            self._calculate_furniture_cost(plan, room_count, bathroom_count, has_study)
            self._calculate_appliance_cost(plan, room_count, bathroom_count, has_study)
            self._calculate_soft_decor_cost(plan, total_area)
            self._calculate_other_cost(plan, total_area)

            # 计算总价
            plan.calculate_total()
            self.plans.append(plan)

        return self.plans

    def _calculate_base_cost(
        self,
        plan: BudgetPlan,
        room_count: int,
        bathroom_count: int,
        kitchen_type: str,
        has_balcony: bool
    ):
        """计算基础装修费用"""
        base_price = self.BASE_PRICE_PER_SQM[plan.plan_type]
        base_total = base_price * plan.total_area

        # 拆改工程
        demo_cost = plan.total_area * 30 * (1 if room_count > 2 else 0.5)
        plan.items.append(BudgetItem(
            category="基础装修费",
            subcategory="拆改工程",
            item_name="主体拆改",
            unit="项",
            quantity=1,
            unit_price=demo_cost,
            total_price=demo_cost,
            notes="拆墙、砌墙、铲墙皮"
        ))

        # 水电改造
        hydropower_items = [
            ("电路改造", "平米", plan.total_area, 50, "布线、开关插座安装"),
            ("水路改造", "平米", plan.total_area, 40, "水管、阀门安装"),
            ("开关插座安装", "个", 30 + room_count * 5, 30, "含底盒安装"),
        ]
        for name, unit, qty, price, notes in hydropower_items:
            total = qty * price
            plan.items.append(BudgetItem(
                category="基础装修费",
                subcategory="水电工程",
                item_name=name,
                unit=unit,
                quantity=qty,
                unit_price=price,
                total_price=total,
                notes=notes
            ))

        # 泥瓦工程
        tile_area = plan.total_area * 0.8  # 贴砖面积估算
        plan.items.append(BudgetItem(
            category="基础装修费",
            subcategory="泥瓦工程",
            item_name="防水工程",
            unit="平米",
            quantity=bathroom_count * 8,
            unit_price=60,
            total_price=bathroom_count * 8 * 60,
            notes="卫生间、厨房防水"
        ))
        plan.items.append(BudgetItem(
            category="基础装修费",
            subcategory="泥瓦工程",
            item_name="墙地砖铺贴",
            unit="平米",
            quantity=tile_area,
            unit_price=50,
            total_price=tile_area * 50,
            notes="含水泥砂浆"
        ))

        # 木工工程
        ceiling_area = plan.total_area * 0.6
        plan.items.append(BudgetItem(
            category="基础装修费",
            subcategory="木工工程",
            item_name="吊顶工程",
            unit="平米",
            quantity=ceiling_area,
            unit_price=base_price * 0.3,
            total_price=ceiling_area * base_price * 0.3,
            notes="客厅、卧室吊顶"
        ))

        # 油漆工程
        wall_area = plan.total_area * 2.5  # 墙面面积估算
        plan.items.append(BudgetItem(
            category="基础装修费",
            subcategory="油漆工程",
            item_name="墙面处理刷漆",
            unit="平米",
            quantity=wall_area,
            unit_price=self.MAIN_MATERIAL_PRICES["paint"][plan.plan_type],
            total_price=wall_area * self.MAIN_MATERIAL_PRICES["paint"][plan.plan_type],
            notes="批腻子、刷乳胶漆"
        ))

        # 计算基础装修总价
        plan.base_cost = sum(item.total_price for item in plan.items if item.category == "基础装修费")

    def _calculate_main_material_cost(
        self,
        plan: BudgetPlan,
        room_count: int,
        bathroom_count: int,
        has_balcony: bool
    ):
        """计算主材费用"""
        # 地板
        floor_area = plan.total_area * 0.7
        plan.items.append(BudgetItem(
            category="主材费",
            subcategory="地板",
            item_name="实木/复合地板",
            unit="平米",
            quantity=floor_area,
            unit_price=self.MAIN_MATERIAL_PRICES["floor"][plan.plan_type],
            total_price=floor_area * self.MAIN_MATERIAL_PRICES["floor"][plan.plan_type],
            brand="大自然/圣象/德尔",
            notes="含踢脚线、安装费"
        ))

        # 瓷砖
        tile_area = plan.total_area * 0.5
        plan.items.append(BudgetItem(
            category="主材费",
            subcategory="瓷砖",
            item_name="墙地砖",
            unit="平米",
            quantity=tile_area,
            unit_price=self.MAIN_MATERIAL_PRICES["tile"][plan.plan_type],
            total_price=tile_area * self.MAIN_MATERIAL_PRICES["tile"][plan.plan_type],
            brand="马可波罗/诺贝尔/东鹏",
            notes="含加工费"
        ))

        # 门
        door_count = room_count + 1 + bathroom_count  # 卧室门+入户门+卫生间门
        for i in range(door_count):
            door_type = "入户门" if i == 0 else ("卫生间门" if i == door_count - 1 else f"卧室门{i}")
            plan.items.append(BudgetItem(
                category="主材费",
                subcategory="门窗",
                item_name=door_type,
                unit="樘",
                quantity=1,
                unit_price=self.MAIN_MATERIAL_PRICES["door"][plan.plan_type],
                total_price=self.MAIN_MATERIAL_PRICES["door"][plan.plan_type],
                brand="TATA/梦天/欧派",
                notes="含门套、五金"
            ))

        # 橱柜
        cabinet_length = 4 if kitchen_type == "closed" else 2
        plan.items.append(BudgetItem(
            category="主材费",
            subcategory="橱柜",
            item_name="整体橱柜",
            unit="延米",
            quantity=cabinet_length,
            unit_price=self.MAIN_MATERIAL_PRICES["cabinet"][plan.plan_type],
            total_price=cabinet_length * self.MAIN_MATERIAL_PRICES["cabinet"][plan.plan_type],
            brand="欧派/金牌/志邦",
            notes="含台面、五金"
        ))

        # 卫浴
        plan.items.append(BudgetItem(
            category="主材费",
            subcategory="卫浴",
            item_name="马桶",
            unit="套",
            quantity=bathroom_count,
            unit_price=self.MAIN_MATERIAL_PRICES["bathroom"][plan.plan_type] * 0.3,
            total_price=bathroom_count * self.MAIN_MATERIAL_PRICES["bathroom"][plan.plan_type] * 0.3,
            brand="科勒/TOTO/九牧"
        ))
        plan.items.append(BudgetItem(
            category="主材费",
            subcategory="卫浴",
            item_name="浴室柜",
            unit="套",
            quantity=bathroom_count,
            unit_price=self.MAIN_MATERIAL_PRICES["bathroom"][plan.plan_type] * 0.3,
            total_price=bathroom_count * self.MAIN_MATERIAL_PRICES["bathroom"][plan.plan_type] * 0.3,
            brand="科勒/TOTO/九牧"
        ))
        plan.items.append(BudgetItem(
            category="主材费",
            subcategory="卫浴",
            item_name="花洒龙头",
            unit="套",
            quantity=bathroom_count,
            unit_price=self.MAIN_MATERIAL_PRICES["bathroom"][plan.plan_type] * 0.2,
            total_price=bathroom_count * self.MAIN_MATERIAL_PRICES["bathroom"][plan.plan_type] * 0.2,
            brand="科勒/TOTO/九牧"
        ))

        plan.main_material_cost = sum(item.total_price for item in plan.items if item.category == "主材费")

    def _calculate_furniture_cost(
        self,
        plan: BudgetPlan,
        room_count: int,
        bathroom_count: int,
        has_study: bool
    ):
        """计算家具费用"""
        # 客厅家具
        plan.items.append(BudgetItem(
            category="家具费",
            subcategory="客厅",
            item_name="沙发",
            unit="套",
            quantity=1,
            unit_price=self.FURNITURE_PRICES["sofa"][plan.plan_type],
            total_price=self.FURNITURE_PRICES["sofa"][plan.plan_type],
            notes="3+1+1组合"
        ))
        plan.items.append(BudgetItem(
            category="家具费",
            subcategory="客厅",
            item_name="电视柜",
            unit="个",
            quantity=1,
            unit_price=self.FURNITURE_PRICES["tv_stand"][plan.plan_type],
            total_price=self.FURNITURE_PRICES["tv_stand"][plan.plan_type]
        ))
        plan.items.append(BudgetItem(
            category="家具费",
            subcategory="客厅",
            item_name="茶几",
            unit="个",
            quantity=1,
            unit_price=self.FURNITURE_PRICES["dining_table"][plan.plan_type] * 0.4,
            total_price=self.FURNITURE_PRICES["dining_table"][plan.plan_type] * 0.4
        ))

        # 餐厅家具
        plan.items.append(BudgetItem(
            category="家具费",
            subcategory="餐厅",
            item_name="餐桌椅",
            unit="套",
            quantity=1,
            unit_price=self.FURNITURE_PRICES["dining_table"][plan.plan_type],
            total_price=self.FURNITURE_PRICES["dining_table"][plan.plan_type],
            notes="1桌4椅"
        ))

        # 卧室家具
        for i in range(room_count):
            bed_type = "主卧" if i == 0 else f"次卧{i}"
            plan.items.append(BudgetItem(
                category="家具费",
                subcategory="卧室",
                item_name=f"{bed_type}床+床垫",
                unit="套",
                quantity=1,
                unit_price=self.FURNITURE_PRICES["bed"][plan.plan_type],
                total_price=self.FURNITURE_PRICES["bed"][plan.plan_type]
            ))
            plan.items.append(BudgetItem(
                category="家具费",
                subcategory="卧室",
                item_name=f"{bed_type}衣柜",
                unit="个",
                quantity=1,
                unit_price=self.FURNITURE_PRICES["wardrobe"][plan.plan_type],
                total_price=self.FURNITURE_PRICES["wardrobe"][plan.plan_type],
                notes="定制衣柜"
            ))
            plan.items.append(BudgetItem(
                category="家具费",
                subcategory="卧室",
                item_name=f"{bed_type}床头柜",
                unit="个",
                quantity=2,
                unit_price=self.FURNITURE_PRICES["desk"][plan.plan_type] * 0.3,
                total_price=2 * self.FURNITURE_PRICES["desk"][plan.plan_type] * 0.3
            ))

        # 书房家具
        if has_study:
            plan.items.append(BudgetItem(
                category="家具费",
                subcategory="书房",
                item_name="书桌+书架",
                unit="套",
                quantity=1,
                unit_price=self.FURNITURE_PRICES["desk"][plan.plan_type],
                total_price=self.FURNITURE_PRICES["desk"][plan.plan_type]
            ))
            plan.items.append(BudgetItem(
                category="家具费",
                subcategory="书房",
                item_name="书椅",
                unit="把",
                quantity=1,
                unit_price=self.FURNITURE_PRICES["desk"][plan.plan_type] * 0.3,
                total_price=self.FURNITURE_PRICES["desk"][plan.plan_type] * 0.3
            ))

        plan.furniture_cost = sum(item.total_price for item in plan.items if item.category == "家具费")

    def _calculate_appliance_cost(
        self,
        plan: BudgetPlan,
        room_count: int,
        bathroom_count: int,
        has_study: bool
    ):
        """计算家电费用"""
        # 客厅家电
        plan.items.append(BudgetItem(
            category="家电费",
            subcategory="客厅",
            item_name="电视",
            unit="台",
            quantity=1,
            unit_price=self.APPLIANCE_PRICES["tv"],
            total_price=self.APPLIANCE_PRICES["tv"]
        ))
        plan.items.append(BudgetItem(
            category="家电费",
            subcategory="客厅",
            item_name="空调",
            unit="台",
            quantity=1 + room_count,
            unit_price=self.APPLIANCE_PRICES["air_conditioner"],
            total_price=(1 + room_count) * self.APPLIANCE_PRICES["air_conditioner"],
            notes="客厅1台+卧室每间1台"
        ))

        # 厨房家电
        plan.items.append(BudgetItem(
            category="家电费",
            subcategory="厨房",
            item_name="油烟机",
            unit="台",
            quantity=1,
            unit_price=self.APPLIANCE_PRICES["range_hood"],
            total_price=self.APPLIANCE_PRICES["range_hood"]
        ))
        plan.items.append(BudgetItem(
            category="家电费",
            subcategory="厨房",
            item_name="燃气灶",
            unit="台",
            quantity=1,
            unit_price=self.APPLIANCE_PRICES["gas_stove"],
            total_price=self.APPLIANCE_PRICES["gas_stove"]
        ))
        plan.items.append(BudgetItem(
            category="家电费",
            subcategory="厨房",
            item_name="热水器",
            unit="台",
            quantity=1,
            unit_price=self.APPLIANCE_PRICES["water_heater"],
            total_price=self.APPLIANCE_PRICES["water_heater"]
        ))

        # 卫生间家电
        plan.items.append(BudgetItem(
            category="家电费",
            subcategory="卫生间",
            item_name="洗衣机",
            unit="台",
            quantity=1,
            unit_price=self.APPLIANCE_PRICES["washing_machine"],
            total_price=self.APPLIANCE_PRICES["washing_machine"]
        ))

        # 餐厅家电
        plan.items.append(BudgetItem(
            category="家电费",
            subcategory="餐厅",
            item_name="冰箱",
            unit="台",
            quantity=1,
            unit_price=self.APPLIANCE_PRICES["refrigerator"],
            total_price=self.APPLIANCE_PRICES["refrigerator"]
        ))

        plan.appliance_cost = sum(item.total_price for item in plan.items if item.category == "家电费")

    def _calculate_soft_decor_cost(self, plan: BudgetPlan, total_area: float):
        """计算软装费用"""
        # 窗帘（每个窗户一套）
        window_count = int(total_area / 15) + 2
        plan.items.append(BudgetItem(
            category="软装费",
            subcategory="窗帘",
            item_name="窗帘套装",
            unit="套",
            quantity=window_count,
            unit_price=self.SOFT_DECOR_PRICES["curtain"],
            total_price=window_count * self.SOFT_DECOR_PRICES["curtain"],
            notes="含轨道/罗马杆"
        ))

        # 灯具
        lamp_count = int(total_area / 20) + 3
        plan.items.append(BudgetItem(
            category="软装费",
            subcategory="灯具",
            item_name="灯具套装",
            unit="套",
            quantity=lamp_count,
            unit_price=self.SOFT_DECOR_PRICES["lamp"],
            total_price=lamp_count * self.SOFT_DECOR_PRICES["lamp"],
            notes="客厅、卧室、餐厅主灯"
        ))

        # 装饰画
        painting_count = int(total_area / 30) + 2
        plan.items.append(BudgetItem(
            category="软装费",
            subcategory="装饰",
            item_name="装饰画",
            unit="幅",
            quantity=painting_count,
            unit_price=self.SOFT_DECOR_PRICES["painting"],
            total_price=painting_count * self.SOFT_DECOR_PRICES["painting"]
        ))

        # 绿植装饰
        plan.items.append(BudgetItem(
            category="软装费",
            subcategory="装饰",
            item_name="绿植盆栽",
            unit="盆",
            quantity=5,
            unit_price=self.SOFT_DECOR_PRICES["plant"],
            total_price=5 * self.SOFT_DECOR_PRICES["plant"]
        ))

        plan.soft_decor_cost = sum(item.total_price for item in plan.items if item.category == "软装费")

    def _calculate_other_cost(self, plan: BudgetPlan, total_area: float):
        """计算其他费用"""
        # 管理费（总价的3-5%）
        estimated_total = (
            plan.base_cost + plan.main_material_cost +
            plan.furniture_cost + plan.appliance_cost + plan.soft_decor_cost
        )
        management_fee = estimated_total * 0.03
        plan.items.append(BudgetItem(
            category="其他费用",
            subcategory="管理费",
            item_name="装修管理费",
            unit="项",
            quantity=1,
            unit_price=management_fee,
            total_price=management_fee,
            notes="工程管理、协调服务"
        ))

        # 垃圾清运费
        plan.items.append(BudgetItem(
            category="其他费用",
            subcategory="清运费",
            item_name="垃圾清运费",
            unit="项",
            quantity=1,
            unit_price=total_area * 15,
            total_price=total_area * 15,
            notes="装修垃圾外运"
        ))

        # 保洁费
        plan.items.append(BudgetItem(
            category="其他费用",
            subcategory="保洁费",
            item_name="开荒保洁",
            unit="项",
            quantity=1,
            unit_price=total_area * 8,
            total_price=total_area * 8,
            notes="装修后首次保洁"
        ))

        plan.other_cost = sum(item.total_price for item in plan.items if item.category == "其他费用")

    def export_to_json(self, filepath: str):
        """导出为JSON格式"""
        data = []
        for plan in self.plans:
            data.append({
                "plan_name": plan.plan_name,
                "plan_type": plan.plan_type,
                "total_area": plan.total_area,
                "cost_breakdown": {
                    "基础装修费": plan.base_cost,
                    "主材费": plan.main_material_cost,
                    "家具费": plan.furniture_cost,
                    "家电费": plan.appliance_cost,
                    "软装费": plan.soft_decor_cost,
                    "其他费用": plan.other_cost
                },
                "total_cost": plan.total_cost,
                "items": [
                    {
                        "category": item.category,
                        "subcategory": item.subcategory,
                        "item_name": item.item_name,
                        "unit": item.unit,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "total_price": item.total_price,
                        "brand": item.brand,
                        "notes": item.notes
                    }
                    for item in plan.items
                ]
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_to_csv(self, filepath: str):
        """导出为CSV格式"""
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['方案', '类别', '子类别', '项目名称', '单位', '数量', '单价', '总价', '品牌', '备注'])

            for plan in self.plans:
                for item in plan.items:
                    writer.writerow([
                        plan.plan_name,
                        item.category,
                        item.subcategory,
                        item.item_name,
                        item.unit,
                        item.quantity,
                        item.unit_price,
                        item.total_price,
                        item.brand,
                        item.notes
                    ])

    def generate_summary(self) -> str:
        """生成预算汇总文本"""
        lines = []
        lines.append("=" * 60)
        lines.append("装修预算费用汇总表")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)

        for plan in self.plans:
            lines.append(f"\n【{plan.plan_name}】")
            lines.append(f"  装修面积：{plan.total_area:.2f} 平方米")
            lines.append(f"  基础装修费：¥{plan.base_cost:,.2f}")
            lines.append(f"  主材费：¥{plan.main_material_cost:,.2f}")
            lines.append(f"  家具费：¥{plan.furniture_cost:,.2f}")
            lines.append(f"  家电费：¥{plan.appliance_cost:,.2f}")
            lines.append(f"  软装费：¥{plan.soft_decor_cost:,.2f}")
            lines.append(f"  其他费用：¥{plan.other_cost:,.2f}")
            lines.append(f"  {'-' * 40}")
            lines.append(f"  预算总价：¥{plan.total_cost:,.2f}")
            lines.append(f"  单方造价：¥{plan.total_cost / plan.total_area:,.2f}/平米")

        return "\n".join(lines)


def main():
    """主函数 - 示例用法"""
    generator = BudgetGenerator()

    # 示例：生成100平米两室一厅一卫的预算
    plans = generator.generate_budget(
        total_area=100,
        room_count=2,
        bathroom_count=1,
        kitchen_type="closed",
        has_balcony=True,
        has_study=False
    )

    # 打印汇总
    print(generator.generate_summary())

    # 导出文件
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    generator.export_to_json(str(output_dir / "budget_economy_standard_luxury.json"))
    generator.export_to_csv(str(output_dir / "budget_economy_standard_luxury.csv"))

    print(f"\n预算文件已导出到 {output_dir}/")


if __name__ == "__main__":
    main()
