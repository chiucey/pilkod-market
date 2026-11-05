# Windows 专项笔记

## DPI 与窗口尺寸

### 现象

窗口每次开关变大一点，最终撑满屏幕。125%/150%/225% 缩放下明显。

### 原因

Tauri/tao 提供两套尺寸 API，**语义不同**：

| API | 含义 |
|-----|------|
| `window.inner_size()` | **客户区**（去掉边框与标题栏） |
| `window.outer_size()` | **外框**（含边框与标题栏） |
| `window.set_size(LogicalSize)` | tao 的 `set_inner_size` → 设**客户区** |
| `window.set_outer_size(...)` | 设外框 |

保存用 `inner_size()` 恢复用 `set_size()` —— 同口径，正确。

保存用 `outer_size()` 恢复用 `set_size()` —— **混用**，每次开关累积一圈边框（本机 1600×900 下边框为 +16×9 px）。

### 规则

**保存与恢复必须统一到客户区，或统一到外框，切勿混用。**

推荐（客户区口径）：

```rust
// 保存
if let (Ok(position), Ok(size)) = (window.outer_position(), window.inner_size()) {
    current.window_x = Some(position.x);
    current.window_y = Some(position.y);
    current.window_width = Some(size.width);
    current.window_height = Some(size.height);
    let _ = settings.update(current);
}
```

```rust
// 恢复
if let Some((width, height)) = clamp_restore_size(stored.window_width, stored.window_height) {
    let _ = window.set_size(tauri::PhysicalSize::new(width, height));
}
```

### 上限钳制

历史脏数据可能存了超大尺寸，恢复后窗口会跑到屏幕外。加钳制：

```rust
const MAX_RESTORE_WIDTH: u32 = 1600;
const MAX_RESTORE_HEIGHT: u32 = 1200;

fn clamp_restore_size(width: Option<u32>, height: Option<u32>) -> Option<(u32, u32)> {
    let width = width?;
    let height = height?;
    if width == 0 || height == 0 {
        return None;      // 0 值视为无效，不恢复
    }
    Some((width.min(MAX_RESTORE_WIDTH), height.min(MAX_RESTORE_HEIGHT)))
}
```

### 逻辑 vs 物理像素

`LogicalSize` 会按 DPI 缩放换算，`PhysicalSize` 是真实像素。持久化用物理像素（`inner_size()` 返回的就是物理像素），恢复时也用 `PhysicalSize`，口径一致。

## 系统命令

### CREATE_NO_WINDOW

Windows 上通过 `Command` 执行 GUI 程序时，不加这个标志会闪黑框：

```rust
use std::os::windows::process::CommandExt;
command.creation_flags(0x0800_0000);
```

### 关机命令对比

| 方式 | 需管理员 | 可被 `shutdown /a` 取消 | 系统弹 UI | 结论 |
|------|---------|----------------------|-----------|------|
| `shutdown /s /t <秒>` | 否 | 是 | 长延迟时弹系统倒计时警告页 | ❌ 会与自定义界面冲突 |
| `shutdown /s /t 0 /f /c "<原因>"` | 否 | 否 | 否 | ✅ 归零瞬间执行 |
| `ExitWindowsEx(EWX_SHUTDOWN)` | 需 `SE_SHUTDOWN_NAME` | 否 | 系统接管 | ⚠️ 兜底用 |
| WMI `Win32_OperatingSystem.ShutDown()` | 通常需要 | 否 | 否 | ❌ 慢、权限高、易被安全软件误报 |

`/c "<原因>"` 会写入系统事件日志与用户提示，便于事后排查。

### 幂等取消

`shutdown /a` 在没有待取消任务时返回非 0，属于正常情况，**刻意忽略返回码**。

## 进程与文件锁

### 单实例互斥量

`tauri-plugin-single-instance` 用系统级 mutex。残留进程会占住它，导致新实例**静默 exit 0**（不是崩溃，很像「启动就闪退」）。

复制/覆盖 exe 前必须杀干净：

```powershell
taskkill /F /IM your-app.exe 2>$null
taskkill /F /IM msedgewebview2.exe 2>$null
```

WebView2 子进程也会锁住 exe（复制时报 Device or resource busy）。

### release 版无控制台

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
```

这行让 release 版不弹控制台 —— panic 时**完全静默**，没有任何输出，表现为「进程莫名消失」。

排查时用 debug 构建保留回溯：

```powershell
cargo build                    # debug 版，有控制台
.\src-tauri\target\debug\your-app.exe
```

## 调试探针

### 窗口标题判定

最轻量的前端渲染判据：读窗口标题。

- 正常渲染 → 标题是 `index.html` 的 `<title>`
- 白屏（Chromium 错误页）→ 标题是 `localhost`

```powershell
Start-Process -FilePath "C:\path\to\app.exe"
Start-Sleep -Seconds 8
(Get-Process | Where-Object { $_.ProcessName -like "yourapp*" } | Select-Object -First 1).MainWindowTitle
```

### UI Automation 探测

能枚举 WebView 内的元素，rect 还能验证尺寸：

```powershell
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::FromHandle($proc.MainWindowHandle)
$all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
                      [System.Windows.Automation.Condition]::TrueCondition)
foreach ($el in $all) { $el.Current.Name }
```

白屏时只有空 `Pane`；正常时有 `<title> - Web 内容` 节点。

注意：`Add-Type` 内联 C# 会被安全策略拦截，**写成 .ps1 脚本文件再执行**即可。

### 截图

`PrintWindow`（含 `PW_RENDERFULLCONTENT`）**拿不到 WebView2 的 GPU 合成内容**，只得到黑图。要用 `CopyFromScreen`（需交互桌面会话；无头环境报「句柄无效」）。

### DevTools 远程调试

`WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` **无效** —— wry 用 `set_additional_browser_arguments` 覆盖了它。唯一可行的是 WindowConfig 的 `additionalBrowserArgs`（需要单独的临时配置文件）。

接通 CDP 后有两个坑：

- WebView2 初始 target 是 `about:blank`，必须等 `location.href` 含 tauri 且 `root.children.length > 0` 之后再操作，否则误判
- 临时测试配置**绝不能**进发布产物（等同于给应用开本地调试后门），自检脚本要检查这一点

## 文件与编码

### settings.json 带 BOM

外部工具写入带 BOM 的内容会让 `serde_json` 解析失败。应用自己写出的文件不带 BOM（serde_json 序列化），但读取时仍应容错：解析失败回落默认值，而不是崩溃。

若出现「窗口尺寸莫名重置」，优先查该文件是否带 BOM。

### 控制台中文乱码

PowerShell 读 UTF-8 日志可能显示乱码（`椤甸潰鍔犺浇` = 页面加载）。这是控制台编码问题，不是文件问题 —— 实际文件是 UTF-8。读的时候指定编码：

```powershell
Get-Content -Encoding UTF8 $log
```
