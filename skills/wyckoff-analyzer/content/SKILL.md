---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4ac5a60b35c545cb0ac65d83d5b2c392
    PropagateID: 4ac5a60b35c545cb0ac65d83d5b2c392
    ReservedCode1: 304502203d1bb5a199fd2c5bae737065d5c50975f27b5a1509e859bedb908816ed28794f022100b1167029a15410e7d6bb437abdd80019db998547daec021562f76bc592bc4d75
    ReservedCode2: 3045022100bd4e879d774172abbd05bbefa3cbba4ba005aa75f89afea54d0a8a9ad626dd3f02205a5bcc7b2e321b04c490f2a2dae68d6c678da3aaf7fe5d2dcc25d3b5f30b55dc
description: |
    维克夫（Wyckoff）量价分析技能。用于分析A股个股的主力阶段判断、量价关系、资金流向、点数图生成。
    触发语："分析[股票]"、"维克夫分析"、"点数图"、"主力在做什么"、"[代码]什么阶段"。
name: wyckoff-analyzer
---

# 维克夫量价分析 Skill

## 第一步：读取框架知识库

```
read /workspace/skills/wyckoff-analyzer/references/wyckoff-framework.md
```

## 第二步：获取股票数据

使用 curl 从新浪API获取K线数据（华数240分钟线=日K）：

```bash
# 示例：获取60天日K线
curl -s --max-time 8 "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002644&scale=240&ma=no&datalen=60"
```

## 第三步：生成点数图

运行脚本生成ASCII点数图：

```bash
python3 /workspace/skills/wyckoff-analyzer/scripts/pf_chart.py <股票代码>
```

例如：
```bash
python3 /workspace/skills/wyckoff-analyzer/scripts/pf_chart.py 002644
```

## 第四步：用图像合成生成可视化点数图

基于K线数据，用 image_synthesize 生成专业的P&F图表：

**提示词模板（直接复制使用）：**

```
Generate a professional Point and Figure (P&F) stock chart for [股票名称]([代码])。

Requirements:
1. Title: '[股票名称]([代码]) 点数图 P&F Chart'
2. Y-axis: price levels based on data (min [最低价], max [最高价])
3. Grid-based P&F chart with X columns (rising/bullish) and O columns (falling/bearish)
4. RED for X columns, GREEN/blue for O columns
5. Current price indicator line at [当前价] yuan
6. Chart parameters: Box size = 0.2 yuan, Reversal = 3 boxes
7. Legend: X = rising (accumulation/markup), O = falling (distribution/markdown)
8. Black background, white text, professional financial terminal style
9. Key levels annotated: Support at [支撑位], Resistance at [压力位]
10. Date: [当前日期]

Based on actual price data: [简要描述价格走势，如：从X元涨到X元后回落]
```

## 第五步：按维克夫框架分析

读取框架后，综合点数图和K线数据，输出结构化分析报告。

## 输出格式

```
## [股票名称]（[代码]）维克夫量价分析

### 点数图摘要
[附上生成的P&F图表URL]

### 一、当前阶段判定
【判定】：[吸筹/拉升/派发/回落]
【依据】：[量价核心证据]

### 二、供求法则验证
- 量价关系：[描述]
- 主力意图：[推断]

### 三、因果法则验证
- 前期蓄势：[判断]
- 点数图目标位：[计算]

### 四、努力与结果验证（量价背离）
- [是否出现背离]

### 五、关键价位
| 类型 | 价位 |
|------|------|
| 压力位 | |
| 支撑位 | |
| 止损位 | |

### 六、操作建议
[最优操作]

### 七、铁律检查
[是否有违背铁律的风险]
```

## 注意事项

- 点数图生成依赖网络数据，若curl超时可跳过图表，仅做文字分析
- 阶段判定以量价为核心，基本面辅助验证
- 始终包含"看不懂就离场"的铁律提醒
- 发送到微信时使用 message 工具的 media 参数
