# 每日金融早报生成器 - 安装指南

## 文件结构

```
daily-financial-report/
├── SKILL.md                           # 技能定义文件
├── README.md                          # 安装说明
├── assets/
│   └── report_template.html          # HTML报告模板
└── references/
    └── data_sources.md               # 数据源参考
```

## 安装方法

### 方法一：直接复制到用户技能目录

1. 将整个 `daily-financial-report` 文件夹复制到 MiniMax Agent 的用户技能目录：
   ```
   ~/.minimax/skills/daily-financial-report/
   ```

2. 重启 MiniMax Agent 或刷新技能列表

### 方法二：打包安装

1. 在 `/workspace/skills/daily-financial-report/` 目录下执行：
   ```bash
   zip -r daily-financial-report.skill .
   ```

2. 在 MiniMax Agent 中导入生成的 `.skill` 文件

## 功能说明

### 触发方式
- 发送"生成每日金融早报"
- 发送"生成今日金融报告"
- 发送"金融市场日报"

### 主要功能
1. **全球股票指数**：覆盖中国A股、美股、亚太（日韩）、欧洲、新兴市场（印度、印尼）
2. **大宗商品**：原油、天然气、煤炭、铜、铝、黄金、白银、农产品等
3. **外汇市场**：美元指数、美元/人民币、美元/日元
4. **加密货币**：比特币、以太坊
5. **重点关注**：英伟达、MiniMax、OpenClaw/QClaw
6. **宏观新闻**：货币政策、地缘政治、经济数据

### 数据来源
- 实时市场数据：stocks_price API
- 金融新闻：多源搜索聚合
- 价格数据：中国国家统计局、我的钢铁网等

## 报告输出

- 生成路径：`/workspace/reports/{日期}_daily_report.html`
- 自动部署到线上可访问

## 自定义修改

如需修改报告格式或数据源，请编辑：
- `assets/report_template.html` - 报告模板
- `references/data_sources.md` - 数据源配置
- `SKILL.md` - 工作流程和触发词
