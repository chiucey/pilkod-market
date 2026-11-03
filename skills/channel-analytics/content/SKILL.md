---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e63a2b0d9e6a036b4df343df07e44aec
    PropagateID: e63a2b0d9e6a036b4df343df07e44aec
    ReservedCode1: 3046022100b71bbb52ff897d921b48195249b2d11387bf941fb94eaecb2855e9dca4ca1a1e022100c71f6a0a8754b3e16605746199b553730016ecfbf7c9dab6f36f593f4b1f7fda
    ReservedCode2: 304402206a3d54aaf33958308da36170503560ecbd3828e53e416cf82257ccadbad84b00022051cfcac764dcc9bd423b0dda602ac5b5c7d16cf033e16ffc60645ac29c5975c1
description: 渠道数据分析专家。Use when users ask to analyze marketing channels, evaluate channel ROI, generate channel reports, or assess channel performance. 当用户要求分析渠道表现、评估各渠道ROI、生成渠道分析报告时使用。
name: channel-analytics
---

# 渠道分析技能

## 核心能力

- 从 MySQL 数据库读取渠道数据
- 执行多维度渠道分析（流量、转化、ROI、成本）
- 生成分析报告（HTML/JSON/Excel/Markdown）
- 提供优化建议

## 使用方法

### 1. 命令行分析
```bash
cd /workspace/channel-analysis/scripts
python main.py analyze
python main.py report --format html
```

### 2. 启动 API 服务
```bash
python main.py api
# 访问 http://localhost:5000/api/analysis
```

### 3. 定时任务
```bash
python main.py schedule
```

## 配置要求

编辑 `analysis_config.py` 修改数据库连接：
```python
@dataclass
class DatabaseConfig:
    host: str = "你的数据库地址"
    port: int = 3306
    database: str = "数据库名"
    user: str = "用户名"
    password: str = "密码"
```

## 交付物

| 类型 | 说明 |
|------|------|
| Web 应用 | 可视化仪表盘 |
| 分析脚本 | Python 自动化脚本 |
| 数据库脚本 | 表结构 + 模拟数据 |
| 报告模板 | HTML/JSON/Excel/Markdown |