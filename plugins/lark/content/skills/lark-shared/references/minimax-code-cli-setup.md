# Pilkod 中准备 lark-cli

这是 `lark` Plugin 的本地集成说明。业务命令、身份和授权以同目录的飞书官方 reference 为准。
本插件携带官方仓库 commit `30e95091fff14f9c5589eece2d66fce2d0065f48` 的全部 28 个 `lark-*` Skills，配套 CLI 版本为 `1.0.93`。

## 何时执行

仅在用户要使用飞书能力，且终端工具实际找不到 `lark-cli`、可执行程序启动失败，或确认已安装版本不支持所需命令时进入此流程。不要因为无关任务触发了 Hook 就下载。

`SessionStart` Hook 先在 PATH 中查找 `lark-cli`；未找到时，再检查本说明指定的独立二进制安装路径：macOS/Linux 为 `~/.minimax/bin/lark-cli`，Windows 为 `%USERPROFILE%\.minimax\bin\lark-cli.exe`。找到独立二进制时，Hook 会把绝对路径提供给模型，模型先验证并复用，不重复安装。Hook 不检查插件数据目录，也不访问网络、运行 CLI、验证版本或读取凭据。

Hook 和终端工具的 PATH 可能不同；若 Hook 未找到 CLI，先在将要执行业务命令的终端中确认：macOS/Linux 用 `command -v lark-cli`，Windows 用 `Get-Command lark-cli -CommandType Application`。如果可用，运行 `--version` 后复用，不能仅因 Hook 的提醒重复安装。旧版本能完成任务时不自动升级。

如果安装后 CLI 不在终端 PATH 中，直接使用实际安装的绝对路径。路径是文本数据，必须按当前 shell 正确引用；不要使用 `eval`、`Invoke-Expression` 或把未转义的路径拼入代码。

## 已有 Node/npm

通过普通终端工具执行，允许安装耗时超过 Hook 的 5 秒预算。推荐给工具 300 秒超时。

macOS/Linux：

```bash
npm install -g @larksuite/cli@1.0.93
lark-cli --version
```

Windows PowerShell：

```powershell
npm.cmd install -g @larksuite/cli@1.0.93
if ($LASTEXITCODE -ne 0) { throw 'lark-cli installation failed' }
lark-cli.cmd --version
if ($LASTEXITCODE -ne 0) { throw 'lark-cli verification failed' }
```

Windows 的 npm 安装会同时生成 `lark-cli.cmd` 和 `lark-cli.ps1`。版本验证和后续业务命令都显式使用 `lark-cli.cmd`，或用 `&` 调用带引号的 `.cmd` 绝对路径；不要使用无扩展名的 `lark-cli`，以免 PowerShell 优先选择 `.ps1` 并被执行策略拦截。即使 CLI 已在 PATH 中，也遵循此规则。遇到 `.ps1` 执行策略报错时改用已有 `.cmd` 入口，无需重装 CLI 或修改执行策略。

官方 README 推荐的 `npx @larksuite/cli@latest install` 是完整安装向导，内部先全局安装 CLI，再安装全局 Skills。本插件已经自带 Skills，因此此处只执行它的 CLI 安装步骤。不要另跑 `npx skills add`，不要把 Skills 安装到用户的全局目录。

如果安装成功但当前 PATH 找不到命令，先用 `npm prefix -g`（Windows 为 `npm.cmd prefix -g`）定位前缀：macOS/Linux 的入口位于 `<prefix>/bin/lark-cli`，Windows 为 `<prefix>/lark-cli.cmd`。后续直接引用实际入口，或在每次工具调用中设置 PATH；不要要求用户仅为此重启 Pilkod。

如果 Node/npm 不存在、版本不符合 npm 包要求，或全局目录不可写，使用下面的独立二进制下载流程。不要仅为准备 CLI 要求用户安装 Node，也不要自动提升管理员权限。

## 无 Node/npm：macOS/Linux

从官方 Release 下载固定平台归档，并用 npm 官方发布包中的 SHA-256 校验。原始校验文件保存在 [lark-cli-1.0.93-checksums.txt](lark-cli-1.0.93-checksums.txt)。默认装入用户目录 `~/.minimax/bin`，不需要 sudo。

在一个终端调用中执行下列完整代码；已有可执行文件会被复用。若是在修复已损坏文件，先说明具体路径和问题，再按当前用户意图处理该文件。

```bash
set -eu
lark_dest_dir="$HOME/.minimax/bin"
if [ -x "$lark_dest_dir/lark-cli" ]; then
  "$lark_dest_dir/lark-cli" --version
else
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) lark_target=darwin-arm64; lark_sha=eaa09754925c00a6858e91518a49ab8e0a24bd4178e4698a7b185046b8ea24e2 ;;
    Darwin-x86_64) lark_target=darwin-amd64; lark_sha=bf37861ce5b5fb10c093ffd8b7305f2a80349280cf32563267c29f81cb864e53 ;;
    Linux-x86_64) lark_target=linux-amd64; lark_sha=10031849a1884bf9165cb01de47102b4847fba81bb9eb76f4168125ea9746c51 ;;
    Linux-aarch64|Linux-arm64) lark_target=linux-arm64; lark_sha=800832bb84b0bf74579f49de3219b2ea8b9e72049c5a3ed239680e4cbc31474c ;;
    Linux-riscv64) lark_target=linux-riscv64; lark_sha=fd7fd87674e8dda2d0e380a2e2ea83f91136d06bb7e8b5b0acbea93a5e830405 ;;
    *) printf '%s\n' 'Unsupported OS or CPU architecture' >&2; exit 1 ;;
  esac
  lark_archive="lark-cli-1.0.93-$lark_target.tar.gz"
  lark_tmp=$(mktemp -d)
  lark_staged=
  trap 'rm -rf "$lark_tmp"; if [ -n "$lark_staged" ]; then rm -f "$lark_staged"; fi' EXIT
  if ! curl --fail --location --proto '=https' --proto-redir '=https' --connect-timeout 10 --max-time 120 \
    "https://github.com/larksuite/cli/releases/download/v1.0.93/$lark_archive" -o "$lark_tmp/cli.tar.gz"; then
    curl --fail --location --proto '=https' --proto-redir '=https' --connect-timeout 10 --max-time 120 \
      "https://registry.npmmirror.com/-/binary/lark-cli/v1.0.93/$lark_archive" -o "$lark_tmp/cli.tar.gz"
  fi
  if command -v shasum >/dev/null 2>&1; then
    lark_actual=$(shasum -a 256 "$lark_tmp/cli.tar.gz")
  else
    lark_actual=$(sha256sum "$lark_tmp/cli.tar.gz")
  fi
  lark_actual=${lark_actual%% *}
  [ "$lark_actual" = "$lark_sha" ] || { printf '%s\n' 'SHA-256 mismatch; installation stopped' >&2; exit 1; }
  tar -xzf "$lark_tmp/cli.tar.gz" -C "$lark_tmp" lark-cli
  mkdir -p "$lark_dest_dir"
  lark_staged=$(mktemp "$lark_dest_dir/.lark-cli.XXXXXX")
  cp "$lark_tmp/lark-cli" "$lark_staged"
  chmod 755 "$lark_staged"
  "$lark_staged" --version
  mv -f "$lark_staged" "$lark_dest_dir/lark-cli"
  lark_staged=
  "$lark_dest_dir/lark-cli" --version
fi
```

## 无 Node/npm：Windows PowerShell

使用系统 PowerShell 下载 `.zip`、校验并解压，不依赖 Bash、Python 或 npm。默认装入 `%USERPROFILE%\.minimax\bin`。

```powershell
$ErrorActionPreference = 'Stop'
$larkDestDir = Join-Path $env:USERPROFILE '.minimax\bin'
$larkDest = Join-Path $larkDestDir 'lark-cli.exe'
if (Test-Path -LiteralPath $larkDest -PathType Leaf) {
  & $larkDest --version
  if ($LASTEXITCODE -ne 0) { throw 'Existing lark-cli cannot run; inspect before replacing it' }
} else {
  $larkArch = $env:PROCESSOR_ARCHITEW6432
  if ([string]::IsNullOrWhiteSpace($larkArch)) { $larkArch = $env:PROCESSOR_ARCHITECTURE }
  switch ($larkArch.ToUpperInvariant()) {
    'AMD64' { $larkTarget = 'windows-amd64'; $larkSha = '18e9320e378a0eefdb3b7004e0c6d42f48da85ae196d2bf5e89e4299ae7674d7' }
    'ARM64' { $larkTarget = 'windows-arm64'; $larkSha = '3739889cab8d938bbe2015032cd3e8de82ba0608b01e6b3ce3740f999199b4fb' }
    default { throw "Unsupported CPU architecture: $larkArch" }
  }
  $larkArchive = "lark-cli-1.0.93-$larkTarget.zip"
  $larkTmp = Join-Path ([System.IO.Path]::GetTempPath()) ('lark-cli-' + [guid]::NewGuid().ToString('N'))
  $larkStaged = $null
  New-Item -ItemType Directory -Path $larkTmp | Out-Null
  try {
    $larkZip = Join-Path $larkTmp 'cli.zip'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    try {
      Invoke-WebRequest -UseBasicParsing -TimeoutSec 120 -Uri "https://github.com/larksuite/cli/releases/download/v1.0.93/$larkArchive" -OutFile $larkZip
    } catch {
      Invoke-WebRequest -UseBasicParsing -TimeoutSec 120 -Uri "https://registry.npmmirror.com/-/binary/lark-cli/v1.0.93/$larkArchive" -OutFile $larkZip
    }
    if ((Get-FileHash -LiteralPath $larkZip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $larkSha) {
      throw 'SHA-256 mismatch; installation stopped'
    }
    $larkExtracted = Join-Path $larkTmp 'extracted'
    Expand-Archive -LiteralPath $larkZip -DestinationPath $larkExtracted
    New-Item -ItemType Directory -Force -Path $larkDestDir | Out-Null
    $larkStaged = Join-Path $larkDestDir ('lark-cli-' + [guid]::NewGuid().ToString('N') + '.exe')
    Copy-Item -LiteralPath (Join-Path $larkExtracted 'lark-cli.exe') -Destination $larkStaged
    & $larkStaged --version
    if ($LASTEXITCODE -ne 0) { throw 'Downloaded lark-cli cannot run' }
    Move-Item -LiteralPath $larkStaged -Destination $larkDest
    $larkStaged = $null
    & $larkDest --version
    if ($LASTEXITCODE -ne 0) { throw 'Installed lark-cli cannot run' }
  } finally {
    Remove-Item -LiteralPath $larkTmp -Recurse -Force
    if ($null -ne $larkStaged -and (Test-Path -LiteralPath $larkStaged)) { Remove-Item -LiteralPath $larkStaged -Force }
  }
}
```

## 让后续命令找到 CLI

Hook、安装命令和后续工具调用运行在不同进程中。一次 `export PATH` 或 `$env:PATH` 设置不会自动传递到下一次调用。

- 独立二进制安装后，macOS/Linux 用 `"$HOME/.minimax/bin/lark-cli" <原命令参数>`；Windows 用 `& "$env:USERPROFILE\.minimax\bin\lark-cli.exe" <原命令参数>`。
- Windows 通过 npm 安装后，用 `lark-cli.cmd <原命令参数>`；若不在 PATH 中，用 `& '<npm 全局前缀>\lark-cli.cmd' <原命令参数>`，将前缀替换为实际路径。
- 官方 Skills 中所有 `lark-cli ...` 示例都可以替换为上述入口，原有参数和工作目录保持不变。
- 如果一个工作流连续多次调用 CLI，可以在该次终端调用开始时把安装目录加入 PATH；每次新工具调用都重复设置。不要写 shell profile 或修改机器全局 PATH。
- 可执行文件的绝对路径不受 CLI 的文件参数限制；`--file`、`--output` 等业务文件参数仍按官方规则使用当前工作目录内的相对路径。

## 安装完成后的流程

先验证 `--version`，再继续用户原任务。应用配置与 OAuth 授权分别按 [配置初始化](lark-shared-config-init.md) 和 [身份与权限](lark-shared-identity-and-permissions.md) 执行。不要读取或手工修改本机凭据，不要把“找到了可执行文件”当作“飞书已登录”。

若下载、校验或启动失败，说明具体阶段和错误并保留可重试入口；不要循环安装、跳过校验、反复提升权限或声称飞书业务已完成。

## 版本与上游来源

- [官方 README](https://github.com/larksuite/cli/blob/30e95091fff14f9c5589eece2d66fce2d0065f48/README.zh.md)
- [官方安装向导](https://github.com/larksuite/cli/blob/30e95091fff14f9c5589eece2d66fce2d0065f48/scripts/install-wizard.js)
- [官方二进制下载实现](https://github.com/larksuite/cli/blob/30e95091fff14f9c5589eece2d66fce2d0065f48/scripts/install.js)

本插件内的 Skills 随 Plugin 版本更新，和用户全局 Skills 目录分开。不要在处理更新提示时改写本插件的只读快照，也不要通过 `lark-cli update` 顺带安装另一套全局 Skills。用户明确要求升级时，先核对官方发行版与命令兼容性，再执行 CLI-only 升级；不要自动降级已经可用的新版本。
