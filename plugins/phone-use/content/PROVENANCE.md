# 来源与改动记录

本插件 0.5.0 起由 `iphone-use` 改名为 `phone-use`，在 iPhone 部分之外新增 Android 部分。iPhone 部分的来源见下文“上游”，Android 部分见“Android 部分”。

## 上游（iPhone 部分）

| 项 | 值 |
| --- | --- |
| 项目 | https://github.com/zhongerxin/iPhone-use |
| 许可证 | MIT，Copyright (c) 2026 ZHONG XIN（原文见 [LICENSE](LICENSE)） |
| 版本 | 0.3.13 |
| Commit | `c103990` |

Mini App 适配（`miniapp/`、`package.json`、`phone-use.mcp.json`、`icon.png` 以及 Python 与 skill 中的画面归属改动）来自基于上游 0.3.8 的本地 MiniMax Code 移植 0.4.0。本版本把这些改动重新应用到上游 0.3.13。

## 原样保留的上游文件（iPhone 部分）

`server/`、`skills/`、`scripts/phone.py`、`scripts/update_app_catalog.py`、`assets/phone-screen.html`、`LICENSE`、`THIRD_PARTY_NOTICES.md`、`ANALYTICS.md`、`CHANGELOG.md`。除下文列出的改动外，内容与上游一致。

## MiniMax 改动

- **埋点**：删除 `server/posthog.json`（上游随包的 PostHog 写入 token）；`server/analytics.py` 改为默认关闭，只有 `IPHONE_USE_ANALYTICS=1` 才启用，`DO_NOT_TRACK` 始终强制关闭；MCP 配置设置 `IPHONE_USE_ANALYTICS=0`。
- **画面**：`server/wda_screen.py` 在 `IPHONE_USE_SCREEN_OWNER=miniapp` 或预览租约有效时不打开第二路预览流；`server/iphone_use.py` 新增 `--screen-action refresh|home|screenshot`，并把画面说明指向 Mini App。
- **包目录稳定性**：iPhone / Android MCP 与 Mini App 工具栏以 `python3 -B` 启动；`scripts/phone.py` 在导入本地模块前禁用字节码写入，避免运行时缓存改变 Host 校验的插件包摘要。
- **USB 辅助程序**：`wda_setup.py` 的 forward 与 `wda_screen.py` 的回退预览都改用随包 `miniapp/node/usb.bundle.cjs`，删除运行时 `npm ci` 与 `tooling/` 目录，环境检查不再要求 npm。
- **Skill**：去掉 Codex 专属的工具名与内嵌 widget 说明，改为 MiniMax Code Mini App 面板的说明。
- **版本**：MCP serverInfo 与资源 URI 使用插件版本（当前 0.5.2）。
- **改名**：插件 ID、目录、MCP 配置文件改为 `phone-use`。iPhone 的内部标识保持不变（MCP 服务名 `iphone_use`、工具前缀 `pua_`、状态目录 `~/.local/share/iphone-use`、环境变量 `IPHONE_USE_*`、skill `iphone-use` / `iphone-use-setup`），已有配置不需要迁移。

## 未随包分发

上游的 `doubao/`、`workbuddy/`、`experiments/`、`ui/` 源码、`.codex-plugin/`、`.agents/`、`.github/`、根目录 `plugin.json` / `mcp.json` / `.mcp.json`、`assets/iphone-use-demo.png`、`assets/icon.svg`，以及 `scripts/` 中的安装、注册、打包、benchmark、smoke、截图 UI 检查脚本与 PostHog 仪表盘定义。

## 构建产物

`miniapp/node/usb.bundle.cjs` 与 `miniapp/node/licenses/` 由仓库 `sources/phone-use/scripts/build-usb-bundle.mjs` 使用锁定的 esbuild 0.25.12，从 `sources/phone-use/package-lock.json`（appium-ios-device 3.1.24，shell-quote 覆盖为 1.11.0）生成。`npm run check:bundle` 会重建并逐字节比对。`sharp` 不打包。

WebDriverAgent 16.14.0（BSD，commit `d17782422d55ff1e5e0ceb74eb1fd509cc0c35b6`）只在用户执行配置时从 GitHub 克隆，不随包分发。

## Android 部分

MiniMax 自行编写，许可证同插件（MIT）。参考项目如下：

| 项目 | 许可证 | 版本 | Commit | 用途 |
| --- | --- | --- | --- | --- |
| [droidrun/mobilerun](https://github.com/droidrun/mobilerun) | MIT | 0.7.0（PyPI `mobilerun` 0.7.0） | `3018561`（tag `v0.7.0`） | 参照其 Portal 客户端实现协议，未复制源码 |
| [mobilerun-core-local](https://pypi.org/project/mobilerun-core-local/0.6.3/) | MIT | 0.6.3（PyPI） | —（GitHub 仓库未公开，以 PyPI 发布包为准） | 同上 |
| [droidrun/mobilerun-portal](https://github.com/droidrun/mobilerun-portal) | AGPL-3.0 | v0.7.25 | `d4cb7d6`（tag `v0.7.25`） | 手机端无障碍服务，用户确认后下载，不随包分发 |

- `server/android_adb.py`、`server/android_use.py`：标准库实现的 stdio MCP 服务 `android_use`（工具前缀 `android_`）。通过用户自己的 `adb` 与手机上的 Mobilerun Portal 无障碍服务通信，只走 `content` 命令（content provider），不开 TCP 端口，不内置 LLM，不需要 API Key，不采集埋点。
- Portal 协议（content provider URI、无障碍服务组件名、键盘输入绑定、无障碍树结构）参照 MIT 许可的 [mobilerun-core-local](https://github.com/droidrun/mobilerun-core-local) 0.6.3 与 [mobilerun](https://github.com/droidrun/mobilerun) 实现，没有复制其源码，也不依赖其 Python 包。许可证原文见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
- Mobilerun Portal APK（AGPL-3.0）不随包分发。`android_setup(action="install_portal", accept_license=true)` 在用户确认许可证后，从上游 GitHub Releases（或用户配置的镜像）下载固定版本 v0.7.25，强制校验大小 53,610,015 字节与 sha256 `6dc9e8327fcaecf3ba0ad5054f19357d832fc923763fb6c9d1ab09f79e3d3297` 后再 `adb install`。
- `miniapp/node/android-frame.mjs`：raw `screencap` 解码、整数倍降采样与 PNG 编码，改写自 MiniMax 早前的 mobilerun 插件分支中的零依赖 PNG 工具（MiniMax 自有代码）。
- `miniapp/node/screen-hub.mjs`、`server.mjs`、`miniapp/client/`：面板按最近使用的手机切换 iPhone / Android，Android 画面由 Mini App 轮询 `adb exec-out screencap` 生成；工具栏按钮在 Android 下调用 `server/android_use.py --screen-action`。
- `server/wda_screen.py` 的 `ScreenHub`（暂停与手势标记）被 Android 服务复用，写在 Android 自己的状态目录 `~/.local/share/phone-use/android`。
