# 配图建议 - 分析文章并提供配图需求
param(
    [string]$File = ""
)

# 导入通用函数
. "$PSScriptRoot/common.ps1"

$ProjectRoot = Get-ProjectRoot

if ([string]::IsNullOrEmpty($File)) {
    # 尝试查找最近的 draft.md 或 final.md
    $WorkspaceType = Get-ActiveWorkspace
    $WorkspacesDir = Join-Path $ProjectRoot "workspaces"
    $WorkspaceDir = Join-Path $WorkspacesDir $WorkspaceType

    if (Test-Path $WorkspaceDir) {
        $ArticleDirs = Get-ChildItem -Path (Join-Path $WorkspaceDir "articles") -Directory -ErrorAction SilentlyContinue
        if ($ArticleDirs) {
            $LatestArticle = $ArticleDirs | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $File = Join-Path $LatestArticle.FullName "draft.md"
            if (-not (Test-Path $File)) {
                $File = Join-Path $LatestArticle.FullName "final.md"
            }
        }
    }
}

if ([string]::IsNullOrEmpty($File) -or -not (Test-Path $File)) {
    Write-Host "❌ 错误: 未找到文件"
    Write-Host "用法: images.ps1 [-File <路径>]"
    exit 1
}

Write-Host "✅ 分析文件: $File"
Write-Host "📸 配图类型: 产品截图、对比图表、场景示意图"

# 输出结果供 AI 使用
$Result = @{
    file = $File
    workspace = Get-ActiveWorkspace
}
Write-Host ($Result | ConvertTo-Json -Compress)
