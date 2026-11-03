# Pilkod For Legal UserPromptSubmit hook for Windows PowerShell 5.1 and later.
#
# Windows twin of work-folder-open.sh with the same grammar: only a prompt that
# does nothing but open Pilkod For Legal receives entry guidance; every other
# prompt gets "{}". The Host's per-turn session id is the only page selector
# (ADR 0050). PowerShell ships with Windows, so users never install Node or
# another runtime (ADR 0064). Keep this file ASCII: Windows PowerShell reads a
# BOM-less script in the ANSI code page, so non-ASCII text uses \u escapes.
$ErrorActionPreference = 'Stop'

function Write-HookOutput([string] $Text) {
  # The Host reads UTF-8. ASCII-only JSON is independent of the console code page.
  $ascii = [regex]::Replace($Text, '[^\x00-\x7F]', { param($m) '\u{0:x4}' -f [int][char]$m.Value })
  $bytes = [Text.Encoding]::ASCII.GetBytes($ascii)
  $stdout = [Console]::OpenStandardOutput()
  $stdout.Write($bytes, 0, $bytes.Length)
  $stdout.Flush()
}

$session = $null
try {
  # Read raw UTF-8 bytes; [Console]::In would decode with the OEM code page.
  $stdin = [Console]::OpenStandardInput()
  $buffer = New-Object System.IO.MemoryStream
  $chunk = New-Object byte[] 65536
  while (($count = $stdin.Read($chunk, 0, $chunk.Length)) -gt 0) {
    $buffer.Write($chunk, 0, $count)
    # Oversized input is never an opening prompt.
    if ($buffer.Length -gt 256000) { Write-HookOutput "{}`n"; exit 0 }
  }
  $payload = [Text.Encoding]::UTF8.GetString($buffer.ToArray()) | ConvertFrom-Json
  $hookEvent = $payload.hook_event_name
  $prompt = $payload.prompt
  if (-not ($hookEvent -is [string]) -or $hookEvent -cne 'UserPromptSubmit' -or -not ($prompt -is [string])) {
    Write-HookOutput "{}`n"; exit 0
  }
  # JavaScript \s, listed explicitly: .NET \s also matches U+0085 but not U+FEFF.
  $ws = '[\t\n\v\f\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]'
  $text = [regex]::Replace($prompt, "^$ws+|$ws+\z", '')
  $name = '(?:@?minimax-for-legal|Pilkod For Legal)'
  # \u8bf7 qing; \u6253\u5f00 dakai; \u542f\u52a8 qidong; \u63d2\u4ef6 chajian;
  # \u5de5\u4f5c\u53f0 gongzuotai; \u9996\u9875 shouye; \u3002 and \uff01 punctuation.
  $opening = "^(?:$name|(?:\u8bf7)?(?:\u6253\u5f00|\u542f\u52a8)$ws*$name(?:$ws*(?:\u63d2\u4ef6|\u5de5\u4f5c\u53f0|\u9996\u9875))?|(?:please$ws+)?open$ws+$name)(?:[\u3002.!\uff01])?\z"
  $options = [Text.RegularExpressions.RegexOptions]'IgnoreCase, CultureInvariant'
  if (-not [regex]::IsMatch($text, $opening, $options)) { Write-HookOutput "{}`n"; exit 0 }
  $candidate = $payload.session_id
  if ($candidate -is [string] -and $candidate -cmatch '^[A-Za-z0-9_-]{1,200}\z') { $session = $candidate }
} catch {
  # Malformed input is not an opening prompt.
  Write-HookOutput "{}`n"; exit 0
}

# A missing or unreadable context file must fail visibly, not as an empty answer.
if ($session) {
  $context = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'work-folder-open-context.txt'), [Text.Encoding]::UTF8)
  Write-HookOutput $context.Replace('__SESSION_ID__', $session)
} else {
  Write-HookOutput ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'work-folder-open-context-no-session.txt'), [Text.Encoding]::UTF8))
}
