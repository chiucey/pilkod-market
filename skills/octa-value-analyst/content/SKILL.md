---
name: octa-value-analyst
description: 整合八层投资框架（第0层战略推演至第7层长期持有）、28本投资经典、25个分析技能的A股/港股企业价值分析系统。当用户要求分析股票、进行估值、查找合理买入区间、评估基本面、长期持有建议、八层分析时触发。
triggers:
  - 企业价值分析
  - 估值
  - 合理区间
  - 基本面
  - 长期持有
  - 八层分析
  - 分析{股票名称}
---

# 八层投资框架分析系统

## 0. 系统概述

整合八层投资框架（第0层战略推演至第7层长期持有）、28本投资经典、25个分析技能的A股/港股企业价值分析系统。

## 1. 依赖配置

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| eastmoney_api_key | string | 是 | 东方财富官方 Skills 接口 API Key |

## 2. 八层分析框架

### 第0层：战略推演（历史节点定位）
- 康波周期阶段定位
- 四周期嵌套定位
- 大类资产时钟指向
- 历史动力学指数监测
- **参考书目**：《涛动周期论》《危局》《历史的逻辑》《论大战略》《预言家的博弈》《博弈论与经济行为》《反直觉的赛局思维》

### 第1层：宏观定位（货币·信用·增长·政策）
- 10年期国债收益率
- 美元/人民币汇率
- 美联储降息预期
- PPI/CPI/PMI 采集
- 政策方向分析
- **参考书目**：《结构性改革》《置身事内》《新质生产力》

### 第2层：行业分析（景气度·五力·另类数据）
- 五力模型评估
- 行业景气度指数
- 另类数据信号
- 供应链安全评级
- 国产替代进度
- **参考书目**：《竞争战略》《科技共和国》《量子金融科技》

### 第3层：市场定位（估值水位·情绪·外资）
- PE/PB 历史分位（5年）
- 股债收益率对比
- 外资机构仓位变化
- 市场情绪指标
- **参考书目**：《股市百年启示录》《异常流行幻象与群众疯狂》《金钱行为学》

### 第4层：财务估值（DCF·ROE·PEG·行业模板）
- DCF 内在价值计算
- 预测 EPS
- ROE × PB 联合判断
- PEG 指标
- 行业模板匹配
- **参考书目**：《证券分析》《财务报表分析与证券估值》《价格的逻辑》《稀缺与价格理论》《价格与价值》

### 第5层：买入决策（86体系·39体系·王子落难·逆向大师）
- 86体系评分（8好+6便宜）
- 39体系状态
- 王子落难匹配度
- 逆向大师信号
- **参考书目**：《投资最重要的事》《巴菲特致股东的信》《投资大师》《段永平投资理念》《大道至简》《百倍成长股》《全力以富买进千倍股》

### 第6层：心理控制（决策日志·博弈模拟·多空碰撞）
- 认知偏误检查
- 群体疯狂识别
- 博弈模拟器预判
- 多空观点对比
- **参考书目**：《思考，快与慢》《更富有、更睿智、更快乐》

### 第7层：长期持有（卖出原则·让跑继续跑）
- 基本面趋势监测
- 估值极端泡沫检测
- 更好机会发现
- 持有状态评估
- **参考书目**：《艾略特波浪理论》《股市博弈论》

## 3. 技能模块依赖

```python
# 核心模块导入（按层对应）
try:
    from skills import (
        a_stock_hk_analysis,        # 第2、4层
        valuation_automation,       # 第4层
        quant_ai_fusion,            # 第3层
        historical_cycle_locator,   # 第0层
        regime_switch_detector,     # 第3层
        cn_stock_news_monitor,      # 第1层
        macro_data_skill,           # 第1层
        supply_chain_radar,         # 第2层
        fifteen_five_scanner,       # 第2层
        anti_involution_screener,   # 第2层
        dgr,                        # 第5层
        post_decision_analyzer,     # 反馈闭环
        game_simulator,             # 第6层
        alternative_data_fusion,    # 第2层
        realtime_market_watcher,    # 第3层
        multi_language_research,    # 第3、6层
        pdf_annual_report,          # 第4层
        eastmoney_client,           # 数据源
    )
except ImportError:
    pass  # 降级处理
```

## 4. 报告输出格式

```
=====================================================================
📊 {公司名称}（{股票代码}）八层投资框架分析报告
   分析时间：{日期} | 当前股价：{价格}元
=====================================================================

## 🌐 第0层：战略推演（历史节点定位）
  - 康波周期阶段：{评估结果}
  - 四周期嵌套定位：{分析结果}
  ...

## 📈 第1层：宏观定位（货币·信用·增长·政策）
  - 10年期国债收益率：{数值}%
  ...

[... 其他各层 ...]

## 🎯 综合结论与反馈闭环
  - 合理估值区间：{区间}
  - 当前操作建议：{买入/持有/卖出}
  - 未来1年期望回报：{数值}%
  - 核心风险：{风险描述}
  - 决策准确率跟踪：{状态}

=====================================================================
⚠️ 免责声明：本分析基于公开数据与量化模型，仅供参考，不构成投资建议。
```

## 5. 核心 Python 代码入口

```python
import re
import json
import yaml
import requests
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

def extract_stock_code(query: str) -> Optional[str]:
    """从用户输入中提取股票代码或名称"""
    match = re.search(r'\b(60\d{4}|00\d{4}|30\d{4}|688\d{3}|\d{5})\b', query)
    if match:
        return match.group(0)
    return None

def get_stock_info(code: str, config: dict) -> Dict[str, Any]:
    """通过东方财富官方 API 获取实时行情和财务数据"""
    url = "https://mkapi2.dfcfs.com/finskillshub/api/claw/query"
    headers = {"apikey": config.get("eastmoney_api_key"), "Content-Type": "application/json"}
    payload = {"toolQuery": f"{code} 最新财务数据"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        return resp.json()
    except Exception:
        return {"price": 0, "name": code}

def run(query: str, context: dict) -> str:
    """主入口函数"""
    config = context.get("config", {})
    stock_code = extract_stock_code(query)
    if not stock_code:
        return "未能识别股票代码或名称，请提供如'分析建设银行'或'分析601939'的指令。"
    # ... 执行八层分析并返回报告
```
