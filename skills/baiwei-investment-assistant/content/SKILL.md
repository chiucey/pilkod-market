---
name: baiwei-investment-assistant
description: 八维投研助手。A股企业价值分析系统，支持宏观周期定位、行业景气扫描、财务估值建模、买入决策、心理控制、长期持有全流程。当用户要求分析股票、进行估值、查找合理买入区间、评估基本面、长期持有建议时使用。
---

# 八维投研助手

## 功能概述

整合八层投资框架（第0层战略推演至第7层长期持有）、28本投资经典、25个分析技能的A股/港股企业价值分析系统。支持宏观周期定位、行业景气扫描、财务估值建模、买入决策、心理控制、长期持有全流程。用户只需提供股票名称/代码，即可获得结构化分析报告，并自动调用所有可用技能模块。

## 触发词

- 企业价值分析
- 估值
- 合理区间
- 基本面
- 长期持有
- 八层分析
- 分析{股票名称}

## 配置项（用户安装后需填写）

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| eastmoney_api_key | string | 是 | 东方财富官方 Skills 接口 API Key |
| pdf_extractor_service | string | 否 | PDF 提取服务类型：parseur, google_docai, azure，默认 parseur |
| pdf_extractor_api_key | string | 否 | 对应服务的 API Key（若使用） |
| webhook_url | string | 否 | 实时推送的企业微信/钉钉 Webhook 地址 |

## 依赖项

- requests
- pandas
- pyyaml
- openpyxl
- matplotlib
- akshare

## 八层投资框架说明

### 第0层：战略推演（历史节点定位）
- 康波周期阶段
- 四周期嵌套定位
- 大类资产时钟指向
- 历史动力学指数

### 第1层：宏观定位（货币·信用·增长·政策）
- 10年期国债收益率
- 美元/人民币汇率
- 美联储降息预期
- PPI/CPI/PMI
- 政策方向

### 第2层：行业分析（景气度·五力·另类数据）
- 五力模型评估
- 行业景气度指数
- 另类数据信号
- 供应链安全评级
- 国产替代进度

### 第3层：市场定位（估值水位·情绪·外资）
- PE历史分位（5年）
- PB历史分位（5年）
- 股债收益率对比
- 外资机构仓位变化
- 市场情绪指标

### 第4层：财务估值（DCF·ROE·PEG·行业模板）
- DCF内在价值
- 预测 EPS
- ROE × PB 联合判断
- PEG指标
- 行业模板定位

### 第5层：买入决策（86体系·39体系·王子落难·逆向大师）
- 86体系评分（8好+6便宜）
- 39体系状态
- 王子落难匹配度
- 逆向大师信号
- 决策记录

### 第6层：心理控制（决策日志·博弈模拟·多空碰撞）
- 当前认知偏误检查
- 群体疯狂识别
- 博弈模拟器预判
- 多空观点对比

### 第7层：长期持有（卖出原则·让跑继续跑）
- 基本面趋势
- 估值极端泡沫检测
- 更好机会发现
- 当前状态

## 使用示例

- "分析贵州茅台"
- "分析600519"
- "帮我分析一下比亚迪的基本面"
- "八层分析中国平安"

## 输出格式

技能将输出包含以下内容的结构化报告：
- 公司名称和股票代码
- 当前股价
- 八层分析结果
- 合理估值区间
- 操作建议
- 期望回报
- 核心风险
- 决策准确率跟踪

## 注意事项

- 本分析基于公开数据与量化模型，仅供参考
- 不构成投资建议
- 投资决策需谨慎

```python
import re
import json
import yaml
import requests
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

# ========== 调用已有技能模块（假设通过 import 导入） ==========
# 这些模块应已安装在 MaxClaw 环境中，若未安装则需在依赖中添加
# 按照用户提供的技能列表，尝试导入（若失败则置为None）
try:
    from skills import (
        a_stock_hk_analysis,        # A股/港股分析
        stock_analysis,             # 美股分析
        valuation_automation,       # DCF自动估值
        quant_ai_fusion,            # 量化+AI
        historical_cycle_locator,   # 康波/库存周期
        regime_switch_detector,     # 风格切换
        cn_stock_news_monitor,      # A股新闻监控
        vn_market_news_monitor,     # 越南市场新闻
        commodity_geo_monitor,      # 大宗商品+港口
        supply_chain_radar,         # 供应链雷达
        macro_data_skill,           # 宏观数据
        service_tech_intensity,     # 软件/专利数据
        earnings_season_scanner,    # 财报季扫描
        fifteen_five_scanner,       # 十五五规划扫描
        anti_involution_screener,   # 反内卷化筛选
        dgr,                        # 决策日志复盘
        post_decision_analyzer,     # 决策准确率统计
        game_simulator,             # 博弈模拟器
        skill_firewall,             # 安全审查
        skill_namer,                # 技能命名规范
        gitbackup,                  # Git备份
        fullbackup,                 # 全量备份
        safe_backup,                # 安全备份
        eastmoney_client,           # 东方财富API
        pdf_annual_report,          # PDF年报提取
        alternative_data_fusion,    # 另类数据融合
        realtime_market_watcher,    # 实时行情预警
        multi_language_research,    # 多语言研报
        automation_workflows,       # 自动化流程
        goal_mode,                  # 主动式目标追踪
        crawl4ai,                   # 智能网页提取
        operator_humanizer,         # 去AI痕迹
        evolve_skill,               # 自繁衍技能
        continuous_learning_skill,  # 持续学习
        agent_workforce_tracker,    # 招标数据追踪
        domestic_ai_chain           # 国内AI产业链
    )
except ImportError:
    # 若技能尚未安装，设为None，运行时将降级处理
    a_stock_hk_analysis = stock_analysis = valuation_automation = quant_ai_fusion = None
    historical_cycle_locator = regime_switch_detector = cn_stock_news_monitor = None
    vn_market_news_monitor = commodity_geo_monitor = supply_chain_radar = None
    macro_data_skill = service_tech_intensity = earnings_season_scanner = None
    fifteen_five_scanner = anti_involution_screener = dgr = post_decision_analyzer = None
    game_simulator = skill_firewall = skill_namer = gitbackup = fullbackup = safe_backup = None
    eastmoney_client = pdf_annual_report = alternative_data_fusion = realtime_market_watcher = None
    multi_language_research = automation_workflows = goal_mode = crawl4ai = operator_humanizer = None
    evolve_skill = continuous_learning_skill = agent_workforce_tracker = domestic_ai_chain = None

# ========== 辅助函数 ==========
def extract_stock_code(query: str) -> Optional[str]:
    """从用户输入中提取股票代码或名称（简单正则匹配）"""
    # 支持 6 位数字（A股）或 5 位（港股）
    match = re.search(r'\b(60\d{4}|00\d{4}|30\d{4}|688\d{3}|\d{5})\b', query)
    if match:
        return match.group(0)
    # 否则尝试匹配常见名称映射（可扩展）
    name_map = {
        "建设银行": "601939",
        "紫金矿业": "601899",
        # 更多映射可在此添加
    }
    for name, code in name_map.items():
        if name in query:
            return code
    return None

def get_stock_info(code: str, config: dict) -> Dict[str, Any]:
    """通过东方财富官方 API 获取实时行情和财务数据"""
    if eastmoney_client:
        # 如果安装了 eastmoney-client 技能，优先使用
        return eastmoney_client.run(f"查询股票{code}", {"config": config}) or {}
    # 否则使用直接请求
    url = "https://mkapi2.dfcfs.com/finskillshub/api/claw/query"
    headers = {"apikey": config.get("eastmoney_api_key"), "Content-Type": "application/json"}
    payload = {"toolQuery": f"{code} 最新财务数据"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        return resp.json()
    except Exception:
        return {"price": 0, "name": code}

def generate_report(analysis: Dict[str, Any]) -> str:
    """按照八层框架生成最终报告文本"""
    lines = []
    lines.append("=" * 68)
    lines.append(f"📊 {analysis['company_name']}（{analysis['stock_code']}）八层投资框架分析报告")
    lines.append(f"   分析时间：{analysis['date']} | 当前股价：{analysis['current_price']}元")
    lines.append("=" * 68)

    # 第0层：战略推演
    lines.append("\n## 🌐 第0层：战略推演（历史节点定位）")
    lines.append(f"  - 康波周期阶段：{analysis.get('layer0', {}).get('kondratieff', '未评估')}")
    lines.append(f"  - 四周期嵌套定位：{analysis.get('layer0', {}).get('cycle_nesting', '未分析')}")
    lines.append(f"  - 大类资产时钟指向：{analysis.get('layer0', {}).get('asset_clock', '未判断')}")
    lines.append(f"  - 历史动力学指数：{analysis.get('layer0', {}).get('historical_dynamics', '未监测')}")
    lines.append(f"  - 参考书目：《涛动周期论》《危局》《历史的逻辑》《论大战略》《预言家的博弈》《博弈论与经济行为》《反直觉的赛局思维》")

    # 第1层：宏观定位
    lines.append("\n## 📈 第1层：宏观定位（货币·信用·增长·政策）")
    lines.append(f"  - 10年期国债收益率：{analysis.get('layer1', {}).get('bond_yield', 'N/A')}%")
    lines.append(f"  - 美元/人民币汇率：{analysis.get('layer1', {}).get('usd_cny', 'N/A')}")
    lines.append(f"  - 美联储降息预期：{analysis.get('layer1', {}).get('fed_expect', '中性')}")
    lines.append(f"  - PPI/CPI/PMI：{analysis.get('layer1', {}).get('macro_indicators', '未采集')}")
    lines.append(f"  - 政策方向：{analysis.get('layer1', {}).get('policy', '未分析')}")
    lines.append(f"  - 参考书目：《结构性改革》《置身事内》《新质生产力》")

    # 第2层：行业分析
    lines.append("\n## 🏭 第2层：行业分析（景气度·五力·另类数据）")
    lines.append(f"  - 五力模型评估：{analysis.get('layer2', {}).get('five_forces', '未分析')}")
    lines.append(f"  - 行业景气度指数：{analysis.get('layer2', {}).get('prosperity_index', 'N/A')}")
    lines.append(f"  - 另类数据信号：{analysis.get('layer2', {}).get('alternative_signals', '无异常')}")
    lines.append(f"  - 供应链安全评级：{analysis.get('layer2', {}).get('supply_chain', '正常')}")
    lines.append(f"  - 国产替代进度：{analysis.get('layer2', {}).get('domestic_substitution', '未评估')}")
    lines.append(f"  - 参考书目：《竞争战略》《科技共和国》《量子金融科技》")

    # 第3层：市场定位
    lines.append("\n## 📊 第3层：市场定位（估值水位·情绪·外资）")
    lines.append(f"  - PE历史分位（5年）：{analysis.get('layer3', {}).get('pe_percentile', 'N/A')}%")
    lines.append(f"  - PB历史分位（5年）：{analysis.get('layer3', {}).get('pb_percentile', 'N/A')}%")
    lines.append(f"  - 股债收益率对比：{analysis.get('layer3', {}).get('equity_bond_spread', 'N/A')}")
    lines.append(f"  - 外资机构仓位变化：{analysis.get('layer3', {}).get('foreign_position', '未监测')}")
    lines.append(f"  - 市场情绪指标：{analysis.get('layer3', {}).get('sentiment', '中性')}")
    lines.append(f"  - 参考书目：《股市百年启示录》《异常流行幻象与群众疯狂》《金钱行为学》")

    # 第4层：财务估值
    lines.append("\n## 💰 第4层：财务估值（DCF·ROE·PEG·行业模板）")
    lines.append(f"  - DCF内在价值：{analysis.get('layer4', {}).get('dcf_value', 'N/A')}元")
    lines.append(f"  - 预测 2025E EPS：{analysis.get('layer4', {}).get('eps_2025e', 'N/A')}元")
    lines.append(f"  - ROE × PB 联合判断：{analysis.get('layer4', {}).get('roe_pb_judge', '未分析')}")
    lines.append(f"  - PEG指标：{analysis.get('layer4', {}).get('peg', 'N/A')}")
    lines.append(f"  - 行业模板定位：{analysis.get('layer4', {}).get('industry_template', '未匹配')}")
    lines.append(f"  - 参考书目：《证券分析》《财务报表分析与证券估值》《价格的逻辑》《稀缺与价格理论》《价格与价值》")

    # 第5层：买入决策
    lines.append("\n## ✅ 第5层：买入决策（86体系·39体系·王子落难·逆向大师）")
    lines.append(f"  - 86体系评分（8好+6便宜）：{analysis.get('layer5', {}).get('eighty_six_score', 'N/A')}")
    lines.append(f"  - 39体系状态：{analysis.get('layer5', {}).get('thirty_nine_state', 'N/A')}")
    lines.append(f"  - 王子落难匹配度：{analysis.get('layer5', {}).get('prince_fallen', 'N/A')}")
    lines.append(f"  - 逆向大师信号：{analysis.get('layer5', {}).get('contrarian_signal', '未触发')}")
    lines.append(f"  - 决策记录：{analysis.get('layer5', {}).get('decision_summary', '本次未记录')}")
    lines.append(f"  - 参考书目：《投资最重要的事》《巴菲特致股东的信》《投资大师》《段永平投资理念》《大道至简》《百倍成长股》《全力以富买进千倍股》")

    # 第6层：心理控制
    lines.append("\n## 🧠 第6层：心理控制（决策日志·博弈模拟·多空碰撞）")
    lines.append(f"  - 当前认知偏误检查：{analysis.get('layer6', {}).get('bias_check', '未发现明显偏误')}")
    lines.append(f"  - 群体疯狂识别：{analysis.get('layer6', {}).get('crowd_madness', '未触发')}")
    lines.append(f"  - 博弈模拟器预判：{analysis.get('layer6', {}).get('game_simulation', '未模拟')}")
    lines.append(f"  - 多空观点对比：{analysis.get('layer6', {}).get('bull_bear', '未收集')}")
    lines.append(f"  - 参考书目：《思考，快与慢》《更富有、更睿智、更快乐》")

    # 第7层：长期持有
    lines.append("\n## 🚀 第7层：长期持有（卖出原则·让跑继续跑）")
    lines.append(f"  - 基本面趋势：{analysis.get('layer7', {}).get('fundamental_trend', '稳定')}")
    lines.append(f"  - 估值极端泡沫检测：{analysis.get('layer7', {}).get('bubble_alert', '未触发')}")
    lines.append(f"  - 更好机会发现：{analysis.get('layer7', {}).get('better_opportunity', '无')}")
    lines.append(f"  - 当前状态：{analysis.get('layer7', {}).get('hold_status', '持有')}")
    lines.append(f"  - 参考书目：《艾略特波浪理论》《股市博弈论》")

    # 综合结论（含反馈闭环）
    lines.append("\n## 🎯 综合结论与反馈闭环")
    lines.append(f"  - 合理估值区间：{analysis.get('conclusion', {}).get('fair_value_range', 'N/A')}")
    lines.append(f"  - 当前操作建议：{analysis.get('conclusion', {}).get('action', '持有')}")
    lines.append(f"  - 未来1年期望回报：{analysis.get('conclusion', {}).get('expected_return', 'N/A')}%")
    lines.append(f"  - 核心风险：{analysis.get('conclusion', {}).get('risks', '无显著风险')}")
    lines.append(f"  - 决策准确率跟踪：{analysis.get('conclusion', {}).get('accuracy_tracking', '待复盘')}")

    lines.append("\n" + "=" * 68)
    lines.append("⚠️ 免责声明：本分析基于公开数据与量化模型，仅供参考，不构成投资建议。")
    return "\n".join(lines)

# ========== 技能主入口 ==========
def run(query: str, context: dict) -> str:
    """
    query: 用户输入的自然语言
    context: 包含配置信息（如 API 密钥）和用户历史上下文
    """
    global config
    config = context.get("config", {})

    # 1. 解析股票代码
    stock_code = extract_stock_code(query)
    if not stock_code:
        return "未能识别股票代码或名称，请提供如'分析建设银行'或'分析601939'的指令。"

    # 2. 获取基础数据（东方财富 API）
    try:
        data = get_stock_info(stock_code, config)
        current_price = data.get("price", 0)
        company_name = data.get("name", stock_code)
    except Exception as e:
        return f"获取股票数据失败：{str(e)}"

    # 3. 构建分析字典
    analysis = {
        "company_name": company_name,
        "stock_code": stock_code,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "current_price": current_price,
        "layer0": {},
        "layer1": {},
        "layer2": {},
        "layer3": {},
        "layer4": {},
        "layer5": {},
        "layer6": {},
        "layer7": {},
        "conclusion": {}
    }

    # 4. 调用各技能模块（每个模块的 run 应返回字典，若不可用则跳过）
    # 第0层：历史周期定位
    if historical_cycle_locator:
        try:
            res = historical_cycle_locator.run(query, context)
            analysis["layer0"].update(res)
        except Exception:
            pass

    # 第1层：宏观数据与政策
    if macro_data_skill:
        try:
            res = macro_data_skill.run(query, context)
            analysis["layer1"].update(res)
        except Exception:
            pass
    if cn_stock_news_monitor:
        try:
            res = cn_stock_news_monitor.run(query, context)
            analysis["layer1"]["policy"] = res.get("policy_trend", "未分析")
        except Exception:
            pass

    # 第2层：行业分析（反内卷筛选、供应链雷达、十五五等）
    if anti_involution_screener:
        try:
            res = anti_involution_screener.run(query, context)
            analysis["layer2"].update(res)
        except Exception:
            pass
    if supply_chain_radar:
        try:
            res = supply_chain_radar.run(query, context)
            analysis["layer2"]["supply_chain"] = res.get("risk_level", "正常")
        except Exception:
            pass
    if fifteen_five_scanner:
        try:
            res = fifteen_five_scanner.run(query, context)
            analysis["layer2"]["domestic_substitution"] = res.get("substitution_progress", "未评估")
        except Exception:
            pass
    if alternative_data_fusion:
        try:
            res = alternative_data_fusion.run(query, context)
            analysis["layer2"]["alternative_signals"] = res.get("signals", "无异常")
        except Exception:
            pass

    # 第3层：市场定位（量化因子、情绪、外资）
    if quant_ai_fusion:
        try:
            res = quant_ai_fusion.run(query, context)
            analysis["layer3"].update(res)
        except Exception:
            pass
    if multi_language_research:
        try:
            res = multi_language_research.run(query, context)
            analysis["layer3"]["foreign_position"] = res.get("foreign_holdings", "未监测")
        except Exception:
            pass
    if realtime_market_watcher:
        try:
            res = realtime_market_watcher.run(query, context)
            analysis["layer3"]["sentiment"] = res.get("sentiment", "中性")
        except Exception:
            pass

    # 第4层：财务估值
    if valuation_automation:
        try:
            res = valuation_automation.run(query, context)
            analysis["layer4"].update(res)
        except Exception:
            pass
    if pdf_annual_report:
        try:
            # 若用户指定"深度分析"，可尝试拉取年报
            if "深度" in query:
                res = pdf_annual_report.run(query, context)
                analysis["layer4"].update(res)
        except Exception:
            pass
    if a_stock_hk_analysis:
        try:
            res = a_stock_hk_analysis.run(query, context)
            analysis["layer4"]["industry_template"] = res.get("industry_template", "未匹配")
        except Exception:
            pass

    # 第5层：买入决策（86/39/王子落难等）
    # 此处可基于估值结果生成简易决策，若有专门决策技能则调用
    decision = {}
    # 若有 dgr 技能，可调用获取历史决策参考
    if dgr:
        try:
            res = dgr.run(query, context)
            decision.update(res)
        except Exception:
            pass
    analysis["layer5"] = decision

    # 第6层：心理控制（博弈模拟器、多空观点）
    if game_simulator:
        try:
            res = game_simulator.run(query, context)
            analysis["layer6"]["game_simulation"] = res.get("simulation", "未模拟")
        except Exception:
            pass
    if multi_language_research:
        try:
            res = multi_language_research.run(query, context)
            analysis["layer6"]["bull_bear"] = res.get("bull_bear_summary", "未收集")
        except Exception:
            pass

    # 第7层：长期持有（基于估值与基本面判断）
    hold_status = "持有"
    bubble = False
    if analysis["layer4"].get("dcf_value") and current_price:
        if current_price > analysis["layer4"]["dcf_value"] * 1.5:
            hold_status = "考虑减持"
            bubble = True
        elif current_price < analysis["layer4"]["dcf_value"] * 0.7:
            hold_status = "增持"
    analysis["layer7"]["hold_status"] = hold_status
    analysis["layer7"]["bubble_alert"] = "触发" if bubble else "未触发"

    # 综合结论
    fair_low = analysis["layer4"].get("dcf_value", current_price) * 0.8 if analysis["layer4"].get("dcf_value") else current_price * 0.9
    fair_high = analysis["layer4"].get("dcf_value", current_price) * 1.2 if analysis["layer4"].get("dcf_value") else current_price * 1.1
    analysis["conclusion"] = {
        "fair_value_range": f"{fair_low:.2f} - {fair_high:.2f} 元",
        "action": "买入" if current_price < fair_low else ("卖出" if current_price > fair_high else "持有"),
        "expected_return": (fair_high / current_price - 1) * 100 if current_price else 0,
        "risks": analysis["layer2"].get("supply_chain", "行业竞争风险"),
        "accuracy_tracking": "请记录本次决策，便于后续复盘"
    }

    # 反馈闭环：若 post_decision_analyzer 可用，可记录本次决策
    if post_decision_analyzer:
        try:
            post_decision_analyzer.run(f"记录决策 {stock_code}", context)
        except Exception:
            pass

    # 生成报告
    return generate_report(analysis)
```
