---
name: android-use
description: 用 Phone Use 的 android_* MCP 工具在 Pilkod 中操作用户的 Android 手机或模拟器：本对话首次使用先按 android-use-setup 取得 android_ready；之后用控件树选择器（text / desc / id / type）点击、输入、滑动、按键、启动 App，默认乐观执行、下一步需要页面时再随动作取观察，只对关键结果显式验收；说明设备像素坐标、截图换算、约 1 秒的单次调用延迟、锁屏与密码认证接管以及右侧 Mini App 实时画面。
---

# 用 android_* 工具完成 Android 任务

先确认用户要交付的结果和完成条件。只使用 `android_*` 工具；`pua_*` 是 iPhone 的工具组，不要对安卓手机调用。设备是 iPhone 还是 Android 不清楚时，先问用户或看 `android_doctor` 是否连着安卓设备。

## READY

本对话首次使用安卓手机、还没有本对话的 `ready=true` 时，按 `android-use-setup` 执行：`android_doctor` → 补缺项 → `android_ready`。之前聊天成功、插件已安装、Mini App 有画面，都不能代替本对话的 READY。已 READY 且没有出现设备或 Portal 错误时直接继续，不为每一步重跑 ready。

`android_ready` 默认附带截图；纯文字任务可传 `screenshot=false`。成功后直接用返回的 `observation` 规划第一步。

## 延迟与节奏

每次读取控件树都要经过 Portal 的 content provider，真机约 1 秒一次（模拟器更快），截图另加数百毫秒。因此：

- 动作默认 `observe="none"`，已知目标和已知路径直接连续执行，不为每次点击专门再 observe 一次。
- 下一步需要看新页面时，在这次动作里设 `observe="tree"`（或需要视觉时 `"both"` / `"screenshot"`），用返回的嵌套 `observation` 同时判断上一步是否生效和规划下一步，省掉单独的 observe 回合。
- 只找一个目标用 `android_find`，等待加载用 `android_wait`（默认 5 秒，最多 20 秒，`gone=true` 等它消失），不要反复拉整棵树。
- `android_launch_app` 会返回 `foreground_package` / `foreground_matches`；`false` 时多半是启动页、权限弹窗或系统转接页，带一次观察确认即可。

工具返回正常只代表该调用执行了一次，不代表业务完成；最终关键结果（发送、提交、设置值、读取到的文本、交付文件）需要实际观察证据。

## 观察结果怎么读

`observation` 包含 `app`（`package` / `activity` / `label`）、`viewport`（设备像素宽高）、`nodes`，键盘弹出时有 `keyboard_visible`，输入框有焦点时有 `focused`。每个节点：

- `type`：短类名，如 `TextView`、`Button`、`EditText`、`ImageView`。
- `text`、`desc`（content description，图标常用）、`hint`；与 `text` 相同的 desc 不重复给出。
- `id`：resource id 的短名（`com.x:id/search` 显示为 `search`）。
- `rect`：`[x, y, width, height]`，**设备像素**。
- 标志只在为真时出现：`clickable`、`long_clickable`、`editable`、`scrollable`、`checkable`、`checked`、`selected`、`focused`、`password`；`enabled=false`、`visible=false`、`in_viewport=false` 只在为假时出现。

默认只返回可见节点、最多 200 个；`truncated=true` 时有 `total_nodes`。树被截断或目标不在树里，不能证明它不存在：可以滑动、缩小范围用 `android_find`，或看截图。

截图以图片块随结果返回，已缩放：**图像像素 × `image.pixel_scale` = 设备像素**。宿主没有显示图片时打开 `image.path`。不要按 Mac 屏幕或 iPhone 点来换算。

## 选择器

`selector` 的字段从刚取得的节点里抄：`text` / `text_contains`、`desc` / `desc_contains`、`label` / `label_contains`（匹配 text、desc 或 hint 任一项）、`id`（短名或完整 `pkg:id/name`；`resource_id` 是别名）、`type`，以及 `enabled` / `clickable` / `editable` / `scrollable` / `checked`。只匹配可见节点；文字匹配区分大小写。

- 多个分开的匹配返回 `ambiguous_target` 和候选列表（含 `tap_point` 与 `index`），加 `index` 或更具体的字段再调一次。
- 容器和它自己的文字子节点同时命中时，取最内层那个；点击位置是节点在屏幕内可见部分的中心。目标文字本身不可点时，点它所在的行或按钮通常同样生效；没生效就改点 `clickable` 的父行。
- `not_found` / `ambiguous_target` 之后不要连换多个选择器盲试：取一次截图看实际页面，再用选择器或 `x` / `y`（设备像素）点击。
- `not_on_screen`：目标在屏幕外，先 `android_swipe` 把它滑进来。

## 动作

- `android_tap`：`selector` 或 `x` / `y`；`duration_ms>=500` 为长按。
- `android_swipe`：`direction` 是手指移动方向，`up` 显示后面的内容；可传 `region`（设备像素）限定列表区域、`distance`（0.1–1，默认 0.6），或用 `x/y → to_x/to_y` 指定起止点。滑动后没有新内容不代表列表已到底，需要结合观察判断。
- `android_type_text`：通过 Portal 键盘输入完整 Unicode 文本（中文无需切输入法）。带 `selector` 会先点该输入框；不带时输入到当前焦点框，焦点稍晚到达也会等待约 2.5 秒。`replace=true` 先清空，`submit=true` 输入后按回车，`verify=true` 回读焦点框内容。文本含换行时需要 `allow_newlines=true`。`no_focused_field` 时先点输入框再输。
- `android_press_key`：`back`、`home`、`recent`、`enter`、`delete`、`tab`、`escape`、`search`、`volume_up` / `volume_down` 等；`long_press=true` 长按。
- `android_launch_app`：按包名启动。不知道包名时先 `android_apps(query="微信")` 按名称或包名搜索；默认只列第三方 App，系统 App 加 `include_system=true`。
- `android_install_apk`：只安装用户明确提供的本地 APK（如用户自己构建的测试包）。不要从网上下载任意 APK 来安装。

`action_executed` 为 false 的错误表示没有发出动作，可以修正参数后重试。结果带 `uncertain` 或 `text_entered="unknown"` 时，动作可能已经生效：先观察真实状态，**不要重放**输入、发送、提交或支付。

## 锁屏、密码与认证接管

- `phone_locked`：预览已自动暂停（`device_locked`）。用 Pilkod 的宿主提问工具请用户解锁，首个选项固定「已完成继续」，第二个可为「暂时无法完成」；用户确认后重跑 `android_ready`，成功会自动解除这次锁屏暂停。
- App 要求密码、PIN、验证码、支付密码或指纹 / 人脸，或者焦点框是 `password=true` 的密码框：不要代填，也不要向用户索取凭据。先 `android_screen(action="pause")`，再用宿主提问工具请用户在手机上完成（首个选项「已完成继续」）。等待期间不做手机动作、读取或截图。用户确认后 `android_screen(action="resume")`，再取一次观察，按新状态继续。
- 支付、删除、发送给他人、修改账号或系统设置等对外可见或不可撤销的操作，执行前单独向用户确认。

## 实时画面

画面在 Pilkod 右侧的 Phone Use Mini App 面板，不在对话里。用户想看时请他打开面板（例如说「打开 Phone Use」）；`android_screen` 只暂停或恢复，不会弹出面板。安卓预览约 2 帧/秒，由面板自己用 screencap 轮询，和控制通道互相独立：预览慢或空白不说明动作失败，也不需要为它重跑 ready、截图或 observe。面板底部的刷新 / 主屏幕 / 截图按钮只供用户点击；用户点过后页面可能变化，按下一次观察到的实际状态继续。

## 出错时

| 错误 | 处理 |
|---|---|
| `device_not_found` / `device_offline` / `no_device` | 设备断开。请用户检查数据线和 USB 调试，再按 `android-use-setup` 跑 doctor。 |
| `portal_unavailable` / `portal_disabled` / `portal_error` | Portal 被系统关闭或卡住：`android_setup(action="enable_portal")`，再 `android_ready`。 |
| `adb_timeout` / `device_busy` | 等两秒重试一次只读调用；动作类先观察再决定，不盲目重放。 |
| `type_text` 返回 `uncertain` | Portal 输入中途失败；先观察输入框当前内容，再决定是否重新输入。 |
| `app_not_found` / `launch_failed` | 用 `android_apps` 核对包名，或请用户确认 App 已安装。 |
| `wait_timeout` | 页面没有在时限内达到预期，取截图看实际情况。 |
| `preview_paused` | 用户正在接管手机，等用户确认完成。 |

同一错误连续出现两次就停下来诊断（doctor / 截图），不要循环重试。完成后用观察证据向用户汇报结果。
