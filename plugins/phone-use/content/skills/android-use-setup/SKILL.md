---
name: android-use-setup
description: 在 Pilkod 中把用户的 Android 手机或模拟器配置为 READY：用 android_doctor 检查 adb、USB 调试授权和 Mobilerun Portal，多设备时选择设备，经用户同意 AGPL-3.0 后下载并安装 Portal（支持用户自选下载镜像），开启其无障碍服务，处理国产 ROM 的 USB 安装与安全设置开关，最后用 android_ready 取得 READY；适用于安卓首次配置、换手机、Portal 失效或断线恢复。
---

# 把 Android 手机配置为 READY

Android 部分只用 `android_*` 工具，不调用 `pua_*`（那是 iPhone 的工具组），也不需要 Xcode、mobilerun CLI、Python 包或 API Key。手机通过 adb 连接，由手机上的 Mobilerun Portal 无障碍服务提供控件树和输入；Portal 不随插件分发，只在用户同意后从上游下载并按固定 SHA-256 校验。

## 先读状态

本对话首次使用安卓手机时，先调用只读的 `android_doctor`，按返回的 `next_step` 只补真实缺项，然后调用 `android_ready`。已有配置（选中的 serial、镜像设置、已安装的 Portal）默认复用，不重装、不重新授权。本对话已 READY 且通道未失效时直接继续手机任务，不为每项任务重跑 doctor。

`android_doctor` 与 `android_setup(action="status")` 返回同一份报告：adb 路径和版本、`devices`、`selected`、`device`、`portal`（`installed_version` / `accessibility_enabled` / `responding`）、`portal_release`（版本、许可证、来源 URL、SHA-256、大小、当前下载源）、`download` 进度和 `next_step`。按下表处理：

| 报告 / 错误 | 处理 |
|---|---|
| `adb_missing` 或 `adb.path=null` | 请用户安装 Android platform-tools（macOS：`brew install android-platform-tools`），或设置 `PHONE_USE_ADB` 为 adb 绝对路径。不要替用户执行 brew。 |
| `devices` 为空 / `no_device` | 请用户用数据线连接手机并在开发者选项打开「USB 调试」，或启动模拟器。 |
| `device_unauthorized` | 请用户在手机弹窗点「允许 USB 调试」（可勾选「始终允许」），完成后重跑 doctor。 |
| `device_offline` | 请用户重新插拔数据线或在手机上切换一次 USB 调试；不要循环重试。 |
| `multiple_devices` | 把 `devices` 中的型号和 serial 列给用户选择，再 `android_setup(action="select", serial=...)`。只有一台在线时自动选用。 |
| `portal.installed_version=null` | 进入下节「安装 Portal」。 |
| 已安装但 `accessibility_enabled=false` 或 `responding=false` | `android_setup(action="enable_portal")`。 |
| `portal_disabled` | 请用户在手机「设置 → 无障碍」里手动打开 Mobilerun Portal，再 `android_ready`。 |

serial、型号、镜像设置和下载缓存保存在用户本机状态目录（默认 `~/.local/share/phone-use/android`，可用 `PHONE_USE_ANDROID_STATE_DIR` 改），不写进源码或 Git。

## 安装 Portal（需要用户同意 AGPL）

Portal 是 droidrun 发布的 AGPL-3.0 开源 APK，安装后会在手机上开启一个无障碍服务。安装前必须用 Pilkod 的宿主提问工具问用户，说明：

- 将从 GitHub 下载 Mobilerun Portal（版本、大小取自报告的 `portal_release`），许可证 AGPL-3.0，源码地址见 `portal_release.source`；
- 安装后会开启它的无障碍服务，用于读取屏幕控件和输入文字；
- 下载源可以是 GitHub（默认）或用户自己信任的镜像，任何来源都会校验固定 SHA-256。

选项示例：「同意，从 GitHub 下载安装」「同意，但我要用镜像/本地 APK」「暂不安装」。工具返回、预选或之前的对话都不算同意；只有用户本次明确同意后，才调用 `android_setup(action="install_portal", accept_license=true)`。没有同意时调用会返回 `license_confirmation_required`，属于正常拦截，不要自行补 `accept_license=true` 绕过。用户拒绝就停在这里，说明安卓功能需要 Portal。

下载在后台进行，单次调用最多等待 `wait_seconds`（默认 45 秒）：

- 返回 `state="downloading"`：下载仍在继续，再调用同一个 `install_portal`（仍带 `accept_license=true`）即可接着等，不会重新下载。
- 返回带 `hint` 的慢速提示：把当前速度告诉用户，问是继续等，还是换成他信任的镜像或自行下载。
- `download_failed`：已下载部分会保留，重试会断点续传；也可以换镜像或用本地文件。
- `checksum_mismatch`：文件与固定版本不符，已丢弃；不要换个参数硬装。
- `download_in_progress`：另一个来源的下载还在跑，等它结束再换源。

镜像只由用户决定，不要自动切换，也不要替用户挑选第三方代理：

- `mirror="https://<前缀>/"`：一种 https 前缀代理，工具会拼成「前缀 + GitHub 原始 URL」；
- `mirror="https://.../com.mobilerun.portal-<版本>.apk"`：完整的 APK https 地址；
- `mirror="github"`：恢复默认 GitHub。

镜像设置会保存，`status` 和 `install_portal` 都可以带 `mirror`。目前清华 TUNA、中科大、阿里云等开源镜像站没有收录这个 APK；用户问起时如实说明，常见的 GitHub 前缀代理都是第三方维护的，是否使用由用户判断，校验 SHA-256 能保证文件不被篡改。用户已有 APK 时传 `apk_path`（绝对路径），同样要求 SHA-256 一致。

下载完成后工具自动执行 `adb install -r -g`、写入无障碍设置并等待 Portal 响应，然后返回最新状态。

## 国产 ROM 的额外开关

小米 MIUI / HyperOS、OPPO ColorOS、vivo OriginOS、华为 HarmonyOS 等可能要求用户在手机「开发者选项」里额外打开：

- 「USB 安装」/「通过 USB 安装应用」：`install_failed`（如 `INSTALL_FAILED_USER_RESTRICTED`）或手机弹出安装确认时，请用户打开开关或在手机上点「继续安装」，然后重试 `install_portal`。已下载的文件会复用。
- 「USB 调试（安全设置）」：`enable_portal` 写入无障碍设置失败、或打开后 Portal 不响应时，请用户打开这个开关；也可以请用户直接在「设置 → 无障碍 → 已下载的服务」里打开 Mobilerun Portal。
- 部分系统会在一段时间后自动关闭无障碍服务或后台限制 Portal：`portal_disabled` / `portal_unavailable` 再出现时调用 `enable_portal`，仍不行就请用户手动打开，并为 Portal 关闭省电限制。

这些设置都由用户本人在手机上完成。需要用户操作时用宿主提问工具等待，首个选项固定「已完成继续」，第二个可为「暂时无法完成」；不要通过 adb 擅自修改用户手机的系统设置（例如常亮、锁屏、开发者选项）。

## 取得 READY

`android_ready` 会在需要时点亮屏幕并尝试收起无密码锁屏，然后通过一次观察证明 Portal 可用。

- `ready=true`：返回 `device`、`portal.version`、`preview` 和 `observation`（默认含截图；文字任务可传 `screenshot=false`）。直接用这份 observation 规划下一步，不立即再 observe。`portal.update_available` 只是提示有固定新版本，不影响使用。
- `phone_locked`：手机有密码、图案或生物识别锁。预览已自动暂停为 `device_locked`。用宿主提问工具请用户解锁（首个选项「已完成继续」），用户确认后重跑 `android_ready`；成功会自动解除这次锁屏暂停。不要索取 PIN 或密码。
- `portal_missing` / `portal_disabled` / `portal_unavailable`：回到上面的安装或 enable 步骤。
- `adb_timeout` / `device_busy`：等两秒再试一次；仍失败就跑 doctor 看设备状态，不要连续重试。

只有 `ready=true` 才开始手机任务，然后按 `android-use` skill 执行。

## 实时画面

画面在 Pilkod 右侧的 Phone Use Mini App 面板，不在对话里。请用户自己打开（例如说「打开 Phone Use」）；`android_screen` 只暂停或恢复预览，不会弹出面板。安卓预览由 Mini App 用 `adb exec-out screencap` 轮询，真机约 2 帧/秒，模拟器稍快；它与控制通道互不依赖，预览空白不说明 READY 失败，也不需要为它重启任何东西。面板显示最近使用的那台手机（iPhone 或 Android）；底部刷新 / 主屏幕 / 截图按钮只给用户点，不是模型工具。
