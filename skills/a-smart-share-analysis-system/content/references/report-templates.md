# 分析报告模板参考

## 报告模板1：简洁版

```markdown
# A股分析报告
**{date}** | **{target}**

## 核心观点
**[买入/持有/卖出]**

## 技术面
- 均线: {ma_status}
- MACD: {macd_signal}
- KDJ: {kdj_signal}

## 资金面
- 北向: {north_flow}
- 融资: {margin_balance}

## 关键价位
| 类型 | 价格 |
|------|------|
| 压力位 | {resistance} |
| 支撑位 | {support} |
| 建议建仓区间 | {entry_zone} |

## 风险提示
{risks}

---
*仅供参考，不构成投资建议*
```

## 报告模板2：详细版

```markdown
# A股市场深度分析报告
**生成时间**: {timestamp}
**分析标的**: {target}
**报告编号**: {report_id}

---

## 执行摘要

### 一句话结论
{one_sentence_summary}

### 投资建议
| 建议类型 | 建议内容 | 置信度 |
|---------|---------|--------|
| 整体建议 | {overall_advice} | {confidence}% |
| 建仓区间 | {entry_zone} | - |
| 目标价位 | {target_price} | - |
| 止损价位 | {stop_loss} | - |

---

## 第一部分：市场概况

### 1.1 指数表现
| 指数 | 当前点位 | 涨跌幅 | 趋势 |
|------|---------|--------|------|
| 上证指数 | {sh_index} | {sh_change}% | {sh_trend} |
| 深证成指 | {sz_index} | {sz_change}% | {sz_trend} |
| 创业板 | {cy_index} | {cy_change}% | {cy_trend} |
| 科创50 | {kc_index} | {kc_change}% | {kc_trend} |

### 1.2 市场情绪
- 上涨家数: {rising_count}
- 下跌家数: {falling_count}
- 涨停家数: {limit_up_count}
- 跌停家数: {limit_down_count}
- 市场热度指数: {heat_index} ({heat_level})

### 1.3 资金动向
- 今日成交额: {total_volume}亿
- 北向资金: {north_capital}亿
- 融资余额: {margin_balance}亿

---

## 第二部分：技术分析

### 2.1 趋势分析
- 长期趋势(MA250): {long_trend}
- 中期趋势(MA60): {mid_trend}
- 短期趋势(MA20): {short_trend}
- 当前趋势判断: {trend_judgment}

### 2.2 均线系统
| 均线 | 数值 | 与价格关系 |
|------|------|-----------|
| MA5 | {ma5} | {ma5_relation} |
| MA10 | {ma10} | {ma10_relation} |
| MA20 | {ma20} | {ma20_relation} |
| MA60 | {ma60} | {ma60_relation} |
| MA120 | {ma120} | {ma120_relation} |
| MA250 | {ma250} | {ma250_relation} |

### 2.3 MACD分析
- DIF值: {dif}
- DEA值: {dea}
- MACD柱: {macd_hist}
- 交叉信号: {macd_signal}

### 2.4 KDJ分析
- K值: {k}
- D值: {d}
- J值: {j}
- 超买/超卖: {kdj_status}

### 2.5 RSI分析
- RSI(6): {rsi6}
- RSI(12): {rsi12}
- RSI(24): {rsi24}
- 当前状态: {rsi_status}

### 2.6 布林带
- 上轨: {boll_upper}
- 中轨: {boll_middle}
- 下轨: {boll_lower}
- 当前位置: {boll_position}

---

## 第三部分：资金分析

### 3.1 北向资金
| 统计周期 | 净买入 | 趋势 |
|---------|--------|------|
| 今日 | {north_today}亿 | {north_today_trend} |
| 近5日 | {north_5d}亿 | {north_5d_trend} |
| 近20日 | {north_20d}亿 | {north_20d_trend} |

### 3.2 融资融券
| 指标 | 数值 | 变化 |
|------|------|------|
| 融资余额 | {margin_balance}亿 | {margin_change} |
| 融券余额 | {short_balance}亿 | {short_change} |
| 融资净买入 | {margin_net_buy}亿 | - |

### 3.3 龙虎榜
- 上榜次数: {top_trade_count}
- 机构净买入: {institution_net_buy}亿
- 游资净买入: {hot_money_net_buy}亿

---

## 第四部分：基本面分析

### 4.1 宏观环境
- 经济周期: {economic_cycle}
- 货币政策: {monetary_policy}
- 财政政策: {fiscal_policy}
- 行业政策: {industry_policy}

### 4.2 估值分析
| 指标 | 当前值 | 历史分位 |
|------|--------|----------|
| PE | {pe} | {pe_percentile}% |
| PB | {pb} | {pb_percentile}% |
| PS | {ps} | {ps_percentile}% |
| 股息率 | {dividend_yield}% | {dy_percentile}% |

---

## 第五部分：综合研判

### 5.1 多维度评分
| 维度 | 评分(1-10) | 说明 |
|------|-----------|------|
| 技术面 | {tech_score} | {tech_reason} |
| 资金面 | {fund_score} | {fund_reason} |
| 基本面 | {fundament_score} | {fundament_reason} |
| 情绪面 | {sentiment_score} | {sentiment_reason} |
| 政策面 | {policy_score} | {policy_reason} |
| **综合评分** | **{total_score}** | {total_reason} |

### 5.2 预测结论
- **短期**(1-5日): {short_term_prediction}
- **中期**(5-20日): {mid_term_prediction}
- **中长期**(20+日): {long_term_prediction}

### 5.3 关键价位
| 类型 | 价格/区间 | 依据 |
|------|----------|------|
| 建仓区间 | {entry_zone} | {entry_reason} |
| 第一压力位 | {resistance1} | {resistance1_reason} |
| 第二压力位 | {resistance2} | {resistance2_reason} |
| 第一支撑位 | {support1} | {support1_reason} |
| 第二支撑位 | {support2} | {support2_reason} |
| 止损位 | {stop_loss} | {stop_loss_reason} |

---

## 第六部分：操作建议

### 6.1 仓位建议
{position_advice}

### 6.2 入场策略
{entry_strategy}

### 6.3 持仓策略
{holding_strategy}

### 6.4 出场策略
{exit_strategy}

---

## 第七部分：风险提示

### 主要风险
1. {risk1}
2. {risk2}
3. {risk3}

### 风险控制建议
{ risk_control_advice}

---

## 附录

### A. 数据来源
{data_sources}

### B. 模型说明
{model_description}

### C. 历史表现
{historical_performance}

---

**免责声明**: 本报告仅供专业投资者参考，不构成任何投资建议。投资者应自行承担投资风险，审慎做出投资决策。

**报告生成时间**: {timestamp}
**分析人员**: A股分析预测系统 v{version}
```

---

## 快捷键说明

| 快捷键 | 功能 |
|--------|------|
| `分析报告` | 生成标准分析报告 |
| `简要报告` | 生成简洁版报告 |
| `详细报告` | 生成详细版报告 |
| `报告优化` | 优化当前报告 |
