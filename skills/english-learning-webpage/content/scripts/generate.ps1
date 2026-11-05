$templatePath = "$PSScriptRoot\..\templates\listening_page_template.html"
$hintPath = "$PSScriptRoot\..\templates\pronunciation_hint_test.html"
$outputPath = "$PSScriptRoot\..\templates\chunk_cut_test.html"

# 检测路径是否正确
Write-Host "Template Path: $templatePath"
Write-Host "Hint Path: $hintPath"
Write-Host "Output Path: $outputPath"

$template = Get-Content -Raw -Path $templatePath -Encoding utf8
$hint = Get-Content -Raw -Path $hintPath -Encoding utf8

# 使用正则表达式提取 DATA
if ($hint -match '(?s)<script id="DATA" type="application/json">(.*?)</script>') {
    $data_json = $Matches[1].Trim()
} else {
    Write-Error "DATA_JSON not found"
    exit 1
}

$output = $template.Replace("{{TITLE}}", "Voyage 第293句连读弱读测试（语块划分功能测试）")
$output = $output.Replace("{{DATA_JSON}}", $data_json)
$output = $output.Replace("{{ID}}", "voyage-293-test")

# 写入新的测试文件
$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
[System.IO.File]::WriteAllText($outputPath, $output, $Utf8NoBomEncoding)

Write-Host "Successfully generated chunk_cut_test.html"
