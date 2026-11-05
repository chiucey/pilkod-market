# MiniMax Multimodal Toolkit — Windows PowerShell Scripts
# All MiniMax APIs tested and working on Windows
# Requires: MINIMAX_API_KEY and MINIMAX_API_HOST environment variables

# ============================================================================
# Common Functions
# ============================================================================

function Get-MiniMaxConfig {
    $apiKey = $env:MINIMAX_API_KEY
    $apiHost = if ($env:MINIMAX_API_HOST) { $env:MINIMAX_API_HOST } else { "https://api.minimaxi.com" }
    if (-not $apiKey) { throw "MINIMAX_API_KEY not set" }
    @{ ApiKey = $apiKey; ApiHost = $apiHost; ApiBase = "$apiHost/v1" }
}

function Invoke-MiniMaxApi {
    param(
        [Parameter(Mandatory)][string]$Endpoint,
        [string]$Method = "POST",
        [object]$Body,
        [switch]$RawResponse,
        [int]$Timeout = 120,
        [hashtable]$Query
    )
    $cfg = Get-MiniMaxConfig
    $url = "$($cfg.ApiBase)/$Endpoint"
    $headers = @{ "Authorization" = "Bearer $($cfg.ApiKey)" }
    $params = @{ Uri = $url; Method = $Method; Headers = $headers; TimeoutSec = $Timeout }
    if ($Query) { $params["Body"] = $Query }
    if ($Body) {
        $params["ContentType"] = "application/json"
        $params["Body"] = ($Body | ConvertTo-Json -Depth 10 -Compress)
    }
    try {
        $response = Invoke-RestMethod @params
    } catch {
        $err = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($err) { throw "API [$($err.base_resp.status_code)]: $($err.base_resp.status_msg)" }
        throw "Request failed: $($_.Exception.Message)"
    }
    if ($response.base_resp -and [int]$response.base_resp.status_code -ne 0) {
        throw "API [$($response.base_resp.status_code)]: $($response.base_resp.status_msg)"
    }
    if ($RawResponse) { return $response }
    return $response.data
}

function Wait-MiniMaxVideoTask {
    param([string]$TaskId, [int]$Interval = 10, [int]$MaxWait = 600)
    $cfg = Get-MiniMaxConfig
    $elapsed = 0
    while ($elapsed -lt $MaxWait) {
        Start-Sleep -Seconds $Interval; $elapsed += $Interval
        $result = Invoke-RestMethod -Uri "$($cfg.ApiBase)/query/video_generation" `
            -Method Get -Headers @{ "Authorization" = "Bearer $($cfg.ApiKey)" } `
            -Body @{ task_id = $TaskId } -TimeoutSec 30
        $status = $result.status
        Write-Host "  [$elapsed s] Status: $status" -ForegroundColor Cyan
        if ($status -eq "Success") { return $result }
        if ($status -eq "Failed") { throw "Video task failed" }
    }
    throw "Video task timed out"
}

function Get-MiniMaxVideoUrl {
    param([string]$FileId)
    $cfg = Get-MiniMaxConfig
    $result = Invoke-RestMethod -Uri "$($cfg.ApiBase)/files/retrieve" `
        -Method Get -Headers @{ "Authorization" = "Bearer $($cfg.ApiKey)" } `
        -Body @{ file_id = $FileId } -TimeoutSec 30
    return $result.file.download_url
}

function Save-HexFile {
    param([string]$Hex, [string]$OutputPath)
    $dir = Split-Path $OutputPath -Parent
    if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $bytes = [byte[]]::new($Hex.Length / 2)
    for ($i = 0; $i -lt $Hex.Length; $i += 2) { $bytes[$i / 2] = [Convert]::ToByte($Hex.Substring($i, 2), 16) }
    [System.IO.File]::WriteAllBytes((Resolve-Path -Path "." -ErrorAction SilentlyContinue).Path + "\$OutputPath", $bytes)
    Write-Host "  Saved: $OutputPath ($($bytes.Length) bytes)" -ForegroundColor Green
    return $OutputPath
}

function Send-MiniMaxUpload {
    param([string]$FilePath, [string]$Purpose = "image")
    $cfg = Get-MiniMaxConfig
    $result = Invoke-RestMethod -Uri "$($cfg.ApiBase)/files/upload" -Method Post `
        -Headers @{ "Authorization" = "Bearer $($cfg.ApiKey)" } `
        -Form @{ file = Get-Item -Path $FilePath; purpose = $Purpose } -TimeoutSec 120
    if ($result.base_resp -and [int]$result.base_resp.status_code -ne 0) {
        throw "Upload failed: $($result.base_resp.status_msg)"
    }
    return $result.data
}

function Ensure-OutputDir {
    param([string]$OutputPath)
    $dir = Split-Path $OutputPath -Parent
    if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}

# ============================================================================
# TTS (Text-to-Speech) — POST /v1/t2a_v2 — returns hex audio
# ============================================================================
function Invoke-MiniMaxTTS {
    param(
        [Parameter(Mandatory)][string]$Text,
        [string]$VoiceId = "female-shaonv",
        [string]$Model = "speech-2.8-hd",
        [string]$Output,
        [double]$Speed = 1.0,
        [double]$Volume = 1.0,
        [int]$Pitch = 0,
        [string]$Emotion = "",
        [string]$Format = "mp3",
        [int]$SampleRate = 32000
    )
    $voiceSetting = @{ voice_id = $VoiceId; speed = $Speed; vol = $Volume; pitch = $Pitch }
    if ($Emotion) { $voiceSetting["emotion"] = $Emotion }
    $body = @{
        model = $Model; text = $Text; voice_setting = $voiceSetting
        audio_setting = @{ sample_rate = $SampleRate; bitrate = 128000; format = $Format; channel = 1 }
        stream = $false; subtitle_enable = $false; output_format = "hex"
    }
    Write-Host "Synthesizing ($Model): $($Text.Substring(0, [Math]::Min(60, $Text.Length)))..." -ForegroundColor Yellow
    $result = Invoke-MiniMaxApi -Endpoint "t2a_v2" -Body $body -RawResponse
    $audioHex = $result.data.audio
    if (-not $audioHex) { throw "No audio data returned" }
    if ($Output) {
        Ensure-OutputDir $Output
        return Save-HexFile -Hex $audioHex -OutputPath $Output
    }
    Write-Host "  Generated $($audioHex.Length) hex chars" -ForegroundColor Green
    return @{ Hex = $audioHex }
}

function Get-MiniMaxVoices {
    $result = Invoke-MiniMaxApi -Endpoint "text_to_speech/voice/list" -Method "GET" -RawResponse
    return $result.data.voices
}

# ============================================================================
# Music Generation — POST /v1/music_generation — lyrics required, returns URL
# Note: Takes 30-300 seconds, use long timeout
# ============================================================================
function Invoke-MiniMaxMusic {
    param(
        [Parameter(Mandatory)][string]$Prompt,
        [string]$Lyrics = "",
        [string]$Model = "music-2.5",
        [string]$Output,
        [switch]$Instrumental,
        [int]$Timeout = 300
    )
    $body = @{ model = $Model; prompt = $Prompt; output_format = "url"; stream = $false }
    if ($Instrumental) {
        $body["lyrics"] = "[intro]`n[outro]"
        $body["prompt"] = "$Prompt, pure music, no lyrics"
    } elseif ($Lyrics) {
        $body["lyrics"] = $Lyrics
    } else {
        throw "Lyrics required (use -Instrumental for background music without vocals)"
    }
    Write-Host "Generating music ($Model, timeout=${Timeout}s)..." -ForegroundColor Yellow
    $result = Invoke-MiniMaxApi -Endpoint "music_generation" -Body $body -RawResponse -Timeout $Timeout
    $audioUrl = $result.data.audio
    if (-not $audioUrl) { throw "No audio URL returned" }
    Write-Host "  Duration: $([math]::Round($result.extra_info.music_duration / 1000, 1))s, Size: $([math]::Round($result.extra_info.music_size / 1MB, 2))MB" -ForegroundColor Cyan
    if ($Output) {
        Ensure-OutputDir $Output
        Invoke-WebRequest -Uri $audioUrl -OutFile $Output -TimeoutSec 120
        Write-Host "  Saved: $Output" -ForegroundColor Green
        return @{ Path = $Output; Url = $audioUrl }
    }
    return @{ Url = $audioUrl }
}

# ============================================================================
# Image Generation — POST /v1/image_generation — returns image URLs
# ============================================================================
function Invoke-MiniMaxImage {
    param(
        [Parameter(Mandatory)][string]$Prompt,
        [string]$Model = "image-01",
        [string]$Output,
        [string]$AspectRatio = "1:1",
        [int]$Width = 0,
        [int]$Height = 0,
        [int]$Count = 1,
        [switch]$PromptOptimizer,
        [string]$RefImage = "",
        [switch]$NoDownload
    )
    $ratioMap = @{
        "1:1" = @{ w = 1024; h = 1024 }; "16:9" = @{ w = 1280; h = 720 }
        "4:3" = @{ w = 1152; h = 864 }; "3:2" = @{ w = 1248; h = 832 }
        "2:3" = @{ w = 832; h = 1248 }; "3:4" = @{ w = 864; h = 1152 }
        "9:16" = @{ w = 720; h = 1280 }; "21:9" = @{ w = 1344; h = 576 }
    }
    $body = @{
        model = $Model
        request_id = [Guid]::NewGuid().ToString("N")
        prompt = $Prompt
    }
    if ($PromptOptimizer) { $body["prompt_optimizer"] = $true }
    if ($RefImage) {
        $refBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $RefImage).Path)
        $body["ref_image"] = "data:image/jpeg;base64,$([Convert]::ToBase64String($refBytes))"
    }
    if ($Count -gt 1) { $body["n"] = $Count }
    Write-Host "Generating image ($Model)..." -ForegroundColor Yellow
    $result = Invoke-MiniMaxApi -Endpoint "image_generation" -Body $body -RawResponse
    $outputs = @()
    $urls = $result.data.image_urls
    if (-not $urls) { throw "No images returned" }
    for ($i = 0; $i -lt $urls.Count; $i++) {
        if ($NoDownload) {
            $outputs += @{ Url = $urls[$i] }
            Write-Host "  URL: $($urls[$i])" -ForegroundColor Green
        } else {
            $suffix = if ($urls.Count -gt 1) { "_$($i+1)" } else { "" }
            $baseName = if ($Output) { [System.IO.Path]::GetFileNameWithoutExtension($Output) } else { "image_$([Guid]::NewGuid().ToString('N').Substring(0,8))" }
            $ext = if ($Output) { [System.IO.Path]::GetExtension($Output) } else { ".png" }
            if (-not $ext) { $ext = ".png" }
            $filePath = if ($Output) {
                $dir = Split-Path $Output -Parent
                if ($dir) { Join-Path $dir "$baseName$suffix$ext" } else { "$baseName$suffix$ext" }
            } else { "minimax-output/${baseName}${suffix}${ext}" }
            Ensure-OutputDir $filePath
            Invoke-WebRequest -Uri $urls[$i] -OutFile $filePath -TimeoutSec 60
            Write-Host "  Saved: $filePath" -ForegroundColor Green
            $outputs += @{ Path = $filePath; Url = $urls[$i] }
        }
    }
    return $outputs
}

# ============================================================================
# Video Generation — POST /v1/video_generation (async) + /v1/query/video_generation
# ============================================================================
function Invoke-MiniMaxVideo {
    param(
        [Parameter(Mandatory)][string]$Prompt,
        [string]$Model = "MiniMax-Hailuo-2.3",
        [string]$Output,
        [string]$Mode = "t2v",
        [string]$FirstFrame = "",
        [string]$LastFrame = "",
        [string]$SubjectImage = "",
        [int]$MaxWait = 600
    )
    $body = @{ model = $Model; prompt = $Prompt }
    # sef and ref modes only support 6s
    if ($Mode -eq "i2v" -and $FirstFrame) {
        $upload = Send-MiniMaxUpload -FilePath $FirstFrame -Purpose "image"
        $body["first_frame_image"] = $upload.file_id
    }
    if ($Mode -eq "sef") {
        if ($FirstFrame) { $upload = Send-MiniMaxUpload -FilePath $FirstFrame -Purpose "image"; $body["first_frame_image"] = $upload.file_id }
        if ($LastFrame) { $upload = Send-MiniMaxUpload -FilePath $LastFrame -Purpose "image"; $body["last_frame_image"] = $upload.file_id }
    }
    if ($Mode -eq "ref" -and $SubjectImage) {
        $upload = Send-MiniMaxUpload -FilePath $SubjectImage -Purpose "image"
        $body["subject_reference_image"] = $upload.file_id
    }
    Write-Host "Generating video ($Mode, $Model)..." -ForegroundColor Yellow
    $result = Invoke-MiniMaxApi -Endpoint "video_generation" -Body $body -RawResponse
    $taskId = $result.task_id
    if (-not $taskId) { throw "No task_id returned" }
    Write-Host "  Task: $taskId (polling up to ${MaxWait}s)..." -ForegroundColor Cyan
    $final = Wait-MiniMaxVideoTask -TaskId $taskId -MaxWait $MaxWait
    $fileId = $final.file_id
    if (-not $fileId) { throw "No file_id in result" }
    $videoUrl = Get-MiniMaxVideoUrl -FileId $fileId
    Write-Host "  Video: $($final.video_width)x$($final.video_height)" -ForegroundColor Cyan
    if ($Output) {
        Ensure-OutputDir $Output
        Invoke-WebRequest -Uri $videoUrl -OutFile $Output -TimeoutSec 120
        Write-Host "  Saved: $Output" -ForegroundColor Green
        return @{ Path = $Output; Url = $videoUrl }
    }
    Write-Host "  URL: $videoUrl" -ForegroundColor Green
    return @{ Url = $videoUrl }
}
