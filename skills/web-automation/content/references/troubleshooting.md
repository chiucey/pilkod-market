# Web Automation Skill 故障排除指南

## 目录
- [安装问题](#安装问题)
- [依赖冲突](#依赖冲突)
- [浏览器问题](#浏览器问题)
- [OCR 问题](#ocr-问题)
- [PDF 问题](#pdf-问题)
- [运行时错误](#运行时错误)
- [环境变量配置](#环境变量配置)

---

## 安装问题

### 问题：pip 安装超时或失败

**症状**：
```
ConnectionError: HTTPSConnectionPool(host='pypi.org', port=443)
```

**解决方案**：
1. 使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2. 或设置全局镜像：
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题：权限不足

**症状**：
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**解决方案**：
1. 使用用户安装：
```bash
pip install --user -r requirements.txt
```

2. 或使用虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 依赖冲突

### 问题：langchain-core 版本冲突

**症状**：
```
ERROR: browser-use 0.2.0 requires langchain-core==0.3.49, but you have langchain-core 0.3.83
```

**解决方案**：
1. 让 pip 自动解决冲突：
```bash
pip install --upgrade browser-use langchain-core
```

2. 或重新安装：
```bash
pip uninstall browser-use langchain-core
pip install browser-use
```

### 问题：playwright 版本冲突

**症状**：
```
ERROR: browser-act requires playwright>=1.52.0, but you have playwright 1.48.0
```

**解决方案**：
```bash
pip install --upgrade playwright
playwright install chromium
```

### 问题：pyee 版本冲突

**症状**：
```
ERROR: patchright requires pyee<14,>=13, but you have pyee 12.0.0
```

**解决方案**：
```bash
pip install --upgrade pyee
```

---

## 浏览器问题

### 问题：Playwright 浏览器未安装

**症状**：
```
Executable doesn't exist at .../chromium-...
```

**解决方案**：
```bash
# 安装所有浏览器
playwright install

# 或只安装 Chromium
playwright install chromium
```

### 问题：浏览器启动失败

**症状**：
```
browserType.launch: Executable doesn't exist
```

**解决方案**：
1. 检查浏览器是否已安装：
```bash
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

2. 重新安装：
```bash
playwright uninstall chromium
playwright install chromium
```

### 问题：无头模式截图失败

**症状**：
```
page.screenshot: Unable to capture screenshot
```

**解决方案**：
1. 确保页面已加载：
```python
await page.wait_for_load_state("networkidle")
await page.screenshot(path="screenshot.png")
```

2. 或使用有头模式测试：
```python
browser = EnhancedAsyncPlaywrightBrowser(headless=False)
```

---

## OCR 问题

### 问题：PaddleOCR 导入失败

**症状**：
```
ModuleNotFoundError: No module named 'paddleocr'
```

**解决方案**：
```bash
pip install paddleocr paddlepaddle
```

### 问题：PaddlePaddle GPU 版本问题

**症状**：
```
OSError: libcudart.so cannot open shared object file
```

**解决方案**：
1. 安装 CPU 版本：
```bash
pip uninstall paddlepaddle-gpu
pip install paddlepaddle
```

2. 或安装正确的 GPU 版本：
```bash
pip install paddlepaddle-gpu -i https://mirror.baidu.com/pypi/simple
```

### 问题：OpenCV 导入失败

**症状**：
```
ImportError: libGL.so.1: cannot open shared object file
```

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install libgl1-mesa-glx

# CentOS/RHEL
sudo yum install mesa-libGL

# 或使用 headless 版本
pip install opencv-python-headless
```

---

## PDF 问题

### 问题：magic-pdf 导入失败

**症状**：
```
ModuleNotFoundError: No module named 'magic_pdf'
```

**原因**：
magic-pdf 的安装包名和导入名不同。

**解决方案**：
```bash
# 安装完整版本
pip install "magic-pdf[full]"

# 或基础版本
pip install magic-pdf
```

### 问题：magic-pdf download 命令不存在

**症状**：
```
error: argument subcommand: invalid choice: 'download'
```

**原因**：
magic-pdf 可能没有 download 子命令，或命令格式已更改。

**解决方案**：
1. 跳过模型下载，首次使用时自动下载
2. 或手动下载模型（参考官方文档）

### 问题：PDF 解析失败

**症状**：
```
Error parsing PDF: ...
```

**解决方案**：
1. 检查 PDF 文件是否有效：
```python
from pypdf import PdfReader
reader = PdfReader("document.pdf")
print(f"页数: {len(reader.pages)}")
```

2. 使用基础 PDF 处理：
```python
from scripts.mineru_service import MinerUService

# 如果 MinerU 不可用，会返回错误
# 可以使用 pypdf 作为备选方案
```

### 问题：MinerU 内存不足

**症状**：
```
MemoryError: Unable to allocate array
```

**解决方案**：
1. 处理较小的 PDF 文件
2. 增加 Python 内存限制
3. 使用分页处理

---

## 运行时错误

### 问题：SSL 证书错误

**症状**：
```
ssl.SSLCertVerificationError: certificate verify failed
```

**解决方案**：
使用增强版浏览器忽略证书错误：
```python
browser = EnhancedAsyncPlaywrightBrowser(
    ignore_https_errors=True
)
```

### 问题：超时错误

**症状**：
```
TimeoutError: page.goto: Timeout 30000ms exceeded
```

**解决方案**：
1. 增加超时时间：
```python
browser = EnhancedAsyncPlaywrightBrowser(
    timeout_strategy="slow"  # 120秒
)
```

2. 或自定义超时：
```python
await browser.goto(url, timeout=60000)  # 60秒
```

### 问题：元素未找到

**症状**：
```
Error: strict mode violation: locator resolved to 0 elements
```

**解决方案**：
1. 等待元素出现：
```python
await page.wait_for_selector("#element", state="visible")
await page.click("#element")
```

2. 使用更宽松的选择器：
```python
elements = await page.query_selector_all(".class")
```

---

## 环境变量配置

### LLM API 配置

**OpenAI**：
```bash
export OPENAI_API_KEY="your-api-key"
# 或在代码中
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

**Anthropic**：
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

**Google**：
```bash
export GOOGLE_API_KEY="your-api-key"
```

### 代理配置

**HTTP 代理**：
```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
```

**在代码中使用代理**：
```python
browser = EnhancedAsyncPlaywrightBrowser(
    proxy={"server": "http://proxy.example.com:8080"}
)
```

---

## 快速诊断

运行环境检测脚本：
```bash
python scripts/check_env.py
```

如果发现问题，根据输出中的修复建议执行相应命令。

---

## 获取帮助

如果以上方法都无法解决问题：

1. 检查 [GitHub Issues](https://github.com/your-repo/issues)
2. 提交新 Issue，包含：
   - 完整的错误信息
   - Python 版本
   - 操作系统
   - 已安装的包列表 (`pip list`)

---

## 常见错误代码

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| `E001` | Python 版本过低 | 升级到 Python 3.8+ |
| `E002` | 核心依赖缺失 | 运行 `pip install -r requirements.txt` |
| `E003` | Playwright 浏览器未安装 | 运行 `playwright install` |
| `E004` | 模块导入失败 | 安装对应的包 |
| `E005` | 权限不足 | 使用 `--user` 或虚拟环境 |
| `E006` | 网络连接失败 | 检查网络或使用镜像 |
| `E007` | SSL 证书错误 | 使用 `ignore_https_errors=True` |
| `E008` | 超时错误 | 增加超时时间 |
| `E009` | 内存不足 | 减少处理数据量 |
| `E010` | API 密钥无效 | 检查环境变量配置 |
