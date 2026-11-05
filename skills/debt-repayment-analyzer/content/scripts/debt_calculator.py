"""
债务还款分析计算器
Debt Repayment Analyzer Calculator
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Debt:
    """单笔债务数据结构"""
    name: str           # 债务名称
    debt_type: str      # 债务类型：信用卡、信用贷、房贷、车贷等
    principal: float    # 本金
    annual_rate: float # 年利率（百分比）
    term_months: int    # 期限（月）
    paid_months: int    # 已还月数
    monthly_payment: float  # 月还款额


def parse_debt_input(text: str) -> List[Debt]:
    """
    解析用户输入的债务数据

    支持格式：
    1. 表格格式（空格分隔）
    2. 自然语言格式

    Args:
        text: 用户输入的债务信息

    Returns:
        Debt对象列表
    """
    debts = []
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

    for line in lines:
        # 跳过表头
        if '名称' in line or '债务' in line and '类型' in line:
            continue
        if line.startswith('#') or line.startswith('-'):
            continue

        parts = line.replace('|', ' ').split()
        if len(parts) >= 6:
            try:
                debt = Debt(
                    name=parts[0],
                    debt_type=parts[1],
                    principal=float(parts[2]),
                    annual_rate=float(parts[3].replace('%', '')),
                    term_months=int(parts[4]),
                    paid_months=int(parts[5]),
                    monthly_payment=float(parts[6]) if len(parts) > 6 else 0
                )
                debts.append(debt)
            except (ValueError, IndexError):
                continue

    return debts


def calculate_monthly_rate(annual_rate: float) -> float:
    """年利率转月利率"""
    return annual_rate / 100 / 12


def calculate_debt_progress(debt: Debt) -> Dict:
    """
    计算单笔债务的还款进度

    Returns:
        包含详细数据的字典
    """
    monthly_rate = calculate_monthly_rate(debt.annual_rate)

    # 计算月供（等额本息）
    if debt.monthly_payment == 0:
        if monthly_rate > 0:
            n = debt.term_months
            r = monthly_rate
            payment = debt.principal * r * (1 + r)**n / ((1 + r)**n - 1)
        else:
            payment = debt.principal / debt.term_months
    else:
        payment = debt.monthly_payment

    # 计算已付利息和已还本金
    total_paid = payment * debt.paid_months
    total_interest_paid = 0

    # 简化计算：按剩余本金比例估算已付利息
    remaining_ratio = 1 - debt.paid_months / debt.term_months
    if remaining_ratio > 0:
        total_interest_paid = total_paid - (debt.principal * (1 - remaining_ratio))

    # 剩余本金（简化计算）
    remaining_principal = debt.principal * remaining_ratio if remaining_ratio > 0 else 0

    # 剩余期限
    remaining_months = max(0, debt.term_months - debt.paid_months)

    # 预估总利息
    if monthly_rate > 0 and payment > 0:
        total_payment = payment * debt.term_months
        total_interest = total_payment - debt.principal
    else:
        total_interest = debt.principal * monthly_rate * debt.term_months

    remaining_interest = total_interest - total_interest_paid

    # 进度百分比
    progress_pct = (debt.paid_months / debt.term_months * 100) if debt.term_months > 0 else 0

    return {
        'debt': debt,
        'monthly_payment': payment,
        'total_paid': total_paid,
        'principal_paid': debt.principal - remaining_principal,
        'interest_paid': total_interest_paid,
        'remaining_principal': remaining_principal,
        'remaining_months': remaining_months,
        'remaining_interest': remaining_interest,
        'total_interest': total_interest,
        'progress_pct': progress_pct
    }


def calculate_total_summary(debts: List[Debt], progress_list: List[Dict]) -> Dict:
    """计算汇总数据"""
    total_principal = sum(d.principal for d in debts)
    total_monthly_payment = sum(d.monthly_payment for d in debts)
    total_remaining = sum(p['remaining_principal'] for p in progress_list)
    total_remaining_months = sum(p['remaining_months'] for p in progress_list)

    # 加权平均利率
    total_weighted_rate = sum(d.principal * d.annual_rate for d in debts)
    avg_rate = total_weighted_rate / total_principal if total_principal > 0 else 0

    # 预估总利息
    total_interest = sum(p['total_interest'] for p in progress_list)
    interest_paid = sum(p['interest_paid'] for p in progress_list)
    remaining_interest = total_interest - interest_paid

    return {
        'total_debt_count': len(debts),
        'total_principal': total_principal,
        'total_monthly_payment': total_monthly_payment,
        'total_remaining': total_remaining,
        'avg_annual_rate': avg_rate,
        'total_term_months': sum(d.term_months for d in debts),
        'total_paid_months': sum(d.paid_months for d in debts),
        'total_remaining_months': total_remaining_months,
        'total_interest': total_interest,
        'interest_paid': interest_paid,
        'remaining_interest': remaining_interest
    }


def generate_repayment_plan(debts: List[Debt], strategy: str = 'avalanche',
                           extra_payment: float = 0) -> List[Dict]:
    """
    生成还款计划

    Args:
        debts: 债务列表
        strategy: 'avalanche' (雪崩法-利率优先) 或 'snowball' (雪球法-余额优先)
        extra_payment: 额外月还款金额

    Returns:
        月度还款计划列表
    """
    # 复制债务数据
    remaining = []
    for d in debts:
        monthly_rate = calculate_monthly_rate(d.annual_rate)
        if monthly_rate > 0:
            n = d.term_months - d.paid_months
            r = monthly_rate
            if r > 0 and n > 0:
                payment = d.principal * r * (1 + r)**n / ((1 + r)**n - 1)
            else:
                payment = d.principal / n if n > 0 else 0
        else:
            payment = d.principal / (d.term_months - d.paid_months) if d.term_months - d.paid_months > 0 else 0

        remaining.append({
            'debt': d,
            'remaining_principal': d.principal - (d.principal * d.paid_months / d.term_months if d.term_months > 0 else 0),
            'monthly_payment': payment,
            'monthly_rate': monthly_rate
        })

    # 根据策略排序
    if strategy == 'avalanche':
        remaining.sort(key=lambda x: x['debt'].annual_rate, reverse=True)
    else:  # snowball
        remaining.sort(key=lambda x: x['remaining_principal'])

    # 生成计划
    plan = []
    month = 1
    available_extra = extra_payment

    while any(r['remaining_principal'] > 0.01 for r in remaining) and month <= 600:
        month_plan = {'month': month, 'payments': [], 'total_payment': 0}

        for item in remaining:
            if item['remaining_principal'] > 0.01:
                # 计算利息
                interest = item['remaining_principal'] * item['monthly_rate']

                # 基础还款
                payment = min(item['monthly_payment'], item['remaining_principal'] + interest)

                # 额外还款（优先给排序靠前的债务）
                if available_extra > 0 and item is remaining[0]:
                    extra = min(available_extra, item['remaining_principal'])
                    payment += extra
                    available_extra -= extra

                principal_paid = payment - interest
                item['remaining_principal'] -= principal_paid

                month_plan['payments'].append({
                    'name': item['debt'].name,
                    'principal': principal_paid,
                    'interest': interest,
                    'total': payment,
                    'remaining': max(0, item['remaining_principal'])
                })
                month_plan['total_payment'] += payment

        if month_plan['payments']:
            plan.append(month_plan)

        month += 1

    return plan


def analyze_and_report(debt_text: str, extra_payment: float = 0) -> str:
    """
    分析债务并生成报表

    Args:
        debt_text: 用户输入的债务信息
        extra_payment: 每月额外还款金额

    Returns:
        格式化报表文本
    """
    debts = parse_debt_input(debt_text)

    if not debts:
        return "❌ 未识别到有效的债务数据，请按以下格式输入：\n\n债务名称 | 类型 | 本金 | 年利率 | 期限(月) | 已还月数 | 月还款额"

    # 计算进度
    progress_list = [calculate_debt_progress(d) for d in debts]

    # 汇总
    summary = calculate_total_summary(debts, progress_list)

    # 生成报表
    report = []
    report.append("=" * 60)
    report.append("📊 债务还款分析报表")
    report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)

    # 一、负债概况
    report.append("\n【一、负债概况】")
    report.append(f"  • 总债务笔数：{summary['total_debt_count']} 笔")
    report.append(f"  • 总负债本金：¥{summary['total_principal']:,.2f}")
    report.append(f"  • 剩余待还本金：¥{summary['total_remaining']:,.2f}")
    report.append(f"  • 月还款总额：¥{summary['total_monthly_payment']:,.2f}")
    report.append(f"  • 加权平均年利率：{summary['avg_annual_rate']:.2f}%")
    report.append(f"  • 已还期限：{summary['total_paid_months']} 个月")
    report.append(f"  • 剩余期限：{summary['total_remaining_months']} 个月")

    # 二、债务明细
    report.append("\n【二、债务明细】")
    report.append("-" * 80)
    report.append(f"{'名称':<12} {'类型':<8} {'本金':>12} {'利率':>8} {'已还':>6} {'剩余本金':>12} {'进度':>8}")
    report.append("-" * 80)

    for p in progress_list:
        d = p['debt']
        report.append(
            f"{d.name:<12} {d.debt_type:<8} ¥{d.principal:>10,.0f} "
            f"{d.annual_rate:>6.2f}% {d.paid_months:>4}月 "
            f"¥{p['remaining_principal']:>10,.0f} {p['progress_pct']:>6.1f}%"
        )
    report.append("-" * 80)

    # 三、还款进度
    report.append("\n【三、还款进度】")
    for p in progress_list:
        d = p['debt']
        bar_len = 30
        filled = int(bar_len * p['progress_pct'] / 100)
        bar = '█' * filled + '░' * (bar_len - filled)
        report.append(f"  {d.name}: [{bar}] {p['progress_pct']:.1f}%")
        report.append(f"    已还本金: ¥{p['principal_paid']:,.0f} | 已付利息: ¥{p['interest_paid']:,.0f}")

    # 四、利息分析
    report.append("\n【四、利息分析】")
    report.append(f"  • 已付利息总额：¥{summary['interest_paid']:,.2f}")
    report.append(f"  • 预估剩余利息：¥{summary['remaining_interest']:,.2f}")
    report.append(f"  • 预估总利息支出：¥{summary['total_interest']:,.2f}")
    report.append(f"  • 利息占本金比例：{(summary['total_interest']/summary['total_principal']*100):.1f}%")

    # 五、还款方案建议
    report.append("\n【五、还款方案建议】")

    # 雪球法
    snowball_plan = generate_repayment_plan(debts, 'snowball', extra_payment)
    snowball_months = len(snowball_plan)
    snowball_total_interest = sum(
        sum(p['interest'] for p in m['payments']) for m in snowball_plan
    )

    # 雪崩法
    avalanche_plan = generate_repayment_plan(debts, 'avalanche', extra_payment)
    avalanche_months = len(avalanche_plan)
    avalanche_total_interest = sum(
        sum(p['interest'] for p in m['payments']) for m in avalanche_plan
    )

    report.append("\n  ┌─────────────────────────────────────────────────────────────────┐")
    report.append("  │                    还款策略对比                                  │")
    report.append("  ├─────────────────────┬─────────────────────┬─────────────────────┤")
    report.append("  │       指标           │   雪球法(余额优先)    │   雪崩法(利率优先)   │")
    report.append("  ├─────────────────────┼─────────────────────┼─────────────────────┤")
    report.append(f"  │   预计还清时间        │     {snowball_months:>3} 个月         │     {avalanche_months:>3} 个月        │")
    report.append(f"  │   预估总利息         │  ¥{snowball_total_interest:>12,.0f}   │  ¥{avalanche_total_interest:>12,.0f}   │")
    report.append("  └─────────────────────┴─────────────────────┴─────────────────────┘")

    if avalanche_total_interest < snowball_total_interest:
        saving = snowball_total_interest - avalanche_total_interest
        report.append(f"\n  💡 建议：采用【雪崩法】可节省利息 ¥{saving:,.0f}，优先偿还高利率债务更划算！")
    else:
        saving = avalanche_total_interest - snowball_total_interest
        report.append(f"\n  💡 建议：采用【雪球法】可节省利息 ¥{saving:,.0f}，先还清小债务可增强信心！")

    # 六、优化建议
    report.append("\n【六、优化建议】")

    # 找出利率最高的债务
    max_rate_debt = max(debts, key=lambda x: x.annual_rate)
    max_rate_pct = max_rate_debt.annual_rate
    avg_rate = summary['avg_annual_rate']

    if max_rate_pct > avg_rate:
        report.append(f"  1. 🔥 优先处理高利率债务：{max_rate_debt.name} ({max_rate_pct}%)")
        report.append(f"     当前利率偏高，建议考虑低息贷款置换或协商降息")

    if extra_payment > 0:
        report.append(f"  2. 💰 额外还款效果：每月多还 ¥{extra_payment:,.0f}")
        avalanche_savings = snowball_months - avalanche_months
        if avalanche_savings > 0:
            report.append(f"     采用雪崩法可提前约 {avalanche_savings} 个月还清")

    # 债务类型建议
    credit_card_debts = [d for d in debts if '信用卡' in d.debt_type]
    if credit_card_debts:
        report.append(f"  3. 💳 信用卡优化：")
        report.append(f"     检测到 {len(credit_card_debts)} 笔信用卡债务")
        report.append(f"     建议：将信用卡债务转为分期或信用贷，降低利息成本")

    report.append("\n" + "=" * 60)
    report.append("报表生成完毕。如需调整参数或有其他债务信息，请继续补充。")
    report.append("=" * 60)

    return '\n'.join(report)


# 交互式输入处理
def parse_natural_language(text: str) -> List[Debt]:
    """
    从自然语言中解析债务信息

    示例：
    "信用卡5万，年利率18%，已经还了3个月，每月还4500"
    """
    import re

    debts = []

    # 匹配模式：名称 + 金额 + 利率 + 已还月数
    patterns = [
        r'([^\s\d]+)[\s\:：]*(\d+(?:\.\d+)?)\s*(?:万|元)',  # 名称 + 金额
        r'(\d+(?:\.\d+)?)\s*(?:万|元)[^\d]*?(\d+(?:\.\d+)?)\s*%',
        r'(\d+)\s*(?:%|年利率)',
    ]

    # 简化实现：按常见格式解析
    lines = text.replace('；', ';').replace('，', ',').split(';')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 提取数字
        numbers = re.findall(r'\d+(?:\.\d+)?', line)
        if len(numbers) < 2:
            continue

        # 确定债务类型
        debt_type = '其他'
        if '信用卡' in line or '卡' in line:
            debt_type = '信用卡'
        elif '房贷' in line or '房子' in line:
            debt_type = '房贷'
        elif '车贷' in line or '车' in line:
            debt_type = '车贷'
        elif '信用贷' in line or '贷款' in line:
            debt_type = '信用贷'

        # 确定金额
        principal = 0
        for n in numbers:
            val = float(n)
            if val >= 100:
                principal = val if val < 1000 else val * 10000  # 假设>1000为元，否则为万
                break

        # 确定利率
        rate_match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
        annual_rate = float(rate_match.group(1)) if rate_match else 0

        # 确定已还月数
        paid_match = re.search(r'已[还支付]?\s*(\d+)\s*(?:个)?月', line)
        paid_months = int(paid_match.group(1)) if paid_match else 0

        # 确定月还款
        payment_match = re.search(r'(?:每月|月供)\s*[还]?\s*(\d+(?:\.\d+)?)', line)
        monthly_payment = float(payment_match.group(1)) if payment_match else 0

        # 确定期限
        term_match = re.search(r'(\d+)\s*(?:期|个月)', line)
        term_months = int(term_match.group(1)) if term_match else 12

        if principal > 0:
            name = f"{debt_type}{len([d for d in debts if d.debt_type == debt_type]) + 1}"
            debts.append(Debt(
                name=name,
                debt_type=debt_type,
                principal=principal,
                annual_rate=annual_rate,
                term_months=term_months,
                paid_months=paid_months,
                monthly_payment=monthly_payment
            ))

    return debts


if __name__ == "__main__":
    # 测试代码
    test_input = """信用卡1  信用卡  50000  18  12  3  4500
信用贷1  信用贷  100000  12  24  6  5000
房贷     房贷    2000000  4.9  360  12  10600"""

    print(analyze_and_report(test_input, extra_payment=1000))
