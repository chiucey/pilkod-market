---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5a097fb15ef69fbd42e353ebab5225ea
    PropagateID: 5a097fb15ef69fbd42e353ebab5225ea
    ReservedCode1: 304402200d0a319ddbd6e080f835753f2817c1d0fa7184ef97ad4838a3353949d481474802207d37dc592bc0cfdd6d918430400a178c6572e077042a97afbd25f4b8a54e90c2
    ReservedCode2: 304402205694602f2570fce342e14a297ffefeeef4b7129459137a9b231baa826b7de95102205e6d4ecb38119252a6bd20195088a51ab0fe980e26428e8689e7c0cc36ec7b9a
description: |-
    根据产品质量管控方案 Q2+Q3+Q4+Q5 对交付物文档进行质量检查（Q1 交付完整性不在检查范围内）。
    当用户说"检查交付物"、"产品质量检查"、"核查材料"、"检查这个文档是否符合要求"、"内容完备性检查"、"信息有效性检查"、"需求可靠性检查"时激活。
    **本 skill 支持扣分位置溯源（标明文档具体位置）和得分依据溯源（标明得分来源位置）。**

    ⚡ 新架构：正则优先 + LLM 辅助。用户更新管控方案后，重新运行 scripts/inspect.py 即可完成最新标准的全量检查。
name: product-quality-check
---

# 产品交付质量检查 Skill（优化版）

## 核心升级说明

本 skill 采用**双引擎架构**，将检查任务分流处理：

| 引擎 | 适用场景 | 工具 |
|------|---------|------|
| **Regex 引擎** | 可 pattern 化的检查项（命名/结构/存在性/数量/命令等） | `scripts/regex_checker.py` |
| **LLM 引擎** | 语义类检查项（描述清晰度、逻辑完整性、跨文档一致性） | `scripts/inspect.py`（LLM prompt 生成）|

> 用户更新 `references/管控方案.md` 后，直接运行 `scripts/inspect.py`，即可按最新标准完成检查。

---

## 文件结构

```
product-quality-check/
├── SKILL.md                        ← 本文件
├── references/
│   ├── 管控方案.md                 ← ⚠️ 用户更新检查标准的主要文件
│   ├── 检查报告模板.md             ← 报告输出格式（可选自定义）
│   └── read_excel.py              ← Excel 读取工具（Python 脚本）
├── scripts/
│   ├── inspect.py                 ← 🔧 主引擎（CLI入口）
│   ├── regex_checker.py           ← 🔧 Regex 核查模块
│   ├── reader.py                   ← 🔧 多格式文档读取器
│   └── read_excel.py              ← Excel 读取（独立脚本）
└── materials/                      ← 📂 检查材料目录（用户放置文档）
```

---

## 工作流程

### Step 0 — 用户放置检查材料

将待检查文档放入 `materials/` 目录，支持格式：

`.md` `.txt` `.docx` `.xlsx` `.xls` `.pdf` `.pptx` `.csv` `.html`

### Step 1 — 更新管控方案（如标准有变化）

编辑 `references/管控方案.md`，按以下格式组织检查项：

```
## Q3：内容完备性（20分）

### 接口说明文档（满分7分，权重：7%）

| 检查项 | 权重 |
|--------|------|
| 涵盖接口描述 | 10% |
| 涵盖请求URL | 20% |
| ... | ... |
```

→ `inspect.py` 会自动从该格式解析所有检查项。

### Step 2 — 运行检查（两种方式）

**方式A：CLI 命令（推荐）**
```bash
cd /workspace/skills/product-quality-check/scripts
python3 inspect.py --materials ../materials --output ../检查报告_输出.md
```

**方式B：指定单个文档**
```bash
python3 inspect.py --materials ../materials --doc "接口说明文档" -v
```

**方式C：输出 JSON 格式（程序调用）**
```bash
python3 inspect.py --materials ../materials --json
```

### Step 3 — 查看报告

报告自动保存为 `检查报告_输出.md`，包含：
- 各维度（Q2/Q3/Q4/Q5）得分
- 每条检查项的**通过/部分通过/失败**状态
- **得分依据**或**扣分位置**溯源信息
- 综合评级（优秀/良好/合格/不合格）
- 整改建议

---

## Regex 引擎支持的检查类型

`regex_checker.py` 自动根据检查项名称路由到对应 Checker：

| Checker | 触发关键词 | 检查内容 |
|---------|-----------|---------|
| `NamingChecker` | 命名、格式、规范、标准产品名 | 文件名含产品名/版本号，无草稿/旧版 |
| `StructureChecker` | 目录、章节、结构、层级 | 必要章节是否存在，编号是否规范 |
| `ExistenceChecker` | 包含、涵盖、提供、具备、说明 | 关键词在标题+正文双重确认 |
| `ParameterChecker` | 参数、字段、类型、必填 | 参数定义表是否完整（名称/类型/必填/说明） |
| `URLChecker` | URL、url、接口地址、endpoint | URL 格式正确且存在 |
| `CommandChecker` | 步骤、命令、部署、回滚、排查 | 带编号的步骤+实际命令是否完整 |
| `CountChecker` | 数量、总数、项、条、个、份 | 统计数量是否达到最低要求 |
| `SignatureChecker` | 签字、公章、签章、审批 | 特定签章标识是否存在 |
| `CrossDocChecker` | （Q5跨文档） | 两个文档间的对应关系是否一致 |

---

## 手工触发检查（通过 Agent）

当用户要求检查时，Agent 按以下步骤执行：

```
1. 读取 references/管控方案.md
   → 理解最新检查标准（维度/权重/一票否决项）

2. 扫描 materials/ 目录，识别文档类型
   → 为每个文档匹配对应的检查项集

3. 逐文档执行检查：
   ├─ 优先用 regex_checker.py 做快速扫描
   └─ 无法用 regex 判断的项 → 读取正文 → 用 LLM 核查

4. 汇总结果，填入报告模板
   → 输出：得分 + 溯源信息 + 整改建议
```

---

## 一票否决项（优先检查）

| 一票否决项 | 检查方法 | 通过条件 |
|-----------|---------|---------|
| 🔴 测试执行记录 | 全文搜索6项内容 | 找到全部6项（基本信息/总体概述/测试范围/执行情况/用例执行列表/结果截图）|
| 🔴 二开能力证明 | 全文搜索三个级别 | 找到配置级/组装级/编码级任一材料 |

**触发效果：** Q3 直接记 0 分，跳过其余 Q3 检查

---

## Q5 跨文档对应检查

Q5 由 `CrossDocChecker` 处理，需要同时读取两个文档：

| 对应关系 | 源文档 | 目标文档 | 检查内容 |
|---------|-------|---------|---------|
| 背景一致 | 产品白皮书 | 立项材料 | 背景描述关键词是否对应 |
| 功能需求对应 | 需求规格说明书 | 产品白皮书 | 功能条目是否完整映射 |
| 接口定义对应 | 接口说明文档 | 功能/接口清单 | 接口数量和名称是否一致 |
| 测试用例覆盖 | 测试用例 | 功能清单 | 用例数量是否 ≥ 功能点数 |
| 执行数量一致 | 测试报告 | 测试用例 | 执行用例数 = 用例总数 |

---

## 维度得分汇总

| 维度 | 满分 | 说明 |
|------|------|------|
| Q2 资产规范性 | 10分 | 命名/目录/无错传 + 各文档专项模板使用 |
| Q3 内容完备性 | 20分 | 各文档内容条目是否涵盖（含两个一票否决项）|
| Q4 信息有效性 | 25分 | 信息真实/准确/一致，无模糊表述 |
| Q5 需求可靠性 | 20分 | 文档之间条目互相呼应、对应一致 |

**综合评级：**
- 70~75分 → ⭐⭐⭐ 优秀
- 60~69分 → ⭐⭐ 良好
- 45~59分 → ⭐ 合格
- 45分以下 → ❌ 不合格

---

## 溯源规范（必须遵守）

**扣分位置：** `在《文档名》第X节/页/行 — [具体问题描述]`
**得分依据：** `在《文档名》第X节 — [引用原文关键句/数据]`
**跨文档溯源：** `在《文档A》第X节 → 在《文档B》第X节 → [对应结果]`

---

## CLI 详细用法

```bash
# 基本用法（检查 materials 目录下所有文档）
python3 inspect.py

# 指定材料目录
python3 inspect.py --materials /path/to/docs

# 检查单个文档
python3 inspect.py --doc "接口说明文档"

# 输出 JSON（程序化调用）
python3 inspect.py --json

# 显示详细检查过程
python3 inspect.py --verbose

# 指定输出路径
python3 inspect.py --output /path/to/report.md
```

## 依赖说明

```bash
# 核心依赖（通常已安装）
pip install openpyxl

# 可选依赖（提升特定格式支持）
pip install python-docx   # .docx 支持
pip install python-pptx    # .pptx 支持
pip install pdfplumber     # PDF 表格支持（推荐）
pip install pypdf          # PDF 支持（备用）
```

---

## 备份说明

本 skill 已备份至：
`/workspace/skills/product-quality-check_BACKUP_20260421/`

如需恢复，运行：
```bash
cp -r /workspace/skills/product-quality-check_BACKUP_20260421/* \
       /workspace/skills/product-quality-check/
```
