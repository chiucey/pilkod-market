# 定义创作需求并保存到 brief 文件
param(
    [string]$ProjectRoot = "."
)

# 导入通用函数
. "$PSScriptRoot/common.ps1"

$ProjectRoot = Get-ProjectRoot
$BriefsDir = Join-Path $ProjectRoot "_briefs"
$WorkspaceType = Get-ActiveWorkspace

# 创建 briefs 目录
New-Item -ItemType Directory -Force -Path $BriefsDir | Out-Null

# 生成 brief 文件名（带时间戳）
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BriefFile = Join-Path $BriefsDir "brief-$Timestamp.md"

# 获取工作区特定的 brief 模板
$Template = ""
switch ($WorkspaceType) {
    "wechat" {
        $Template = Join-Path $ProjectRoot ".content/templates/brief-templates/wechat-brief-template.md"
    }
    "video" {
        $Template = Join-Path $ProjectRoot ".content/templates/brief-templates/video-brief-template.md"
    }
    default {
        $Template = Join-Path $ProjectRoot ".content/templates/brief-templates/general-brief-template.md"
    }
}

# 复制模板或创建基本模板
if (Test-Path $Template) {
    Copy-Item $Template $BriefFile
    Write-Host "✅ 已创建 brief 文件: $BriefFile"
    Write-Host "📝 使用工作区模板: $WorkspaceType"
} else {
    # 创建基本模板
    @"
# 写作需求 Brief

## 基本信息
- **创建时间**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- **工作区类型**:
- **目标平台**:

## 写作目标
<!-- 描述你想写什么，为什么写，写给谁看 -->

## 核心信息
<!-- 你希望读者了解什么？获得什么？ -->

## 素材与参考
<!-- 相关链接、数据、案例等 -->

## 要求与限制
- **字数**:
- **风格**:
- **截止时间**:
- **其他要求**:
"@ | Out-File -FilePath $BriefFile -Encoding UTF8
    Write-Host "✅ 已创建 brief 文件: $BriefFile"
}

# 输出文件路径供 AI 使用
$Result = @{
    brief_file = $BriefFile
    workspace = $WorkspaceType
}
Write-Host ($Result | ConvertTo-Json -Compress)
