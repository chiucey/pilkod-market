# 依赖安装说明

## 快速安装

### 方法 1：使用安装脚本（推荐）

#### Linux/macOS
```bash
cd /workspace/projects/web-automation
bash scripts/install_dependencies.sh
```

#### Windows
```cmd
cd \path\to\web-automation
python scripts\install_dependencies.py
```

### 方法 2：手动安装

```bash
# 升级 pip
pip install --upgrade pip

# 安装所有 Python 依赖（不指定版本号，避免冲突）
pip install playwright browser-use paddleocr paddlepaddle opencv-python magic-pdf pillow pypdf beautifulsoup4 lxml pyyaml langchain python-docx numpy requests

# 安装 Playwright 浏览器
playwright install chromium

# 系统依赖：LibreOffice
# Ubuntu/Debian: sudo apt-get install libreoffice
# macOS: brew install libreoffice
# Windows: 从 https://www.libreoffice.org/download/ 下载安装
```

---

## 版本兼容性说明

### PaddleOCR 版本问题

**重要提示**：PaddleOCR 3.x 版本与 2.x 版本的 API 不兼容！

- **PaddleOCR 2.x**（推荐用于生产环境）
  - API 稳定，文档齐全
  - `scripts/ocr_service.py` 基于 2.x 开发
  - 安装：`pip install "paddleocr>=2.8.0,<3.0.0"`

- **PaddleOCR 3.x**（最新版本，API 变化大）
  - 新架构，性能提升
  - API 完全重写，与 2.x 不兼容
  - 需要修改 `scripts/ocr_service.py`
  - 安装：`pip install paddleocr`（默认安装 3.x）

### 推荐配置

**稳定配置**（推荐）：
```bash
pip install "paddleocr>=2.8.0,<3.0.0" "paddlepaddle>=2.6.0,<3.0.0"
```

**最新配置**（需修改代码）：
```bash
pip install paddleocr paddlepaddle
```

### 其他依赖版本说明

当前安装脚本使用**无版本约束**的方式安装，避免版本冲突：

| 包名 | 当前版本 | 说明 |
|------|---------|------|
| playwright | 1.58.0 | ✅ 稳定 |
| browser-use | 0.12.2 | ✅ 最新 |
| paddleocr | 3.4.0 | ⚠️ API 变化 |
| paddlepaddle | 3.3.0 | ⚠️ API 变化 |
| opencv-python | 4.13.0 | ✅ 稳定 |
| magic-pdf | 0.6.1 | ✅ 稳定 |
| pillow | 12.1.0 | ✅ 稳定 |
| pypdf | 6.6.2 | ✅ 稳定 |
| beautifulsoup4 | 4.14.3 | ✅ 稳定 |
| lxml | 6.0.2 | ✅ 稳定 |
| pyyaml | 6.0.2 | ✅ 稳定 |
| langchain | 0.3.28 | ✅ 稳定 |
| python-docx | 1.2.0 | ✅ 稳定 |
| numpy | 2.4.1 | ✅ 稳定 |
| requests | 2.32.5 | ✅ 稳定 |

---

## 故障排除

### 问题 1：PaddleOCR 初始化失败

**错误信息**：
```
Unknown argument: use_gpu
Unknown argument: show_log
```

**原因**：PaddleOCR 3.x API 变化

**解决方案**：
```bash
# 方案 1：降级到 2.x（推荐）
pip uninstall paddleocr paddlepaddle -y
pip install "paddleocr>=2.8.0,<3.0.0" "paddlepaddle>=2.6.0,<3.0.0"

# 方案 2：修改 scripts/ocr_service.py 适配 3.x API
```

### 问题 2：langchain 依赖冲突

**错误信息**：
```
ModuleNotFoundError: No module named 'langchain.docstore'
```

**原因**：langchain 版本过高

**解决方案**：
```bash
pip install "langchain>=0.1.0,<1.0.0"
```

### 问题 3：Playwright 浏览器未安装

**错误信息**：
```
Executable doesn't exist
```

**解决方案**：
```bash
playwright install chromium
```

### 问题 4：LibreOffice 未安装

**错误信息**：
```
Command 'libreoffice' not found
```

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# CentOS/RHEL
sudo yum install libreoffice

# macOS
brew install libreoffice

# Windows
# 下载并安装：https://www.libreoffice.org/download/
```

---

## 环境要求

- Python 3.8+
- pip 20.0+
- 2GB+ 磁盘空间（用于模型下载）
- 稳定的网络连接（首次运行下载模型）

---

## 测试安装

运行以下命令测试依赖是否安装成功：

```bash
# 测试 Playwright
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

# 测试 PaddleOCR
python -c "from paddleocr import PaddleOCR; print('PaddleOCR OK')"

# 测试 OCR 服务
cd /workspace/projects/web-automation
python scripts/ocr_service.py --help

# 测试爬虫
python scripts/crawler.py --help
```

---

## 更新依赖

如果需要更新依赖到最新版本：

```bash
# 更新所有包
pip install --upgrade playwright browser-use paddleocr paddlepaddle opencv-python magic-pdf pillow pypdf beautifulsoup4 lxml pyyaml langchain python-docx numpy requests

# 更新 Playwright 浏览器
playwright install chromium
```

---

## 清理环境

如果需要完全清理环境：

```bash
# 卸载所有包
pip uninstall playwright browser-use paddleocr paddlepaddle opencv-python magic-pdf pillow pypdf beautifulsoup4 lxml pyyaml langchain python-docx numpy requests -y

# 清理缓存
pip cache purge

# 删除模型文件（可选）
rm -rf ~/.paddleocr ~/.paddlex ~/.paddle
```
