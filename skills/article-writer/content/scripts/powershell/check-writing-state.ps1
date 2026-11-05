# 检查写作状态脚本
# 用于 /write 命令

# 导入通用函数
. "$PSScriptRoot\common.ps1"

# 获取项目根目录
$ProjectRoot = Get-ProjectRoot
Set-Location $ProjectRoot

# 获取当前故事
$StoryName = Get-ActiveStory
$StoryDir = "stories\$StoryName"

Write-Host "写作状态检查"
Write-Host "============"
Write-Host "当前故事：$StoryName"
Write-Host ""

# 检查方法论文档
function Test-MethodologyDocs {
    $missing = @()

    if (-not (Test-Path "memory\constitution.md")) {
        $missing += "宪法"
    }
    if (-not (Test-Path "$StoryDir\specification.md")) {
        $missing += "规格"
    }
    if (-not (Test-Path "$StoryDir\creative-plan.md")) {
        $missing += "计划"
    }
    if (-not (Test-Path "$StoryDir\tasks.md")) {
        $missing += "任务"
    }

    if ($missing.Count -gt 0) {
        Write-Host "⚠️ 缺少以下基准文档：" -ForegroundColor Yellow
        foreach ($doc in $missing) {
            Write-Host "  - $doc"
        }
        Write-Host ""
        Write-Host "建议按照七步方法论完成前置步骤："
        Write-Host "1. /constitution - 创建创作宪法"
        Write-Host "2. /specify - 定义故事规格"
        Write-Host "3. /clarify - 澄清关键决策"
        Write-Host "4. /plan - 制定创作计划"
        Write-Host "5. /tasks - 生成任务清单"
        return $false
    }

    Write-Host "✅ 方法论文档完整" -ForegroundColor Green
    return $true
}

# 检查待写作任务
function Test-PendingTasks {
    $tasksFile = "$StoryDir\tasks.md"

    if (-not (Test-Path $tasksFile)) {
        Write-Host "❌ 任务文件不存在" -ForegroundColor Red
        return $false
    }

    # 统计任务状态
    $content = Get-Content $tasksFile -Raw
    $pending = ([regex]::Matches($content, '^- \[ \]', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
    $inProgress = ([regex]::Matches($content, '^- \[~\]', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
    $completed = ([regex]::Matches($content, '^- \[x\]', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count

    Write-Host ""
    Write-Host "任务状态："
    Write-Host "  待开始：$pending"
    Write-Host "  进行中：$inProgress"
    Write-Host "  已完成：$completed"

    if ($pending -eq 0 -and $inProgress -eq 0) {
        Write-Host ""
        Write-Host "🎉 所有任务已完成！" -ForegroundColor Green
        Write-Host "建议运行 /analyze 进行综合验证"
        return $true
    }

    # 显示下一个待写作任务
    Write-Host ""
    Write-Host "下一个写作任务："
    $lines = $content -split "`n"
    foreach ($line in $lines) {
        if ($line -match '^- \[ \]') {
            Write-Host $line
            break
        }
    }

    return $true
}

# 检查已完成内容
function Test-CompletedContent {
    $contentDir = "$StoryDir\content"

    if (Test-Path $contentDir) {
        $mdFiles = Get-ChildItem "$contentDir\*.md" -ErrorAction SilentlyContinue
        $chapterCount = $mdFiles.Count

        if ($chapterCount -gt 0) {
            Write-Host ""
            Write-Host "已完成章节：$chapterCount"
            Write-Host "最近写作："

            $recentFiles = $mdFiles |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 3

            foreach ($file in $recentFiles) {
                Write-Host "  - $($file.Name)"
            }
        }
    }
    else {
        Write-Host ""
        Write-Host "尚未开始写作"
    }
}

# 主流程
if (-not (Test-MethodologyDocs)) {
    exit 1
}

Test-PendingTasks | Out-Null
Test-CompletedContent

Write-Host ""
Write-Host "准备就绪，可以开始写作"