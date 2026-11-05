# Windows 开发环境预检与配置指南

Tauri v2 在 Windows 上需要四件套：**Node.js（含 npm）、Microsoft C++ 生成工具（MSVC）、Rust（rustup + stable-msvc 工具链）、WebView2 运行时**。开工前必须先体检，缺什么补什么，全部绿灯才进入开发。

> 本文命令均为 **Windows PowerShell 5.1** 语法。PowerShell 5.1 不支持 `&&` / `||`，需要串联时改用分号并在关键步骤后检查 `$LASTEXITCODE`。

## 一、预检命令与判据

逐条执行下列命令，按「判据」判定：

| # | 检查项 | 命令 | 通过判据 |
|---|--------|------|---------|
| 1 | Node.js | `node -v` | `v22.x` 或更高（Vite 8 要求 ≥20.19 / ≥22.12；Node 18 已 EOL） |
| 2 | npm | `npm -v` | 任意现代版本（10.x+），能联网装包即可 |
| 3 | Rust 编译器 | `rustc -V` | ≥ 1.77.2（Tauri v2 MSRV；建议直接用最新 stable） |
| 4 | Cargo | `cargo -V` | 与 rustc 同版本正常输出 |
| 5 | 工具链 | `rustup show active-toolchain` | 活动工具链为 `stable-x86_64-pc-windows-msvc`（不是 gnu，不是 alpha/nightly） |
| 6 | MSVC 链接器 | `& "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath` | 返回一个安装路径（如 `C:\Program Files\Microsoft Visual Studio\2022\BuildTools`） |
| 7 | WebView2 | `Test-Path "${env:ProgramFiles(x86)}\Microsoft\EdgeWebView\Application"` | 路径为 True，且含版本号子目录（Win10/11 一般自带） |
| 8 | Windows 版本 | `cmd /c ver` | Windows 10 1803+ 或 Windows 11 |
| 9 | Git（可选） | `git --version` | 有则更好，没有不阻塞 |
| 10 | 磁盘空间 | `Get-PSDrive C \| Select-Object Used, Free` | C 盘剩余 ≥ 15 GB（MSVC 约 7 GB + Rust + target 缓存） |

**PATH 未生效的兜底检测**：命令报「找不到」不代表没装。先查默认安装位置与注册表，找到了就是 PATH 问题，不是缺件：

```powershell
# 兜底 1：默认安装路径
@(
  "$env:ProgramFiles\nodejs\node.exe",
  "${env:ProgramFiles(x86)}\nodejs\node.exe",
  "$env:LOCALAPPDATA\Programs\nodejs\node.exe",
  "$env:USERPROFILE\.cargo\bin\cargo.exe"
) | ForEach-Object { "{0,-60} {1}" -f $_, (Test-Path $_) }

# 兜底 2：注册表（能发现装在 D 盘等自定义路径的情况，比写死路径可靠）
Get-ItemProperty `
  'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' `
  -ErrorAction SilentlyContinue |
  Where-Object { $_.DisplayName -match '^(Node\.js|Rust|Visual Studio|WebView2)' } |
  Select-Object DisplayName, DisplayVersion, InstallLocation
```

## 二、缺件安装教程（按推荐顺序：先 MSVC，再 Rust，再 Node）

安装顺序很重要：**先装 VS 生成工具，再装 Rust**。rustup 安装时会检测 MSVC 是否就绪，顺序反了也能补，但容易在第一次 `cargo build` 时报 `link.exe not found`。

### 1. Microsoft C++ 生成工具（MSVC）

- **下载**：https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/ → 「下载生成工具」得到 `vs_BuildTools.exe`（约 2-4 MB 引导器）
- **教程**：https://learn.microsoft.com/zh-cn/visualstudio/install/workload-component-id-vs-build-tools
- **步骤**：
  1. 运行 `vs_BuildTools.exe`，等待安装器加载；
  2. 在「工作负载」页勾选 **「使用 C++ 的桌面开发」**（Desktop development with C++）；
  3. 右侧默认组件保留 **MSVC v143** 与 **Windows 11 SDK（10.0.22621 或更新）**；
  4. 点安装，约需 6-8 GB 磁盘、20-60 分钟（视网速）。
- **注意**：不需要装完整 Visual Studio IDE；装完无需手动配 PATH，安装器自动注册。

### 2. Rust（rustup + stable-msvc）

- **下载**：https://www.rust-lang.org/zh-CN/tools/install → 点击下载 `rustup-init.exe`（直链 https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe ）
- **教程**：https://www.rust-lang.org/zh-CN/learn
- **步骤**：
  1. 双击 `rustup-init.exe`；若提示未检测到 Visual Studio C++ 生成工具，先回到第 1 步装好 MSVC；
  2. 出现选项时输入 `1`（默认：`stable-x86_64-pc-windows-msvc`）；
  3. 安装完成后命令行会提示 cargo 已加入 `%USERPROFILE%\.cargo\bin`。
- **国内加速（可选）**：安装前设置环境变量
  ```powershell
  $env:RUSTUP_DIST_SERVER = "https://rsproxy.cn"
  $env:RUSTUP_UPDATE_ROOT = "https://rsproxy.cn/rustup"
  ```
  装完后建议配置 crates 镜像（写入 `%USERPROFILE%\.cargo\config.toml`）：
  ```toml
  [source.crates-io]
  replace-with = 'rsproxy-sparse'
  [source.rsproxy-sparse]
  registry = "sparse+https://rsproxy.cn/index/"
  ```
  参考：https://rsproxy.cn/

### 3. Node.js（LTS）

- **下载**：https://nodejs.org/zh-cn/download → 选 **22.x LTS** 的 `.msi`（Windows 64 位）
- **教程**：https://nodejs.org/zh-cn/learn
- **步骤**：运行 msi，一路「下一步」，保持默认勾选 **Add to PATH** 与 **Automatically install the necessary tools**（后者可不勾，MSVC 已单独安装）。
- **国内加速（可选）**：`npm config set registry https://registry.npmmirror.com`

### 4. WebView2 运行时

- Windows 10（大部分更新版）与 Windows 11 已预装，第 7 项检查通过即可跳过。
- 未预装时下载 Evergreen 独立安装包：https://developer.microsoft.com/zh-cn/microsoft-edge/webview2/
- **教程**：https://learn.microsoft.com/zh-cn/microsoft-edge/webview2/

### 5. Git（可选）

- **下载**：https://git-scm.com/download/win
- 安装默认选项即可；若习惯 bash 语法，可直接使用其附带的 Git Bash（本工作流命令以 PowerShell 为主）。

## 三、环境变量（PATH）配置教程

适用场景：文件在默认位置存在，但 `node -v` / `cargo -V` 报「找不到」。

**方案 A：图形界面（推荐小白）**

1. `Win + R` 输入 `sysdm.cpl` → 「高级」→ 「环境变量」；
2. 在「用户变量」或「系统变量」中选中 `Path` → 「编辑」→ 「新建」，逐条加入：
   - `C:\Program Files\nodejs`
   - `%USERPROFILE%\.cargo\bin`
3. 一路确定。**必须重新打开终端 / 重启 IDE 才生效**。

**方案 B：命令行永久写入（用户级 Path）**

```powershell
# 注意：setx 会把当前 PATH 快照写入，若系统 Path 很长可能截断（上限 1024 字符），推荐用方案 A
setx PATH "$env:PATH;C:\Program Files\nodejs;$env:USERPROFILE\.cargo\bin"
```

**方案 C：当前会话临时生效（验证用）**

```powershell
$env:PATH = "$env:USERPROFILE\.cargo\bin;C:\Program Files\nodejs;$env:PATH"
```

> 只在当前进程生效，关掉终端就没了 —— 适合先验证、再决定要不要永久写入。

## 四、最终综合验证（全部通过才算环境就绪）

按顺序执行，**五条全绿才放行进入开发**：

```powershell
# ① 四件套版本全部正常输出且满足阈值
node -v; npm -v; rustc -V; cargo -V

# ② 活动工具链是 stable-msvc
rustup show active-toolchain

# ③ MSVC 链接器就绪（返回安装路径）
& "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" `
  -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -property installationPath

# ④ WebView2 存在
Test-Path "${env:ProgramFiles(x86)}\Microsoft\EdgeWebView\Application"

# ⑤ 链接器实战验证：空项目编译一次（能过 = MSVC + Rust + linker 全链路 OK）
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
$tmp = Join-Path $env:TEMP ("env-check-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
Push-Location $tmp
cargo new env-check
Push-Location env-check
cargo build
if ($LASTEXITCODE -eq 0) { Write-Output "ENV_OK" } else { Write-Output "ENV_FAIL" }
Pop-Location
Pop-Location
```

第 ⑤ 步是判定性测试：`cargo build` 需要调用 `link.exe`，能编译通过说明 MSVC 与 Rust 已正确联动；若报 `error: linker 'link.exe' not found`，回第二节第 1 项重装/修复 VS 生成工具。

## 五、常见报错对照表

| 报错 | 根因 | 解法 |
|------|------|------|
| 找不到 node / cargo | PATH 未生效或未安装 | 先做兜底检测；文件存在→配 PATH（方案 A）；不存在→装件 |
| `error: linker 'link.exe' not found` | 未装 MSVC 或只装了 SDK 没装工具集 | 装「使用 C++ 的桌面开发」工作负载（含 MSVC v143） |
| `error: Microsoft Visual C++ 14.0 or greater is required` | 同上 | 同上 |
| rustup 装到了 `*-gnu` 工具链 | 安装时选错选项 | `rustup toolchain install stable-x86_64-pc-windows-msvc` 后 `rustup default stable-x86_64-pc-windows-msvc` |
| `npx tauri` 报找不到 tauri | 没有全局装 Tauri CLI | **正常，不需要全局装**：项目 `devDependencies` 自带 `@tauri-apps/cli`，进项目目录用 `npx tauri ...` 即可 |
| `npm install` 超时 | 默认源在国外 | `npm config set registry https://registry.npmmirror.com` |
| cargo 拉依赖超时 | crates.io 访问慢 | 配置 rsproxy 镜像（见第二节第 2 项） |
| WebView2 检查为空但系统是 Win11 | 企业裁剪镜像 | 装 Evergreen 运行时（见第二节第 4 项） |
| PowerShell 报「无法加载文件…未对文件进行数字签名」 | 执行策略限制 | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 后重试 |
