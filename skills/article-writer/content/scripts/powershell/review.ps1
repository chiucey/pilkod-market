# 内容审校 - 三遍审校机制 (content/style/detail)
param(
    [string]$File = "",
    [ValidateSet("content", "style", "detail")]
    [string]$Mode = "content"
)

# 导入通用函数
. "$PSScriptRoot/common.ps1"

$ProjectRoot = Get-ProjectRoot

if ([string]::IsNullOrEmpty($File) -or -not (Test-Path $File)) {
    Write-Host "❌ 错误: 未找到文件"
    Write-Host "用法: review.ps1 -File <路径> [-Mode <content|style|detail>]"
    exit 1
}

Write-Host "✅ 审校文件: $File"
Write-Host "📋 审校模式: $Mode"

switch ($Mode) {
    "content" {
        Write-Host "🔍 第一遍: 内容审校 (事实准确、逻辑清晰、结构合理)"
    }
    "style" {
        Write-Host "🎨 第二遍: 风格审校 (降AI味、删套话、加真实细节)"
    }
    "detail" {
        Write-Host "✨ 第三遍: 细节打磨 (标点、排版、节奏优化)"
    }
}

# 输出结果供 AI 使用
$Result = @{
    file = $File
    mode = $Mode
    workspace = Get-ActiveWorkspace
}
Write-Host ($Result | ConvertTo-Json -Compress)
