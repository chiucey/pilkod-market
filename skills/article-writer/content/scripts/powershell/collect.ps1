# 素材搜索 - 从个人素材库搜索相关内容
param(
    [string]$BriefFile = "",
    [string]$Query = ""
)

# 导入通用函数
. "$PSScriptRoot/common.ps1"

$ProjectRoot = Get-ProjectRoot
$MaterialsDir = Join-Path $ProjectRoot "materials"

# 如果没有指定 brief，使用最新的
if ([string]::IsNullOrEmpty($BriefFile)) {
    $BriefsDir = Join-Path $ProjectRoot "_briefs"
    if (Test-Path $BriefsDir) {
        $BriefFile = Get-ChildItem -Path $BriefsDir -Filter "*.md" |
                     Sort-Object LastWriteTime -Descending |
                     Select-Object -First 1 -ExpandProperty FullName
    }
}

if ([string]::IsNullOrEmpty($BriefFile) -or -not (Test-Path $BriefFile)) {
    Write-Host "❌ 错误: 未找到 brief 文件"
    Write-Host "用法: collect.ps1 [-BriefFile <路径>] [-Query <搜索词>]"
    exit 1
}

Write-Host "✅ 使用 brief: $BriefFile"
Write-Host "📁 素材库目录: $MaterialsDir"

# 检查素材库是否存在
if (-not (Test-Path $MaterialsDir)) {
    Write-Host "⚠️  素材库目录不存在，请先导入素材"
    Write-Host "   使用: content materials import"
    exit 1
}

# 输出结果供 AI 使用
$Result = @{
    brief_file = $BriefFile
    materials_dir = $MaterialsDir
    query = $Query
    workspace = Get-ActiveWorkspace
}
Write-Host ($Result | ConvertTo-Json -Compress)
