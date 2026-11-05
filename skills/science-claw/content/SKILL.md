---
name: science-claw
description: ScienceClaw - 全流程科研 AI Agent 助手。当用户要求进行自主科学研究、文献综述、学术论文生成、科学数据分析、药物发现研究、天文学/化学/生物医学研究、多格式科研报告输出（PDF/DOCX/PPTX/XLSX）、访问1900+科学工具、执行跨数据库检索、处理科研数据集、自动化研究工作流、或需要 AI 辅助科研全流程时使用。
---

# ScienceClaw - 科研全流程 AI Agent

ScienceClaw 是基于 LangChain DeepAgents 和 AIO Sandbox 构建的个人科研助手，采用超越 OpenClaw 的全新架构，提供更强的安全性、透明度和用户体验。

## 核心能力

### 安全优先架构
- **Docker 容器隔离**：Agent 运行在完全隔离的沙箱环境中
- **无主机访问**：无法访问宿主机系统、个人文件或环境变量
- **本地化数据**：所有生成数据保存在本地 `./workspace` 目录
- **隐私保护**：无数据上传到外部服务器

### 全流程透明度
- **可追溯**：每一步操作（搜索、爬取、推理、工具调用、报告生成）完全可见
- **可审计**：始终知道结果来源、执行的操作、结论推导过程

### 四层工具架构

| 层级 | 描述 | 示例 |
|------|------|------|
| 内置工具 | 核心搜索和爬取能力 | `web_search`, `web_crawl` |
| ToolUniverse | 1900+ 科学工具，即用型 | UniProt, OpenTargets, PDB, ADMET, PubMed |
| 沙箱工具 | 文件操作和代码执行 | `read_file`, `write_file`, `execute`, `shell` |
| 自定义 @tool | 用户定义的 Python 函数 | 用户自己的工具 |

## 科学领域覆盖

### 八大科研领域

| 领域 | 能力 |
|------|------|
| 药物发现与生物医学 | 靶点识别 (OpenTargets)、ADMET 预测、药物安全 (FAERS)、蛋白分析 (UniProt, PDB, AlphaFold)、基因组学 (GWAS, GTEx)、临床试验 |
| 天文学与空间科学 | SIMBAD 天文对象、SDSS 天空调查、NASA 系外行星档案、JPL Horizons 星历、NASA DONKI 太阳事件、小天体数据库 |
| 地球与环境科学 | USGS 地震与水文、ERDDAP 海洋/气候数据、SoilGrids、空气质量 (WAQI)、OpenMeteo 天气/气候、海洋区域 |
| 化学与材料科学 | COD 晶体结构、分子性质预测、SMILES 分析、化合物相似性、化学计算 |
| 生物多样性 | GBIF 物种记录、OBIS 海洋生物多样性、POWO 植物分类、WoRMS 海洋物种、eBird 分类学、古生物学数据库 |
| 社会科学与统计 | 世界银行指标、Eurostat、美国人口普查数据、Wikidata 知识图谱、DBpedia |
| 学术文献 | 多源搜索 (PubMed, arXiv, OpenAlex, Semantic Scholar, DBLP, INSPIRE-HEP, Crossref, DOAJ, CORE) |
| 数据科学与计算 | HuggingFace 模型/数据集、OpenML、GitHub 仓库、科学计算软件、图像处理 |

## 工作流程

### 自主科研流程

```
需求输入 → 任务拆解 → 工具调用 → 闭环执行 → 成果输出
```

1. **接收需求**：理解科研术语，精准捕捉核心诉求
2. **拆解任务**：将复杂需求转化为可执行的步骤清单
3. **调用工具**：自主启用 1900+ 科研专用工具
4. **执行闭环**：端到端自动化执行
5. **输出成果**：直接交付可提交、可引用、可复用的科研成品

### 多格式报告生成

| 格式 | 特性 |
|------|------|
| PDF | 封面页、目录、图表（柱状/饼状/折线）、文中引用、参考文献、学术样式 |
| DOCX | 封面页、目录、表格、图片、蓝色上标引用、Word 原生格式 |
| PPTX | 标题页、要点、图片幻灯片 |
| XLSX | 电子表格创建和操作、CSV/TSV 数据处理 |

## 内置技能

| 技能 | 用途 |
|------|------|
| `pdf` | 读取、创建、合并、分割、OCR、专业 PDF 研究报告生成 |
| `docx` | 创建和编辑 Word 文档（封面、目录、表格、图表） |
| `pptx` | 生成和编辑 PowerPoint 幻灯片 |
| `xlsx` | 创建和操作 Excel 电子表格、CSV/TSV 数据处理 |
| `tool-creator` | 创建和升级自定义 @tool 函数（编写 → 测试 → 保存） |
| `skill-creator` | 创建和完善技能（草稿 → 测试 → 审核 → 迭代） |
| `find-skills` | 搜索、发现和安装社区技能 |
| `tooluniverse` | 统一访问 1900+ 科学工具 |

## 使用方式

### Claude Code
```bash
git clone https://github.com/AgentTeam-TaichuAI/ScienceClaw
```

### Windows 桌面应用（一键安装）
1. 下载 ScienceClaw Desktop v0.0.4
2. 解压并运行安装程序
3. 通过桌面快捷方式启动

### macOS / Linux（Docker 部署）
```bash
git clone https://github.com/AgentTeam-TaichuAI/ScienceClaw.git
docker compose -f docker-compose-release.yml up -d --pull always
# 打开 http://localhost:5173 并登录
```

### 开发者（从源码构建）
```bash
docker compose up -d --build
```

## 扩展能力

### 自定义工具
- **自然语言创建**：在对话中描述需求，Agent 自动创建、测试和保存新工具
- **手动挂载**：将任何带 `@tool` 装饰器的 Python 文件放入 `Tools/` 目录，自动检测和热加载

## 快速开始示例

### 文献综述任务
```
"帮我做一篇关于 AlphaFold 在蛋白结构预测中突破的文献综述"
```
→ 自动全网检索高质量论文 → 多源数据库交叉验证 → 整理总结生成报告

### 药物性质预测
```
"分析候选药物分子的 ADMET 性质"
```
→ PubChem 数据获取 → Lipinski 五规则计算 → ADMET 预测 → 生成分析报告

### 多领域研究
```
"研究气候变化对海洋生物多样性的影响"
```
→ 跨库数据检索 → GBIF/OBIS 数据整合 → 影响分析 → 生成可视化报告

## 参考资源

详细的技术文档、工具列表和最佳实践请参阅：
- `/workspace/temp-skills/science-claw/references/`
- 官方文档：scienceclaw.taichu.cn
- GitHub：github.com/AgentTeam-TaichuAI/ScienceClaw
