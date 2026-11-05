# ASCII source is intentional: Windows PowerShell 5.1 can read it without a BOM.
# PATH and standalone install path; no network, install, CLI invocation or auth.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

$cliCommand = Get-Command lark-cli -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -ne $cliCommand) { exit 0 }

$pluginRoot = $env:PLUGIN_ROOT
if ([string]::IsNullOrWhiteSpace($pluginRoot)) { $pluginRoot = $env:MINIMAX_PLUGIN_ROOT }
if ([string]::IsNullOrWhiteSpace($pluginRoot)) { exit 0 }

$standaloneCli = $null
if (-not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
  $standaloneCli = Join-Path $env:USERPROFILE '.minimax\bin\lark-cli.exe'
}
if ($null -ne $standaloneCli -and (Test-Path -LiteralPath $standaloneCli -PathType Leaf)) {
  $reminder = @"
Lark plugin: lark-cli is already installed at this absolute path: $standaloneCli
Use the PowerShell call operator & with that quoted absolute executable path, or prepend its directory to PATH in EACH terminal invocation. Verify --version before first use. Do not reinstall merely because the Hook PATH did not contain it. An executable path is not proof of Feishu authentication.
"@
} else {
  $setupDoc = Join-Path $pluginRoot 'skills\lark-shared\references\minimax-code-cli-setup.md'
  $reminder = @"
Lark plugin dependency check: lark-cli was not found in the Hook PATH or the standalone installation directory.
Before the first Lark/Feishu operation, read this plugin's installation reference: $setupDoc
The terminal tool may have a different PATH: if it already resolves lark-cli, reuse it. Otherwise use the normal PowerShell terminal tool to install CLI version 1.0.93; with working Node/npm the CLI-only command is: npm.cmd install -g @larksuite/cli@1.0.93
If Node/npm is absent or the global prefix is unwritable, follow the reference's official standalone binary download and SHA-256 verification procedure. This plugin already includes all upstream lark-* Skills; do not install another global Skills copy or run the all-in-one installation wizard.
For npm installations, use lark-cli.cmd --version and lark-cli.cmd for ALL subsequent commands, or use & with the quoted absolute .cmd path, even when it is already on PATH. Do not invoke extensionless lark-cli: PowerShell may select the .ps1 shim and block it under the execution policy. Reuse the .cmd entry instead of reinstalling or changing execution policy. For standalone installations, use & with the quoted .exe path. Verify --version, then resume the original request. Do not start a download for an unrelated task. Configuration and OAuth are separate and follow lark-shared.
"@
}

@{ hookSpecificOutput = @{ hookEventName = 'SessionStart'; additionalContext = $reminder } } |
  ConvertTo-Json -Depth 3 -Compress
