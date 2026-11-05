# 每日基金收益报表

自动化获取基金净值数据，分析持仓收益，生成美观的飞书消息卡片并定时推送。

## 功能特性

- 📊 **实时净值获取**：从天天基金网公开API获取基金净值数据
- 📈 **智能收益分析**：计算当日收益、累计收益、持仓分布等
- 📱 **飞书消息推送**：发送美观的富文本卡片消息
- ⏰ **定时任务**：支持每个交易日自动执行
- 📋 **历史记录**：自动保存每日报表数据

## 快速开始

### 1. 配置持仓

编辑 `assets/portfolio.json` 文件，添加您的基金持仓：

```json
{
  "holdings": [
    {
      "code": "000001",
      "name": "基金名称",
      "shares": 1000.00,
      "cost": 1.5000,
      "buy_date": "2024-01-15"
    }
  ]
}
```

### 2. 配置飞书Webhook

1. 打开飞书群聊
2. 点击群设置 → 群机器人 → 添加机器人
3. 选择「自定义机器人」
4. 复制Webhook地址

### 3. 安装依赖

```bash
pip install requests pandas
```

### 4. 测试运行

```bash
python scripts/generate_report.py \
  --portfolio assets/portfolio.json \
  --feishu-webhook "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

## 使用方法

### 基本用法

```bash
python scripts/generate_report.py \
  --portfolio assets/portfolio.json \
  --feishu-webhook "YOUR_WEBHOOK_URL"
```

### 仅生成报表（不发送）

```bash
python scripts/generate_report.py \
  --portfolio assets/portfolio.json \
  --feishu-webhook "YOUR_WEBHOOK_URL" \
  --no-send
```

### 指定输出目录

```bash
python scripts/generate_report.py \
  --portfolio assets/portfolio.json \
  --feishu-webhook "YOUR_WEBHOOK_URL" \
  --output data/my_reports
```

## 设置定时任务

### 使用 cron（Linux/macOS）

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每个交易日下午16:00执行）
0 16 * * 1-5 cd /workspace/temp-skills/daily-fund-report && python scripts/generate_report.py --portfolio assets/portfolio.json --feishu-webhook "YOUR_WEBHOOK_URL"
```

### 使用 Windows 任务计划程序

1. 打开「任务计划程序」
2. 创建基本任务
3. 设置触发器：每天 16:00（工作日）
4. 设置操作：启动程序 `python.exe`，参数为脚本路径

## 文件结构

```
daily-fund-report/
├── SKILL.md                    # 技能定义文件
├── _meta.json                   # 元数据
├── scripts/
│   ├── generate_report.py       # 主程序
│   ├── fetch_fund_data.py       # 净值获取
│   ├── analyze_returns.py       # 收益分析
│   └── send_feishu.py           # 飞书推送
├── assets/
│   ├── portfolio_template.json  # 持仓模板
│   └── feishu_card_template.json # 消息卡片模板
├── references/
│   └── fund_data_source.md      # 数据源文档
└── data/
    └── reports/                 # 报表存储目录
```

## 示例输出

```
==================================================
📊 每日基金收益报表
==================================================

📅 2024年12月20日

💰 总资产：¥15,234.56
📈 今日收益：+¥156.78 (+1.04%)
💵 累计收益：+¥1,234.56 (+8.82%)

【持仓明细】
----------------------------------------
1. 平安先锋混合A (000001)
   持有份额：1000.00份
   今日收益：+¥12.34 (+0.82%)
   累计收益：+¥123.45 (+8.23%)
   持仓占比：30.0%

2. 广发稳健增长A (270002)
   持有份额：2000.00份
   今日收益：+¥24.60 (+1.00%)
   累计收益：+¥246.00 (+10.00%)
   持仓占比：25.0%
...
```

## 注意事项

1. **交易日限制**：净值数据仅在工作日更新
2. **净值时间**：盘中显示估算净值，收盘后更新实际净值
3. **数据延迟**：接口数据可能存在几分钟延迟
4. **投资风险**：报表仅供参考，投资决策需谨慎

## 常见问题

### Q: 净值获取失败怎么办？

A: 检查网络连接，确认基金代码正确，接口可能临时维护。

### Q: 如何添加更多基金？

A: 在 `portfolio.json` 的 `holdings` 数组中添加新条目。

### Q: 可以设置不同的推送时间吗？

A: 修改 cron 表达式或任务计划程序设置。

### Q: 支持哪些类型的基金？

A: 支持所有在天天基金网有数据的开放式基金，包括股票型、混合型、债券型、指数型等。

## 许可证

本项目仅供个人学习使用，数据来源为公开API。
