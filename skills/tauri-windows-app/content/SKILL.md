---
name: tauri-windows-app
description: 用 Tauri v2（Rust 后端 + Web 前端）开发 Windows 桌面应用的完整工作流与避坑手册，覆盖开发环境预检与配置引导、需求门禁澄清、设计契约、编码分层、自测、打包白屏与旧资源排错、版本化归档交付、双形态 exe 产物、Windows 系统能力（托盘/通知/单实例/开机自启/关机）、图标生成与 NSIS 打包、高分屏窗口尺寸问题、Rust 体积与冷启动优化。只要用户提到 Tauri、tauri.conf、Cargo.toml、WebView2、MSVC、rustc/cargo、NSIS、桌面应用、Windows 小工具、把它打包成 exe、装到 Windows 桌面、白屏、托盘常驻、开机自启、便携版 exe 等场景，就应使用本技能，即使用户没有明说"用技能"，也应当先加载本技能再动手。
---

# Tauri v2 桌面应用开发（Windows 为主）

## 适用场景

- 开发环境预检与配置引导：Node.js / MSVC / Rust / WebView2 体检，缺什么就出教程补什么
- 从零搭建 Tauri v2 桌面应用（Rust 后端 + Web 前端）
- 打包后 exe **打开是白屏**或**界面显示的是旧版本**
- 需要调用 Windows 系统能力：关机/重启、托盘常驻、系统通知、单实例、开机自启
- 生成应用图标（PNG/ICO）并打出 NSIS 安装包
- 窗口在高分屏（125%/150%/225% DPI）下每次开关都变大
- 安装包体积过大、冷启动慢，需要量化优化

**不覆盖**：非 Tauri 技术栈（Electron / Flutter / Qt）的选型对比；UI 视觉稿像素级还原应由使用者提供素材。

## 与使用者协作的基线

使用者是全栈型桌面产品开发者：做过大量桌面交互产品与小工具，具备专业 UI 设计能力，精通 Rust 打包与体积优化。因此**可以直接使用专业术语**（客户区/外框、DPI 缩放、`custom-protocol` feature、NSIS bundle、`#[cfg(target_os = "windows")]`），不必降低技术密度；但**在需求与设计取舍上不要替他做决定**。

使用者的机器环境不一定总是配好的 —— 环境不过关时，要按小白也能照做的方式引导配置，不自嗨。

## 核心原则

0. **环境先行（最高优先级）**：开工前先做开发环境预检（Node.js / MSVC / Rust / WebView2），不满足就生成配置教程引导用户补齐，全部绿灯才动手。详见第 0 步与 `references/env-setup.md`。
1. **门禁原则**：需求存在歧义或关键信息缺失时，先提问到确认，再写代码。详见第 1 步。
2. **需求直接落地**：把需求拆成「界面状态 + 交互行为 + 系统调用」三块，再写代码。不要为了流程而拉专家团队、写 PRD、设计文档。
3. **打包必须用 CLI**：`npx tauri build`，**绝不**用裸 `cargo build --release`（原因见坑位 1）。
4. **打包后必须自检**：跑 `scripts/verify-bundle.mjs`，确认前端资源真的嵌进 exe 了。
5. **Windows 优先但可移植**：系统调用用 `#[cfg(target_os = "windows")]` 保护，非 Windows 分支给出可编译的兜底。
6. **交付物是 exe，不是源码**：最终必须交出 **NSIS 安装包**（`<AppName>_<版本>_Setup.exe`）与**免安装便携版**（`<AppName>_<版本>_Portable.exe`）两套可运行产物，并在 exe 上完成验收（详见第 7-8 步）。dev 通过 ≠ 交付通过。
7. **版本只增不覆**：每次重新打包前必须递增版本号，产物文件名带版本，`release/` 中**禁止覆盖或删除旧版本产物**，历史版本一律保留可回溯。

## 每阶段怎么向使用者通报

工作流是**严格串行**的：上一阶段未通过，不得进入下一阶段。每推进一个阶段都要简要通报一次，让使用者知道现在在哪、下一步要做什么。通报形式如下：

| 阶段 | 通报内容 |
|------|---------|
| 第 0 步 环境预检 | 体检结果表（检查项 / 实测 / 判定）；缺件时给编号的安装引导（下载地址 / 步骤 / PATH 配置 / 镜像加速），并以复检全绿收口 |
| 第 1 步 需求门禁 | 编号确认清单，标明哪些已明确、哪些待确认 |
| 第 2 步 设计 | 结构化 Markdown：状态机表格 + 命令契约表格 + 目录结构，不写空话 |
| 第 3-4 步 编码 | 改动按文件列出；关键决策在代码注释或回复里给出一句理由（**为什么**这么写，而不是写什么） |
| 第 5 步 自测 | 表格化的用例与实测结果；失败项不得含糊带过 |
| 第 6 步 打包 | 先声明本次版本号（相对上版升了哪一位、为什么），再给两种产物及其路径（`_Setup.exe` 与 `_Portable.exe`），附 `verify-bundle.mjs` 结论与体积数据 |
| 第 7-8 步 交付 | 可执行 exe 的绝对路径、版本号、体积与安装方式，附 `CHANGELOG.md` 本版记录。**不要用"已完成"三个字收尾** |

始终使用与使用者相同的语言回复（默认中文）；代码、命令、配置保持原样。

---

## 工作流程

### 第 0 步：开发环境预检（先体检，后干活）

任何新项目开工前（含环境类报错排查时），先跑一遍体检。**环境不满足不得进入第 1 步**。

> 下列命令为 **Windows PowerShell 5.1** 语法。Git Bash 用户可自行换成等价 bash 写法，但注意 PowerShell 5.1 不支持 `&&` / `||`。

**A. 体检命令与判据**

```powershell
node -v          # v22.x 或更高（Vite 8 要求 ≥20.19 / ≥22.12）
npm -v
rustc -V         # ≥ 1.77.2（Tauri v2 MSRV）
cargo -V
rustup show active-toolchain    # 活动工具链必须是 stable-x86_64-pc-windows-msvc

# MSVC 检测：返回安装路径即通过
& "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" `
  -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -property installationPath

# WebView2 检测
Get-ChildItem "${env:ProgramFiles(x86)}\Microsoft\EdgeWebView\Application" -Directory `
  -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
```

命令报「找不到」**不代表没装**：先查默认安装位置与注册表，找到了就是 PATH 问题，不是缺件。

```powershell
# 兜底检测 1：默认路径
@(
  "$env:ProgramFiles\nodejs\node.exe",
  "${env:ProgramFiles(x86)}\nodejs\node.exe",
  "$env:LOCALAPPDATA\Programs\nodejs\node.exe",
  "$env:USERPROFILE\.cargo\bin\cargo.exe"
) | ForEach-Object { "{0,-60} {1}" -f $_, (Test-Path $_) }

# 兜底检测 2：注册表（能发现装在 D 盘等自定义路径的情况）
Get-ItemProperty `
  'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' `
  -ErrorAction SilentlyContinue |
  Where-Object { $_.DisplayName -match '^(Node\.js|Rust|Visual Studio|WebView2)' } |
  Select-Object DisplayName, DisplayVersion, InstallLocation
```

**B. 不满足时的引导（面向小白）**

输出一张「体检结果表：检查项 / 实测 / 判定」，然后对每个缺件给出：

1. **下载地址**：VS 生成工具 https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/ ；Rust https://www.rust-lang.org/zh-CN/tools/install ；Node.js LTS https://nodejs.org/zh-cn/download ；WebView2 https://developer.microsoft.com/zh-cn/microsoft-edge/webview2/ 。
2. **安装步骤**：先装 MSVC（勾选「使用 C++ 的桌面开发」工作负载），再装 Rust（选项输 1），最后装 Node（msi 保持 Add to PATH）。顺序不能反。
3. **PATH 配置教程**：`sysdm.cpl` → 高级 → 环境变量 → Path 编辑新增 `C:\Program Files\nodejs` 与 `%USERPROFILE%\.cargo\bin`，改完必须**重开终端 / 重启 IDE** 才生效。
4. **国内加速（可选）**：npm 源 `https://registry.npmmirror.com`，Rust 走 rsproxy 镜像。

完整教程、判据表与常见报错对照见 `references/env-setup.md`。安装由用户人工完成，装完后**必须回来重跑本步体检**，直到全绿。

**C. 综合验证（全绿判据，五条缺一不可）**

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

# ⑤ 链接器实战验证：空项目编译一次
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"   # cargo 常不在 PATH
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

第 ⑤ 步是判定性测试：`cargo build` 要调 `link.exe`，能过说明 MSVC 与 Rust 已正确联动；报 `link.exe not found` 就回炉重装 VS 生成工具。

---

### 第 1 步：需求门禁（不确定就问，禁止猜测开发）

动手前，先对照下表逐项扫描需求。只要存在两种以上合理解读，就**停在这里**，用编号清单一次性把所有不确定项问清楚（一次问完，避免挤牙膏式反复打断），拿到明确答复后才进入第 2 步。

| 门禁项 | 必须明确的点 |
|--------|---------------|
| 目标与边界 | 这个程序解决什么问题？明确不做什么？目标机器是哪些 Windows 版本？ |
| 界面状态 | 有哪几个互斥状态？空态/加载态/错误态分别显示什么？每个状态显示哪些内容？ |
| 交互行为 | 点击后发生什么？哪些是「只选中不执行」？有无需要二次确认的破坏性操作？ |
| 系统调用 | 需要托盘/通知/单实例/开机自启/关机中的哪些？是否需要管理员权限？ |
| 数据持久化 | 哪些设置要记住？运行态要不要落盘？（**默认不要**） |
| 视觉规范 | 主色/强调色/危险色、字号阶、圆角、间距栅格、主题（浅色/深色/护眼） |
| 窗口模型 | 尺寸、最小尺寸、是否 frameless、标题栏自绘还是系统原生、是否记忆位置大小 |
| 验收标准 | 怎样算做完？有没有必须在打包产物上验证的场景？ |

**放行条件**：上表全部有明确答案，或使用者明确授权「你来定」并对默认方案点头。**允许带着已确认的部分先开工**——但绝不允许带着未确认项闷头写完再说。

**防误触是硬要求**：像「选档位后立即执行危险操作」这类设计，必须改为「点选只回填输入框 → 显式点主按钮才执行」。定时关机这类会关机/删文件的操作尤其要遵守。

---

### 第 2 步：设计（可实施，不写空话）

输出可实施的设计方案，供使用者确认后再写代码。包含四块：

1. **窗口模型与状态机** —— 窗口尺寸/最小尺寸/有无边框，界面有哪些互斥状态，状态之间如何迁移（用表格列出「状态 / 触发条件 / 界面表现 / 可用操作」）。
2. **命令契约清单** —— 表格列出「命令名 / 入参 / 返回值 / 错误语义」。这是前后端唯一的事实来源，第 4 步编码时按此实现。
3. **数据模型与持久化策略** —— 哪些字段存、存在哪、什么时候读写；运行态明确不持久化。
4. **目录结构与依赖版本** —— `src/`、`src-tauri/src/commands.rs`、`src-tauri/src/core/` 的职责划分，以及要用到的 crate / npm 包及版本。

设计完成后请使用者确认，再进入第 3 步。

---

### 第 3 步：搭建骨架

从 `assets/tauri-template/` 复制模板，或按 `references/tauri-v2-setup.md` 手动搭建。核心配置见该参考文件，关键点：

- `tauri.conf.json`：`windows[0]` 设 `visible: false`（前端 ready 后再 show，防白屏闪烁）、`decorations: false`（自绘标题栏）
- `build.beforeBuildCommand`：`"npm run build"`
- `capabilities/default.json`：权限标识符格式是 **`core:<模块>:allow-<命令>`**（v2 有 `core:` 前缀）
- `src-tauri/Cargo.toml`：**必须**声明 `custom-protocol` feature（见坑位 1）

---

### 第 4 步：编码

Rust 侧分层：`commands/`（对外命令，薄）→ `core/`（业务模块）→ 状态管理。系统调用**必须**收敛到单一模块（如 `core/shutdown.rs`），不允许散落在多处。

前端用 React + TypeScript strict，状态用 `useState`/`useReducer`，不要引入 Redux 等重型库。

工作纪律：

- **每完成一个可运行里程碑，立即编译验证**（`npm run build` + `cargo check`），不要攒到最后一起排错。
- 下方「致命坑位」清单逐条对照落实。

详见 `references/tauri-v2-patterns.md`（前后端契约、事件、i18n、主题变量化）。

---

### 第 5 步：编码后自测（打包前的代码级验证）

打包前先把低代价的错误挡在前面，失败项不得流入打包：

```powershell
npm run typecheck        # tsc --noEmit，前端类型
npm test                 # Vitest 单测（模板自带 vitest.config.ts）
cargo check --manifest-path src-tauri/Cargo.toml
cargo test --manifest-path src-tauri/Cargo.toml
npm run tauri dev        # dev 模式手验主流程
```

**dev 通过 ≠ 交付通过**。dev 走 `http://localhost:1420`，release 走 `tauri://localhost` 内嵌资源，两者的资源加载路径完全不同，最终结论必须以打包产物为准。

---

### 第 6 步：打包（产出可交付的 .exe，版本号先 +1）

**打包前必须先递增版本号**，同步改两处并保持一致：

```jsonc
// src-tauri/tauri.conf.json
"version": "1.0.1"
```
```toml
# src-tauri/Cargo.toml
[package]
version = "1.0.1"   # 与 tauri.conf.json 同步
```

**版本递增规则**：以上一次交付的版本为基数——问题修复/微调 → 第三位 +1（patch）；新增功能/界面改动 → 第二位 +1（minor）；不兼容的大改 → 第一位 +1（major）。**同一版本号不得打包两次**；忘记升版本就重新打包属于违规操作，必须先补升版本再出包。

然后执行打包：

```powershell
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"   # cargo 常不在 PATH

# 手动清 dist，规避 Vite emptyOutDir 在部分环境报 ETIMEDOUT 的问题（dist 是可再生的构建产物）
if (Test-Path dist) { Remove-Item -Recurse -Force dist }
npm run build

npx tauri build                                # 完整打包：便携版 exe + NSIS 安装包
node scripts/verify-bundle.mjs                 # 自检：前端资源是否真的嵌进 exe
```

图标缺失会导致打包直接失败，先用 `scripts/generate-icons.mjs` 生成，确认 `src-tauri/icons/` 下有 `32x32.png`、`128x128.png`、`icon.ico`。

**打包产物形态**（这是最终交付给用户的东西，必须齐全）：

| 产物 | 生成位置 | 交付用途 |
|------|---------|---------|
| NSIS 安装包 | `src-tauri/target/release/bundle/nsis/<ProductName>_<版本>_x64-setup.exe` | **主交付物**：带安装向导、开始菜单/桌面快捷方式、卸载入口 |
| 免安装便携版 | `src-tauri/target/release/<app-name>.exe` | 绿色版，双击即用，适合内网/受限机器/U 盘携带 |
| MSI（可选） | `src-tauri/target/release/bundle/msi/*.msi` | 企业域控静默分发（`msiexec /i xxx.msi /qn`）时需要 |

需要临时只出便携版、跳过安装包装箱时用 `npx tauri build --no-bundle`。

**打包后必做三件事**：

1. 跑 `verify-bundle.mjs`（白屏资源缺失 / 旧资源 / 调试端口外泄三项体检）。
2. 记录产物数据：便携版 exe 体积、NSIS 安装包体积、冷启动耗时（用于优化前后的量化对比）。
3. 体积不达标时按优化项处理：`panic = "abort"`、`strip = true`、`opt-level = "z"`、`lto = true`、`codegen-units = 1`，并裁剪未用依赖与 `default-features`。

---

### 第 7 步：打包产物验收（必须在 exe 上验，不可只在 dev 验）

这一阶段的操作对象**只能是上一步产出的 exe**，不能是 `npm run dev` 的浏览器窗口。

**A. 安装与便携双路径实测（强制）**

1. 双击 NSIS 安装包走完整安装向导 → 安装完成自动运行 → 走通主功能路径。
2. 另找干净目录单独双击便携版 exe → 走通同样的主功能路径（便携版不得依赖安装时写入的注册表/目录）。
3. 通过开始菜单卸载（NSIS 产物）→ 确认卸载干净、托盘残留清除。

复制/覆盖 exe 前先杀干净残留进程（否则会因文件锁报 Device or resource busy）：

```powershell
taskkill /F /IM your-app.exe 2>$null
taskkill /F /IM msedgewebview2.exe 2>$null
```

**B. 验收用例清单**（输出为表格：用例 / 前置条件 / 步骤 / 预期 / 实测 / 结论）

至少覆盖三类：

1. **冒烟路径**：主功能端到端走通（前端调用 → Rust 命令 → 返回结果 → 界面更新）。
2. **边界值**：空输入、极大/极小值、重复点击、快速连续操作、窗口最小化/还原循环 5 次以上尺寸不漂移。
3. **异常路径**：权限不足（如关机被组策略拒绝）、文件被占用、配置损坏、单实例二次启动、WebView2 运行时缺失。

**C. 系统能力实测**：托盘图标与菜单、系统通知、单实例互斥、开机自启、高分屏（125%/150%）下的界面与窗口尺寸恢复。

未通过项必须修复后**升版本重新走第 6 步再验**；若确认为外部限制，需明确标注为**已知限制**并取得使用者同意。

---

### 第 8 步：交付（版本化归档，不覆盖旧版）

把产物复制到项目 `release/` 目录，按统一命名交付：

```
release/
  <AppName>_<版本>_Setup.exe        # NSIS 安装包（主交付物）
  <AppName>_<版本>_Portable.exe     # 免安装便携版
  CHANGELOG.md                      # 每版一行：版本 / 日期 / 变更要点 / 产物体积
```

**归档铁律**：

- 每次打包版本号 +1（规则见第 6 步），产物文件名天然带版本号。
- `release/` 中**禁止覆盖、改名或删除任何旧版本产物**——旧版本是回滚与问题对照的依据。
- 新产物落盘前先确认同名文件不存在；存在即说明忘升版本，回第 6 步先改版本号。
- 每次交付在 `release/CHANGELOG.md` 追加一行版本记录。

交付说明须包含：需求清单逐条落实情况、本版与上版产物路径与体积、包名/版本号/目标架构（x64/x86/ARM64）、运行前置条件（WebView2 运行时、管理员权限需求）、已知限制、后续可优化项。

---

## 致命坑位（务必避开）

### 1. 打包白屏：release 版被当成 dev 版构建

**现象**：exe 双击打开是纯白窗口，或显示 Chromium 的「ERR_CONNECTION_REFUSED」错误页。

**机制**（Tauri v2 编译期决定，非运行时）：

- `tauri` crate 的 build.rs：`let dev = !custom_protocol;`
- `tauri-codegen` 资源嵌入分支：dev 模式 → `EmbeddedAssets::default()`（**不嵌入任何前端资源**）；release → 嵌入整个 `dist/`
- 运行时 `#[cfg(dev)]` 加载 `devUrl`（`http://localhost:1420`），`#[cfg(not(dev))]` 加载 `frontendDist`（`tauri://localhost`）

**根因**：`custom-protocol` feature 缺失。CLI 会自动传 `--features tauri/custom-protocol`，**裸 `cargo build --release` 不会**。

**修复**：`src-tauri/Cargo.toml` 显式声明，并**用 CLI 构建**：

```toml
[features]
custom-protocol = ["tauri/custom-protocol"]
```

```powershell
npx tauri build         # ✅ 正确
cargo build --release   # ❌ 白屏
```

**唯一判据**：exe 里能不能搜到 `dist/assets` 的文件名。搜不到 = 白屏版。`scripts/verify-bundle.mjs` 封装了这条判据。

**诊断技巧**：在 Rust 侧加 `Builder::on_page_load` + `Webview::eval_with_callback` 探测 `document.getElementById('root')` 与 `document.body.innerText`，能一次拿到「页面实际加载了什么」的铁证。release 版 `windows_subsystem = "windows"` 无控制台，panic 完全静默，必须靠日志或探针。

### 2. 静默发布旧前端资源

**现象**：改了界面但 exe 里还是上一版。不白屏，但界面是旧的。

**根因**：`tauri-build` 只对 `frontendDist` 发 `cargo:rerun-if-changed`，当配置来源变化时（如 `--config` 传临时配置），build script 指纹会沿用上次结果。

**修复**：`src-tauri/build.rs` 显式声明依赖：

```rust
println!("cargo:rerun-if-changed={}/../dist", manifest_dir);
println!("cargo:rerun-if-changed={}/../dist/assets", manifest_dir);
```

### 3. 高分屏下窗口越放越大

**现象**：每次关闭窗口再打开，窗口变大一点，最终撑满屏幕。

**根因**：保存用 `window.inner_size()`（**客户区**），恢复用 `window.set_size(LogicalSize)`（tao 的 `set_inner_size`，也是**客户区**）—— 这两个同口径，本是对的；但若改用 `outer_size()`（含边框）保存再 `set_size` 恢复，每开关一次就多累积一圈边框（本机 1600×900 下边框为 +16×9 px）。

**规则**：**保存与恢复必须统一到客户区**（`inner_size()` ↔ `set_size`），或统一到外框（`outer_size()` ↔ `outer_size`），**切勿混用**。同时给恢复值加上限钳制、跳过 0 值。

### 4. `tauri-plugin-tray` 这个 crate 不存在

Tauri v2 已把托盘并入主 crate。照抄旧教程写 `tauri-plugin-tray` 会直接编译失败：

```rust
// ✅ 正确
use tauri::tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState};
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::image::Image;
// ❌ 错误：could not find `tauri-plugin-tray` in registry
```

### 5. 插件版本不要用预发布版

`3.0.0-alpha.x` 与 tauri 2.x 不兼容。固定用 2.x 稳定版：`tauri-plugin-single-instance` 2.5.x、`tauri-plugin-notification` 2.7.x、`tauri-plugin-store` 2.5.x。

### 6. 打包校验不要 grep 变量名

生产构建会压缩重命名标识符，`grep -c "settingsOpen" dist/assets/*.js` **永远为 0**，与代码是否缺失无关。要 grep **字符串字面量**（如 `frontend_ready`、中文文案），那些不会被改名。

### 7. Vite `emptyOutDir` 在部分环境失败

报 `spawnSync ... ETIMEDOUT`（被安全删除钩子拦截）。绕过：先 `Remove-Item -Recurse -Force dist` 再 `npm run build`。

### 8. NSIS 工具链下载被代理拦截

报 `CONNECT proxy failed: 502` 或 `peer closed connection without sending TLS close_notify`。解法：

```powershell
$env:TAURI_BUNDLER_TOOLS_GITHUB_MIRROR = "https://ghproxy.net/https://github.com"
```

工具链会缓存到 `%LOCALAPPDATA%\tauri\NSIS`，后续可直接打包。

### 9. 单实例互斥量会占住文件

残留的进程会持有单实例互斥量与 exe 文件锁，导致新实例**静默 exit 0**（不是崩溃），且复制 exe 报 Device or resource busy。测试或复制前先杀干净（见第 7 步 A 段的 taskkill 命令）。

### 10. release 版 panic 完全静默

`#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]` 让 release 版没有控制台，panic 时不输出任何东西，表现为「进程莫名消失」。排查时用 debug 构建（`cargo build`）保留回溯，或写日志。

### 11. 版本号不同步 / 忘升版本

`tauri.conf.json` 的 `version` 与 `src-tauri/Cargo.toml` 的 `version` 必须同步修改，只改一处会出现「应用信息与安装包元数据不一致」。同版本号重复出包会导致产物覆盖、无法回溯——**每次打包前先升版本**，`release/` 下出现同名文件就是违规信号。

---

## 参考资料

- `references/env-setup.md` —— 开发环境预检判据表、各组件安装教程与下载地址、PATH 环境变量配置、国内镜像加速、综合验证方法、常见报错对照
- `references/tauri-v2-setup.md` —— 环境搭建、依赖版本、配置文件详解、图标生成、capabilities 权限
- `references/tauri-v2-patterns.md` —— 前后端契约、事件机制、状态机、Windows 系统调用（关机/托盘/通知/单实例）、主题变量化、i18n
- `references/windows-notes.md` —— Windows 专项：DPI、窗口尺寸口径、CREATE_NO_WINDOW、系统命令、调试探针

## 资源

- `scripts/verify-bundle.mjs` —— 打包自检（白屏 + 旧资源 + 调试端口三项），用法 `node scripts/verify-bundle.mjs`，在项目根目录执行
- `scripts/generate-icons.mjs` —— 纯 JS 生成 PNG/ICO 图标，无原生依赖；`node scripts/generate-icons.mjs --shape power --surface 0b1220`
- `assets/tauri-template/` —— 骨架模板（package.json / tauri.conf.json / Cargo.toml / capabilities / build.rs / 前端与 Rust 源码）
