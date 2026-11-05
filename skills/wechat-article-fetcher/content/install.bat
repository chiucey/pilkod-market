@echo off
chcp 65001 >nul
echo ========================================
echo 微信公众号文章抓取工具 - 安装脚本
echo ========================================
echo.

:: 检查Python
echo [1/4] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

:: 检查Node.js
echo [2/4] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo.

:: 安装Python依赖
echo [3/4] 安装 Python 依赖...
pip install selenium requests Pillow -q
if errorlevel 1 (
    echo [警告] Python 依赖安装可能有问题
)
echo Python 依赖安装完成
echo.

:: 安装Node.js依赖
echo [4/4] 安装 Node.js 依赖...
npm install -g docx
if errorlevel 1 (
    echo [警告] Node.js 依赖安装可能有问题
)
echo Node.js 依赖安装完成
echo.

:: 可选：安装OCR
echo ========================================
echo OCR 工具安装（可选）
echo ========================================
echo.
echo 是否安装 EasyOCR（推荐，约500MB）？
echo 输入 Y 安装，其他键跳过
set /p install_ocr="请选择: "

if /i "%install_ocr%"=="Y" (
    echo 正在安装 EasyOCR...
    pip install easyocr -q
    if errorlevel 1 (
        echo [警告] EasyOCR 安装失败
    ) else (
        echo EasyOCR 安装成功
    )
)
echo.

:: 完成
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用方法:
echo   python scripts\fetch_article.py "微信文章链接"
echo.
echo 示例:
echo   python scripts\fetch_article.py "https://mp.weixin.qq.com/s/xxxxxx"
echo.
pause
