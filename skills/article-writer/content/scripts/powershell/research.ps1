# 信息搜索与调研
param(
    [string]$BriefFile = "",
    [string]$Query = "",
    [string]$Url = ""
)

# 导入通用函数
. "$PSScriptRoot/common.ps1"

$ProjectRoot = Get-ProjectRoot
$KnowledgeBaseDir = Join-Path $ProjectRoot "_knowledge_base"

# 如果没有指定 brief，使用最新的
if ([string]::IsNullOrEmpty($BriefFile)) {
    $BriefsDir = Join-Path $ProjectRoot "_briefs"
    if (Test-Path $BriefsDir) {
        $BriefFile = Get-ChildItem -Path $BriefsDir -Filter "*.md" |
                     Sort-Object LastWriteTime -Descending |
                     Select-Object -First 1 -ExpandProperty FullName
    }
}

Write-Host "✅ 知识库目录: $KnowledgeBaseDir"
if (-not [string]::IsNullOrEmpty($Query)) {
    Write-Host "🔍 搜索关键词: $Query"
}
if (-not [string]::IsNullOrEmpty($Url)) {
    Write-Host "🌐 文档URL: $Url"
}

# 创建知识库目录
if (-not (Test-Path $KnowledgeBaseDir)) {
    New-Item -ItemType Directory -Force -Path $KnowledgeBaseDir | Out-Null
}

# 输出结果供 AI 使用
$Result = @{
    brief_file = $BriefFile
    knowledge_base = $KnowledgeBaseDir
    query = $Query
    url = $Url
    workspace = Get-ActiveWorkspace
}
Write-Host ($Result | ConvertTo-Json -Compress)
