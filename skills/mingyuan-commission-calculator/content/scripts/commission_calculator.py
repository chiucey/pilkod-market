#!/usr/bin/env python3
"""
明源佣金计算引擎
用于根据佣金规则和sales数据计算佣金
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class CommissionRule:
    """佣金规则"""
    name: str                           # 规则名称
    role: str                          # 适用角色
    commission_type: str                # 佣金类型
    base: str                           # 计算基数
    rate_or_amount: float              # 比例或金额
    trigger_condition: str = ""         # 触发条件
    start_date: Optional[str] = None   # 有效开始日期
    end_date: Optional[str] = None      # 有效结束日期
    exclude_scope: str = ""            # 排除范围
    priority: int = 3                  # 优先级
    description: str = ""              # 规则描述

    def is_valid(self, transaction_date: str) -> bool:
        """检查规则是否在有效期内"""
        if not transaction_date:
            return True
        if self.start_date and transaction_date < self.start_date:
            return False
        if self.end_date and transaction_date > self.end_date:
            return False
        return True

    def is_excluded(self, note: str) -> bool:
        """检查是否在排除范围内"""
        if not self.exclude_scope or not note:
            return False
        exclusions = [e.strip() for e in self.exclude_scope.split(',')]
        return any(ex in note for ex in exclusions if ex)

    def calculate(self, transaction_price: float, area: float = 0,
                  premium: float = 0, quantity: int = 1) -> float:
        """计算佣金"""
        if self.commission_type == "比例佣金":
            base_amount = self._get_base_amount(transaction_price, premium)
            return base_amount * self.rate_or_amount / 100
        elif self.commission_type == "固定奖励":
            return self.rate_or_amount * quantity
        elif self.commission_type == "阶梯奖励":
            return self._calculate_tiered_commission(quantity)
        elif self.commission_type == "溢价分成":
            return premium * self.rate_or_amount / 100
        else:
            return 0

    def _get_base_amount(self, transaction_price: float, premium: float) -> float:
        """获取计算基数对应的金额"""
        if self.base == "成交总价":
            return transaction_price
        elif self.base == "溢价部分":
            return premium
        elif self.base == "溢价金额":
            return premium
        else:
            return transaction_price

    def _calculate_tiered_commission(self, quantity: int) -> float:
        """计算阶梯佣金（简化版本）"""
        total = 0
        remaining = quantity
        tiers = [
            (5, 2000),    # 前5套，每套2000
            (5, 3000),    # 接下来5套，每套3000
            (999, 5000)   # 超过10套，每套5000
        ]
        for threshold, amount in tiers:
            if remaining <= 0:
                break
            deduct = min(remaining, threshold)
            total += deduct * amount
            remaining -= deduct
        return total


@dataclass
class SalesTransaction:
    """销售交易记录"""
    room_id: str                        # 房间号
    salesperson: str                    # 销售人员
    role: str = ""                      # 角色
    transaction_price: float = 0        # 成交总价
    transaction_date: str = ""          # 成交日期
    area: float = 0                     # 面积
    payment_method: str = ""            # 付款方式
    base_price: float = 0               # 底价
    note: str = ""                      # 备注

    @property
    def premium(self) -> float:
        """溢价金额"""
        return max(0, self.transaction_price - self.base_price)


@dataclass
class CommissionResult:
    """佣金计算结果"""
    room_id: str
    salesperson: str
    role: str
    rule_name: str
    commission_type: str
    base: float
    rate: float
    amount: float
    calculation: str
    transaction_price: float = 0
    area: float = 0


@dataclass
class CommissionSummary:
    """佣金汇总"""
    salesperson: str
    role: str
    transaction_count: int = 0
    total_transaction_price: float = 0
    base_commission: float = 0
    bonus_commission: float = 0

    @property
    def total_commission(self) -> float:
        return self.base_commission + self.bonus_commission


class CommissionCalculator:
    """佣金计算引擎"""

    def __init__(self):
        self.rules: List[CommissionRule] = []
        self.transactions: List[SalesTransaction] = []
        self.results: List[CommissionResult] = []
        self.summary: List[CommissionSummary] = []

    def load_rules(self, rules_data: List[Dict[str, Any]]) -> None:
        """加载佣金规则"""
        self.rules = []
        for r in rules_data:
            rule = CommissionRule(
                name=r.get('规则名称', r.get('name', '')),
                role=r.get('适用角色', r.get('role', '')),
                commission_type=r.get('佣金类型', r.get('commission_type', '比例佣金')),
                base=r.get('计算基数', r.get('base', '成交总价')),
                rate_or_amount=float(r.get('比例/金额', r.get('rate', 0))),
                trigger_condition=r.get('触发条件', r.get('trigger', '')),
                start_date=r.get('有效开始', r.get('start_date')),
                end_date=r.get('有效结束', r.get('end_date')),
                exclude_scope=r.get('排除范围', r.get('exclude', '')),
                priority=int(r.get('优先级', r.get('priority', 3))),
                description=r.get('描述', r.get('description', ''))
            )
            self.rules.append(rule)

        # 按优先级排序
        self.rules.sort(key=lambda x: x.priority)

    def load_transactions(self, transactions_data: List[Dict[str, Any]]) -> None:
        """加载销售数据"""
        self.transactions = []
        for t in transactions_data:
            transaction = SalesTransaction(
                room_id=t.get('房间全称', t.get('room_id', t.get('房间号', ''))),
                salesperson=t.get('业务员', t.get('salesperson', t.get('置业顾问', ''))),
                role=t.get('角色', t.get('role', '')),
                transaction_price=float(t.get('成交总价', t.get('transaction_price', 0))),
                transaction_date=str(t.get('认购日期', t.get('transaction_date', t.get('签约日期', '')))),
                area=float(t.get('面积', t.get('area', 0))),
                payment_method=t.get('付款方式', t.get('payment_method', '')),
                base_price=float(t.get('底价', t.get('base_price', 0))),
                note=t.get('备注', t.get('note', ''))
            )
            self.transactions.append(transaction)

    def calculate(self) -> None:
        """执行佣金计算"""
        self.results = []

        for transaction in self.transactions:
            applicable_rules = self._get_applicable_rules(transaction)

            for rule in applicable_rules:
                if rule.is_excluded(transaction.note):
                    continue

                amount = rule.calculate(
                    transaction.transaction_price,
                    transaction.area,
                    transaction.premium
                )

                if amount > 0:
                    calculation = self._build_calculation_string(rule, transaction, amount)

                    result = CommissionResult(
                        room_id=transaction.room_id,
                        salesperson=transaction.salesperson,
                        role=transaction.role or rule.role,
                        rule_name=rule.name,
                        commission_type=rule.commission_type,
                        base=transaction.transaction_price,
                        rate=rule.rate_or_amount,
                        amount=amount,
                        calculation=calculation,
                        transaction_price=transaction.transaction_price,
                        area=transaction.area
                    )
                    self.results.append(result)

        self._build_summary()

    def _get_applicable_rules(self, transaction: SalesTransaction) -> List[CommissionRule]:
        """获取适用的规则"""
        applicable = []

        for rule in self.rules:
            # 检查角色匹配
            if rule.role and transaction.role:
                if rule.role != transaction.role:
                    continue

            # 检查有效期
            if not rule.is_valid(transaction.transaction_date):
                continue

            # 检查触发条件（简化匹配）
            if rule.trigger_condition:
                if rule.trigger_condition not in transaction.note and \
                   rule.trigger_condition not in transaction.payment_method:
                    continue

            applicable.append(rule)

        return applicable

    def _build_calculation_string(self, rule: CommissionRule,
                                   transaction: SalesTransaction,
                                   amount: float) -> str:
        """构建计算说明字符串"""
        if rule.commission_type == "比例佣金":
            return f"{transaction.transaction_price:.2f} × {rule.rate_or_amount}% = {amount:.2f}"
        elif rule.commission_type == "固定奖励":
            return f"1套 × {rule.rate_or_amount}元 = {amount:.2f}"
        elif rule.commission_type == "阶梯奖励":
            return f"阶梯奖励：{amount:.2f}"
        elif rule.commission_type == "溢价分成":
            return f"({transaction.transaction_price:.2f} - {transaction.base_price:.2f}) × {rule.rate_or_amount}% = {amount:.2f}"
        else:
            return f"计算金额：{amount:.2f}"

    def _build_summary(self) -> None:
        """构建佣金汇总"""
        summary_dict: Dict[str, CommissionSummary] = {}

        for result in self.results:
            key = result.salesperson
            if key not in summary_dict:
                summary_dict[key] = CommissionSummary(
                    salesperson=result.salesperson,
                    role=result.role
                )

            summary = summary_dict[key]
            summary.transaction_count += 1
            summary.total_transaction_price += result.transaction_price

            if result.commission_type == "比例佣金":
                summary.base_commission += result.amount
            else:
                summary.bonus_commission += result.amount

        self.summary = list(summary_dict.values())
        self.summary.sort(key=lambda x: x.total_commission, reverse=True)

    def get_detail_table(self) -> str:
        """获取佣金明细表"""
        lines = []
        lines.append("| 房间全称 | 业务员 | 角色 | 规则名称 | 佣金类型 | 计算基数 | 比例 | 佣金金额 | 计算说明 |")
        lines.append("|---------|--------|------|----------|----------|----------|------|----------|----------|")

        for r in self.results:
            lines.append(f"| {r.room_id} | {r.salesperson} | {r.role} | {r.rule_name} | "
                        f"{r.commission_type} | {r.base:.2f} | {r.rate} | {r.amount:.2f} | {r.calculation} |")

        return '\n'.join(lines)

    def get_summary_table(self) -> str:
        """获取佣金汇总表"""
        lines = []
        lines.append("| 序号 | 业务员 | 角色 | 成交套数 | 成交总额 | 基础佣金 | 奖励佣金 | 总佣金 |")
        lines.append("|-----|--------|------|---------|---------|---------|---------|--------|")

        for i, s in enumerate(self.summary, 1):
            lines.append(f"| {i} | {s.salesperson} | {s.role} | {s.transaction_count} | "
                        f"{s.total_transaction_price:.2f} | {s.base_commission:.2f} | "
                        f"{s.bonus_commission:.2f} | {s.total_commission:.2f} |")

        return '\n'.join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "results": [
                {
                    "room_id": r.room_id,
                    "salesperson": r.salesperson,
                    "role": r.role,
                    "rule_name": r.rule_name,
                    "commission_type": r.commission_type,
                    "base": r.base,
                    "rate": r.rate,
                    "amount": r.amount,
                    "calculation": r.calculation,
                    "transaction_price": r.transaction_price,
                    "area": r.area
                }
                for r in self.results
            ],
            "summary": [
                {
                    "salesperson": s.salesperson,
                    "role": s.role,
                    "transaction_count": s.transaction_count,
                    "total_transaction_price": s.total_transaction_price,
                    "base_commission": s.base_commission,
                    "bonus_commission": s.bonus_commission,
                    "total_commission": s.total_commission
                }
                for s in self.summary
            ]
        }


def parse_rules_from_text(text: str) -> List[Dict[str, Any]]:
    """从文本中解析佣金规则（简化实现）"""
    rules = []

    # 简单的规则提取逻辑
    patterns = [
        r'([\u4e00-\u9fa5a-zA-Z0-9]+)\s*[：:]\s*([\u4e00-\u9fa5]+)',
        r'([\u4e00-\u9fa5]+)\s*×\s*(\d+(?:\.\d+)?)\s*%',
        r'([\u4e00-\u9fa5]+)\s*奖励\s*(\d+(?:\.\d+)?)\s*元',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) >= 2:
                rules.append({
                    'name': f'提取规则{len(rules)+1}',
                    'role': '置业顾问',
                    'commission_type': '比例佣金',
                    'base': '成交总价',
                    'rate': 0,
                    'description': f'{match[0]}: {match[1]}'
                })

    return rules


# 示例使用
if __name__ == "__main__":
    # 创建计算器实例
    calculator = CommissionCalculator()

    # 加载示例规则
    sample_rules = [
        {
            "规则名称": "基础佣金",
            "适用角色": "置业顾问",
            "佣金类型": "比例佣金",
            "计算基数": "成交总价",
            "比例/金额": 3,
            "优先级": 1
        },
        {
            "规则名称": "126㎡以上奖励",
            "适用角色": "置业顾问",
            "佣金类型": "固定奖励",
            "计算基数": "套数",
            "比例/金额": 3000,
            "优先级": 2
        },
        {
            "规则名称": "溢价分成",
            "适用角色": "置业顾问",
            "佣金类型": "溢价分成",
            "计算基数": "溢价部分",
            "比例/金额": 20,
            "优先级": 3
        }
    ]

    calculator.load_rules(sample_rules)

    # 加载示例销售数据
    sample_transactions = [
        {
            "房间全称": "1栋101",
            "业务员": "张三",
            "角色": "置业顾问",
            "成交总价": 1000000,
            "面积": 120,
            "底价": 900000
        },
        {
            "房间全称": "1栋201",
            "业务员": "张三",
            "角色": "置业顾问",
            "成交总价": 1500000,
            "面积": 135,
            "底价": 1300000
        },
        {
            "房间全称": "2栋101",
            "业务员": "李四",
            "角色": "置业顾问",
            "成交总价": 800000,
            "面积": 90,
            "底价": 750000
        }
    ]

    calculator.load_transactions(sample_transactions)

    # 执行计算
    calculator.calculate()

    # 输出结果
    print("=" * 80)
    print("佣金明细表")
    print("=" * 80)
    print(calculator.get_detail_table())
    print()
    print("=" * 80)
    print("佣金汇总表")
    print("=" * 80)
    print(calculator.get_summary_table())
    print()
    print("=" * 80)
    print("JSON格式输出")
    print("=" * 80)
    print(json.dumps(calculator.to_dict(), ensure_ascii=False, indent=2))
