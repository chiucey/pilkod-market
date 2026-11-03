# 快速安装指南

## 一键安装

### Linux / macOS

```bash
# 1. 进入项目目录
cd web-automation

# 2. 运行安装脚本
./install.sh

# 3. 验证安装
python scripts/check_env.py
```

### Windows

```batch
# 1. 进入项目目录
cd web-automation

# 2. 运行安装脚本
install.bat

# 3. 验证安装
python scripts/check_env.py
```

## 手动安装

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 3. 下载 Magic-PDF 模型

```bash
magic-pdf download
```

### 4. 验证安装

```bash
python scripts/check_env.py
```

## 依赖说明

### 核心依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| playwright | >=1.40.0 | 浏览器自动化 |
| browser-use | >=0.2.0 | LLM 智能交互 |
| paddleocr | >=3.0.0 | OCR、PP-StructureV3、PP-ChatOCRv4、PaddleOCR-VL（已整合所有功能） |
| paddlepaddle | >=2.6.0 | 深度学习框架 |
| magic-pdf | >=0.7.0 | PDF 智能解析 |

### 辅助依赖

| 依赖 | 用途 |
|------|------|
| opencv-python | 图像处理 |
| beautifulsoup4 | HTML 解析 |
| pillow | 图像处理 |
| pypdf | PDF 处理 |
| lxml | XML/HTML 解析 |
| pyyaml | 配置文件解析 |
| langchain | LLM 集成 |
| python-docx | Word 文档处理 |
| numpy | 数值计算 |
| requests | HTTP 请求 |
| aiohttp | 异步 HTTP 请求 |
| transformers | VL 能力支持 |
| torch | VL 能力支持 |

## 系统要求

### Python 版本
- Python 3.8 或更高版本

### 操作系统
- Linux (Ubuntu 18.04+)
- macOS 10.14+
- Windows 10+

### 磁盘空间
- 至少 5GB 可用空间（用于安装依赖和模型）

### GPU 加速（可选）
- NVIDIA GPU（用于 PaddleOCR 加速）
- CUDA 11.2+
- cuDNN 8.0+

## 常见问题

### Q: 安装失败，提示权限错误

A: 使用 `--user` 参数安装到用户目录：
```bash
pip install --user -r requirements.txt
```

### Q: Playwright 浏览器下载失败

A: 配置国内镜像：
```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### Q: PaddleOCR 识别速度慢

A: 启用 GPU 加速：
```bash
pip install paddlepaddle-gpu
```

### Q: Magic-PDF 模型下载失败

A: 配置国内镜像：
```bash
export HF_ENDPOINT=https://hf-mirror.com
magic-pdf download
```

### Q: 内存不足

A: 使用轻量级模型：
```bash
# 在代码中配置
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ch',
    use_gpu=False,  # 禁用 GPU
    det_model_dir=None,  # 使用轻量级模型
    rec_model_dir=None
)
```

## 环境检测

安装完成后，运行环境检测脚本验证所有依赖是否正确安装：

```bash
python scripts/check_env.py
```

检测内容包括：
- Python 版本
- Playwright 浏览器
- PaddleOCR
- PaddlePaddle
- PaddleStructure
- Magic-PDF
- GPU 可用性（如果适用）

## 下一步

安装完成后，请参考：
- [Playwright CLI 使用指南](references/playwright-cli-guide.md)
- [复杂页面处理指南](references/complex-page-processing.md)
- [反爬对抗指南](references/anti-scraping-advanced.md)
- [工作流引擎指南](references/workflow-guide.md)
