# Phone Use（`phone-use`）

让 Pilkod 的 Agent 操作一台真实手机，用于移动端 App 自动化开发与验证：打开正在开发的 App、点击、输入、滑动、读取界面树并核对结果。右侧 Mini App 面板实时显示手机画面，iPhone 和 Android 共用同一个面板，自动显示最近使用的那台。

| | iPhone | Android |
| --- | --- | --- |
| MCP 服务 | `iphone_use`（工具前缀 `pua_`） | `android_use`（工具前缀 `android_`） |
| Skill | `iphone-use`、`iphone-use-setup` | `android-use`、`android-use-setup` |
| 连接方式 | USB + 你自己签名的 WebDriverAgent | adb + Mobilerun Portal 无障碍服务 |
| 宿主要求 | macOS + Xcode | 装有 adb 的 macOS / Linux |
| 参考项目 | 移植自 ZHONG XIN 的 MIT 项目 [iPhone-use](https://github.com/zhongerxin/iPhone-use) 0.3.13（commit `c103990`） | Pilkod 自行编写，Portal 协议参照 MIT 的 [mobilerun](https://github.com/droidrun/mobilerun) 0.7.0（commit `3018561`）与 [mobilerun-core-local](https://pypi.org/project/mobilerun-core-local/0.6.3/) 0.6.3；手机端使用 AGPL-3.0 的 [Mobilerun Portal](https://github.com/droidrun/mobilerun-portal) v0.7.25（commit `d4cb7d6`，不随包分发） |

来源与改动见 [PROVENANCE.md](PROVENANCE.md)。本插件 0.5.0 起由 `iphone-use` 改名而来；iPhone 的内部标识（服务名、工具、状态目录、环境变量、skill 名）保持不变，已有配置不需要迁移。

**埋点默认关闭。** iPhone 部分删除了上游随包的 PostHog token，`phone-use.mcp.json` 设置 `IPHONE_USE_ANALYTICS=0`，详见 [ANALYTICS.md](ANALYTICS.md)。Android 部分不采集任何埋点。

**Android 部分不内置 LLM，也不需要 API Key**：由会话里的 Agent 直接调用 `android_*` 工具操作手机。

## 运行要求

通用：

- `PATH` 上有 Python 3.9+（`python3`）和 Node.js 20.19+ / 22.12+ / 24+（`node`），运行时不需要 npm
- 支持 Mini App 的 Pilkod 桌面端

iPhone：

- macOS，安装完整 Xcode（不能只装 Command Line Tools），版本需支持手机的 iOS 版本
- 通过 USB 连接、已解锁并信任此电脑的 iPhone；iOS 提示时打开开发者模式
- 自己的 Apple 开发者团队（免费 Personal Team 可用于短期真机测试，描述文件通常 7 天过期）

Android：

- Android Platform Tools 中的 `adb`（`PATH`、`PHONE_USE_ADB`、`ANDROID_HOME` / `ANDROID_SDK_ROOT` 或 Homebrew 默认路径均可）
- Android 8.0+ 真机或模拟器；真机需打开开发者选项和 USB 调试，并在手机上允许此电脑调试
- 首次使用时需要联网下载 Mobilerun Portal APK（约 51 MB，AGPL-3.0），安装前会征求你的同意

Windows 上 MCP 服务不可用（依赖 `fcntl`）。非 macOS 上 iPhone 部分不可用，面板只显示 Android。

## 使用

在会话里可以这样说：

- 打开 Phone Use，显示我的手机画面
- 连接我的安卓手机，打开设置看看电池用量
- 用我的 Apple 开发者团队配置 iPhone，再打开我正在开发的 App 走一遍登录流程

Mini App 的画面路由是 `/screen`。

MCP 服务和 Mini App 工具栏通过 `python3 -B` 启动 Python，命令行 fallback 也会禁用字节码写入，避免在插件目录生成 `__pycache__/*.pyc`、改变包摘要并触发预览打开时的 `CANDIDATE_CHANGED`。若旧版本已出现该错误，请升级到 0.5.2 并重新加载插件；手机配置与状态目录继续复用。

## 首次配置：iPhone

Agent 按 `iphone-use-setup` 执行，主要步骤：

1. 每个会话首次 `pua_ready` 之前先调 `pua_setup(action="status")`。
2. 未配置时，用 `pua_doctor` 与 `pua_setup(action="discover")` 检查 Xcode 和 USB 设备。Xcode 账号由你自己登录，不要把 Apple 密码或验证码发到会话里。
3. 连接 iPhone，点“信任此电脑”；iOS 出现开发者模式、UI 自动化设置时按提示打开。
4. `pua_setup(action="fetch")` 把固定 commit 的 WebDriverAgent 克隆到状态目录；`configure` 保存 `udid`、`team_id` 和你能签名的 bundle id。默认本地端口 `18100`、设备端口 `8100`，预览流使用设备端口 `9100`。
5. 依次执行 `build`、`start`。`start` 使用随包 USB 转发程序 `miniapp/node/usb.bundle.cjs`，并启动 Xcode 测试 runner。
6. 服务可用后，`pua_ready(recover=true, screenshot=false)` 检查状态、会话、前台 App、视口与解锁。打开 Phone Use 面板查看画面；画面空白不代表控制通道断开。

运行时文件位于 `~/.local/share/iphone-use`（可用 `IPHONE_USE_STATE_DIR` 覆盖），包括设备配置、签名输入、构建产物、日志和共享预览状态，不在插件目录里。

## 首次配置：Android

Agent 按 `android-use-setup` 执行，主要步骤：

1. `android_doctor`（只读）检查 adb、设备、USB 调试授权、Portal 与无障碍服务。
2. 多台设备时由你选择，`android_setup(action="select", serial=...)` 保存。模拟器也可以。
3. Portal 未安装时，Agent 会先说明：它是 AGPL-3.0 的 Mobilerun Portal APK，从上游 GitHub 下载，装好后作为无障碍服务启用。你同意后才调用 `android_setup(action="install_portal", accept_license=true)`。
   - 下载固定版本 v0.7.25，校验大小与 sha256，校验失败会丢弃；中断后再次调用会断点续传。
   - GitHub 慢时可传 `mirror`（以 `/` 结尾的 https 前缀代理，或直接给 `.apk` 的 https 地址），或设置 `PHONE_USE_PORTAL_MIRROR`。清华、中科大、阿里云等公共镜像目前都不同步这个项目，可用的只有个人维护的 GitHub 前缀代理；无论哪个来源都必须通过同一个 sha256 校验。
   - 小米、OPPO、vivo、华为等国产系统可能要求额外打开“USB 安装”“USB 调试（安全设置）”，或在手机上手动确认安装；无障碍服务被系统关闭时用 `android_setup(action="enable_portal")` 重新开启。
4. `android_ready` 检查设备在线、亮屏解锁、Portal 可用。熄屏时会唤醒；没有锁屏密码时自动解锁，有密码时暂停预览，请你在手机上解锁后再继续。

运行时文件位于 `~/.local/share/phone-use/android`（可用 `PHONE_USE_ANDROID_STATE_DIR` 覆盖），包括选中的设备、Portal 下载缓存、截图和共享预览状态。

Android 坐标统一为设备像素。真机上每次读取界面（Portal content 调用）约 1.2 秒，主要是 `app_process` 启动开销，所以动作默认不附带观察，需要时再请求。

## 画面与 Agent 如何分工

面板根据两个状态目录里谁最近被 MCP 使用来决定显示哪台手机，切换时会清空旧画面。

iPhone：

- Mini App 进程独占 MJPEG 预览。面板轮询期间写 `miniapp-screen-lease.json`，是预览端口唯一的 USB 客户端。
- MCP 服务是独立的 Python 进程。设置了 `IPHONE_USE_SCREEN_OWNER=miniapp` 时不打开预览端口；手机操作仍走控制端口和共享的 `operation.lock`。
- 面板上的刷新、主屏幕、截图按钮调用 `python3 server/iphone_use.py --screen-action refresh|home|screenshot`。主屏幕会抢 `operation.lock`，Agent 正在操作时返回“忙”，不会打断它。
- 暂停与手势标记写在 MCP 维护的 `screen-state.json` 中，由面板读取。`pua_screen(action="pause"|"resume")` 不会自动弹出面板，需要提醒用户打开 Phone Use。
- `miniapp.json` 没有 `mcpEndpoints`。Agent 的 MCP 是 `phone-use.mcp.json` 声明的 stdio 进程，不是页面内的 HTTP 服务。

Android：

- 面板可见且未暂停时，Mini App 进程运行 `adb -s <serial> exec-out screencap`（raw 格式，不在手机上压缩 PNG），在 Node 里按整数倍降采样到宽 540 左右并编码 PNG。最多 3 路交错抓取，起始间隔不小于 300ms；画面不变时不重复发送。实测真机（华为 OCE-AN10，1080x2376）约 1.8–2.6 fps，模拟器约 2.7 fps，达不到 iPhone MJPEG 的流畅度。
- 预览不发送任何输入；三个按钮调用 `python3 server/android_use.py --screen-action refresh|home|screenshot`，主屏幕同样遵守 `operation.lock`。
- 锁屏 / 认证暂停与手势标记写在 Android 状态目录的 `screen-state.json` 中，暂停期间不抓帧。

面板状态：连接中、实时、已暂停、已锁屏、认证中、未连接。手机未连接或预览暂停时，主屏幕和截图按钮不可用。

## Tested environment

0.5.0 的本地测试环境：macOS 26（arm64）、Node v24、Python 3.14、adb（Homebrew）。

- Android 真机：华为 OCE-AN10（HarmonyOS 4.2 / Android 12，1080x2376，无锁屏密码）。已跑通 doctor、多设备选择、Portal 下载（含中断续传与 sha256 校验）与安装、无障碍自动开启、READY（含熄屏唤醒）、应用搜索与启动、按 id / 文本点击、中文输入（追加 / 替换 / 回读）、滑动、等待、预览暂停 / 恢复、面板实时画面与三个按钮。
- Android 模拟器：sdk_gphone64_arm64（Android 14）。
- iPhone 部分代码只改了版本号和面板文案；本次测试时没有连接 iPhone，READY、WebDriverAgent 与实时画面沿用 0.4.1 的验证范围（同样未连真机）。

仓库 CI 在 Linux 上跑不依赖真机的检查：Python 单测、Mini App Node 入口测试、USB bundle 一致性检查。

## Data & access

**读取的文件**

- 插件目录内的文件（页面、USB bundle、`server/iphone_use.py`、`server/android_use.py`）。
- 配置完成后，读取 `~/.local/share/iphone-use/` 下的 `config.json`、`screen-state.json`、`device.json`。目录可用 `IPHONE_USE_STATE_DIR` 或 `WDA_STATE_DIR` 覆盖。
- 读取 `~/.local/share/phone-use/android/` 下的 `config.json`（serial、型号、adb 路径、最近使用时间）与 `screen-state.json`。目录可用 `PHONE_USE_ANDROID_STATE_DIR` 覆盖。
- 配置期间，MCP 还会读取状态目录中的 Xcode 工程文件，并通过 Apple 自带工具读取手机的开发者配对信息。

**写入的文件**

- 只有在 iPhone 的合法 `config.json` 存在且面板正在显示 iPhone 时，Mini App 才在状态目录写 `miniapp-screen-lease.json`，避免 MCP 再开一路预览流。写入方式是同目录临时文件加 rename。
- 面板按钮和所有 Agent 工具都通过 Python 服务写同一状态目录（配置、任务、日志、会话 ID、预览暂停文件、构建产物）。截图按钮会写 macOS 剪贴板，并使用复制后立即删除的临时 PNG。
- Mini App 不写 `context.dataDir`；持久状态都在上述共享目录，保证 MCP 进程与面板看到同一台手机。

**网络**

- 面板本身不发出站请求，预览数据来自 USB 设备或 adb。
- `android_setup(action="install_portal")` 在用户同意后从 `github.com/droidrun/mobilerun-portal` 的 Releases（或用户配置的镜像）下载 Portal APK。Android 部分没有其他出站请求。
- 埋点默认不访问 `us.i.posthog.com`，本包也不携带写入 token。
- `pua_setup(action="fetch")` 从 `https://github.com/appium/WebDriverAgent.git` 克隆固定 commit。
- `pua_apps` 在 `source=apple` 或 `source=auto` 且本地目录与设备上都找不到时，可能查询 Apple 公开搜索 API（`itunes.apple.com`）。

**Mini App 启动的进程**

- 面板可见、未暂停、宿主为 macOS 且 `config.json` 有 udid 时：`node miniapp/node/usb.bundle.cjs stream <udid> <mjpeg-port>`。参数以数组传递，udid 来自配置文件而不是页面。
- 面板显示 Android 且未暂停时：`<adb> -s <serial> exec-out screencap`，最多 3 个并发。adb 路径与 serial 来自 Android `config.json` 并做格式校验，不来自页面。
- 三个面板按钮：`python3 -B server/iphone_use.py --screen-action refresh|home|screenshot`，Android 下改为 `server/android_use.py`。

**MCP 服务在配置期间可能启动的进程**

- `node miniapp/node/usb.bundle.cjs forward <udid> <local-port> <device-port>`（只监听 `127.0.0.1`）
- `git`：获取固定版本的 WebDriverAgent
- `xcodebuild`：构建并运行测试 runner

**Android MCP 服务启动的进程**

- `adb`：`devices`、`shell`（`content`、`input`、`settings`、`am`、`pm`、`dumpsys`、`getprop`、`screencap`）、`install`、`exec-out screencap`

## 目录结构

```text
.pilkod-plugin/plugin.json    插件清单
phone-use.mcp.json             两个 stdio MCP：iphone_use（埋点关闭、Mini App 独占预览）与 android_use
package.json                   pilkod Mini App 声明
miniapp/miniapp.json           入口、/screen 路由，无 mcpEndpoints
miniapp/client/                实时画面页面
miniapp/node/server.mjs        Node 入口：start(context)
miniapp/node/screen-hub.mjs    iPhone MJPEG 与 Android screencap 预览、平台选择
miniapp/node/android-frame.mjs raw screencap 解码与 PNG 编码
miniapp/node/usb.bundle.cjs    随包 usbmux 转发与预览流（构建产物）
miniapp/node/licenses/         bundle 内依赖的许可证与清单
server/                        Python MCP 服务与配置流程（iphone_use.py、android_use.py 等）
skills/iphone-use/             iPhone 日常操作 skill
skills/iphone-use-setup/       iPhone 首次配置 skill
skills/android-use/            Android 日常操作 skill
skills/android-use-setup/      Android 首次配置 skill
assets/phone-screen.html       MCP 资源兼容页面（非右侧面板）
scripts/                       上游 CLI 与 App 目录更新脚本
```

## 开发与重建

构建与测试源码位于仓库 `sources/phone-use/`，不随插件分发：

```sh
cd sources/phone-use
npm ci --ignore-scripts
npm run build          # 重建 miniapp/node/usb.bundle.cjs 与 licenses/
npm run check:bundle   # 与已提交产物逐字节比对
npm test               # Mini App Node 入口测试 + Python 单测
```

## 许可证

[MIT](LICENSE)，Copyright (c) 2026 ZHONG XIN。Android 部分为 Pilkod 编写，同样以 MIT 发布。Mobilerun Portal（AGPL-3.0）不随包分发。第三方条款见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 与 `miniapp/node/licenses/`。
