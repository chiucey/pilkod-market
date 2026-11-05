# Tauri v2 开发模式与实战技巧

## 前后端契约

### 命令（Rust → 前端）

Rust 侧用 `#[tauri::command]` 暴露：

```rust
#[tauri::command]
pub fn start_countdown(
    app: AppHandle,
    timer: State<'_, TimerController>,
    total_seconds: u64,
    source_label: String,
    force_close: bool,
) -> Result<TimerSnapshot, String> {
    timer.start(&app, StartParams { total_seconds, source_label, force_close })
}
```

前端 invoke（**参数名用 camelCase**，Tauri v2 自动转换 snake_case↔camelCase）：

```ts
export function startCountdown(totalSeconds: number, sourceLabel: string, forceClose: boolean) {
  return invoke<TimerSnapshot>('start_countdown', { totalSeconds, sourceLabel, forceClose })
}
```

**必须核对**：`#[tauri::command]` 的函数名、参数名、参数个数、返回结构 与 `invoke` 调用完全一致。Rust 的 `State<'_, T>` 与 `AppHandle` 这类注入参数**不出现在**前端调用参数里。

### 事件（Rust → 前端）

Rust 侧用常量定义事件名，前端 import 同一个常量 —— 不要两边各写字符串字面量：

```rust
pub const TICK_EVENT: &str = "tick";
pub const STATE_CHANGED_EVENT: &str = "state-changed";
```

```ts
export const EVENT_TICK = 'tick'
export const EVENT_STATE_CHANGED = 'state-changed'
```

事件名里的 `-` 是合法的，但风格上统一用小写连字符。

### 序列化约定

Rust 侧结构体加 `#[serde(rename_all = "camelCase")]` 让字段名与前端类型一致：

```rust
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct TimerSnapshot {
    pub total_ms: u64,
    pub remaining_ms: u64,
    pub state: TimerState,
}
```

枚举同理：

```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TimerState { Idle, Running, Warning }
```

## 状态机与倒计时

### 计时基准

用 `std::time::Instant`（单调时钟）而非 `SystemTime` —— 系统时间被 NTP 调整或用户手动改会导致倒计时跳变：

```rust
let start = Instant::now();
// 剩余 = total_duration.saturating_sub(start.elapsed());
```

### 真值放在 Rust 侧

前端不要自己维护一份倒计时（双计时器必然漂移）。Rust 每秒发 `tick` 事件，前端订阅后用 `requestAnimationFrame` 在两次 tick 之间做平滑插值渲染：

- 逻辑：每秒更新一次真值
- 视觉：rAF 插值，60fps 平滑

### 失效机制

状态变更时用 `generation` 计数使旧的异步任务失效，避免「取消后旧 tick 又把界面改回运行中」：

```rust
let generation = shared.generation.load(Ordering::SeqCst);
if generation != shared.generation.load(Ordering::SeqCst) { return; }  // 已失效，丢弃
```

## Windows 系统调用

### 关机/重启

**不要**用 `shutdown /s /t <秒>` 把长倒计时交给系统 —— 系统会弹自己的蓝色倒计时警告页，与自定义界面冲突，用户看到两套倒计时。

正确做法：应用自己计时（Instant），归零瞬间执行立即关机：

```rust
#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;

fn hidden_command(program: &str) -> Command {
    let mut command = Command::new(program);
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(CREATE_NO_WINDOW);
    }
    #[cfg(not(target_os = "windows"))]
    { let _ = &mut command; }
    command
}
```

`CREATE_NO_WINDOW` **必须加**，否则每次调用闪一个黑框（Windows 上非常刺眼）。

取消用 `shutdown /a`（幂等，没有待取消任务时返回非 0，**刻意忽略返回码**）。

### 权限

Windows 客户端默认把「关闭系统」权限授予 Users 组，普通用户即可调用 `shutdown /s`。**不要**申请管理员权限（会触发 UAC 弹窗，且域环境/GPO 下反而可能失败）。

不要用需要提权或易被安全软件误报的手段：PowerShell 脚本、WMI `Win32_OperatingSystem.ShutDown()`、`net stop`、改注册表策略。

### 失败处理

命令返回非 0 退出码必须**可感知**，不能静默失败：

```rust
if output.status.success() { Ok(()) } else {
    Err(ShutdownError::new(format!("系统拒绝了关机请求（退出码 {:?}）", output.status.code())))
}
```

前端据此弹错误提示并写日志。

## 托盘常驻

### API 位置（v2 已并入主 crate）

```rust
use tauri::tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState};
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::image::Image;
```

### 创建

```rust
let icon = TrayIconBuilder::with_id("main-tray")
    .icon(Image::from_bytes(include_bytes!("../icons/tray.png"))?)
    .tooltip("标题")
    .menu(&menu)
    .on_menu_event(move |app, event| match event.id().as_ref() {
        MENU_SHOW => show_main_window(app),
        MENU_CANCEL => on_cancel(app),
        MENU_QUIT => on_quit(app),
        _ => {}
    })
    .on_tray_icon_event(|tray, event| {
        if let TrayIconEvent::Click { button: MouseButton::Left, button_state: MouseButtonState::Up, .. } = event {
            show_main_window(tray.app_handle());
        }
    })
    .build(app)?;
```

注意 `TrayIconBuilder` 是 **builder 模式**，`on_tray_icon_event` 直接挂在 builder 上（不是运行期 setter）。

### 关闭窗口 = 隐藏到托盘

```rust
.on_window_event(|window, event| {
    if let WindowEvent::CloseRequested { api, .. } = event {
        api.prevent_close();   // 阻止真正关闭
        let _ = window.hide();  // 隐藏到托盘，进程仍在
    }
})
```

**这是「关窗不中断任务」的关键**。若用户要求「关窗即退出」，则去掉 `prevent_close()` 并在退出前做清理。

### 托盘退出需要二次确认

倒计时进行中时，托盘「退出」不应直接退出（会静默丢掉用户的计划）。做法是发事件让前端弹确认：

```rust
if timer.is_running() {
    let _ = app.emit(REQUEST_QUIT_EVENT, ());
    show_main_window(app);   // 唤起窗口让前端弹窗
} else {
    app.exit(0);
}
```

## 单实例

```rust
.plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
    show_main_window(app);   // 第二次启动只唤起已有窗口
}))
```

该插件是纯 Rust 实现，**没有 JS API**，所以 capabilities 里**不需要** `single-instance:default`（加了会报错）。

## 系统通知

```rust
use tauri_plugin_notification::NotificationExt;
app.notification()
    .builder()
    .title("标题")
    .body("正文")
    .show()?;
```

通知权限在 capabilities 里写 `"notification:default"`。通知失败应**静默降级**为应用内提示，不要因通知失败影响主流程。

## 持久化

用 `tauri-plugin-store`：

```rust
.plugin(tauri_plugin_store::Builder::new().build())
```

结构体序列化存储。**注意**：若文件被外部工具写入带 BOM 的内容，`serde_json` 解析会失败。应用自己写出的文件不带 BOM，但读取时应容错（解析失败回落默认值而非崩溃）。

**运行态通常不要持久化**：比如「倒计时进行中」不应持久化，否则重启应用会突然开始关机。用户设想的「重启后继续」通常只是「记住上次用的时长/单位」。

## 前端主题变量化

多主题必须全部走 CSS 变量，组件里不写死颜色：

```css
:root {                    /* 浅色（默认） */
  --bg-app: #f4f6fb;
  --bg-card: #ffffff;
  --text-primary: #0f172a;
  --primary: #3b82f6;
  --primary-end: #06b6d4;
  --danger: #ef4444;
  --ring-track: #e2e8f0;
  color-scheme: light;
}
[data-theme='dark'] { /* 深色 */ }
[data-theme='eye-care'] { /* 护眼色：米黄底 + 墨绿字 */ }
```

主题挂到根元素：

```ts
useEffect(() => {
  document.documentElement.dataset.theme = settings.theme
}, [settings.theme])
```

SVG 里的颜色也能用变量：

```tsx
<stop offset="0%" stopColor="var(--primary)" />
<stop offset="100%" stopColor="var(--primary-end)" />
```

组件里**不要**出现 `settings.theme === 'light' ? '#E2E8F0' : '#1E293B'` 这类判断 —— 应该让 CSS 变量统一接管。

## i18n

文案全部外置到 `locales/zh-CN.json` / `locales/en-US.json`，组件内不硬编码用户可见文案。

让 TS 在编译期校验键集一致：

```ts
import zhCN from '../locales/zh-CN.json'
import enUS from '../locales/en-US.json'

export type MessageKey = keyof typeof zhCN
type Dictionary = Record<MessageKey, string>
const DICTIONARIES: Record<Locale, Dictionary> = {
  'zh-CN': zhCN as Dictionary,
  'en-US': enUS as Dictionary,   // 漏译/多译在 tsc 阶段就报错
}
```

动态 key 不要用模板字符串拼接（会逃过类型检查），改用显式映射表：

```ts
export const PRESET_MESSAGE_KEYS: Record<string, MessageKey> = {
  p5m: 'preset.5m',
  p10m: 'preset.10m',
}
```

## 环形进度（内联 SVG）

固定规格：viewBox `0 0 240 240`、圆心 (120,120)、半径 113、线宽 14。

```tsx
const RADIUS = 113
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const progress = totalMs > 0 ? Math.min(1, Math.max(0, remainingMs / totalMs)) : 0
const dashOffset = CIRCUMFERENCE * (1 - progress)

<circle cx={120} cy={120} r={RADIUS} fill="none"
        stroke="var(--ring-track)" strokeWidth={14} />
<circle cx={120} cy={120} r={RADIUS} fill="none"
        stroke={`url(#${gradientId})`} strokeWidth={14}
        strokeLinecap="round"
        strokeDasharray={CIRCUMFERENCE}
        strokeDashoffset={dashOffset}
        transform="rotate(-90 120 120)" />   {/* 12 点方向起始 */}
```

进度末端光点（现代感细节）：

```tsx
const angle = (progress * 360 - 90) * (Math.PI / 180)
const dotX = 120 + RADIUS * Math.cos(angle)
const dotY = 120 + RADIUS * Math.sin(angle)
```

渐变 id 用 `useId()` 生成，避免多个实例冲突。

## 交互防误触

危险操作（关机、删除、支付）必须**两步确认**：

1. 点选只是**选中 + 回填输入框**，不执行
2. 显式点主按钮才执行

二次确认弹窗的**默认焦点必须落在安全选项**（「继续倒计时」而非「确定取消」）：

```tsx
<Dialog.Content onOpenAutoFocus={(event) => {
  event.preventDefault()        // 阻止 Radix 默认聚焦
  keepRef.current?.focus()      // 显式聚焦安全项
}}>
```

Enter 键会触发焦点所在按钮，所以焦点落在安全项上就等价于「Enter = 继续倒计时」。

## 常驻自检日志

把「运行时到底加载了什么」做进日志，比临时加诊断代码再重编译一轮高效得多：

```rust
// lib.rs
.on_page_load(|webview, payload| {
    log::info(&format!("页面加载：{}", payload.url().as_str()));
})
```

```rust
// commands.rs —— 前端 ready 时
let result = webview.eval("document.getElementById('root')?.children.length ?? -1");
log::info(&format!("前端就绪：url={url} root_children={result}"));
```

以后再出白屏，日志里直接能分辨是 devUrl 误构建（url 是 localhost:1420）还是前端崩了（root_children=-1）。
