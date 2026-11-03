---
name: state-owned-doc-automation
description: 国资资料库自动化工具，实现文档自动分类、规范重命名、归档存储与 Web 检索。当用户要求"配置路径"、"启动监听"、"启动检索"、"归档文档"、"查找文件"时使用。
---

# 国资资料库自动化技能

基于 MiniMax AI 的国资资料自动归档与检索系统，支持文件分类、重命名、归档和全文搜索。

## 核心功能

- **自动分类**：AI 智能分析文档内容，分类到 A-F 类资料库
- **规范命名**：按 `YYYYMMDD_单位_主题_版本.扩展名` 格式重命名
- **实时监听**：监控待归档目录，新文件自动处理
- **Web 检索**：浏览器搜索已归档文件，支持标签筛选

## 分类体系

| 分类 | 说明 |
|------|------|
| A 类 | 企业基础信息库（组织架构、基础画像） |
| B 类 | 财务与经营动态库（财务决算、经营分析、预算投资） |
| C 类 | 战略规划与改革重组库（五年规划、专项改革、重组整合） |
| D 类 | 项目与投资监管库（投资项目、基金业务） |
| E 类 | 内控合规与监督库（法治合规、社会责任与 ESG） |
| F 类 | 国资监管政策法规库（国资委规章、省级文件） |

## 工作流程

### 第一步：首次配置路径

**触发**：用户首次使用或需要修改路径配置

**执行方式**（二选一）：

#### 方式一（推荐）：运行配置向导

```
python setup_wizard.py
```

弹出图形界面让用户选择三个目录：
- **资料库根目录**（SHARED_BASE_PATH）：存放 A-F 分类子目录的总目录
- **待归档目录**（WATCH_DIR）：放入待处理文件的目录
- **备份目录**（PROCESSED_DIR）：可选，默认为 `backup`

**Agent 操作**：
1. 执行 `python setup_wizard.py`
2. 告知用户："即将弹出配置窗口，请在窗口中选择对应文件夹"
3. 用户完成选择后确认配置已保存

#### 方式二：手动修改配置

直接编辑 <filepath>temp-skills/state-owned-doc-automation/config.py</filepath> 中的路径变量：

```python
SHARED_BASE_PATH = r"归档库根目录路径"
WATCH_DIR = r"待归档文件夹路径"
PROCESSED_DIR = r"备份目录路径"
```

### 第二步：安装依赖

首次运行时检查并安装依赖：

```bash
pip install -r requirements.txt
```

依赖包含：watchdog, requests, python-docx, pdfplumber, openpyxl, xlrd, jieba, Whoosh, openai, Flask

### 第三步：启动监听服务

**触发**：用户要求"启动监听"、"开始归档"、"监控文件夹"

**执行**：
```bash
python watchdog_listener.py
```

**说明**：
- 监听服务持续运行，需保持终端窗口
- 放入待归档目录的 Word/PDF/Excel/TXT/PPT 文件会自动处理
- 处理后文件移动到归档库对应分类目录

**停止监听**：
- 按 `Ctrl+C` 或告知 Agent 停止

### 第四步：启动 Web 检索服务

**触发**：用户要求"启动检索"、"搜索文件"、"查找归档文件"

**执行**：
```bash
python app.py
```

启动后自动打开浏览器访问 `http://127.0.0.1:5050`

**功能**：
- 关键词搜索（文件名/内容）
- 热门标签筛选
- 分类筛选（A-F 类）
- 点击文件名直接打开文件

### 第五步：命令行检索（可选）

**触发**：用户需要在终端快速检索

```bash
python searcher.py 关键词
```

## 文件命名规范

归档文件按以下格式重命名：

```
YYYYMMDD_单位简称_主题_版本.扩展名
```

示例：
- `20260417_川省属国企_基金投资情况表_正式稿.xlsx`
- `20260420_川发展_国家级并购基金政策体系_.docx`

## 故障排查

### 依赖缺失
```
ModuleNotFoundError: No module named 'xxx'
```
**解决**：运行 `pip install -r requirements.txt`

### 配置路径无效
检查 `config.py` 中的路径是否存在，确保有读写权限

### AI API 错误
- 检查 `config.py` 中 `AI_API_KEY` 是否正确
- 系统会自动降级为本地规则分类（准确率降低但可继续运行）
- 可在 config.py 中切换模型：`AI_MODEL = "abab6.5s-chat"`

### 查看日志
日志文件位于 `logs/archive.log`，包含处理详情和错误信息

## 启动脚本

| 脚本 | 功能 |
|------|------|
| `setup_wizard.py` | 首次配置（图形界面） |
| `watchdog_listener.py` | 启动文件监听归档 |
| `app.py` | 启动 Web 检索服务 |
| `searcher.py` | 命令行检索 |

## 环境要求

- Python 3.9+
- Windows 系统（支持 UNC 路径和映射盘符）
- MiniMax API Key（可选，未配置时使用本地规则分类）