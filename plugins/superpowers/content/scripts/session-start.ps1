# ASCII source is intentional: Windows PowerShell 5.1 can read it without a BOM.
# SessionStart: inject the using-superpowers Skill so the Superpowers workflow
# applies from the first turn. Read-only: no network, no writes.
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8

$pluginRoot = $env:PLUGIN_ROOT
if ([string]::IsNullOrWhiteSpace($pluginRoot)) { $pluginRoot = $env:MINIMAX_PLUGIN_ROOT }
if ([string]::IsNullOrWhiteSpace($pluginRoot)) { exit 0 }

$skillPath = Join-Path $pluginRoot 'skills\using-superpowers\SKILL.md'
if (-not (Test-Path -LiteralPath $skillPath -PathType Leaf)) { exit 0 }

# Read as UTF-8 explicitly; PowerShell 5.1 would otherwise use the ANSI code page.
$content = [System.IO.File]::ReadAllText($skillPath, $utf8).Replace("`r`n", "`n").TrimEnd("`n")
$nl = "`n"
$context = '<EXTREMELY_IMPORTANT>' + $nl + 'You have superpowers.' + $nl + $nl +
  '**Below is the full content of your superpowers:using-superpowers skill - your introduction to using skills. For all other skills, load them with the skill tool (for example superpowers:brainstorming):**' +
  $nl + $nl + $content + $nl + '</EXTREMELY_IMPORTANT>'

@{ hookSpecificOutput = @{ hookEventName = 'SessionStart'; additionalContext = $context } } |
  ConvertTo-Json -Depth 3 -Compress
