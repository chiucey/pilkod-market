---
name: ashare-data
description: 中国A股行情数据获取工具。当需要从Wind金融数据库（MySQL RDS）获取A股股票的基础信息、日行情、财务数据、资金流向、股东数据时使用。严格遵循单表查询原则，每次只查询一张表。扩展支持部分指数数据。
metadata: {"openclaw":{"emoji":"📊","requires":{"bins":["python3"],"packages":["pymysql"]}}}
---

# AShare Data Skill (`ashare-data`)

**初始配置**

使用前，必须检查文件夹中是否有config文档，且其中是否有有效的数据库连接方式。若没有，需要提醒用户配置数据库连接方式。

**设计原则**:

1. **单表查询**: 每次只查询一张表，避免多表联立查询
2. **流程拆解**: 先获取股票代码 → 再获取对应数据
3. **A股为主**: 主要识别A股数据，扩展支持相关指数数据
4. **字典分离**: 数据字典单独保存，便于后续扩展

**数据获取流程**:
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. 股票代码查询  │ ──▶ │  2. 选择数据类型  │ ──▶ │  3. 单表数据获取  │
│  asharedescription│     │  行情/财务/其他   │     │  指定表查询      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Quick Start

```bash
# 查询股票代码（支持名称、拼音、代码模糊匹配）
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py code --keyword 茅台

# 获取日行情数据
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py eod --code 600519.SH --start 20250320 --end 20250325

# 获取财务指标（关键指标如ROE、PE、PB等）
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py finance --code 600519.SH --period 20231231

# 获取资金流向数据
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py moneyflow --code 600519.SH --start 20250320 --end 20250325

# 获取指数成分股（支持沪深300、上证50等）
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py index --code 000300.SH --date 20240201

# 列出所有支持的数据表
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py list
```

## 支持的A股数据表（13张，全部有完整数据字典）

| 类别 | 表名 | 说明 | 字典 |
|------|------|------|------|
| **基础信息** | `AShareDescription` | 股票基本资料 | ✓ |
| **行情数据** | `AShareEODPrices` | 日行情数据 | ✓ |
| | `AShareEODDerivativeIndicator` | 日行情衍生指标(PE/PB/市值) | ✓ |
| | `AShareMoneyFlow` | 资金流向 | ✓ |
| **财务数据** | `AShareBalanceSheet` | 资产负债表 | ✓ |
| | `AShareIncome` | 利润表 | ✓ |
| | `AShareCashFlow` | 现金流量表 | ✓ |
| | `AShareFinancialIndicator` | 财务指标(ROE/ROA等) | ✓ |
| | `AShareTTMHis` | TTM财务数据 | ✓ |
| **行业分类** | `AShareIndustriesCode` | 行业代码表 | ✓ |
| | `AShareSWNIndustriesClass` | 申万行业分类 | ✓ |
| **指数数据** | `AIndexDescription` | A股指数基本资料 | ✓ |
| | `AIndexHS300FreeWeight` | A股指数月权重（沪深300、上证50等） | ✓ |

注: ✓ 表示已有完整数据字典定义（通过 MinerU 从原始 PDF 提取）

注: ✓ 表示已有完整数据字典定义（schema/目录下的JSON文件）

## Commands

### `code`

查询股票代码。支持名称、拼音、代码模糊匹配。

```bash
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py code --keyword 茅台 --limit 20 --verbose
```

Arguments:
- `--keyword`, `-k` (必填): 搜索关键词，可匹配股票名称、拼音、Wind代码、交易代码
- `--limit`, `-l`: 返回数量限制，默认20
- `--verbose`, `-v`: 显示详细信息（公司全称、拼音等）

### `eod`

获取日行情数据。支持复权价格。

```bash
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py eod --code 600519.SH --start 20250320 --end 20250325 --adjust --format table
```

Arguments:
- `--code`, `-c` (必填): Wind代码，如 `600519.SH`, `000858.SZ`
- `--start`, `-s` (必填): 开始日期 `YYYYMMDD`
- `--end`, `-e` (必填): 结束日期 `YYYYMMDD`
- `--adjust`, `-a`: 使用后复权价格
- `--format`, `-f`: 输出格式 `table`（默认）或 `json`

### `finance`

获取财务指标数据。可选择只返回关键指标。

```bash
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py finance --code 600519.SH --period 20231231 --format json
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py finance --code 600519.SH --full
```

Arguments:
- `--code`, `-c` (必填): Wind代码
- `--period`, `-p`: 报告期 `YYYYMMDD`，默认最新报告期
- `--full`: 返回所有财务指标，不只是关键指标
- `--format`, `-f`: 输出格式 `table` 或 `json`

**关键指标包括**: 基本每股收益(EPS)、每股净资产(BPS)、净资产收益率(ROE)、总资产报酬率(ROA)、投入资本回报率(ROIC)、销售毛利率、销售净利率、资产负债率、流动比率、速动比率、净利润同比增长率等。

### `income`

获取利润表数据（未来扩展命令，暂未实现完整功能）。

### `balance`

获取资产负债表数据（未来扩展命令，暂未实现完整功能）。

### `moneyflow`

获取资金流向数据。包含超大单、大单、中单、小单的买卖金额和数量。

```bash
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py moneyflow --code 600519.SH --start 20250320 --end 20250325 --format table
```

Arguments:
- `--code`, `-c` (必填): Wind代码
- `--start`, `-s` (必填): 开始日期 `YYYYMMDD`
- `--end`, `-e` (必填): 结束日期 `YYYYMMDD`
- `--format`, `-f`: 输出格式 `table` 或 `json`

**资金分类定义**:
- **超大单**: 单笔挂单金额 > 100万元
- **大单**: 单笔挂单金额 20万元 ~ 100万元
- **中单**: 单笔挂单金额 4万元 ~ 20万元
- **小单**: 单笔挂单金额 < 4万元

### `index`

获取指数成分股信息。支持沪深300(000300.SH)、上证50(000016.SH)、中证500(000905.SH)等指数。

```bash
# 获取沪深300成分股
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py index --code 000300.SH --date 20240201

# 获取上证50成分股
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py index --code 000016.SH --date 20240201
```

Arguments:
- `--code`, `-c` (必填): 指数Wind代码，如 `000300.SH`（沪深300），`000016.SH`（上证50）
- `--date`, `-d` (必填): 查询日期 `YYYYMMDD`
- `--top`, `-t`: 返回前N名成分股（默认返回全部）

**支持的指数代码**:
- `000300.SH`: 沪深300指数
- `000016.SH`: 上证50指数  
- `000905.SH`: 中证500指数
- `000852.SH`: 中证1000指数
- `399006.SZ`: 创业板指
- `399001.SZ`: 深证成指

### `indexinfo`

查询指数基本信息。支持按代码、名称、发布机构、类型、市场等条件查询。

```bash
# 查询特定指数信息
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py indexinfo --code 000300.SH

# 按名称模糊查询
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py indexinfo --name 沪深300

# 按发布机构查询
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py indexinfo --publisher 中证指数有限公司 --limit 50

# 查询A股股票类指数
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py indexinfo --market SH --type 股票类 --limit 20
```

Arguments:
- `--code`, `-c`: 指数Wind代码，如 `000300.SH`（可选）
- `--name`, `-n`: 指数名称关键词（模糊匹配）
- `--publisher`, `-p`: 发布机构
- `--type`, `-t`: 指数类型，如股票类、债券类、业绩基准类等
- `--market`, `-m`: 交易市场，如SH（上海）、SZ（深圳）、WIND等
- `--limit`, `-l`: 返回数量限制，默认20
- `--format`, `-f`: 输出格式 `table`（默认）或 `json`

**常用指数类型**:
- `股票类`: 股票指数
- `债券类`: 债券指数
- `业绩基准类`: 基金业绩基准指数
- `商品类`: 商品指数
- `多资产类`: 多资产配置指数

**常用交易市场**:
- `SH`: 上海证券交易所
- `SZ`: 深圳证券交易所
- `WIND`: 万得指数
- `BZPE`: 标准普尔指数
- `CS`: 中证指数

### `list`

列出所有支持的A股数据表及其状态。

```bash
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py list
```

显示哪些表已有数据字典定义（✓ 标记），哪些表尚未有完整字典（空格标记）。

## 数据字典系统

技能内置完整的数据字典系统，位于 `schema/` 目录，所有字典已通过 MinerU 从原始 PDF 文档提取并转换为简洁的 Markdown 格式：

```
schema/
├── AIndexDescription.md          # A股指数基本资料
├── AIndexHS300FreeWeight.md      # A股指数月权重
├── AShareBalanceSheet.md         # 资产负债表
├── AShareCashFlow.md             # 现金流量表
├── AShareDescription.md          # 股票基本资料
├── AShareEODDerivativeIndicator.md # 日行情衍生指标
├── AShareEODPrices.md            # 日行情
├── AShareFinancialIndicator.md   # 财务指标
├── AShareIncome.md               # 利润表
├── AShareIndustriesCode.md       # 行业代码表
├── AShareMoneyFlow.md            # 资金流向
├── AShareSWNIndustriesClass.md   # 申万行业分类
└── AShareTTMHis.md               # TTM财务数据
```

**数据字典特点**:
- ✅ **完整提取**: 所有字段定义、类型、注释、有值率等信息
- ✅ **标准化格式**: 统一的 Markdown 表格格式
- ✅ **实时更新**: 基于最新 Wind 数据字典 PDF 提取
- ✅ **详细说明**: 包含业务主键、数据频率、历史长度等元数据

**支持的表数量**: 13张（已覆盖所有核心A股数据表）

每个字典文件包含：
- 表名、中文名、描述
- 主键、业务键
- 所有字段定义（名称、类型、注释）
- 索引信息
- 常用过滤条件
- 关键指标（如财务表）

## 数据库配置

**安全原则**:

- 不硬编码密码到脚本中
- 支持环境变量配置
- 只读操作，不修改数据库内容

## 使用场景

### 1. 股票筛选与查询
```bash
# 查找银行股
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py code --keyword 银行 --limit 50

# 查找科创板股票
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py code --keyword .SH --limit 50
```

### 2. 行情数据分析
```bash
# 获取最近一个月行情
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py eod --code 000858.SZ --start 20250301 --end 20250326

# 获取估值指标（PE/PB/市值）
# 需要直接查询 ashareeodderivativeindicator 表
```

### 3. 财务分析
```bash
# 获取贵州茅台最新财务指标
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py finance --code 600519.SH

# 获取历史财务指标对比
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py finance --code 600519.SH --period 20230930
```

### 4. 资金流向监控
```bash
# 监控主力资金流向
/root/.openclaw/workspace/skills/ashare-data/scripts/ashare_data.py moneyflow --code 300750.SZ --start 20250320 --end 20250325
```

## 注意事项

1. **单表查询**: 每次只查询一张表，不执行多表联立查询（设计原则）
2. **数据权限**: 确保有数据库读取权限
3. **网络连接**: 数据库位于阿里云RDS，需要网络可达
4. **性能优化**: 大范围查询时建议使用日期限制和分页
5. **错误处理**: 连接失败或查询错误会显示明确错误信息

## 扩展开发

如需新增支持的数据表：

1. 在 `SUPPORTED_TABLES` 字典中添加表名和描述
2. 在 `schema/` 目录创建对应的JSON字典文件
3. 如需新命令，在 `main()` 函数中添加对应的命令解析器

数据字典JSON格式参考现有文件，包含表结构、字段定义、索引、过滤条件等完整信息。
