# 撰写初稿 - 基于 brief、研究和素材创作文章
param(
    [string]$BriefFile = ""
)

# 导入通用函数
. "$PSScriptRoot/common.ps1"

$ProjectRoot = Get-ProjectRoot
$WorkspaceType = Get-ActiveWorkspace

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
    Write-Host "用法: write.ps1 [-BriefFile <路径>]"
    exit 1
}

# 确定工作区和文章目录
$WorkspacesDir = Join-Path $ProjectRoot "workspaces"
$WorkspaceDir = Join-Path $WorkspacesDir $WorkspaceType

# 创建工作区目录
if (-not (Test-Path $WorkspaceDir)) {
    New-Item -ItemType Directory -Force -Path $WorkspaceDir | Out-Null
}

# 生成文章目录
$ArticleId = (Get-ChildItem -Path $WorkspaceDir -Directory | Measure-Object).Count + 1
$ArticleId = "{0:D3}" -f $ArticleId
$ArticleDir = Join-Path $WorkspaceDir "articles/$ArticleId"

New-Item -ItemType Directory -Force -Path $ArticleDir | Out-Null

Write-Host "✅ 使用 brief: $BriefFile"
Write-Host "📝 文章目录: $ArticleDir"
Write-Host "🎯 工作区: $WorkspaceType"

# 输出结果供 AI 使用
$Result = @{
    brief_file = $BriefFile
    article_dir = $ArticleDir
    workspace = $WorkspaceType
    draft_file = Join-Path $ArticleDir "draft.md"
}
Write-Host ($Result | ConvertTo-Json -Compress)
