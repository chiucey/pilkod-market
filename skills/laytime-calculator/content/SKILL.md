---
name: laytime-calculator
description: LAYTIME（装卸时间）计算技能，支持单港/双港卸货，自动滞期判断，用户可修改判断，生成HTML/PDF报告
dependency:
  python:
    - pandas>=2.0.0
---

# LAYTIME Calculator

## When To Trigger

遇到以下需求时，使用本技能：

- 上传 SOF（Statement of Facts）+ 合同条款文件
- 用户说"计算LAYTIME"、"算一下这个案子"、"LAYTIME计算"
- 需要计算滞期费（Demurrage）或速遣费（Despatch）

## 核心约束

1. **单Agent模式** - 严禁启动sub-agent，所有步骤在同一会话完成
2. **合同原文是唯一依据** - 未经对照合同条款，不得自行判断
3. **货量从SOF精确读取** - 不估算
4. **LLM只判断，Python做计算** - 数值累加交给脚本
5. **输出用英文，对话用中文**
6. **合同无约定 = 照算**

## 核心工作流（两轮迭代）

### 第一轮：基础判断 + 找滞期点

```
阶段1: 解析
  输入: SOF + 合同
  输出: extracted/contract.json, extracted/sof_parsed.json

阶段2: 第一轮LLM判断
  输入: contract.json + sof_parsed.json
  输出: extracted/judgments1.json
  要求: 逐条判断是否计入，基于合同条款（SHEX、WWD等），不考虑"一旦滞期永久滞期"

阶段3: 第一轮Python累加（强制执行）
  脚本: laytime-calculator/scripts/calculate_demurrage.py
  输入: extracted/judgments1.json
  输出: extracted/interim_result.json
  功能: 累加时间，找到滞期点，标记位置
  执行: python3 laytime-calculator/scripts/calculate_demurrage.py 用户上传/{案例目录}
```

### 第二轮：滞期后重新判断

```
阶段4: 第二轮判断（Python自动执行）
  脚本: laytime-calculator/scripts/apply_demurrage_rules.py
  输入: judgments1.json + interim_result.json
  输出: extracted/judgments2.json
  功能: 滞期点前保持 + 滞期点后重新判断（周末/节假日/雨天→INCL，Shifting→EXCL）
  执行: python3 laytime-calculator/scripts/apply_demurrage_rules.py 用户上传/{案例目录}

阶段5: 用户修改（可中断点）
  输入: judgments2.json
  输出: extracted/judgments_final.json, extracted/judgments_changelog.json
  用户可指定时间戳修改判断，记录到changelog

阶段6: 最终计算（强制执行）
  脚本: laytime-calculator/scripts/calculate_final.py
  输入: judgments2.json 或 judgments_final.json
  输出: calculation/result.json
  功能: 重新累加，计算滞期费/速遣费
  执行: python3 laytime-calculator/scripts/calculate_final.py 用户上传/{案例目录}

阶段7: 渲染
  脚本: 基础设定/LAYTIME_TEMPLATES/render_laytime_v2.py
  输入: calculation/result.json
  输出: calculation/output/LTC_*.html
  执行: python3 基础设定/LAYTIME_TEMPLATES/render_laytime_v2.py 用户上传/{案例目录}
```

## 文件结构

```
用户上传/{船名}_{港口}_{货物}/
├── uploads/                           # 原始上传文件
├── extracted/
│   ├── contract.json                  # 合同条款结构化
│   ├── sof_parsed.json                # SOF事件时间线
│   ├── judgments1.json                # 第一轮判断（基础）
│   ├── interim_result.json            # 中间结果（含滞期点）
│   ├── judgments2.json                # 第二轮判断（滞期后）
│   ├── judgments_final.json           # 最终判断（用户修改后）
│   └── judgments_changelog.json       # 用户修改记录
├── calculation/
│   ├── result.json                    # 最终计算结果
│   └── output/
│       └── LTC_*.html
└── README.md
```

## 关键规则

### ⚠️ NOR递交规则 vs Laytime计算规则（必须区分）

**这是最常见的错误来源！这两个规则是独立的，互不影响！**

#### 错误示例
```
❌ 合同条款：NOR ATDNSHINC + 8,000 MT/WWD SHEX
❌ 错误判断：ATDNSHINC允许周末递交NOR → 周末也计数
```

#### 正确理解
```
✅ ATDNSHINC：只影响NOR何时递交/生效（周末可递交）
✅ WWD SHEX：只影响laytime计算（周末仍排除）

结论：周末递交NOR立即生效，但周末时间不计数
```

#### 强制判断流程
```
步骤1：确定NOR递交规则 → 判断NOR何时递交/生效
步骤2：确定Laytime起算时间 → 计算起算点
步骤3：确定Laytime计算规则 → 独立判断每个时间段

⚠️ 步骤1和步骤3是独立的！详见 references/rules.md
```

### 复合事件拆分（重要）

**定义**：同一条SOF记录中包含多个性质不同的子事件，需要拆分为多条记录分别判断。

**典型场景**：
1. **检疫等待期间有下雨**：WAITING FOR CLEARANCE + RAIN PERIODS
2. **等泊位期间有恶劣天气**：WAITING FOR BERTH + FOG/STORM
3. **装卸期间天气中断**：DISCHARGING + RAIN INTERRUPTION

**拆分示例**：

```
输入（原始SOF记录）:
30-MAR MON 0000-2400 "WAITING FOR CARGO SAMPLING. RAIN PERIODS: 0000-0200, 0606-1045, 1340-1512"

输出（拆分后的judgments）:
[
  {
    "date": "2026-03-30",
    "time_range": "0000-0200",
    "event": "SUSPENDED DUE TO RAIN",
    "hours": 2.0,
    "status": "EXCL",
    "reason": "Weather interruption - rain (WWD clause)"
  },
  {
    "date": "2026-03-30", 
    "time_range": "0200-0606",
    "event": "WAITING FOR CARGO SAMPLING",
    "hours": 4.1,
    "status": "INCL",
    "reason": "Working day, waiting for phytosanitary clearance"
  },
  {
    "date": "2026-03-30",
    "time_range": "0606-1045",
    "event": "SUSPENDED DUE TO RAIN",
    "hours": 4.65,
    "status": "EXCL",
    "reason": "Weather interruption - rain (WWD clause)"
  },
  ...
]
```

**拆分识别信号**：
- RAIN PERIODS: 0000-0200, 0606-1045
- RAIN FROM 1700-2015
- RAIN AT 0930-1230
- FOG/STORM PERIODS
- 多个时间段用逗号分隔

**拆分判断原则**：
- 雨天时间段 → EXCL（滞期前）/ INCL（滞期后）
- 非雨天时间段 → 按主事件性质判断（如QUARANTINE → INCL）
- 保持时间连续性（拆分后时间总和 = 原始时间段）

### "一旦滞期，永久滞期"原则

**含义**：
- Laytime期间：受WWD、SHEX等条款约束，周末/恶劣天气不计入
- 进入滞期后：所有时间都计入，除非合同明确约定排除或属于船东过错

**滞期后仍排除的情况**：
- Shifting/移泊（船东行为）
- 船东原因延误（设备故障、船员罢工）
- 合同明确约定滞期期间仍排除的情况

### 排除规则优先级

1. 合同有明示？→ 按合同执行（第一原则）
2. 合同无明示，查默认规则？→ 按默认规则执行（第二原则）
3. 无规则可依？→ RAG查书（第三原则）
4. 无依据？→ 标注"待确认"，按"计入"处理

## 修改模块

用户可指定时间戳修改判断：

```
用户: "03-27 14:00 这条应该是 INCL"
我: 
  1. 用时间戳定位 judgments2.json 中的条目
  2. 修改 status 和 reason
  3. 设置 user_confirmed: true
  4. 添加修改记录到 judgments_changelog.json
  5. 生成 judgments_final.json
  6. 重新运行 Python 计算脚本
  7. 重新生成 HTML
```

## 渲染规范

**模板位置**：`基础设定/LAYTIME_TEMPLATES/`
- `template_1port.html` - 单港模板
- `template_2port.html` - 双港模板
- `render_laytime_v2.py` - 渲染脚本

**执行方式**：
```bash
python3 基础设定/LAYTIME_TEMPLATES/render_laytime_v2.py 用户上传/{案例目录}
```

**禁止行为**：
- ❌ 禁止手写HTML
- ❌ 禁止手动.replace()替换模板
- ❌ 禁止新建或修改模板文件

## 标准Python脚本

**脚本位置**：`laytime-calculator/scripts/`

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `calculate_demurrage.py` | 第一轮：累加+找滞期点 | judgments1.json | interim_result.json |
| `apply_demurrage_rules.py` | 第二轮：滞期后重新判断 | judgments1.json + interim_result.json | judgments2.json |
| `calculate_final.py` | 最终计算 | judgments2.json | result.json |

**执行顺序**：
```bash
# 步骤1: 找滞期点
python3 laytime-calculator/scripts/calculate_demurrage.py 用户上传/{案例目录}

# 步骤2: 滞期后重新判断
python3 laytime-calculator/scripts/apply_demurrage_rules.py 用户上传/{案例目录}

# 步骤3: 最终计算
python3 laytime-calculator/scripts/calculate_final.py 用户上传/{案例目录}

# 步骤4: 渲染HTML
python3 基础设定/LAYTIME_TEMPLATES/render_laytime_v2.py 用户上传/{案例目录}
```

**禁止行为**：
- ❌ 禁止新建或修改脚本
- ❌ 禁止跳过任何步骤
- ❌ 禁止手动计算滞期点

## 详细文档

- `references/workflow.md` - 完整工作流细节
- `references/rules.md` - 判断规则表
- `references/nor_workflow.md` - NOR/Laytime起算工作流
- `references/demurrage_rules.md` - 滞期判断规则

## 已完成案例

1. SDM CHONGQING NANSHA DDGS（单港）
2. PAIWAN BRAVE JIANGYIN BARLEY（单港）
3. LYRIC SUN MACHONG BARLEY（单港）
4. AL WATHBA ZHANGZHOU JIANGYIN BARLEY（双港）
5. BAKKEDAL ZHANGZHOU JIANGYIN BARLEY（双港）

## 注意事项

1. 不要自行启动sub-agent - 单Agent模式是核心约束
2. 不要估算货量 - 从SOF精确读取
3. 不要跳过合同对照 - 合同原文是唯一依据
4. 不要用LLM累加数值 - 交给Python
5. 不要随意判断 - 无依据时标注"待确认"
