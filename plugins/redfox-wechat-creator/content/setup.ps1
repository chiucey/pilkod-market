# wechat-content-suite 安装脚本（Windows PowerShell）
# 用法：在 plugin 根目录执行  powershell -ExecutionPolicy Bypass -File .\setup.ps1
#
# 完成三件事：
#   1) 创建/复用项目虚拟环境 .venv
#   2) 安装 Python 依赖
#   3) 引导配置 REDFOX_API_KEY（持久到用户环境变量）

$ErrorActionPreference = 'Stop'

# 切到脚本所在目录（plugin 根目录）
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ScriptDir
Write-Host "[setup] 工作目录: $ScriptDir" -ForegroundColor Cyan

# 1) Python 可用性
$python = (Get-Command python -ErrorAction SilentlyContinue) ?? (Get-Command py -ErrorAction SilentlyContinue)
if (-not $python) {
    Write-Host "[FAIL] 未检测到 python，请先安装 Python 3.9+ 并加入 PATH" -ForegroundColor Red
    exit 1
}
Write-Host "[setup] 使用 Python: $($python.Source)" -ForegroundColor Green
& $python.Source --version

# 2) 创建/复用虚拟环境
$VenvDir = Join-Path $ScriptDir '.venv'
if (-not (Test-Path $VenvDir)) {
    Write-Host "[setup] 创建虚拟环境 $VenvDir" -ForegroundColor Cyan
    & $python.Source -m venv $VenvDir
}
$venvPy = Join-Path $VenvDir 'Scripts\python.exe'
if (-not (Test-Path $venvPy)) {
    Write-Host "[FAIL] 虚拟环境创建失败：找不到 $venvPy" -ForegroundColor Red
    exit 1
}

# 3) 升级 pip + 安装依赖
Write-Host "[setup] 升级 pip 并安装 requirements.txt" -ForegroundColor Cyan
& $venvPy -m pip install --upgrade pip | Out-Null
& $venvPy -m pip install -r (Join-Path $ScriptDir 'requirements.txt')
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] 依赖安装失败" -ForegroundColor Red
    exit $LASTEXITCODE
}

# 4) Playwright 浏览器
Write-Host "[setup] 安装 Playwright Chromium 浏览器" -ForegroundColor Cyan
& $venvPy -m playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] playwright install chromium 失败，可稍后手动重试" -ForegroundColor Yellow
}

# 5) REDFOX_API_KEY
Write-Host ""
Write-Host "=== REDFOX_API_KEY 配置 ===" -ForegroundColor Cyan
$existing = [Environment]::GetEnvironmentVariable('REDFOX_API_KEY', 'User')
if ($existing) {
    Write-Host "[ok] 用户级 REDFOX_API_KEY 已存在（前 8 位：$($existing.Substring(0, [Math]::Min(8,$existing.Length)))...）" -ForegroundColor Green
} else {
    $key = Read-Host "请输入 REDFOX_API_KEY（留空跳过，需用到红狐 API 的 skill 将无法运行）"
    if ($key) {
        [Environment]::SetEnvironmentVariable('REDFOX_API_KEY', $key, 'User')
        # 当前进程同步生效
        $env:REDFOX_API_KEY = $key
        Write-Host "[ok] REDFOX_API_KEY 已写入用户环境变量" -ForegroundColor Green
    } else {
        Write-Host "[skip] 跳过 API Key 配置" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[done] 安装完成。使用前请确保新开一个终端让 REDFOX_API_KEY 生效。" -ForegroundColor Green
Write-Host "       手动激活虚拟环境：. .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
