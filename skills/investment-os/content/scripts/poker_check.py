#!/usr/bin/env python3
"""
涟漪投资操作系统 - 扑克验证器
功能：交易前风控检查，源自涟漪扑克决策验证器v1.0

触发条件：追涨 / 补仓 / 全仓
输出：PASS / FAIL / 需要V确认

涟漪扑克三问：
  ❓ 第一问：涟漪会追牌吗？
  ❓ 第二问：涟漪会All-in吗？
  ❓ 第三问：涟漪能接受这手输吗？
"""

import json
import sys
import datetime
from typing import Optional


# ==================== 涟漪扑克三问核心逻辑 ====================

def poker_q1_chase(position_info: dict) -> dict:
    """
    ❓ 第一问：涟漪会追牌吗？
    触发：追涨时必须调用
    """
    reasons = []
    conclusion = "追"
    action = "不投资"

    # 追涨场景分析
    stock = position_info.get("stock", "N/A")
    entry_zone = position_info.get("entry_zone", "N/A")
    current_pct = position_info.get("current_pct", 0)  # 当前持仓盈亏%
    vol_ratio = position_info.get("vol_ratio", 1.0)
    ma_trend = position_info.get("ma_trend", "震荡")

    # 涟漪扑克逻辑
    if current_pct > 5:
        reasons.append(f"该标的已有浮盈+{current_pct:.1f}%，追涨是'收益锁定'心理在作祟")
        reasons.append("涟漪知道：在扑克里，有好牌时不加注是愚蠢的，但追涨≠加好注")
        conclusion = "追"
    elif vol_ratio > 2.0:
        reasons.append(f"放量{vol_ratio}x，典型的'追涨放量'，在扑克里=看到公共牌后冲动跟注")
        reasons.append("涟漪知道：放量可能是主力出货，不是买入信号")
        conclusion = "追"
    elif ma_trend == "空头":
        reasons.append("MA空头排列=趋势向下，追涨=逆势，扑克里=明牌诈唬失败后继续跟注")
        reasons.append("涟漪知道：逆势追涨是散户最常见的错误之一")
        conclusion = "追"
    else:
        reasons.append("综合判断：追涨理由不充分")
        conclusion = "不追"
        action = "PASS，可考虑轻仓试探"

    return {
        "question": "❓ 第一问：涟漪会追牌吗？",
        "trigger": "追涨",
        "analysis": reasons,
        "conclusion": conclusion,
        "recommendation": action,
        "pass": conclusion != "追"
    }


def poker_q2_allin(position_info: dict) -> dict:
    """
    ❓ 第二问：涟漪会All-in吗？
    触发：全仓时必须调用
    """
    reasons = []
    confidence = position_info.get("confidence", 5)  # 置信度1-10
    seven_question_score = position_info.get("seven_question_score", 0)
    total_position = position_info.get("total_position", 0)  # 当前总仓位%
    this_trade_position = position_info.get("this_trade_position", 0)  # 本次交易仓位%

    # All-in判断
    if total_position + this_trade_position >= 90:
        reasons.append(f"总仓位{total_position}% + 本次{this_trade_position}% = {total_position+this_trade_position}%")
        reasons.append("涟漪永远不全仓（全仓=扑克里的All-in）")
        reasons.append("涟漪的仓位永远有退路")
        conclusion = "会All-in（错误）"
        action = "FAIL，拒绝全仓，建议≤25%"
        passed = False
    elif seven_question_score >= 9 and confidence >= 9:
        reasons.append(f"七问评分={seven_question_score}，置信度={confidence}，达到All-in条件")
        reasons.append("但涟漪的铁律：永远不全仓，保留30%+现金")
        conclusion = "不会全仓（但可以重仓）"
        action = "降为半仓（≤40%）执行"
        passed = True
    elif total_position >= 60:
        reasons.append(f"当前总仓位{total_position}%，涟漪铁律：总仓位≤80%")
        reasons.append(f"剩余子弹有限，不适合大幅加仓")
        conclusion = "仓位已重，不All-in"
        action = "PASS，本次≤20%"
        passed = True
    else:
        reasons.append("仓位尚轻，可以正常建仓")
        conclusion = "不会All-in"
        action = "PASS，按正常仓位执行"
        passed = True

    return {
        "question": "❓ 第二问：涟漪会All-in吗？",
        "trigger": "全仓",
        "analysis": reasons,
        "conclusion": conclusion,
        "recommendation": action,
        "pass": passed
    }


def poker_q3_can_lose(position_info: dict) -> dict:
    """
    ❓ 第三问：涟漪能接受这手输吗？
    触发：补仓时必须调用
    """
    reasons = []
    risk_pct = position_info.get("risk_pct", 2.0)  # 本笔交易风险占总资金%
    total_loss_today = position_info.get("today_loss_pct", 0)  # 今日亏损%
    consecutive_loss = position_info.get("consecutive_loss", 0)  # 连续亏损次数
    emotional_state = position_info.get("emotional_state", "平静")
    stoploss_pct = position_info.get("stoploss_pct", 5)  # 止损幅度%

    max_acceptable_risk = 2.0  # 涟漪BRM：单笔风险≤2%
    
    # 第三问分析
    if risk_pct > max_acceptable_risk:
        reasons.append(f"本笔交易风险{risk_pct:.1f}% > 涟漪BRM上限{max_acceptable_risk}%")
        reasons.append("涟漪能接受：这手输了不会影响涟漪的情绪和决策")
        reasons.append("但涟漪不能接受：单笔风险超过2%（扑克资金管理铁律）")
        conclusion = "不能接受"
        action = "FAIL，降低仓位使风险≤2%"
        passed = False
    elif emotional_state != "平静":
        reasons.append(f"涟漪当前情绪状态：{emotional_state}（非平静）")
        reasons.append("涟漪知道：情绪不稳定时的决策质量最低")
        reasons.append("涟漪接受：停止，等情绪恢复再决策")
        conclusion = "不能接受（情绪）"
        action = "FAIL，等5分钟，情绪恢复后再评估"
        passed = False
    elif today_loss_today > 3.0:
        reasons.append(f"今日已亏损{today_loss_today:.1f}%，情绪大概率已受影响")
        reasons.append("涟漪知道：亏钱后想回本=报复交易=扑克里的'tilt'")
        conclusion = "不能接受（报复交易风险）"
        action = "FAIL，今日不再开新仓"
        passed = False
    elif consecutive_loss >= 3:
        reasons.append(f"涟漪已连续亏损{consecutive_loss}笔，触发强制系统检查")
        reasons.append("涟漪知道：连续亏损后不停止=继续失血")
        conclusion = "不能接受（系统检查）"
        action = "FAIL，执行系统检查，不报复交易"
        passed = False
    else:
        reasons.append(f"本笔交易风险{risk_pct:.1f}% ≤ {max_acceptable_risk}%")
        reasons.append(f"今日亏损{today_loss_today:.1f}%，情绪{emotional_state}")
        reasons.append("涟漪能接受这手输：即使亏损也不会影响决策和情绪")
        conclusion = "能接受"
        action = "PASS，仓位合适"
        passed = True

    return {
        "question": "❓ 第三问：涟漪能接受这手输吗？",
        "trigger": "补仓",
        "analysis": reasons,
        "conclusion": conclusion,
        "recommendation": action,
        "pass": passed
    }


def poker_validate(action_type: str, position_info: dict) -> dict:
    """
    扑克验证主函数
    action_type: 追涨 / 补仓 / 全仓 / 其他
    position_info: 相关交易信息
    返回：验证结果
    """
    results = []
    all_passed = True
    needs_v_confirm = False

    if action_type in ["追涨", "全仓"]:
        q1 = poker_q1_chase(position_info)
        results.append(q1)
        if not q1["pass"]:
            all_passed = False
            needs_v_confirm = True

    if action_type in ["补仓", "全仓"]:
        q3 = poker_q3_can_lose(position_info)
        results.append(q3)
        if not q3["pass"]:
            all_passed = False
            needs_v_confirm = True

    if action_type == "全仓":
        q2 = poker_q2_allin(position_info)
        results.append(q2)
        if not q2["pass"]:
            all_passed = False
            needs_v_confirm = True

    # 汇总
    if all_passed:
        final_result = "✅ PASS"
        final_action = "可执行，建议按正常仓位建仓"
    elif len([r for r in results if r["pass"]]) > 0:
        final_result = "⚠️ 部分通过"
        final_action = "降低仓位50%执行，或等待更好的时机"
    else:
        final_result = "❌ FAIL"
        final_action = "拒绝执行，等待更好的时机"

    return {
        "action_type": action_type,
        "result": final_result,
        "final_action": final_action,
        "needs_v_confirm": needs_v_confirm,
        "questions": results,
        "timestamp": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M CST"),
    }


def format_output(v: dict) -> str:
    """格式化输出为可读文本"""
    lines = [
        f"\n{'='*50}",
        f"🌊 涟漪扑克验证器 | {v['timestamp']}",
        f"触发类型: {v['action_type']}",
        f"验证结果: {v['result']}",
        f"{'='*50}",
    ]
    for q in v["questions"]:
        lines.append(f"\n{q['question']} ({'✅' if q['pass'] else '❌'})")
        lines.append(f"  触发: {q['trigger']}")
        for r in q["analysis"]:
            lines.append(f"    • {r}")
        lines.append(f"  结论: {q['conclusion']}")
        lines.append(f"  建议: {q['recommendation']}")
    
    lines.append(f"\n{'='*50}")
    lines.append(f"最终判定: {v['result']}")
    lines.append(f"最终行动: {v['final_action']}")
    if v["needs_v_confirm"]:
        lines.append("⚠️ 需要V确认后方可执行")
    lines.append(f"{'='*50}\n")
    return "\n".join(lines)


# ==================== 主程序 ====================

def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    
    # 解析命令行参数
    action_type = "其他"
    position_info = {
        "stock": "N/A",
        "entry_zone": "N/A",
        "current_pct": 0,
        "vol_ratio": 1.0,
        "ma_trend": "震荡",
        "confidence": 5,
        "seven_question_score": 0,
        "total_position": 0,
        "this_trade_position": 0,
        "risk_pct": 2.0,
        "today_loss_pct": 0,
        "consecutive_loss": 0,
        "emotional_state": "平静",
        "stoploss_pct": 5,
    }

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "追涨":
            action_type = "追涨"
        elif arg == "补仓":
            action_type = "补仓"
        elif arg == "全仓":
            action_type = "全仓"
        elif arg.startswith("--stock="):
            position_info["stock"] = arg.split("=", 1)[1]
        elif arg.startswith("--current_pct="):
            try:
                position_info["current_pct"] = float(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--vol_ratio="):
            try:
                position_info["vol_ratio"] = float(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--ma_trend="):
            position_info["ma_trend"] = arg.split("=", 1)[1]
        elif arg.startswith("--total_pos="):
            try:
                position_info["total_position"] = float(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--this_pos="):
            try:
                position_info["this_trade_position"] = float(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--risk_pct="):
            try:
                position_info["risk_pct"] = float(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--7q="):
            try:
                position_info["seven_question_score"] = float(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--emotion="):
            position_info["emotional_state"] = arg.split("=", 1)[1]
        elif arg.startswith("--consecutive_loss="):
            try:
                position_info["consecutive_loss"] = int(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--today_loss="):
            try:
                position_info["today_loss_pct"] = float(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--entry_zone="):
            position_info["entry_zone"] = arg.split("=", 1)[1]
        elif arg.startswith("--confidence="):
            try:
                position_info["confidence"] = float(arg.split("=", 1)[1])
            except ValueError:
                pass

    # 如果没有指定action，从参数推断
    if action_type == "其他":
        if position_info["this_trade_position"] >= 80:
            action_type = "全仓"
        elif position_info["current_pct"] > 0:
            action_type = "追涨"
        else:
            action_type = "补仓"

    print(f"\n{'='*50}", flush=True)
    print(f"🌊 涟漪扑克验证器 v1.0", flush=True)
    print(f"   {now.strftime('%Y-%m-%d %H:%M CST')}", flush=True)
    print(f"{'='*50}", flush=True)

    print(f"\n📋 交易信息:", flush=True)
    print(f"  操作类型: {action_type}", flush=True)
    for k, v in position_info.items():
        if k != "emotional_state":
            print(f"  {k}: {v}", flush=True)
    print(f"  emotional_state: {position_info['emotional_state']}", flush=True)

    result = poker_validate(action_type, position_info)
    output = format_output(result)
    print(output, flush=True)

    print("📋 JSON输出:", flush=True)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    print(f"\n{'='*50}\n", flush=True)

    return result


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[退出]", flush=True)
    except Exception as e:
        print(f"\n[ERROR] {e}", flush=True)
        import traceback
        traceback.print_exc()
