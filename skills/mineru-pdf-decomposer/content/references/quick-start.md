# MinerU 快速开始参考

## 安装命令速查

```bash
# 方法1：pip 安装
pip install -U "mineru[core]" --extra-index-url https://wheels.myhloli.com

# 方法2：uv 安装
pip install uv
uv pip install -U "mineru[core]"

# 方法3：源码安装
git clone https://github.com/opendatalab/MinerU.git
cd MinerU
uv pip install -e .[core]
```

## 模型下载命令

```bash
# 从 ModelScope 下载（国内推荐）
python -m mineru.cli.models_download -s modelscope -m all

# 从 HuggingFace 下载
python -m mineru.cli.models_download -s huggingface -m all
```

## 命令行使用

```bash
# 基本用法
mineru -p input.pdf -o output/

# 批量处理
mineru -p "*.pdf" -o output/

# 指定解析模式
mineru -p input.pdf -o output/ -m auto    # 自动检测
mineru -p input.pdf -o output/ -m ocr     # OCR 模式

# 指定语言
mineru -p input.pdf -o output/ -l ch      # 中文
mineru -p input.pdf -o output/ -l en      # 英文
mineru -p input.pdf -o output/ -l auto    # 自动检测
```

## Python API 快速示例

### 方式1：简洁 API（推荐）

```python
from mineru import Dataset

# 单文件处理
dataset = Dataset.from_file("paper.pdf")
result = dataset.process()
print(result.markdown)
```

### 方式2：详细 API

```python
from mineru.data.dataset import PymuDocDataset
from mineru.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader

pdf_file_name = "paper.pdf"
name_without_suff = pdf_file_name.split(".")[0]

# 初始化数据集
dataset = PymuDocDataset(pdf_file_name)

# 解析
dataset.parse(
    method="auto",  # auto/ocr/pdfminer/tesseract
    lang="ch"       # ch/en/auto
)

# 获取 Markdown 结果
md_content = dataset.piped_md

# 写入文件
with open(f"{name_without_suff}.md", "w", encoding="utf-8") as f:
    f.write(md_content)
```

## 常用配置

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MINERU_API_MAX_CONCURRENT_REQUESTS` | 最大并发数 | 无限制 |
| `MINERU_PDF_RENDER_TIMEOUT` | PDF 渲染超时(秒) | 300 |
| `MINERU_INTRA_OP_NUM_THREADS` | CPU 内部线程数 | CPU 核心数 |

### 配置文件

配置文件位置：`~/.magic-pdf.json`

```json
{
  "models-dir": "/path/to/models",
  "device-mode": "cuda",  // cuda/cpu/mps
  "parse_method": "auto"
}
```