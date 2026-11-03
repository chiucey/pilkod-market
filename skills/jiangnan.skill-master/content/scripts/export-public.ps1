$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir '..')

$distDir = Join-Path $repoRoot 'dist'
$publicDir = Join-Path $distDir 'public'

Write-Host "Exporting public package to: $publicDir"

if (Test-Path $publicDir) {
  Remove-Item -Recurse -Force $publicDir
}
New-Item -ItemType Directory -Force -Path $publicDir | Out-Null

$filesToCopy = @(
  'README.md',
  'SKILL.md',
  'EVALUATION-v1.1.md',
  'LICENSE'
)

foreach ($rel in $filesToCopy) {
  $src = Join-Path $repoRoot $rel
  if (Test-Path $src) {
    Copy-Item -Force -Path $src -Destination (Join-Path $publicDir $rel)
  }
}

$dirsToCopy = @(
  'outputs'
)

foreach ($rel in $dirsToCopy) {
  $src = Join-Path $repoRoot $rel
  if (Test-Path $src) {
    Copy-Item -Recurse -Force -Path $src -Destination (Join-Path $publicDir $rel)
  }
}

Write-Host "Done. Public package created (references excluded)."