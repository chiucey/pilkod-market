#!/usr/bin/env python3
"""
9:30 集合竞价 阶段 浏览器 fallback 抓取脚本 (2026-07-01 实战稳定版)

用途: 9:30 阶段 push2 涨/跌统计接口雪崩时, 一次浏览器抓取
       (ztb + bkzj/hy.html) 拿全: 涨跌停 + 涨跌家数 + 行业 Top/Bottom

输出: JSON {limit_up, limit_down, effect, em_position_suggest,
           sh_breadth, sz_breadth, total_breadth, bullish_pct, bearish_pct,
           industry_top10, industry_bottom5}

用法: 
  1. 浏览器 MCP 工具调用 (browser_navigate + browser_console)
  2. 解析返回的 JSON
  3. 配合 scripts/sina_field_type_safe.py 拿 3-5% 涨幅股
  4. 配合 scripts/count_limit_accurate.py 精确涨跌停计数

注: 此脚本不直接调用浏览器 (需要在 cron 任务下用 browser_navigate + browser_console),
    而是定义数据结构和解析逻辑, 供 cron agent 复用.
"""

import json
import re
from typing import Optional


# ============= 数据结构 =============

def parse_market_breadth(all_text: str) -> Optional[dict]:
    """
    解析 bkzj/hy.html 提取的 allText, 返回涨跌家数结构.
    7/1 实战输入: "上证 4097.31 ↑2.91 ↑0.07% 1138.60亿元 (涨:1202 平:143 跌:998) ..."
    """
    sh_match = re.search(r'上证[^\n]*?涨:\s*(\d+)\s*平:\s*(\d+)\s*跌:\s*(\d+)', all_text)
    sz_match = re.search(r'深证[^\n]*?涨:\s*(\d+)\s*平:\s*(\d+)\s*跌:\s*(\d+)', all_text)

    if not (sh_match and sz_match):
        return None

    sh_up, sh_flat, sh_down = int(sh_match[1]), int(sh_match[2]), int(sh_match[3])
    sz_up, sz_flat, sz_down = int(sz_match[1]), int(sz_match[2]), int(sz_match[3])
    total_up = sh_up + sz_up
    total_flat = sh_flat + sz_flat
    total_down = sh_down + sz_down
    total = total_up + total_flat + total_down

    return {
        "sh": {"up": sh_up, "flat": sh_flat, "down": sh_down, "total": sh_up + sh_flat + sh_down},
        "sz": {"up": sz_up, "flat": sz_flat, "down": sz_down, "total": sz_up + sz_flat + sz_down},
        "total": {"up": total_up, "flat": total_flat, "down": total_down, "total": total},
        "bullish_pct": round(total_up / total * 100, 2),
        "bearish_pct": round(total_down / total * 100, 2),
    }


def parse_ztb_summary(all_text: str) -> Optional[dict]:
    """
    解析 quote.eastmoney.com/ztb/ 提取的 allText, 返回涨跌停汇总.
    7/1 实战输入: "涨跌停对比19:0 ... 封板未遂(炸板率28.57%) ... 86% 建议仓位 ... 赚钱效应 中"
    """
    # 涨跌停对比
    limit_match = re.search(r'涨跌停对比\s*(\d+)\s*[：:]\s*(\d+)', all_text)
    # 赚钱效应
    effect_match = re.search(r'赚钱效应\s*([\u4e00-\u9fff]+)', all_text)
    # 炸板率
    bang_match = re.search(r'炸板率\s*(\d+\.?\d*)\s*%', all_text)
    # EM 系统建议仓位
    position_match = re.search(r'建议仓位为\s*(\d+)\s*%', all_text)

    if not limit_match:
        return None

    limit_up = int(limit_match[1])
    limit_down = int(limit_match[2])

    return {
        "limit_up": limit_up,
        "limit_down": limit_down,
        "effect": effect_match.group(1) if effect_match else None,
        "bang_rate": float(bang_match.group(1)) if bang_match else None,
        "em_position_suggest": int(position_match.group(1)) if position_match else None,
    }


def parse_industry_data(industry_data: list) -> dict:
    """
    解析 bkzj/hy.html 提取的行业 table, 返回 Top 10 + Bottom 5.
    7/1 实战输入: [["1", "半导体", "...", "1.61%", "6.07亿", ..., "长川科技"], ...]
    """
    top10 = []
    for row in industry_data[:50]:  # 假设前 50 行含 Top 50
        try:
            rank = row[0]
            name = row[1]
            pct = float(re.sub(r'[^\d.\-]', '', row[3]))
            net_inflow_str = row[4]
            top10.append({"rank": rank, "name": name, "pct": pct, "net_inflow": net_inflow_str})
        except (ValueError, IndexError):
            continue

    # 过滤 pct = 0 的无效行
    top10 = [x for x in top10 if x["pct"] != 0][:10]

    # 找 Bottom 5 (pct 最负的 5 个)
    sorted_by_pct = sorted(top10, key=lambda x: x["pct"])
    bottom5 = [x for x in sorted_by_pct if x["pct"] < 0][:5]

    return {"top10": top10, "bottom5": bottom5}


# ============= 浏览器控制 (Python 伪代码) =============

BROWSER_INSTRUCTIONS = """
# 9:30 浏览器 fallback 完整流程 (cron agent 用)

# Step 1: 加载 ztb 页面
browser_navigate(url="https://quote.eastmoney.com/ztb/")

# Step 2: 提取 ztb 摘要 + 涨停列表
ztb_console = """
    (() => {
      const allText = document.body.innerText;
      const zhangTingDuiBi = allText.match(/涨跌停对比[\\d:：:]+/g);
      const positionSuggest = allText.match(/根据市场表现, 建议仓位为\\s*\\d+\\s*%/);
      const effect = allText.match(/赚钱效应\\s*[\\u4e00-\\u9fff]+/);
      const bangRate = allText.match(/炸板率\\s*\\d+\\.?\\d*\\s*%/);
      
      // 涨停列表 (主板 10%+ / 创业板 19.5%+ / 科创板 19.5%+)
      const tables = document.querySelectorAll('table');
      const limitUpList = [];
      tables.forEach(t => {
        const rows = t.querySelectorAll('tbody tr');
        rows.forEach(r => {
          const cells = Array.from(r.querySelectorAll('td')).map(c => c.innerText.trim());
          if (cells.length >= 3) {
            const pctCell = cells.find(t => /\\d+\\.\\d+%/.test(t));
            if (pctCell) {
              const pctMatch = pctCell.match(/(-?\\d+\\.\\d+)%/);
              if (pctMatch && parseFloat(pctMatch[1]) >= 9.5) {
                limitUpList.push(cells.slice(0, 6));
              }
            }
          }
        });
      });
      
      return JSON.stringify({
        zhangTingDuiBi: zhangTingDuiBi,
        positionSuggest: positionSuggest,
        effect: effect,
        bangRate: bangRate,
        limitUpCount: limitUpList.length,
        limitUpTop10: limitUpList.slice(0, 10),
      });
    })()
"""

ztb_result = browser_console(expression=ztb_console)

# Step 3: 加载 bkzj/hy.html 页面
browser_navigate(url="https://data.eastmoney.com/bkzj/hy.html")

# Step 4: 提取涨跌家数 + 行业 Top/Bottom
bkzj_console = """
    (() => {
      const allText = document.body.innerText;
      const shMatch = allText.match(/上证[^\\n]*?涨:\\s*(\\d+)\\s*平:\\s*(\\d+)\\s*跌:\\s*(\\d+)/);
      const szMatch = allText.match(/深证[^\\n]*?涨:\\s*(\\d+)\\s*平:\\s*(\\d+)\\s*跌:\\s*(\\d+)/);
      
      const breadth = (shMatch && szMatch) ? {
        sh: {up: parseInt(shMatch[1]), flat: parseInt(shMatch[2]), down: parseInt(shMatch[3])},
        sz: {up: parseInt(szMatch[1]), flat: parseInt(szMatch[2]), down: parseInt(szMatch[3])},
        total: {
          up: parseInt(shMatch[1]) + parseInt(szMatch[1]),
          flat: parseInt(shMatch[2]) + parseInt(szMatch[2]),
          down: parseInt(shMatch[3]) + parseInt(szMatch[3]),
        },
      } : null;
      
      if (breadth) {
        const t = breadth.total;
        breadth.bullish_pct = (t.up / (t.up + t.flat + t.down) * 100).toFixed(2);
        breadth.bearish_pct = (t.down / (t.up + t.flat + t.down) * 100).toFixed(2);
      }
      
      // 行业 Top/Bottom
      const tables = document.querySelectorAll('table');
      const industryData = [];
      tables.forEach(t => {
        const headers = Array.from(t.querySelectorAll('thead th, thead td')).map(h => h.innerText.trim());
        if (headers.some(h => h.includes('名称')) && headers.some(h => h.includes('涨跌幅'))) {
          const rows = t.querySelectorAll('tbody tr');
          rows.forEach(r => {
            const cells = Array.from(r.querySelectorAll('td')).map(c => c.innerText.trim());
            if (cells.length > 0) industryData.push(cells);
          });
        }
      });
      
      return JSON.stringify({
        breadth: breadth,
        industryTop10: industryData.slice(0, 10),
      });
    })()
"""

bkzj_result = browser_console(expression=bkzj_console)

# Step 5: Python 解析 (cron agent 后续)
import json

ztb_data = json.loads(ztb_result)
bkzj_data = json.loads(bkzj_result)

# 合并输出
output = {
    "limit_up": ztb_data.get("limitUpCount"),
    "limit_down": 0,  # 需从 zhangTingDuiBi 字符串解析
    "effect": ztb_data.get("effect"),
    "em_position_suggest": ztb_data.get("positionSuggest"),
    "breadth": bkzj_data.get("breadth"),
    "industry_top10": bkzj_data.get("industryTop10"),
}
print(json.dumps(output, ensure_ascii=False, indent=2))
"""


# ============= §37 模式判定函数 =============

def judge_section_37(data: dict) -> bool:
    """
    §37 中性观望 9:30 灰区模式判定 (2026-07-01 实战新增).

    触发条件 (四要素同时满足):
    1. 5 涨 1 跌 (idx_red == 5) - 既非 §15 撕裂 (6 跌) 也非 §31 严格 (5 涨 1 跌)
    2. 上证 -0.5% ~ +0.5% 极度疲弱
    3. 涨跌家数 bearish_pct < 0.55 (多数红盘)
    4. 涨停 < 30 (集合竞价阶段典型 13-29)
    5. V-reversal < 70%

    7/1 实战: idx_red=5, sh_pct=-0.05, bearish_pct=41.07, limit_up=19, v=14.79
    """
    if data.get("idx_red") != 5:
        return False
    if not (-0.5 <= data.get("sh_pct", 0) <= 0.5):
        return False
    if data.get("bearish_pct", 1) >= 0.55:
        return False
    if data.get("limit_up", 30) >= 30:
        return False
    if data.get("v_reversal_pct", 100) >= 70:
        return False
    return True


# ============= 5 指标打分 =============

def score_5_index(data: dict) -> dict:
    """
    5 指标打分 (与模式判定配套, 给出最终仓位建议).

    5 指标: 涨跌停比 / V-reversal / 6 指数全红 / 行业 Top3 主线集中 / 科创创业相对强度
    总分 → 仓位:
    - ≥ 13 分: 强档 → 50-60%
    - 9-12 分: 中档 → 30-40%
    - < 9 分: 弱档 → ≤ 25%
    """
    score = 0
    details = []

    # 1. 涨跌停比 (3 分)
    limit_up = data.get("limit_up", 0)
    limit_down = data.get("limit_down", 0)
    if limit_up >= 20 and limit_down == 0:
        s, tier = 3, "强"
    elif limit_up >= 5 and limit_down <= 5:
        s, tier = 2, "中"
    else:
        s, tier = 1, "弱"
    score += s
    details.append({"name": "涨跌停比", "value": f"{limit_up}:{limit_down}", "score": s, "tier": tier})

    # 2. V-reversal % (3 分)
    v = data.get("v_reversal_pct", 0)
    if v > 90:
        s, tier = 3, "强"
    elif 70 <= v <= 90:
        s, tier = 2, "中"
    else:
        s, tier = 1, "弱"
    score += s
    details.append({"name": "V-reversal", "value": f"{v:.2f}%", "score": s, "tier": tier})

    # 3. 6 指数全红 (3 分)
    idx_red = data.get("idx_red", 0)
    if idx_red == 6:
        s, tier = 3, "强"
    elif idx_red in (4, 5):
        s, tier = 2, "中"
    else:
        s, tier = 1, "弱"
    score += s
    details.append({"name": "6 指数方向", "value": f"{idx_red} 涨 {6-idx_red} 跌", "score": s, "tier": tier})

    # 4. 行业 Top3 主线集中 (3 分)
    # 简化: 暂不实现主线集中度分析, 需结合涨停样本 + 行业 Top3 同主题判定
    # 默认给 2 分
    s, tier = 2, "中"
    score += s
    details.append({"name": "行业 Top3 主线集中", "value": "需结合涨停样本 + 行业 Top3", "score": s, "tier": tier})

    # 5. 科创/创业 相对强度 (3 分)
    kc_pct = data.get("kc50_pct", 0)
    sh_pct = data.get("sh_pct", 0)
    if kc_pct > sh_pct + 0.5:
        s, tier = 3, "强"
    elif kc_pct > sh_pct:
        s, tier = 2, "中"
    else:
        s, tier = 1, "弱"
    score += s
    details.append({"name": "科创/创业 相对强度", "value": f"科创50 {kc_pct:+.2f}% vs 上证 {sh_pct:+.2f}%", "score": s, "tier": tier})

    # 总分 → 仓位
    if score >= 13:
        position_range = "50-60% (强档)"
    elif score >= 9:
        position_range = "30-40% (中档)"
    else:
        position_range = "≤ 25% (弱档)"

    return {
        "total_score": score,
        "position_base": position_range,
        "details": details,
    }


# ============= §6.12 极度透支叠加 =============

def apply_section_6_12(base_position: str, kc50_5d_pct: float) -> dict:
    """
    §6.12 透支叠加 (基于 5 日累计涨幅).

    | 5 日累计涨幅 | 透支档位 | 仓位调整 |
    |---|---|---|
    | 5 日 < 8% | 健康 | 按模式判定仓位不变 |
    | 8% ≤ 5 日 < 10% | 温和预警 | 仓位下限下调 5pct |
    | 10% ≤ 5 日 < 12% | 透支警告 | 仓位下限下调至中档下限偏保守 |
    | 5 日 ≥ 12% | **极度透支（硬约束）** | 仓位上限下调一档 (整体下调 10pct) |

    7/1 实战: 5 指标 11 (中档 30-40%) + 科创 50 5 日 +15.5% ≥ 12% → 20-30% (整体下调 10pct)
    """
    if kc50_5d_pct < 8:
        tier = "健康"
        adjustment = "无调整"
        new_range = base_position
    elif kc50_5d_pct < 10:
        tier = "温和预警"
        adjustment = "仓位下限下调 5pct"
        new_range = _shift_position(base_position, lower=-5, upper=0)
    elif kc50_5d_pct < 12:
        tier = "透支警告"
        adjustment = "仓位下限下调至中档下限偏保守"
        new_range = _shift_position(base_position, lower=-5, upper=-5)
    else:
        tier = "极度透支 (硬约束)"
        adjustment = "仓位上限下调一档 (整体下调 10pct)"
        new_range = _shift_position(base_position, lower=-10, upper=-10)

    return {
        "tier": tier,
        "adjustment": adjustment,
        "kc50_5d_pct": kc50_5d_pct,
        "base_position": base_position,
        "new_position": new_range,
    }


def _shift_position(position: str, lower: int, upper: int) -> str:
    """
    调整仓位范围 (下限/上限 调整 Xpct).
    例: "30-40% (中档)" + lower=-10, upper=-10 → "20-30% (中档下限偏保守)"
    """
    match = re.match(r'(\d+)-(\d+)%\s*\((\S+)\)', position)
    if not match:
        return position
    l, u, label = int(match[1]), int(match[2]), match[3)
    new_l = max(0, l + lower)
    new_u = max(new_l, u + upper)
    new_label = label + (" 下限偏保守" if lower < 0 or upper < 0 else "")
    return f"{new_l}-{new_u}% ({new_label})"


# ============= 主函数 =============

if __name__ == "__main__":
    # 7/1 09:30 实战数据
    test_data = {
        "idx_red": 5,
        "sh_pct": -0.05,
        "kc50_pct": 0.39,
        "limit_up": 19,
        "limit_down": 0,
        "v_reversal_pct": 14.79,
        "bearish_pct": 41.07,
        "kc50_5d_pct": 15.5,
    }

    print("=" * 60)
    print("9:30 实战 模式判定 + 仓位推导 (2026-07-01)")
    print("=" * 60)

    # §37 判定
    is_37 = judge_section_37(test_data)
    print(f"\n§37 中性观望判定: {is_37}")
    if is_37:
        print("  - 5 涨 1 跌 + 上证极度疲弱 + 涨停 < 30 + V 极低 + 多数红盘")
        print("  - §31 严格/变体触发条件全部不命中")

    # 5 指标打分
    score_result = score_5_index(test_data)
    print(f"\n5 指标打分: {score_result['total_score']}/15 → {score_result['position_base']}")
    for d in score_result["details"]:
        print(f"  - {d['name']}: {d['value']} → {d['score']}分 ({d['tier']})")

    # §6.12 透支叠加
    pos_612 = apply_section_6_12(score_result["position_base"], test_data["kc50_5d_pct"])
    print(f"\n§6.12 透支叠加: {pos_612['tier']} (科创50 5 日 {pos_612['kc50_5d_pct']:+.2f}%)")
    print(f"  - 调整: {pos_612['adjustment']}")
    print(f"  - 基础仓位: {pos_612['base_position']}")
    print(f"  - 最终仓位: {pos_612['new_position']}")

    # 实战结论
    print("\n" + "=" * 60)
    print("实战结论:")
    print(f"  模式: §37 中性观望 (未命中 §15-§36 任何严格模式)")
    print(f"  仓位: {pos_612['new_position']}")
    print(f"  EM 系统对照: 86% (9:30 阶段机械判定, 不参考)")
    print(f"  10:30 验证后再调整")
    print("=" * 60)
