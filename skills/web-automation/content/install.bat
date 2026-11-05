@echo off
REM Web Automation Skill 依赖安装脚本
REM 支持选择性安装，避免版本冲突

echo ==========================================
echo   Web Automation Skill 依赖安装脚本
echo ==========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 显示 Python 版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 📦 Python 版本: %PYTHON_VERSION%
echo.

echo 请选择安装模式：
echo   1) 基础安装（仅浏览器自动化）
echo   2) 完整安装（包含 OCR）
echo   3) 完整安装（包含 PDF）
echo   4) 完整安装（所有功能）
echo   5) 自定义安装
echo.
set /p choice="请输入选项 [1-5]: "

if "%choice%"=="1" goto basic_install
if "%choice%"=="2" goto ocr_install
if "%choice%"=="3" goto pdf_install
if "%choice%"=="4" goto full_install
if "%choice%"=="5" goto custom_install
echo ❌ 无效选项，退出
pause
exit /b 1

:basic_install
echo.
echo 📦 开始基础安装...
goto install_core

:ocr_install
echo.
echo 📦 开始安装（包含 OCR）...
set INSTALL_OCR=true
goto install_core

:pdf_install
echo.
echo 📦 开始安装（包含 PDF）...
set INSTALL_PDF=true
goto install_core

:full_install
echo.
echo 📦 开始完整安装...
set INSTALL_OCR=true
set INSTALL_PDF=true
goto install_core

:custom_install
echo.
set /p install_ocr="安装 OCR 功能？[y/N]: "
if /i "%install_ocr%"=="y" set INSTALL_OCR=true

set /p install_pdf="安装 PDF 功能？[y/N]: "
if /i "%install_pdf%"=="y" set INSTALL_PDF=true
goto install_core

:install_core
echo.
echo ==========================================
echo   第 1 步：升级 pip
echo ==========================================
python -m pip install --upgrade pip setuptools wheel

echo.
echo ==========================================
echo   第 2 步：安装核心依赖
echo ==========================================
pip install "playwright>=1.48.0"
pip install "browser-use>=0.2.0"
pip install "langchain>=0.1.0"
pip install "langchain-openai>=0.1.0"
pip install "langchain-anthropic>=0.1.0"
pip install "langchain-google-genai>=0.1.0"
pip install "requests>=2.28.0"
pip install "aiohttp>=3.8.0"
pip install "beautifulsoup4>=4.12.0"
pip install "lxml>=4.9.0"
pip install "pyyaml>=6.0"
pip install "numpy>=1.24.0"

echo.
echo ==========================================
echo   第 3 步：安装 Playwright 浏览器
echo ==========================================
playwright install chromium
if errorlevel 1 (
    echo ⚠️  Playwright 浏览器安装失败，请手动运行: playwright install chromium
)

REM OCR 安装
if "%INSTALL_OCR%"=="true" (
    echo.
    echo ==========================================
    echo   第 4 步：安装 OCR 依赖
    echo ==========================================
    
    echo 📦 安装 PaddlePaddle...
    pip install "paddlepaddle>=2.6.0"
    if errorlevel 1 (
        echo ⚠️  PaddlePaddle 安装失败
        echo    GPU 用户请参考: https://www.paddlepaddle.org.cn/install/quick
    )
    
    echo 📦 安装 PaddleOCR...
    pip install "paddleocr"
    if errorlevel 1 (
        echo ⚠️  PaddleOCR 安装失败
    )
    
    echo 📦 安装图像处理库...
    pip install opencv-python pillow
    if errorlevel 1 (
        echo ⚠️  图像处理库安装失败
    )
) else (
    echo.
    echo ⏭️  跳过 OCR 依赖安装
)

REM PDF 安装
if "%INSTALL_PDF%"=="true" (
    echo.
    echo ==========================================
    echo   第 5 步：安装 PDF 依赖
    echo ==========================================
    
    echo 📦 安装 MinerU (magic-pdf)...
    pip install "magic-pdf[full]"
    if errorlevel 1 (
        echo ⚠️  MinerU 安装失败，尝试基础版本...
        pip install "magic-pdf"
        if errorlevel 1 (
            echo ⚠️  magic-pdf 安装失败
        )
    )
    
    echo 📦 安装 PDF 处理库...
    pip install pypdf python-docx
    if errorlevel 1 (
        echo ⚠️  PDF 处理库安装失败
    )
) else (
    echo.
    echo ⏭️  跳过 PDF 依赖安装
)

echo.
echo ==========================================
echo   第 6 步：环境检查
echo ==========================================
python scripts/check_env.py

echo.
echo ==========================================
echo   安装完成！
echo ==========================================
echo.
echo 📝 后续步骤：
echo.
echo 1. 如果 Playwright 浏览器未安装，请运行：
echo    playwright install chromium
echo.

if "%INSTALL_PDF%"=="true" (
    echo 2. 如果需要使用 PDF 功能，请确保 magic-pdf 正确安装
    echo    首次使用时会自动下载模型
    echo.
)

if "%INSTALL_OCR%"=="true" (
    echo 3. 如果需要使用 OCR 功能，请确保 PaddleOCR 正确安装
    echo    首次使用时会自动下载模型
    echo.
)

echo 4. 测试安装：
echo    python scripts/check_env.py
echo.

pause
