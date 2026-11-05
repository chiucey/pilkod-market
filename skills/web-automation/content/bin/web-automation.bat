@echo off
REM Web Automation 启动脚本 (Windows)

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.."

REM 激活虚拟环境（如果存在）
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 如果没有提供参数，显示帮助
if "%1"=="" (
    echo Web Automation - 智能网页自动化工具
    echo.
    echo 可用命令:
    echo.
    echo 浏览器管理:
    echo   python scripts\playwright_manager.py create      # 创建浏览器
    echo   python scripts\playwright_manager.py close       # 关闭浏览器
    echo   python scripts\playwright_manager.py screenshot  # 截图
    echo.
    echo 页面交互:
    echo   python scripts\browser_wrapper.py navigate       # 导航
    echo   python scripts\browser_wrapper.py click          # 点击
    echo   python scripts\browser_wrapper.py fill           # 填充
    echo   python scripts\browser_wrapper.py scroll         # 滚动
    echo   python scripts\browser_wrapper.py extract        # 提取
    echo.
    echo 图像识别:
    echo   python scripts\ocr_service.py recognize          # OCR 识别
    echo   python scripts\ocr_service.py extract-table      # 表格提取
    echo   python scripts\ocr_service.py detect-elements    # 元素检测
    echo.
    echo 文档处理:
    echo   python scripts\mineru_service.py parse-pdf       # 解析 PDF
    echo   python scripts\mineru_service.py extract-tables   # 提取表格
    echo   python scripts\mineru_service.py analyze-layout   # 布局分析
    echo.
    echo 文档转换:
    echo   python scripts\document_converter.py convert      # 转换文档
    echo   python scripts\document_converter.py batch         # 批量转换
    echo   python scripts\document_converter.py check-env    # 检查环境
    echo.
    echo 查看完整文档:
    echo   type SKILL.md
    echo.
    echo 参考文档:
    echo   - references\playwright-guide.md    # Playwright 指南
    echo   - references\browser-use-guide.md   # browser-use 指南
    echo   - references\paddleocr-guide.md     # PaddleOCR 指南
    echo   - references\mineru-guide.md        # MinerU 指南
    echo   - references\conversion-guide.md    # 文档转换指南
    echo   - references\anti-scraping.md       # 反爬策略
    echo.
    echo 快速开始:
    echo   python scripts\playwright_manager.py create --headless=False
    echo   python scripts\browser_wrapper.py navigate --url=https://example.com
    echo   python scripts\playwright_manager.py close
    echo.
) else (
    REM 如果提供了参数，直接传递给 playwright_manager
    python scripts\playwright_manager.py %*
)
