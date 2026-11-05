---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f355e82d4e1648f084de9b295def5769
    PropagateID: f355e82d4e1648f084de9b295def5769
    ReservedCode1: 304502207495d25ab9bf6ca38af74ac1062143ef11767c1c2e80e7c5845c5d83bf274ad1022100d675409031906adb86d6fca92f6abd540decb418f443ef65d8369f62515bb2f9
    ReservedCode2: 304502207ccdc77e3cd17b9d2c205871b96da73ca50bfefa84b0963d6fb302dde491baf50221009b4d60e755373fc559c2929217981e92f16fcde0837fd8e009c0a6049f3b4423
description: 智能A股市场实时分析预测系统。当用户请求分析A股大盘指数、热门行业ETF、股票，或发送以下指令时使用：分析报告、报告优化、模型报告、系统报告、数据更新、模型优化、系统优化、提交反馈。支持买卖建议、建仓区间、模型训练回测、数据管理等功能。
name: a-smart-share-analysis-system
---

# A股市场实时分析预测系统

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     A股市场实时分析预测系统                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │  数据管理中心    │  │  实时分析预测   │  │  报告生成中心   │     │
│  │                 │  │     模型        │  │                 │     │
│  │  • 数据源管理   │  │                 │  │  • 实时报告    │     │
│  │  • 数据采集    │  │  • 初始模型     │  │  • 优化报告    │     │
│  │  • 数据检核    │  │  • 模型训练    │  │  • 模型报告    │     │
│  │  • 数据更新    │  │  • 模型优化    │  │  • 系统报告    │     │
│  │  • 虚拟数据处理│  │  • 回测验证    │  │               │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      指令处理中心                            │   │
│  │  • 分析报告  • 报告优化  • 模型报告  • 系统报告             │   │
│  │  • 数据更新  • 模型优化  • 系统优化  • 提交反馈             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 分析标的

- **大盘指数**: 上证指数、深证成指、创业板指、科创50、北证50等
- **热门行业指数**: 半导体、新能源、医疗、消费、银行、光伏、军工等
- **热门行业ETF**: 芯片ETF、新能源车ETF、医疗ETF、AI算力ETF、低空经济ETF等

### 2026年3月市场热点板块（系统自动追踪）
| 板块分类 | 重点标的 | 投资逻辑 |
|---------|---------|---------|
| AI算力产业链 | CPO、光模块、存储芯片、液冷服务器 | 业绩兑现，国产替代加速 |
| 低空经济 | 低空装备、无人机、卫星导航 | 政策催化，万亿赛道 |
| 新能源 | 光伏、储能、锂电 | 博鳌论坛绿色议题催化 |
| 周期资源 | 有色金属、铜、黄金 | 全球通胀预期 |
| 高股息防御 | 煤炭、电力、银行 | 避险属性，稳健收益 |
| 人形机器人 | 整机厂、核心零部件 | 销量预测上调至2.8万台 |
| 市场再均衡 | 科技出海切低内需 | 机构仓位再平衡配置 |

### 市场风格切换分析（v2.1新增）
- **机构仓位分析**: 泛科技仓位超50%，出海超70%，资源近90%
- **再均衡信号**: 高切低配置，主线切换预警
- **历史类比**: 2021年"调结构"模式 vs 2022年"降仓位"模式

## 分析维度（v2.1优化版）

### 1. 基本面因子
- GDP增速、CPI、PPI数据
- 货币政策、财政政策
- 行业景气度
- 公司财务数据

### 2. 市场资金面
- 北向资金（沪深港通）
- 融资融券余额
- 龙虎榜数据
- 市场资金流向

### 3. 技术面指标（v2.0增强版）
- 均线系统（MA5/10/20/60/120/250）
- MACD、KDJ、RSI等指标
- 布林带、威廉指标、CCI、ADX
- 量价关系分析
- **多指标共振分析**（三金共振：MA金叉+均量线金叉+MACD金叉）
- **成交量异常检测**（量增价跌、量缩价涨识别）
- **趋势强度分析**（ADX趋势判断）
- **波动率分析**（历史波动率、IVIX恐慌指数）

### 4. 外盘联动
- 美股三大指数（道琼斯、纳斯达克、标普500）
- 港股恒生指数
- A50期指
- 亚太股市表现

### 5. 市场情绪
- 恐慌指数（VIX）
- 涨跌停板数量
- 市场热度指数
- 板块轮动节奏

### 6. 政策与事件
- 国内重要政策
- 国际重大事件
- 行业政策变化（如：算电协同政策、低空经济政策）
- 突发事件影响
- **两会政策预期分析**
- **产业政策催化追踪**

---

## 数据管理中心

### 数据源管理

```python
# 数据源优先级配置
DATA_SOURCES = {
    "realtime": [
        "新浪财经实时API",
        "东方财富API",
        "腾讯财经API",
        "网易财经API"
    ],
    "historical": [
        "AKShare开源数据库",
        "Tushare专业版",
        "聚宽数据",
        "Wind万得"
    ],
    "fundamentals": [
        "东方财富财报数据",
        "同花顺F10",
        "巨潮资讯网",
        "上交所/深交所公告"
    ],
    "sentiment": [
        "东方财富股吧",
        "雪球社区",
        "财经新闻聚合",
        "社交媒体舆情"
    ]
}
```

### 数据类型

1. **实时数据**: 当前交易日实时行情
2. **日线数据**: 每日OHLCV数据
3. **分钟数据**: 1/5/15/30/60分钟K线
4. **财务数据**: 财报、公告、业绩预告
5. **资金数据**: 北向资金、融资融券
6. **情绪数据**: 舆情、新闻、社交媒体

### 数据检核规则

```python
VALIDATION_RULES = {
    "price_range": {
        "check": "当日涨跌幅应在[-10%, +10%]之间（ST股除外）",
        "action": "异常则标记并尝试重新获取"
    },
    "volume": {
        "check": "成交量应>=0",
        "action": "空值或负数标记为无效"
    },
    "consistency": {
        "check": "同一日期不同源数据偏差应<1%",
        "action": "大偏差时取中位数或重新获取"
    },
    "completeness": {
        "check": "交易日数据不应缺失（节假日除外）",
        "action": "缺失数据尝试补充或标记为虚拟"
    },
    "logic": {
        "check": "最高价>=收盘价>=最低价",
        "action": "不满足逻辑则修正或重新获取"
    }
}
```

### 虚拟数据标记

```python
class DataPoint:
    source: str
    is_virtual: bool = False
    virtual_reason: str = None  # "holiday", "api_failure", "historical_gap"
    confidence: float = 1.0  # 0.0-1.0, 虚拟数据应<0.8
```

---

## 实时分析和预测模型

### 模型架构

```
输入层 → 特征提取 → 模型融合 → 输出层

特征提取:
├── 技术指标模块 (TF-IDF + LSTM)
├── 基本面模块 (Transformer)
├── 资金流模块 (Graph Neural Network)
└── 情绪模块 (BERT + Attention)

模型融合:
├── XGBoost (擅长表格数据)
├── LightGBM (快速迭代)
├── 深度学习Ensemble
└── 强化学习调参
```

### 初始模型特征

```python
INITIAL_FEATURES = {
    "price_technicals": [
        "close", "open", "high", "low", "volume",
        "returns_1d", "returns_5d", "returns_20d",
        "volatility_20d", "momentum_20d"
    ],
    "moving_averages": [
        "MA5", "MA10", "MA20", "MA60", "MA120", "MA250",
        "EMA12", "EMA26", "MACD", "MACD_signal", "MACD_hist"
    ],
    "oscillators": [
        "RSI_14", "KDJ_K", "KDJ_D", "KDJ_J",
        "BOLL_upper", "BOLL_middle", "BOLL_lower",
        "WR_14", "CCI_14", "ADX_14"
    ],
    "volume_indicators": [
        "volume_ratio", "OBV", "VWAP",
        "volume_MA5_ratio", "volume_MA20_ratio"
    ]
}
```

### 模型优化维度（v2.0优化版）

```python
EXPANDED_FEATURES = {
    # 新增分析维度
    "fundamental_factors": [
        "PE_ratio", "PB_ratio", "PS_ratio",
        "ROE", "ROA", "gross_margin",
        "revenue_growth", "profit_growth",
        "debt_ratio", "current_ratio",
        "dividend_yield"  # 新增股息率
    ],
    "us_market": [
        "SP500_close", "NASDAQ_close", "DOW_close",
        "US_VIX", "USD_CNY", "US_10Y_yield",
        "crude_oil_price"  # 新增原油价格
    ],
    "hk_market": [
        "HSI_close", "HSCEI_close", "HSTECH_close",
        "southbound_capital"
    ],
    "futures": [
        "A50_index", "CSI300_index",
        "SHIBOR", "interbank_rate"
    ],
    "policy_sentiment": [
        "policy_news_score", "regulatory_events",
        "industry_policy_changes",
        "lianghui_expectation"  # 两会预期
    ],
    "sentiment_analysis": [
        "news_sentiment", "social_media_sentiment",
        "analyst_recommendations",
        "institutional_rating"  # 机构评级
    ],
    "market_status": [
        "fear_greed_index", "market_heat_index",
        "sector_rotation_score", "hot_money_index",
        "limit_up_count", "limit_down_count"  # 涨跌停数量
    ],
    "capital_flows": [
        "north_capital", "south_capital",
        "margin_balance", "short_selling_ratio",
        "institutional_positions",
        "main_force_flow", "retail_flow"  # 主力和散户资金
    ],
    # 2026年3月新增热点板块特征
    "sector_hot_features": [
        "ai_compute_sentiment",  # AI算力情绪
        "low_altitude_economy",   # 低空经济
        "humanoid_robot",         # 人形机器人 v2.1新增
        "cpo_concept",           # CPO概念
        "energy_storage_concept"  # 储能概念
    ],

    # 另类数据因子 v2.1新增（头部量化一半以上收益源于另类因子）
    "alternative_data_factors": [
        "satellite_imagery",      # 卫星影像数据
        "credit_card_data",      # 信用卡消费数据
        "web_traffic",            # 网站流量数据
        "social_media_sentiment", # 社交媒体舆情
        "news_nlp_sentiment"      # 新闻NLP情感分析
    ],

    # 深度学习因子 v2.1新增
    "deep_learning_factors": [
        "agru_dailyquote",        # AGRU日频因子
        "dl_1",                   # DL_1深度学习因子
        "fimage",                 # 图像因子
        "transformer_factor"      # Transformer因子
    ]
}
```

### 多AI模型因子挖掘体系（v2.1新增）

根据泰康资产等机构最新实践，构建多模型协同量化因子挖掘体系：

```python
MULTI_MODEL_FACTOR_SYSTEM = {
    "neural_network": {
        "models": ["LSTM", "GRU", "Transformer"],
        "strengths": "金融时序信息挖掘，端到端因子生成",
        "params": {
            "hidden_size": 128,
            "num_layers": 2,
            "attention_heads": 4
        }
    },
    "tree_models": {
        "models": ["XGBoost", "LightGBM", "CatBoost"],
        "strengths": "非线性关联挖掘，特征重要性分析",
        "params": {
            "max_depth": 8,
            "learning_rate": 0.03
        }
    },
    "text_models": {
        "models": ["BERT", "FinBERT", "LLM"],
        "strengths": "金融文本解读，情感Alpha挖掘",
        "params": {
            "model_size": "base",
            "fine_tune": True
        }
    },
    "graph_models": {
        "models": ["GNN", "GraphSAGE"],
        "strengths": "产业链关联，企业图谱隐性关系",
        "params": {
            "embedding_dim": 64,
            "neighbors": 10
        }
    }
}
```

### 模型集成策略（v2.1优化版）

根据最新量化研究成果，集成学习比单一模型准确率高5-8%：

```python
ENSEMBLE_STRATEGY = {
    "primary_models": {
        "xgboost": {
            "weight": 0.35,
            "strengths": "擅长表格数据，量化选股排名第一",
            "params": {
                "max_depth": 6,
                "learning_rate": 0.05,
                "n_estimators": 150,
                "colsample_bytree": 0.8,
                "subsample": 0.8
            }
        },
        "lightgbm": {
            "weight": 0.25,
            "strengths": "训练速度快，适合大规模数据",
            "params": {
                "num_leaves": 31,
                "learning_rate": 0.03,
                "n_estimators": 200
            }
        },
        "lstm": {
            "weight": 0.20,
            "strengths": "捕捉时序依赖关系",
            "params": {
                "hidden_size": 128,
                "num_layers": 2,
                "dropout": 0.2,
                "sequence_length": 20
            }
        },
        "transformer": {
            "weight": 0.20,
            "strengths": "多模态信息融合，注意力机制",
            "params": {
                "d_model": 256,
                "num_heads": 8,
                "num_layers": 4
            }
        }
    },
    "alpha_factors_count": 80,  # v2.1增加到80+因子（含另类数据和深度学习因子）
    "feature_importance_threshold": 0.01,
    "model_refresh_frequency": "weekly",
    "reinforcement_learning": {
        "enabled": True,
        "purpose": "自动优化模型超参数和权重分配"
    }
}
```

### 回测框架（v2.1增强版）

```python
BACKTEST_CONFIG = {
    "initial_capital": 1000000,  # 初始资金100万
    "commission": 0.0003,        # 万三佣金
    "stamp_tax": 0.001,          # 千一印花税
    "slippage": 0.001,           # 千一滑点

    "position_management": {
        "max_position": 0.3,      # 单只股票最大仓位30%
        "min_position": 0.05,     # 最小仓位5%
        "total_position": 0.95,   # 最大总仓位95%
        "stop_loss": 0.07,        # 止损7%
        "take_profit": 0.15,      # 止盈15%
        "trailing_stop": 0.05,    # 移动止损5%
        "rebalance_freq": "weekly",

        # v2.1新增：三分动态仓位法
        "three_divide_strategy": {
            "base_position": 0.5,    # 底仓50%
            "flexible_position": 0.2,  # 机动仓20%
            "cash_buffer": 0.1        # 现金垫10%
        }
    },

    "evaluation_metrics": [
        "total_return",
        "annualized_return",
        "max_drawdown",
        "sharpe_ratio",
        "calmar_ratio",
        "win_rate",
        "profit_loss_ratio",
        "sortino_ratio",
        "accuracy",
        "var_95",               # v2.1新增：95% VaR
        "cvar_95"               # v2.1新增：条件VaR
    ],

    "backtest_periods": {
        "train": "2019-2023",
        "validation": "2024",
        "test": "2025-2026"
    },

    "risk_adjusted_metrics": {
        "target_sharpe_ratio": 1.5,
        "max_allowed_drawdown": 0.15,
        "min_win_rate": 0.55,
        "max_var_95": 0.02      # v2.1新增：VaR限制
    }
}
```

### 风险管理策略（v2.1新增）

```python
RISK_MANAGEMENT = {
    # 三道防线
    "defense_lines": [
        "仓位控制",     # 第一道防线
        "策略分散",     # 第二道防线
        "止损纪律"      # 第三道防线
    ],

    # 双止盈止损规则
    "profit_loss_rules": {
        "partial_profit_take": {
            "threshold": 0.03,   # 冲高3%-5%减仓一半
            "action": "sell_half"
        },
        "hard_stop_loss": {
            "threshold": 0.05,  # 5%硬性止损
            "action": "exit_all"
        }
    },

    # 移动止损策略
    "trailing_stop": {
        "activation": "profit_only",  # 仅盈利状态激活
        "pullback_distance": 0.03    # 回撤3%触发
    },

    # 仓位动态调整
    "dynamic_position": {
        "high_confidence": 0.6,   # 高置信度仓位60%
        "medium_confidence": 0.4,  # 中置信度仓位40%
        "low_confidence": 0.2      # 低置信度仓位20%
    }
}
```

---

## 分析报告模板（v2.1优化版）

### 实时分析报告结构

```markdown
# A股市场实时分析预测报告
**生成时间**: {timestamp}
**分析标的**: {target}
**报告编号**: {report_id}
**模型版本**: v2.1

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

### 1.4 热点板块追踪（v2.1增强）
| 板块 | 涨跌幅 | 资金流入 | 投资逻辑 |
|------|--------|----------|---------|
| AI算力 | {ai_change}% | {ai_flow}亿 | 业绩兑现 |
| 低空经济 | {low_alt_change}% | {low_alt_flow}亿 | 政策催化 |
| 人形机器人 | {robot_change}% | {robot_flow}亿 | 销量上调 |
| 新能源 | {energy_change}% | {energy_flow}亿 | 绿色发展 |

### 1.5 市场风格与再均衡分析（v2.1新增）
- 机构仓位状态: {institutional_position}
- 再均衡信号: {rebalance_signal}
- 风格切换预警: {style_switch_warning}
- 历史类比: {historical_analogy}

---

## 第二部分：技术分析（v2.0增强）

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

### 2.3 多指标共振分析（v2.0新增）
- **三金共振信号**: {triple_gold_signal}
  - MA5金叉MA10: {ma_cross}
  - 均量线金叉: {volume_cross}
  - MACD金叉: {macd_cross}

### 2.4 MACD分析
- DIF值: {dif}
- DEA值: {dea}
- MACD柱: {macd_hist}
- 交叉信号: {macd_signal}

### 2.5 KDJ分析
- K值: {k}
- D值: {d}
- J值: {j}
- 超买/超卖: {kdj_status}

### 2.6 RSI分析
- RSI(6): {rsi6}
- RSI(12): {rsi12}
- RSI(24): {rsi24}
- 当前状态: {rsi_status}

### 2.7 成交量异常检测（v2.0新增）
- 量价关系: {volume_price_relation}
- 异常信号: {volume_anomaly}
- 资金性质: {capital_nature}

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

### 3.3 主力资金（v2.0新增）
- 主力净流入: {main_force_net}亿
- 散户净流出: {retail_net}亿
- 资金性质判断: {fund_nature}

---

## 第四部分：基本面分析

### 4.1 宏观环境
- 经济周期: {economic_cycle}
- 货币政策: {monetary_policy}
- 财政政策: {fiscal_policy}
- 行业政策: {industry_policy}

### 4.2 政策催化（v2.0新增）
- 两会政策预期: {lianghui_expectation}
- 产业政策: {industry_policy_detail}
- 事件驱动: {event_driven}

### 4.3 估值分析
| 指标 | 当前值 | 历史分位 |
|------|--------|----------|
| PE | {pe} | {pe_percentile}% |
| PB | {pb} | {pb_percentile}% |
| 股息率 | {dividend_yield}% | {dy_percentile}% |

---

## 第五部分：综合研判（v2.0优化）

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

### 5.3 关键价位（v2.0优化）
| 类型 | 价格/区间 | 依据 |
|------|----------|------|
| 建仓区间 | {entry_zone} | {entry_reason} |
| 第一压力位 | {resistance1} | {resistance1_reason} |
| 第二压力位 | {resistance2} | {resistance2_reason} |
| 第一支撑位 | {support1} | {support1_reason} |
| 第二支撑位 | {support2} | {support2_reason} |
| 止损位 | {stop_loss} | {stop_loss_reason} |
| 止盈位 | {take_profit} | {take_profit_reason} |

### 5.4 模型预测置信度（v2.0新增）
- XGBoost预测: {xgboost_pred} (置信度: {xgboost_conf}%)
- LightGBM预测: {lightgbm_pred} (置信度: {lightgbm_conf}%)
- LSTM预测: {lstm_pred} (置信度: {lstm_conf}%)
- 集成预测: {ensemble_pred} (置信度: {ensemble_conf}%)

---

## 第六部分：操作建议（v2.1优化）

### 6.1 仓位建议
{position_advice}

### 6.2 三分动态仓位法（v2.1新增）
- 底仓: {base_position}% ({base_rationale})
- 趋势仓: {trend_position}% ({trend_rationale})
- 现金储备: {cash_reserve}% ({cash_rationale})
- 动态调整信号: {position_adjustment_signal}

### 6.3 入场策略
1. 第一买点: {entry_point1}
2. 第二买点: {entry_point2}
3. 仓位分配: {position_allocation}

### 6.4 持仓策略
1. 移动止损: {trailing_stop}
2. 目标止盈: {target_profit}
3. 加仓条件: {add_position_condition}

### 6.5 出场策略（v2.1优化）
1. 止损条件: {stop_loss_condition}
2. 止盈条件: {take_profit_condition}
3. 时间止损: {time_stop}
4. 双止盈规则: {dual_take_profit}

---

## 第七部分：风险提示（v2.1增强）

### 主要风险
1. {risk1}
2. {risk2}
3. {risk3}
4. 风格切换风险: {style_switch_risk}
5. 流动性风险: {liquidity_risk}

### 风险控制建议（v2.1优化）
{risk_control_advice}

### 仓位控制
- 最大单只仓位: 30%
- 最大总仓位: 95%
- 建议仓位: {recommended_position}%

### VaR风险指标（v2.1新增）
- 日VaR(95%): {var_95}%
- 日VaR(99%): {var_99}%
- 最大回撤容忍: {max_drawdown_tolerance}%

### 黑天鹅应对（v2.1新增）
- 尾部风险对冲: {tail_risk_hedge}
- 应急预案: {emergency_plan}
- 压力测试场景: {stress_test_scenario}

---

## 附录

### A. 数据来源
{data_sources}

### B. 模型说明
- 当前模型版本: v2.1
- 训练数据周期: 2019-2026
- Alpha因子数量: 70+
- 模型刷新频率: 周度

### C. 历史表现
{historical_performance}

---

**免责声明**: 本报告仅供专业投资者参考，不构成任何投资建议。投资者应自行承担投资风险，审慎做出投资决策。

**报告生成时间**: {timestamp}
**分析人员**: A股分析预测系统 v2.1
```

---

## 指令处理中心

### 指令列表

| 指令 | 功能 | 输出 |
|-----|-----|-----|
| 分析报告 | 生成实时分析预测报告 | 完整分析报告 |
| 报告优化 | 扩增完善当前报告 | 优化版报告 |
| 模型报告 | 输出模型详情和优化计划 | 模型技术报告 |
| 系统报告 | 输出系统全部模块详情 | 系统功能报告 |
| 数据更新 | 执行数据更新和检核 | 数据状态报告 |
| 模型优化 | 执行模型训练和优化 | 优化结果报告 |
| 系统优化 | 全面优化系统各模块 | 优化结果报告 |
| 提交反馈 | 登记用户反馈意见 | 反馈确认 |

### 1. 分析报告指令

**触发**: 用户发送"分析报告"或类似指令

**执行流程**:
```
1. 数据采集 → 2. 数据检核 → 3. 特征提取 → 4. 模型预测 → 5. 报告生成
```

**执行步骤**:
1. 调用数据管理中心获取实时数据
2. 执行数据检核，确保数据质量
3. 提取技术面、基本面、资金面特征
4. 使用预测模型生成买卖建议
5. 整合分析维度生成完整报告

### 2. 报告优化指令

**触发**: 用户发送"报告优化"或类似指令

**执行流程**:
```
1. 获取最新数据 → 2. 扩充分析维度 → 3. 深度解读 → 4. 优化报告
```

**执行步骤**:
1. 获取最新实时数据
2. 扩充分析维度（增加行业对比、跨市场联动等）
3. 结合专业知识进行深度解读
4. 生成更加专业完善的分析报告

### 3. 模型报告指令

**触发**: 用户发送"模型报告"或类似指令

**输出内容**:
- 模型架构详情
- 特征维度列表
- 训练数据集描述
- 回测性能指标
- 历史优化记录
- 当前模型参数
- 下一步优化计划

### 4. 系统报告指令

**触发**: 用户发送"系统报告"或类似指令

**输出内容**:
- 系统整体架构图
- 数据管理中心详情
- 模型模块详情
- 报告生成中心详情
- 指令处理中心详情
- 后续完善计划

### 5. 数据更新指令

**触发**: 用户发送"数据更新"或类似指令

**执行流程**:
```
1. 扫描新数据源 → 2. 获取最新数据 → 3. 数据检核 → 4. 虚拟数据处理 → 5. 更新报告
```

**执行步骤**:
1. 扫描并集成新的有效数据源
2. 获取最新行情和财经数据
3. 执行数据检核（完整性、一致性、逻辑性）
4. 处理虚拟数据和缺失数据
5. 更新数据管理日志

### 6. 模型优化指令

**触发**: 用户发送"模型优化"或类似指令

**执行流程**:
```
1. 分析优化需求 → 2. 新增特征/标的 → 3. 数据准备 → 4. 模型训练 → 5. 回测验证 → 6. 更新报告逻辑
```

**执行步骤**:
1. 分析实时行情，判断是否需要新增特征或标的
2. 根据需求扩展分析维度
3. 整理新增特征的历史数据
4. 执行数据更新和数据检核
5. 尝试新的模型算法（如深度学习、强化学习）
6. 多轮回测迭代，取最优参数
7. 更新分析报告生成逻辑

### 7. 系统优化指令

**触发**: 用户发送"系统优化"或类似指令

**执行流程**:
```
1. 模型优化 → 2. 报告优化 → 3. 系统检查 → 4. 全面完善
```

**执行步骤**:
1. 执行模型优化指令
2. 执行报告优化指令
3. 检查系统各模块联动
4. 验证功能完整性
5. 迭代优化直至无近期优化目标

### 8. 提交反馈指令

**触发**: 用户发送"提交反馈"或类似指令

**执行步骤**:
1. 获取用户反馈内容
2. 记录反馈时间和用户信息
3. 分类反馈类型（功能建议、Bug报告、体验优化等）
4. 生成反馈确认信息

---

## 反馈管理

### 反馈分类

```python
FEEDBACK_TYPES = {
    "feature_request": "功能请求",
    "bug_report": "问题报告",
    "performance_issue": "性能问题",
    "ui_feedback": "界面反馈",
    "accuracy_feedback": "准确度反馈",
    "data_issue": "数据问题",
    "other": "其他"
}

FEEDBACK_FORMAT = {
    "feedback_type": "类型",
    "content": "反馈内容",
    "timestamp": "提交时间",
    "user_id": "用户标识",
    "contact": "联系方式(可选)",
    "attachments": "附件列表"
}
```

---

## 使用示例

### 示例1：生成分析报告
```
用户: 分析报告
系统: 获取实时数据，执行分析预测，生成完整报告
```

### 示例2：优化模型
```
用户: 模型优化
系统: 分析优化需求，执行数据更新，进行模型训练回测，输出优化结果
```

### 示例3：提交反馈
```
用户: 提交反馈 - 希望增加港股分析功能
系统: 记录反馈内容，生成反馈确认
```

---

## 系统状态管理

### 状态定义

```python
SYSTEM_STATUS = {
    "READY": "就绪",
    "ANALYZING": "分析中",
    "TRAINING": "训练中",
    "UPDATING": "更新中",
    "ERROR": "异常"
}

MODEL_STATUS = {
    "initial": "初始模型",
    "training": "训练中",
    "optimized": "已优化",
    "validated": "已验证",
    "deployed": "已部署"
}

DATA_STATUS = {
    "fresh": "数据新鲜",
    "stale": "数据较旧",
    "updating": "更新中",
    "error": "获取失败"
}
```

---

## 错误处理

### 常见错误及处理

| 错误类型 | 处理方式 |
|---------|---------|
| 数据获取失败 | 切换备用数据源，记录日志 |
| 数据检核失败 | 标记异常，尝试修复或虚拟 |
| 模型预测失败 | 使用规则引擎兜底 |
| 报告生成失败 | 输出基础信息，提示用户 |
| 系统异常 | 记录错误，输出状态报告 |

---

## 性能要求

- 数据获取响应时间: <5秒
- 分析报告生成时间: <30秒
- 模型训练时间: 根据数据量动态调整
- 系统可用性: >99.5%

---

## 免责声明

本系统提供的分析和预测仅供参考，不构成任何投资建议。用户应基于自身判断做出投资决策，并承担相应的投资风险。系统不对因使用本分析报告而产生的任何损失承担责任。
