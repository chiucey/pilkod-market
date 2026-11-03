#!/usr/bin/env python3
"""
投资认知记忆系统初始化脚本
用于在 /memories/investment_cognition/ 目录下初始化记忆系统
"""

import os
from datetime import datetime

# 记忆系统根目录
MEMORY_ROOT = "/memories/investment_cognition"

# 目录结构
DIRECTORIES = [
    "",
    "technical",
    "sentiment",
    "fundamental",
    "policy",
    "retail_psychology",
    "smart_money",
    "watchlist",
    "recent_analysis"
]

# 索引文件内容
INDEX_TEMPLATE = """# 投资认知记忆系统 - 总索引

## 系统信息
- **创建时间**：{created_time}
- **版本**：1.0.0
- **维护者**：投资认知系统

## 统计概览

| 维度 | 认知数量 | 最后更新 |
|------|---------|---------|
| 技术面 (technical) | 0 | - |
| 情绪面 (sentiment) | 0 | - |
| 基本面 (fundamental) | 0 | - |
| 政策面 (policy) | 0 | - |
| 散户心理 (retail_psychology) | 0 | - |
| 主力意图 (smart_money) | 0 | - |
| 关注票池 (watchlist) | 0 | - |
| 近期盘面 (recent_analysis) | 0 | - |
| **总计** | **0** | - |

## 核心认知 TOP 10
*暂无记录*

## 待验证认知
*暂无待验证项目*

## 最近更新
*暂无更新记录*

## 系统说明

本记忆系统采用八大维度框架：
1. **技术面**：价格形态、技术指标、量价关系
2. **情绪面**：市场情绪、板块轮动、人气指标
3. **基本面**：财务质量、竞争优势、估值水平
4. **政策面**：宏观政策、产业政策、监管动向
5. **散户心理**：行为偏差、认知陷阱、反向思维
6. **主力意图**：资金动向、建仓痕迹、控盘特征
7. **关注票池**：重点跟踪标的清单
8. **近期盘面**：盘面解读、操作记录、复盘反思

## 量化评分体系

每个认知条目采用四维评分：
- **逻辑完整性**：推理链条是否完整
- **数据支撑度**：是否有数据/证据支撑
- **时效适用性**：在当前环境下是否适用
- **可执行性**：能否转化为具体操作

综合评分 = 逻辑完整性 + 数据支撑度 + 时效适用性 + 可执行性
满分100分，80分以上为高质量认知。
"""

# 各维度初始化内容模板
DIMENSION_TEMPLATES = {
    "technical": """# 技术面认知库

## 说明
本文件存储与技术分析相关的投资认知，包括：
- 均线系统应用
- MACD、KDJ等指标用法
- 趋势判断方法
- 量价关系分析
- 形态识别与应用

## 权重
技术面在投资决策中权重为 **20%**

## 认知列表

---
""",
    "sentiment": """# 情绪面认知库

## 说明
本文件存储与市场情绪相关的投资认知，包括：
- 市场情绪周期判断
- 贪婪恐惧指数应用
- 板块轮动规律
- 人气指标解读

## 权重
情绪面在投资决策中权重为 **15%**

## 认知列表

---
""",
    "fundamental": """# 基本面认知库

## 说明
本文件存储与基本面分析相关的投资认知，包括：
- 财务指标分析框架
- 估值方法与应用
- 行业周期判断
- 公司竞争力评估

## 权重
基本面在投资决策中权重为 **25%**

## 认知列表

---
""",
    "policy": """# 政策面认知库

## 说明
本文件存储与政策分析相关的投资认知，包括：
- 宏观经济政策解读
- 产业政策影响评估
- 监管动向分析
- 政策传导机制

## 权重
政策面在投资决策中权重为 **20%**

## 认知列表

---
""",
    "retail_psychology": """# 散户心理认知库

## 说明
本文件存储与投资者行为相关的认知，包括：
- 常见认知偏差识别
- 行为陷阱规避方法
- 反向思维应用
- 群体行为分析

## 权重
散户心理在投资决策中权重为 **10%**

## 认知列表

---
""",
    "smart_money": """# 主力意图认知库

## 说明
本文件存储与主力资金分析相关的认知，包括：
- 主力建仓特征识别
- 控盘行为分析
- 出货信号判断
- 龙虎榜解读

## 权重
主力意图在投资决策中权重为 **10%**

## 认知列表

---
""",
    "watchlist": """# 关注票池

## 说明
本文件记录重点关注的投资标的，包括：
- 入池标准
- 标的详细信息
- 持仓状态
- 跟踪要点

## 管理原则
- 定期复核：每月评估是否保留
- 动态调整：根据市场变化更新
- 有进有出：保持池子活性

## 标的列表

### A级（重点持仓/密切关注）

| 标的代码 | 标的名称 | 行业 | 入池日期 | 关注理由 | 状态 |
|---------|---------|------|---------|---------|------|
| - | - | - | - | - | - |

### B级（跟踪观察）

| 标的代码 | 标的名称 | 行业 | 入池日期 | 关注理由 | 状态 |
|---------|---------|------|---------|---------|------|
| - | - | - | - | - | - |

### C级（备选研究）

| 标的代码 | 标的名称 | 行业 | 入池日期 | 关注理由 | 状态 |
|---------|---------|------|---------|---------|------|
| - | - | - | - | - | - |

---
""",
    "recent_analysis": """# 近期盘面分析

## 说明
本文件记录近期盘面解读、操作记录和复盘反思，为投资决策积累素材。

## 记录规范
- 每日/每周定期记录
- 记录关键事件和点位
- 关联到具体认知条目
- 定期复盘总结

## 日期索引

### {current_date}

**今日盘面**
- 上证指数：--
- 深证成指：--
- 创业板指：--
- 成交量：--

**主要热点**
-

**重要消息**
-

**操作记录**
-

**明日关注**
-

---
"""
}

def create_directory_structure():
    """创建目录结构"""
    for directory in DIRECTORIES:
        path = os.path.join(MEMORY_ROOT, directory)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"✓ 创建目录: {path}")
        else:
            print(f"· 目录已存在: {path}")

def create_index_file():
    """创建总索引文件"""
    index_path = os.path.join(MEMORY_ROOT, "_index.md")
    content = INDEX_TEMPLATE.format(
        created_time=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ 创建索引文件: {index_path}")

def create_dimension_files():
    """创建各维度文件"""
    for dim, content in DIMENSION_TEMPLATES.items():
        file_path = os.path.join(MEMORY_ROOT, dim, f"{dim}.md")

        # 特殊处理需要日期的文件
        if dim == "recent_analysis":
            content = content.format(
                current_date=datetime.now().strftime("%Y-%m-%d")
            )

        # 检查文件是否已存在
        if os.path.exists(file_path):
            print(f"· 文件已存在，跳过: {file_path}")
            continue

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 创建维度文件: {file_path}")

def create_readme():
    """创建README说明文件"""
    readme_path = os.path.join(MEMORY_ROOT, "README.md")
    readme_content = """# 投资认知记忆系统

## 系统简介

这是一个系统化的投资认知管理工具，通过量化评估帮助投资者：
- 将主观认知转化为客观框架
- 避免情绪对决策的影响
- 构建可复用的投资体系
- 持续积累和迭代投资认知

## 目录结构

```
/memories/investment_cognition/
├── _index.md                 # 总索引
├── README.md                 # 本说明文件
├── technical/               # 技术面认知
├── sentiment/               # 情绪面认知
├── fundamental/              # 基本面认知
├── policy/                   # 政策面认知
├── retail_psychology/        # 散户心理认知
├── smart_money/              # 主力意图认知
├── watchlist/                # 关注票池
└── recent_analysis/          # 近期盘面分析
```

## 使用方式

### 添加新认知

1. 输入投资观点或认知
2. 系统进行联网校验
3. 输出量化评估报告
4. 用户决策是否加入
5. 确认后写入对应维度

### 查询认知

直接询问特定维度的内容，例如：
- "技术面有哪些认知？"
- "关注票池里有哪些标的？"
- "散户心理方面有什么认知？"

### 更新认知

1. 提出修改意见
2. 系统重新评估
3. 更新记录

## 量化评分体系

四维评分（每项25分，满分100）：
- **逻辑完整性**：推理是否严密
- **数据支撑度**：是否有证据
- **时效适用性**：是否适合当前环境
- **可执行性**：能否转化为操作

评分80+为高质量认知，60-79建议加入，40-59谨慎加入。

## 维护周期

- 高评分认知（80+）：每季度复核
- 中评分认知（40-79）：每月复核
- 低评分认知（<40）：每周复核

---
*本系统由 AI 辅助维护*
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ 创建README: {readme_path}")

def main():
    print("=" * 50)
    print("投资认知记忆系统 - 初始化")
    print("=" * 50)
    print()

    print("正在初始化记忆系统...")
    print()

    create_directory_structure()
    create_index_file()
    create_dimension_files()
    create_readme()

    print()
    print("=" * 50)
    print("初始化完成！")
    print(f"记忆系统位置: {MEMORY_ROOT}")
    print("=" * 50)

if __name__ == "__main__":
    main()
