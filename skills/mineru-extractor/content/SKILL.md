---
name: mineru-extractor
description: 使用 MinerU Online API 提取 PDF/文档文件内容的技能。支持在线 URL 解析和本地文件上传解析两种方式，从 config.json 读取配置参数，并自动检测配置是否正确填写。当用户需要解析 PDF、提取文档文本、处理股票公告文件、从 URL 批量解析文档时，必须使用此技能。触发关键词包括：MinerU提取、MinerU解析、公告解析、PDF解析、文档提取、mineru_extractor。
---

# MinerU Extractor 技能

通过 MinerU Online API 解析在线 URL 或本地 PDF 文档，提取结构化文本内容（Markdown 格式）。

启动时**自动检测** `config.json` 是否存在且已正确填写，若未配置则给出明确提示。

---

## CMD 命令用法

### 第一步：检测配置

```bash
python mineru_extractor.py check-config
python mineru_extractor.py check-config --config D:/project/config.json
```

### 第二步：提取文档内容

```bash
# 解析在线 URL（默认模式）
python mineru_extractor.py extract https://example.com/notice.pdf

# 解析本地文件
python mineru_extractor.py extract 公告.pdf --source local

# 结果保存到文件
python mineru_extractor.py extract 公告.pdf --source local --output result.txt
python mineru_extractor.py extract https://example.com/notice.pdf --output result.txt

# 指定 config.json 路径
python mineru_extractor.py --config D:/project/config.json extract 公告.pdf --source local

# 终端显示完整内容（默认超 2000 字截断）
python mineru_extractor.py extract https://example.com/notice.pdf --full
```

---

## 所有参数速览

| 参数                    | 说明                                       |
| ----------------------- | ------------------------------------------ |
| `--config 路径`         | config.json 路径（全局选项，默认当前目录） |
| `extract <源>`          | 本地文件路径 或 https:// URL               |
| `--source online/local` | 来源方式，默认 `online`（URL 自动识别）    |
| `--output/-o 路径`      | 结果保存路径（不指定则打印到终端）         |
| `--full`                | 终端显示时输出完整内容                     |

---

## 配置检测规则

| 检测项          | 判定为未配置的条件   |
| --------------- | -------------------- |
| 文件存在        | `config.json` 不存在 |
| MINERU_BASE_URL | 缺失或为空           |

---

## Python 调用方式

```python
from scripts.mineru_extractor import validate_config, MineruOnlineExtractor, ConfigError

try:
    config = validate_config("config.json")
except ConfigError as e:
    print(e); exit(1)

extractor = MineruOnlineExtractor(config)

# 解析在线 URL
text = extractor.extract_file("https://example.com/notice.pdf", source_method="online")

# 解析本地文件
text = extractor.extract_file("/path/to/file.pdf", source_method="local")

if text:
    print(text)
```

---

## 注意事项

- MinerU 采用异步任务机制，解析需要等待（默认最多轮询 60 次，每次间隔 5 秒，约 5 分钟）
- 返回值为**清洗后的 Markdown 文本字符串**，失败时返回空字符串
- 需要安装依赖：`pip install requests`
- MinerU Token 获取：https://mineru.net

---

## 核心脚本

详见 `scripts/mineru_extractor.py`，包含：
- `ConfigError` — 配置异常类
- `validate_config(config_path)` — 检测配置是否正确填写
- `load_config(config_path)` — 读取 config.json（validate_config 别名）
- `MineruOnlineExtractor` 类 — 核心提取逻辑
- `clean_text()` — 文本清洗工具