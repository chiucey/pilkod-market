# stock-analysis-pro

专业级多维度股票分析技能，为投资者提供全面的股票分析服务。

## 核心功能

| 功能 | 说明 |
|------|------|
| 🎯 四维分析 | 基本面 + 技术面 + 估值 + 风险 |
| 📊 20+指标 | MA/MACD/RSI/KDJ/BOLL等 |
| 💹 估值模型 | PE/PB/PEG/DCF/DDM |
| 🔒 安全合规 | 数据隔离、禁止交易执行 |
| 🧪 测试完备 | 单元测试覆盖 |
| 📝 文档完善 | 4份专业参考手册 |

## 支持市场

- **美股**：AAPL, MSFT, GOOGL 等
- **港股**：0700.HK, 9988.HK 等
- **A股**：600519.SS, 000001.SZ 等

## 安装依赖

```bash
pip install yfinance pandas numpy ta matplotlib
```

## 快速使用

### Python调用

```python
from src.main import run

# 基本分析
result = run({
    'symbol': 'AAPL',
    'market': 'us',
    'period': '1y'
})

print(result['data']['report'])

# 带对比分析
result = run({
    'symbol': 'AAPL',
    'market': 'us',
    'compare': 'MSFT'
})
```

### 命令行运行

```bash
python src/main.py
```

## 目录结构

```
stock-analysis-pro/
├── SKILL.md                 # 核心技能定义
├── _meta.json               # 元数据
├── src/
│   └── main.py             # 主执行代码
├── tests/
│   └── test_main.py        # 单元测试
├── config/
│   └── settings.yaml       # 配置文件
├── references/             # 参考文档
│   ├── technical_indicators.md
│   ├── valuation_models.md
│   ├── risk_assessment.md
│   └── financial_indicators.md
├── instructions/
│   └── system_prompt.md    # AI指令
├── scripts/
│   ├── validate_skill.py   # 验证脚本
│   └── package_skill.py    # 打包脚本
└── assets/
```

## 分析维度

### 1. 技术面分析
- 趋势指标：MA/EMA/MACD/DMI
- 动量指标：RSI/KDJ/WR/ROC
- 成交量指标：OBV/VR
- 波动性指标：BOLL/ATR

### 2. 基本面分析
- 盈利能力：毛利率/净利率/ROE/ROA
- 成长能力：营收增速/净利润增速
- 偿债能力：资产负债率/流动比率

### 3. 估值分析
- 相对估值：PE/PB/PEG/PS
- 绝对估值：DCF/DDM

### 4. 风险评估
- Beta系数
- 波动率
- 最大回撤
- VaR

## 单元测试

```bash
cd tests
python test_main.py
```

## ⚠️ 免责声明

本技能仅提供数据展示与技术分析，**不构成任何投资建议**。投资有风险，决策需谨慎。
