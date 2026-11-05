#!/usr/bin/env python3
"""
社保退休政策参数验证脚本

用于验证：
1. 城市政策配置JSON格式
2. 延迟退休年龄计算
3. 计发月数对应关系
4. 最低缴费年限计算

使用方法：
    python validate_policy_params.py
"""

import json
import sys
from typing import Dict, List, Tuple, Any

# 计发月数标准表（国家统一规定）
STANDARD_ISSUANCE_MONTHS = {
    40: 233, 41: 230, 42: 226, 43: 223, 44: 220,
    45: 216, 46: 212, 47: 207, 48: 204, 49: 199,
    50: 195, 51: 190, 52: 185, 53: 180, 54: 175,
    55: 170, 56: 164, 57: 158, 58: 152, 59: 145,
    60: 139, 61: 132, 62: 125, 63: 117, 64: 109,
    65: 101, 66: 93, 67: 84, 68: 75, 69: 65, 70: 56
}

# 延迟退休配置
DELAY_CONFIG = {
    "male": {"original": 60, "final": 63, "delay_per_4_months": 1},
    "female_worker": {"original": 50, "final": 55, "delay_per_2_months": 1},
    "female_cadre": {"original": 55, "final": 58, "delay_per_4_months": 1}
}

# 最低缴费年限
MIN_CONTRIBUTION_YEARS = {
    2025: 15, 2026: 15, 2027: 15, 2028: 15, 2029: 15,
    2030: 15.5, 2031: 16, 2032: 16.5, 2033: 17, 2034: 17.5,
    2035: 18, 2036: 18.5, 2037: 19, 2038: 19.5, 2039: 20
}

# ============================================================
# 核心假设参数（必展示，可调整）
# ============================================================
DEFAULT_ASSUMPTIONS = {
    "social_wage_growth_rate": 0.05,      # 社平工资年增长率：5%
    "account_interest_rate": 0.04,        # 个人账户年利率：4%
    "inflation_rate": 0.03,               # 通胀率：3%
    "pension_growth_rate": 0.03,          # 养老金年涨幅：3%
    "balance_tolerance": 0.15,            # 余额合理性容差：±15%
}

def get_assumptions(custom: Dict[str, float] = None) -> Dict[str, float]:
    """
    获取计算假设参数

    参数:
    - custom: 自定义参数（如 {"social_wage_growth_rate": 0.03}）

    返回: 合并后的假设参数
    """
    assumptions = DEFAULT_ASSUMPTIONS.copy()
    if custom:
        assumptions.update(custom)
    return assumptions


def format_assumptions_report(assumptions: Dict[str, float]) -> str:
    """
    格式化假设报告（输出报告必含）

    返回: 假设展示文本
    """
    return f"""【核心假设】（以下参数用于本次计算，用户可调整）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 社平工资增长率：{assumptions['social_wage_growth_rate']*100:.0f}%/年（默认5%）
    └ 用于预测未来社平工资和账户积累

💰 个人账户利率：{assumptions['account_interest_rate']*100:.0f}%/年
    └ 按复利计算历年利息

📊 通胀率：{assumptions['inflation_rate']*100:.0f}%/年
    └ 用于计算养老金实际购买力

🔄 养老金年涨幅：{assumptions['pension_growth_rate']*100:.0f}%/年
    └ 退休后按此比例调整（历史惯例）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
如需调整，请告知：如"社平工资按3%增长"、"账户利率按5%计算"
"""


# ============================================================
# 投入产出比计算函数
# ============================================================

def calculate_total_investment(
    monthly_payment: float,
    contribution_months: int,
    inflation_rate: float = None,
    contribution_type: str = "flexible"
) -> Dict[str, float]:
    """
    计算总投入

    参数:
    - monthly_payment: 月缴费金额（元）
    - contribution_months: 缴费月数
    - inflation_rate: 通胀率（默认从假设获取）
    - contribution_type: 参保类型（flexible/employee）

    返回: 投入分析字典
    """
    if inflation_rate is None:
        inflation_rate = DEFAULT_ASSUMPTIONS["inflation_rate"]

    years = contribution_months / 12

    # 不考虑折现的原始投入
    raw_investment = monthly_payment * contribution_months

    # 考虑资金时间价值的投入（简化计算）
    # 假设资金均匀流出，平均存了 years/2 年
    discount_factor = 1 / ((1 + inflation_rate) ** (years / 2))
    discounted_investment = raw_investment * discount_factor

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_months": contribution_months,
        "total_years": round(years, 1),
        "raw_investment": round(raw_investment, 0),
        "discounted_investment": round(discounted_investment, 0),
        "inflation_rate": inflation_rate,
        "discount_factor": round(discount_factor, 3)
    }


def calculate_total_output(
    monthly_pension: float,
    retirement_age: int,
    life_expectancy: int = 85,
    pension_growth_rate: float = None,
    inflation_rate: float = None
) -> Dict[str, float]:
    """
    计算总产出

    参数:
    - monthly_pension: 月养老金（元）
    - retirement_age: 退休年龄
    - life_expectancy: 预期寿命（默认85岁）
    - pension_growth_rate: 养老金年涨幅（默认从假设获取）
    - inflation_rate: 通胀率（默认从假设获取）

    返回: 产出分析字典
    """
    if pension_growth_rate is None:
        pension_growth_rate = DEFAULT_ASSUMPTIONS["pension_growth_rate"]
    if inflation_rate is None:
        inflation_rate = DEFAULT_ASSUMPTIONS["inflation_rate"]

    # 领取年限
    years_received = life_expectancy - retirement_age

    # 不考虑折现的原始产出
    raw_output = monthly_pension * 12 * years_received

    # 考虑养老金增长和通胀的实际购买力
    # 简化：平均增长率约为 (pension_growth_rate - inflation_rate) / 2
    real_growth_rate = (pension_growth_rate - inflation_rate) / 2
    real_discount_factor = 1 / ((1 + inflation_rate + real_growth_rate) ** (years_received / 2))
    discounted_output = raw_output * real_discount_factor

    return {
        "monthly_pension": round(monthly_pension, 2),
        "retirement_age": retirement_age,
        "life_expectancy": life_expectancy,
        "years_received": years_received,
        "raw_output": round(raw_output, 0),
        "discounted_output": round(discounted_output, 0),
        "pension_growth_rate": pension_growth_rate,
        "inflation_rate": inflation_rate,
        "real_growth_rate": round(real_growth_rate, 3)
    }


def calculate_roi_metrics(
    investment: Dict[str, float],
    output: Dict[str, float]
) -> Dict[str, float]:
    """
    计算投入产出比指标

    返回: ROI指标字典
    """
    # 回本年限
    payback_years = investment["raw_investment"] / (output["monthly_pension"] * 12)

    # 投入产出比
    raw_roi_ratio = output["raw_output"] / investment["raw_investment"]
    discounted_roi_ratio = output["discounted_output"] / investment["discounted_investment"]

    # 简单年化收益率（忽略养老金增长）
    years_received = output["years_received"]
    simple_annual_return = (output["raw_output"] - investment["raw_investment"]) / investment["raw_investment"] / years_received * 100

    # 划算判断
    if raw_roi_ratio > 1.5:
        verdict = "优秀 ✅"
    elif raw_roi_ratio > 1.2:
        verdict = "良好 ✓"
    elif raw_roi_ratio > 1.0:
        verdict = "一般"
    else:
        verdict = "亏本 ❌"

    return {
        "payback_years": round(payback_years, 1),
        "raw_roi_ratio": round(raw_roi_ratio, 2),
        "discounted_roi_ratio": round(discounted_roi_ratio, 2),
        "simple_annual_return_pct": round(simple_annual_return, 1),
        "verdict": verdict,
        "net_gain": round(output["discounted_output"] - investment["discounted_investment"], 0)
    }


def analyze_marginal_benefit(
    base_monthly_payment: float,
    base_monthly_pension: float,
    extra_payment: float,
    extra_pension: float,
    pension_growth_rate: float = None
) -> Dict[str, float]:
    """
    边际效益分析

    参数:
    - base_monthly_payment: 基础月缴费
    - base_monthly_pension: 基础月养老金
    - extra_payment: 增量月缴费
    - extra_pension: 增量月养老金
    - pension_growth_rate: 养老金年涨幅

    返回: 边际效益分析
    """
    if pension_growth_rate is None:
        pension_growth_rate = DEFAULT_ASSUMPTIONS["pension_growth_rate"]

    # 增量投入与收益比
    marginal_roi = extra_pension / extra_payment if extra_payment > 0 else 0

    # 考虑养老金增长后的边际收益率
    # 假设领取20年
    years = 20
    growth_factor = ((1 + pension_growth_rate) ** years - 1) / pension_growth_rate if pension_growth_rate > 0 else years
    marginal_total_benefit = extra_pension * 12 * growth_factor
    marginal_total_payment = extra_payment * 12 * years
    marginal_roi_ratio = marginal_total_benefit / marginal_total_payment if marginal_total_payment > 0 else 0

    # 年化边际收益率
    marginal_annual_return = (marginal_roi_ratio - 1) / years * 100 if years > 0 else 0

    # 判断是否划算
    if marginal_annual_return > 5:
        is_worthwhile = "划算 ✅"
    elif marginal_annual_return > 3:
        is_worthwhile = "一般"
    else:
        is_worthwhile = "不太划算"

    return {
        "extra_monthly_payment": round(extra_payment, 2),
        "extra_monthly_pension": round(extra_pension, 2),
        "marginal_roi": round(marginal_roi, 2),
        "marginal_total_benefit": round(marginal_total_benefit, 0),
        "marginal_total_payment": round(marginal_total_payment, 0),
        "marginal_roi_ratio": round(marginal_roi_ratio, 2),
        "marginal_annual_return_pct": round(marginal_annual_return, 1),
        "is_worthwhile": is_worthwhile
    }


def format_roi_report(
    scenario_name: str,
    investment: Dict[str, float],
    output: Dict[str, float],
    roi: Dict[str, float]
) -> str:
    """
    格式化投入产出比报告
    """
    return f"""
【{scenario_name}】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
投入分析：
- 月缴费：{investment['monthly_payment']:.0f}元
- 缴费年限：{investment['total_years']}年
- 总投入（原始）：{investment['raw_investment']:.0f}元
- 总投入（折现）：{investment['discounted_investment']:.0f}元

产出分析：
- 月养老金：{output['monthly_pension']:.0f}元
- 领取年限：{output['years_received']}年
- 总产出（原始）：{output['raw_output']:.0f}元
- 总产出（折现）：{output['discounted_output']:.0f}元

投入产出指标：
- 回本年限：{roi['payback_years']:.1f}年
- 投入产出比：{roi['raw_roi_ratio']:.2f}
- 年化收益率：{roi['simple_annual_return_pct']:.1f}%
- 综合评估：{roi['verdict']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


class ValidationError(Exception):
    """验证错误"""
    pass


def load_city_policy_config(config_path: str) -> Dict[str, Any]:
    """加载并验证城市政策配置"""
    import os
    # 获取脚本所在目录的父目录（即技能根目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(script_dir)
    # 构建相对于技能根目录的路径
    full_path = os.path.join(skill_root, config_path)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise ValidationError(f"配置文件不存在: {full_path}")
    except json.JSONDecodeError as e:
        raise ValidationError(f"JSON格式错误: {e}")


def validate_city_config(config: Dict[str, Any]) -> List[str]:
    """验证城市配置的完整性"""
    errors = []
    required_cities = ["杭州", "上海", "北京", "深圳", "广州", "武汉"]

    if "cities" not in config:
        errors.append("缺少 'cities' 字段")
        return errors

    for city in required_cities:
        if city not in config["cities"]:
            errors.append(f"缺少必需城市配置: {city}")
            continue

        city_config = config["cities"][city]
        required_fields = ["social_avg_wage_monthly", "medical_years_male", "medical_years_female"]

        for field in required_fields:
            if field not in city_config:
                errors.append(f"{city}: 缺少字段 '{field}'")

    return errors


def calculate_delay_retirement_age(birth_year: int, gender: str,
                                    female_type: str = "worker") -> Tuple[int, int]:
    """
    计算延迟后的退休年龄

    返回: (退休年龄, 延迟月数)
    """
    if gender == "male":
        config = DELAY_CONFIG["male"]
        delay_months = (birth_year - 1965) * 12 // 4
    elif gender == "female":
        if female_type == "worker":
            config = DELAY_CONFIG["female_worker"]
            delay_months = (birth_year - 1974) * 12 // 2
        else:  # cadre
            config = DELAY_CONFIG["female_cadre"]
            delay_months = (birth_year - 1971) * 12 // 4
    else:
        raise ValidationError(f"无效性别: {gender}")

    # 限制最大延迟月数
    max_delay = (config["final"] - config["original"]) * 12
    delay_months = min(max(0, delay_months), max_delay)

    retirement_age = config["original"] * 12 + delay_months
    years = retirement_age // 12
    months = retirement_age % 12

    return (years + months / 12, delay_months)


def validate_issuance_months(age: int) -> Tuple[bool, int]:
    """
    验证计发月数

    返回: (是否有效, 正确月数)
    """
    if age not in STANDARD_ISSUANCE_MONTHS:
        return (False, 0)
    return (True, STANDARD_ISSUANCE_MONTHS[age])


def validate_min_contribution_years(retirement_year: int) -> Tuple[bool, float, float]:
    """
    验证最低缴费年限

    返回: (是否有效, 计算年限, 实际年限)
    """
    if retirement_year < 2025:
        return (False, 15, 15)
    if retirement_year > 2039:
        return (True, 20, 20)

    years = MIN_CONTRIBUTION_YEARS.get(retirement_year, 15)
    return (True, years, years)


def calculate_pension(social_avg_wage: float, avg_contribution_index: float,
                       contribution_years: float, account_balance: float,
                       issuance_months: int) -> Dict[str, float]:
    """
    计算养老金

    返回: 包含各项养老金的字典
    """
    # 基础养老金
    basic_pension = (social_avg_wage * (1 + avg_contribution_index) / 2 *
                     contribution_years / 100)

    # 个人账户养老金
    personal_account_pension = account_balance / issuance_months

    # 月养老金总额
    total_monthly = basic_pension + personal_account_pension

    return {
        "basic_pension": round(basic_pension, 2),
        "personal_account_pension": round(personal_account_pension, 2),
        "total_monthly": round(total_monthly, 2)
    }


def validate_hangzhou_women_special_rules(birth_year: int, insurance_year: int,
                                             has_enterprise_record: bool) -> Dict[str, Any]:
    """
    验证杭州女性灵活就业特殊规则

    返回: 退休年龄和建议
    """
    result = {
        "retirement_age": None,
        "reason": "",
        "eligible_for_50": False
    }

    # 判断2025年前是否有浙江参保记录
    if insurance_year < 2025:
        result["eligible_for_50"] = True
        result["reason"] = "2025年前已有浙江参保记录"
    elif has_enterprise_record:
        result["eligible_for_50"] = True
        result["reason"] = "有企业参保记录，按女工人身份"
    else:
        result["eligible_for_50"] = False
        result["reason"] = "2025年后首次参保且无企业记录，需55岁退休"

    # 计算退休年龄
    if result["eligible_for_50"]:
        age, delay = calculate_delay_retirement_age(birth_year, "female", "worker")
        result["retirement_age"] = round(age, 1)
    else:
        age, delay = calculate_delay_retirement_age(birth_year, "female", "worker")
        result["retirement_age"] = 55  # 固定55岁

    return result


def calculate_avg_contribution_index_from_balance(
    account_balance: float,
    contribution_months: int,
    start_year: int,
    end_year: int,
    avg_social_wage: float,
    interest_rate: float = None
) -> float:
    """
    通过账户余额反推平均缴费指数

    参数:
    - account_balance: 账户余额（元）
    - contribution_months: 缴费月数
    - start_year: 开始缴费年份
    - end_year: 结束缴费年份（通常是当前年份）
    - avg_social_wage: 月均社平工资（元）
    - interest_rate: 年化利息率（默认从DEFAULT_ASSUMPTIONS获取）

    返回: 平均缴费指数
    """
    if interest_rate is None:
        interest_rate = DEFAULT_ASSUMPTIONS["account_interest_rate"]

    # 计算缴费年数
    years = contribution_months / 12

    # 利息系数（按复利计算各年缴费的利息）
    # 简化：假设各年缴费均匀分布，平均存了 years/2 年
    interest_factor = 1 + interest_rate * (years / 2)

    # 反推月均缴费本金
    # 账户余额 = 月均本金 × 月数 × 利息系数
    monthly_principal = account_balance / (contribution_months * interest_factor)

    # 反推月均缴费基数（8%进入个人账户）
    monthly_base = monthly_principal / 0.08

    # 计算平均缴费指数 = 月均缴费基数 / 月均社平工资
    avg_index = monthly_base / avg_social_wage

    return round(avg_index, 2)


def validate_account_balance(
    account_balance: float,
    contribution_months: int,
    avg_contribution_index: float,
    avg_social_wage: float
) -> Dict[str, Any]:
    """
    验证账户余额的合理性

    返回: 验证结果（理论值、误差率、是否合理）
    """
    years = contribution_months / 12
    interest_factor = 1 + 0.04 * (years / 2)

    # 计算理论账户余额
    annual_base = avg_social_wage * 12 * avg_contribution_index
    annual_principal = annual_base * 0.08
    theoretical_balance = annual_principal * years * interest_factor

    # 计算误差率
    error_rate = (account_balance - theoretical_balance) / theoretical_balance

    return {
        "theoretical_balance": round(theoretical_balance, 0),
        "actual_balance": account_balance,
        "error_rate": round(error_rate * 100, 1),
        "is_reasonable": abs(error_rate) <= 0.15  # 允许15%误差
    }


def run_tests() -> Tuple[int, int, List[str]]:
    """
    运行所有测试

    返回: (通过数, 失败数, 错误列表)
    """
    passed = 0
    failed = 0
    errors = []

    # 测试1: 延迟退休年龄计算
    print("测试1: 延迟退休年龄计算")
    test_cases = [
        (1975, "male", 62.5, "worker"),   # 1975年男性，延迟30个月
        (1980, "male", 63.0, "worker"),   # 1980年男性，延迟36个月
        (1982, "female", 54.0, "worker"), # 1982年女性工人，(1982-1974)×12÷2=48个月=4年
        (1970, "female", 55.0, "cadre"),  # 1970年女性干部，(1970-1971)<0，最小0
    ]

    for birth_year, gender, expected_age, female_type in test_cases:
        try:
            actual_age, delay = calculate_delay_retirement_age(
                birth_year, gender, female_type
            )
            if abs(actual_age - expected_age) < 0.1:
                print(f"  ✅ {birth_year}年{gender}({female_type}): {actual_age}岁")
                passed += 1
            else:
                print(f"  ❌ {birth_year}年{gender}({female_type}): 期望{expected_age}, 实际{actual_age}")
                failed += 1
                errors.append(f"延迟退休: {birth_year}年{gender}({female_type})")
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
            failed += 1
            errors.append(str(e))

    # 测试2: 计发月数验证
    print("\n测试2: 计发月数验证")
    test_cases = [
        (50, 195), (55, 170), (60, 139), (63, 117)
    ]

    for age, expected_months in test_cases:
        valid, actual_months = validate_issuance_months(age)
        if valid and actual_months == expected_months:
            print(f"  ✅ {age}岁: {actual_months}个月")
            passed += 1
        else:
            print(f"  ❌ {age}岁: 期望{expected_months}, 实际{actual_months if valid else '无效'}")
            failed += 1
            errors.append(f"计发月数: {age}岁")

    # 测试3: 最低缴费年限验证
    print("\n测试3: 最低缴费年限验证")
    test_cases = [
        (2029, 15.0), (2030, 15.5), (2035, 18.0), (2039, 20.0)
    ]

    for year, expected_years in test_cases:
        valid, calc_years, actual_years = validate_min_contribution_years(year)
        if valid and abs(actual_years - expected_years) < 0.1:
            print(f"  ✅ {year}年: {actual_years}年")
            passed += 1
        else:
            print(f"  ❌ {year}年: 期望{expected_years}, 实际{actual_years}")
            failed += 1
            errors.append(f"最低缴费年限: {year}年")

    # 测试4: 养老金计算
    print("\n测试4: 养老金计算")
    basic = calculate_pension(
        social_avg_wage=12000,
        avg_contribution_index=1.0,
        contribution_years=20,
        account_balance=100000,
        issuance_months=139
    )

    expected_basic = 12000 * 2 / 2 * 20 / 100  # 2400
    expected_personal = 100000 / 139  # ~719
    expected_total = expected_basic + expected_personal  # ~3119

    if abs(basic["basic_pension"] - expected_basic) < 1:
        print(f"  ✅ 基础养老金: {basic['basic_pension']}元")
        passed += 1
    else:
        print(f"  ❌ 基础养老金: 期望{expected_basic}, 实际{basic['basic_pension']}")
        failed += 1
        errors.append("基础养老金计算")

    if abs(basic["personal_account_pension"] - expected_personal) < 1:
        print(f"  ✅ 个人账户养老金: {basic['personal_account_pension']}元")
        passed += 1
    else:
        print(f"  ❌ 个人账户养老金: 期望{expected_personal}, 实际{basic['personal_account_pension']}")
        failed += 1
        errors.append("个人账户养老金计算")

    # 测试5: 杭州女性特殊规则
    print("\n测试5: 杭州女性特殊规则")

    test_cases = [
        (1982, 2024, True, 54.0, True),   # 2024年参保，有记录，延迟48个月=4年
        (1985, 2025, False, 55.0, False), # 2025年参保，无记录，55岁
        (1980, 2023, True, 53.0, True),   # 1980年女性工人，延迟36个月=3年，50+3=53岁
    ]

    for birth_year, insurance_year, has_enterprise, expected_age, expected_eligible in test_cases:
        result = validate_hangzhou_women_special_rules(
            birth_year, insurance_year, has_enterprise
        )
        age_ok = abs(result["retirement_age"] - expected_age) < 0.1
        eligible_ok = result["eligible_for_50"] == expected_eligible

        if age_ok and eligible_ok:
            print(f"  ✅ {birth_year}年生，{insurance_year}年参保: {result['retirement_age']}岁, 50岁资格:{result['eligible_for_50']}")
            passed += 1
        else:
            print(f"  ❌ {birth_year}年生，{insurance_year}年参保: 年龄{result['retirement_age']}(期望{expected_age}), 50岁资格:{result['eligible_for_50']}(期望{expected_eligible})")
            failed += 1
            errors.append(f"杭州女性规则: {birth_year}年")

    # 测试6: 通过账户余额反推平均缴费指数
    print("\n测试6: 账户余额反推缴费指数")

    test_cases_balance = [
        # (账户余额, 缴费月数, 开始年, 结束年, 月均社平工资, 期望指数)
        # 公式: 指数 = 余额 / (月数 × 利息系数 × 0.08 × 社平)
        # 58000元: 58000 / (120 × 1.2 × 0.08 × 7743) = 0.65
        (58000, 120, 2018, 2024, 7743, 0.65),
        # 139000元: 139000 / (147 × 1.245 × 0.08 × 7743) = 1.23
        (139000, 147, 2018, 2024, 7743, 1.23),
        # 30000元: 30000 / (60 × 1.1 × 0.08 × 7500) = 0.76
        (30000, 60, 2020, 2024, 7500, 0.76),
    ]

    for balance, months, start_y, end_y, avg_wage, expected_index in test_cases_balance:
        result = calculate_avg_contribution_index_from_balance(
            balance, months, start_y, end_y, avg_wage
        )
        if abs(result - expected_index) <= 0.05:
            print(f"  ✅ 余额{balance}元，{months}月 → 指数{result}")
            passed += 1
        else:
            print(f"  ❌ 余额{balance}元，{months}月 → 期望{expected_index}, 实际{result}")
            failed += 1
            errors.append(f"缴费指数反推: {balance}元")

    # 测试7: 账户余额合理性验证
    print("\n测试7: 账户余额合理性验证")

    validation_cases = [
        # (余额, 月数, 指数, 社平工资, 是否合理)
        # 理论值 = 月数 × 利息系数 × 0.08 × 社平 × 指数
        # 58000元(指数0.65): 理论值约58000，合理
        (58000, 120, 0.65, 7743, True),
        # 50000元(指数1.0): 理论值约89000，偏低不合理
        (50000, 120, 1.0, 7743, False),
        # 139000元(指数1.2): 理论值约136000，合理
        (139000, 147, 1.2, 7743, True),
    ]

    for balance, months, index, wage, expected_reasonable in validation_cases:
        result = validate_account_balance(balance, months, index, wage)
        if result["is_reasonable"] == expected_reasonable:
            print(f"  ✅ 余额{balance}元，指数{index} → 合理:{result['is_reasonable']}, 误差{result['error_rate']}%")
            passed += 1
        else:
            print(f"  ❌ 余额{balance}元，指数{index} → 期望合理:{expected_reasonable}, 实际:{result['is_reasonable']}, 理论值:{result['theoretical_balance']}")
            failed += 1
            errors.append(f"余额验证: {balance}元")

    return passed, failed, errors


def main():
    """主函数"""
    print("=" * 60)
    print("社保退休政策参数验证脚本")
    print("=" * 60)

    # 验证城市配置
    print("\n验证城市政策配置...")
    try:
        config_path = "references/city_policy_rules.json"
        config = load_city_policy_config(config_path)
        errors = validate_city_config(config)
        if errors:
            print("  ⚠️ 配置验证发现以下问题:")
            for error in errors:
                print(f"    - {error}")
        else:
            print("  ✅ 城市配置验证通过")
    except ValidationError as e:
        print(f"  ❌ 配置加载失败: {e}")
        return 1

    # 运行测试
    print("\n" + "=" * 60)
    print("运行功能测试...")
    print("=" * 60)

    passed, failed, errors = run_tests()

    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")

    if failed > 0:
        print("\n失败的测试:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("\n✅ 所有测试通过!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
