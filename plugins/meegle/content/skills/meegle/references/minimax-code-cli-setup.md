# Pilkod 中准备 Meegle CLI

本插件携带官方仓库 commit `e5ca19052b81cbba99c48ef0eab1f515552076e1` 的完整 `skills/meegle`，配套真实 npm 发行版 `@lark-project/meegle@1.0.26`。仅在执行飞书项目任务且 CLI 缺失或已确认不兼容时安装。Hook 只检测本地路径，不运行 CLI、不联网、不认证，不因无关会话安装依赖。

## 先复用已有 CLI

终端 PATH 可能不同于 Hook PATH，先查 `command -v meegle`（Windows：`Get-Command meegle.cmd,meegle.exe -CommandType Application -ErrorAction SilentlyContinue`）。找到后用实际入口 `--version` 验证。Hook 也检查 `~/.minimax/bin/meegle` 或 Windows `%USERPROFILE%\.minimax\bin\meegle.exe`，找到即复用，不重复安装。已有兼容版本不自动降级；不在任务中自动更新插件 Skill 快照。

## Node/npm 可用：只装 CLI

```bash
npm install -g @lark-project/meegle@1.0.26
meegle --version
```

Windows PowerShell：

```powershell
npm.cmd install -g @lark-project/meegle@1.0.26
if ($LASTEXITCODE -ne 0) { throw 'Meegle npm installation failed' }
meegle.cmd --version
if ($LASTEXITCODE -ne 0) { throw 'Installed meegle cannot run' }
```

npm 元数据要求 Node >=16，建议受支持的 LTS。不要执行 `meegle install`、`npx skills add` 或全量安装向导；插件已包含 Skill。不自动 sudo、改全局 PATH、shell profile、用户偏好或认证。

npm 安装后若 PATH 未找到命令，用 `npm prefix -g` / `npm.cmd prefix -g` 定位：POSIX 为 `<prefix>/bin/meegle`，Windows 为 `<prefix>\meegle.cmd`。Windows npm 安装后全部示例用 `.cmd`，避免 PowerShell 选择 `.ps1` shim；绝对路径用 `& '带空格的路径\meegle.cmd' ...`，无需修改执行策略。

## 无 Node 或全局前缀不可写：官方 npm 归档中的独立二进制

官方 npm 包实际包含 darwin/linux/win32 的 arm64/x64 独立二进制。本插件已对下载的完整归档验证 registry SHA-512 integrity，并记录对应 SHA-256。直接下载这个固定归档并核对 SHA-256 后提取本机二进制，无需 Node、Python 或管理员权限；不是另猜 GitHub Release 地址。

- URL：`https://registry.npmjs.org/@lark-project/meegle/-/meegle-1.0.26.tgz`
- SHA-256：`f77e74d2c9b15fcfc0433faab3ac088933809c41254905c32538c499006d2504`
- 各二进制许可证随归档提供；安装时保留 `LICENSE`、`THIRD_PARTY_NOTICES.md` 和 `third_party_licenses`。

POSIX（在当前工作区的独立 staging 目录下载，后续按宿主规则清理；不覆盖已有入口）：

```bash
set -eu
meegle_dest="$HOME/.minimax/bin/meegle"
if [ -e "$meegle_dest" ]; then
  "$meegle_dest" --version
else
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) meegle_target=darwin-arm64 ;;
    Darwin-x86_64) meegle_target=darwin-x64 ;;
    Linux-aarch64|Linux-arm64) meegle_target=linux-arm64 ;;
    Linux-x86_64) meegle_target=linux-x64 ;;
    *) printf '%s\n' 'Unsupported OS/architecture'; exit 1 ;;
  esac
  meegle_stage=$(mktemp -d "$PWD/.meegle-install.XXXXXX")
  curl --fail --location --proto '=https' --proto-redir '=https' --connect-timeout 10 --max-time 120 \
    'https://registry.npmjs.org/@lark-project/meegle/-/meegle-1.0.26.tgz' -o "$meegle_stage/meegle.tgz"
  if command -v shasum >/dev/null 2>&1; then
    meegle_hash=$(shasum -a 256 "$meegle_stage/meegle.tgz")
  else
    meegle_hash=$(sha256sum "$meegle_stage/meegle.tgz")
  fi
  [ "${meegle_hash%% *}" = 'f77e74d2c9b15fcfc0433faab3ac088933809c41254905c32538c499006d2504' ] || { printf '%s\n' 'SHA-256 mismatch'; exit 1; }
  tar -xzf "$meegle_stage/meegle.tgz" -C "$meegle_stage" "package/bin/meegle-$meegle_target" package/LICENSE package/THIRD_PARTY_NOTICES.md package/third_party_licenses
  chmod 755 "$meegle_stage/package/bin/meegle-$meegle_target"
  "$meegle_stage/package/bin/meegle-$meegle_target" --version
  mkdir -p "$HOME/.minimax/bin" "$HOME/.minimax/licenses/meegle-1.0.26"
  cp -R "$meegle_stage/package/LICENSE" "$meegle_stage/package/THIRD_PARTY_NOTICES.md" "$meegle_stage/package/third_party_licenses" "$HOME/.minimax/licenses/meegle-1.0.26/"
  cp -n "$meegle_stage/package/bin/meegle-$meegle_target" "$meegle_dest"
  "$meegle_dest" --version
fi
```

Windows PowerShell（使用系统 `tar.exe`，若不可用则报告缺失，不假设 `Expand-Archive` 支持 tgz）：

```powershell
$ErrorActionPreference = 'Stop'
$meegleDest = Join-Path $env:USERPROFILE '.minimax\bin\meegle.exe'
if (Test-Path -LiteralPath $meegleDest) {
  & $meegleDest --version
  if ($LASTEXITCODE -ne 0) { throw 'Existing meegle cannot run' }
} else {
  if (-not (Get-Command tar.exe -CommandType Application -ErrorAction SilentlyContinue)) { throw 'tar.exe is required to extract the official tgz' }
  $meegleArch = $env:PROCESSOR_ARCHITEW6432
  if ([string]::IsNullOrWhiteSpace($meegleArch)) { $meegleArch = $env:PROCESSOR_ARCHITECTURE }
  switch ($meegleArch.ToUpperInvariant()) {
    'AMD64' { $meegleTarget = 'win32-x64' }
    'ARM64' { $meegleTarget = 'win32-arm64' }
    default { throw 'Unsupported architecture' }
  }
  $meegleStage = Join-Path (Get-Location).Path ('.meegle-install-' + [guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Path $meegleStage | Out-Null
  $meegleArchive = Join-Path $meegleStage 'meegle.tgz'
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  Invoke-WebRequest -UseBasicParsing -TimeoutSec 120 -Uri 'https://registry.npmjs.org/@lark-project/meegle/-/meegle-1.0.26.tgz' -OutFile $meegleArchive
  if ((Get-FileHash -LiteralPath $meegleArchive -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'f77e74d2c9b15fcfc0433faab3ac088933809c41254905c32538c499006d2504') { throw 'SHA-256 mismatch' }
  tar.exe -xzf $meegleArchive -C $meegleStage "package/bin/meegle-$meegleTarget.exe" package/LICENSE package/THIRD_PARTY_NOTICES.md package/third_party_licenses
  if ($LASTEXITCODE -ne 0) { throw 'Extraction failed' }
  $meegleBinary = Join-Path $meegleStage "package\bin\meegle-$meegleTarget.exe"
  & $meegleBinary --version
  if ($LASTEXITCODE -ne 0) { throw 'Downloaded meegle cannot run' }
  New-Item -ItemType Directory -Force -Path (Split-Path $meegleDest) | Out-Null
  $meegleLicenses = Join-Path $env:USERPROFILE '.pilkod\licenses\meegle-1.0.26'
  New-Item -ItemType Directory -Force -Path $meegleLicenses | Out-Null
  Copy-Item -LiteralPath (Join-Path $meegleStage 'package\LICENSE'),(Join-Path $meegleStage 'package\THIRD_PARTY_NOTICES.md'),(Join-Path $meegleStage 'package\third_party_licenses') -Destination $meegleLicenses -Recurse
  [System.IO.File]::Copy($meegleBinary, $meegleDest, $false)
  & $meegleDest --version
  if ($LASTEXITCODE -ne 0) { throw 'Installed meegle cannot run' }
}
```

## 继续原任务

每次终端调用使用已发现的绝对路径，或在该次调用设置 PATH；一次 PATH 变更不跨进程持久化。独立入口为 `"$HOME/.minimax/bin/meegle"` / `& "$env:USERPROFILE\.minimax\bin\meegle.exe"`。上游业务示例替换入口即可。

安装成功不等于认证成功。按 [Auth Guard](auth-guard.md) 复用 profile、检查 host，用非 TTY device-code 授权；网络错误不要求重登。CLI 本身可能显示官方遥测提示；不因提示自动修改偏好，用户明确请求才操作。下载/校验/启动失败应报告具体阶段，不循环安装或跳过校验。
