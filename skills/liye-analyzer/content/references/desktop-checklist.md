# 桌面问题排障清单

> 麒麟桌面 / 统信 UOS 桌面 / 通用 Linux 桌面（GNOME / KDE）通用思路。
> 桌面问题通常需要"日志 + 复现"双线分析；sosreport 不收集用户态日志（`~/.log/`），
> 必要时让用户手动提供。

## 一、显示栈（Display Server）

### Xorg
- 日志：`var/log/Xorg.0.log` 或 `var/log/Xorg.0.log.old`
- 关键错误：
  - `(EE) No screens found` → 显卡驱动问题
  - `(EE) Failed to load module` → 驱动未安装
  - `(EE) NVIDIA` / `(EE) amdgpu` → 厂商驱动问题
  - `Cannot run in framebuffer mode` → 启动模式错误
- **麒麟桌面 + 飞腾**：`xorg.conf` 看 `Driver` 字段（`modesetting` / `hygon` / `phytium`）

### Wayland
- 默认日志在 journald：`journalctl -u plasmashell.service`（KDE）或 `gnome-shell`
- 麒麟 UKUI 部分组件仍在 XWayland：`$DISPLAY=:0` 的应用可能是 XWayland 模式
- **Wayland 黑屏**：`WAYLAND_DEBUG=1` 启动（需要用户配合）

## 二、显卡驱动

### 国产芯片
- **鲲鹏 + 景嘉微**：`dmesg | grep jm` 或 `lsmod | grep jm` → 景嘉微驱动
- **飞腾 + 飞腾自研 GPU**：`/dev/dri/`、`/sys/class/drm/`
- **海光 + AMD**：`amdgpu` 内核驱动

### 通用
- **NVIDIA**：`nvidia-smi` 输出（sos 不一定采集） / `var/log/nvidia-installer.log`
- **AMD**：`amdgpu` 驱动 + `dmesg | grep amdgpu`
- **Intel**：`i915` 驱动

### 关键日志位置
- 显卡驱动错误：`dmesg | grep -i -E 'drm|amdgpu|nvidia|i915'`
- 显卡状态：`/sys/class/drm/card*/` 下的 `uevent` / `status`

## 三、桌面环境

### 麒麟 UKUI
- 日志：`journalctl -u ukui-*`（部分服务在 `usr/lib/systemd/user/`）
- 配置：`etc/xdg/ukui/`
- 故障模式：UKUI 启动失败 → 检查 `ukui-session.service`、session dbus

### UOS DDE
- DDE 服务：`dde-session-loader.service`、`dde-dock.service` 等
- 日志：`journalctl -u dde-*`
- 部分组件在用户态（`~/.log/deepin/`），sosreport 不收集

### GNOME / KDE（通用）
- GNOME：`gnome-shell` 日志在 journald
- KDE：`plasmashell.log`、`kwin.log`（部分在用户态）

## 四、输入法

- **fcitx5**（麒麟/UOS 默认）：`journalctl -u fcitx5*`
- **ibus**：`journalctl -u ibus`
- 配置：`~/.config/fcitx5/`、`~/.config/ibus/`
- 故障：输入法不显示 → 检查 `XMODIFIERS`、`GTK_IM_MODULE`、`QT_IM_MODULE`

## 五、用户态服务失败

- `systemctl --user --failed`（需用户态视角，sosreport 可能不收集）
- 替代：`var/log/user.log` 或 journald 按 user slice 过滤：
  - `journalctl _UID=<uid> -p err`

## 六、桌面常见故障模式

| 现象 | 优先排查 |
|------|----------|
| 桌面进不去（黑屏） | `Xorg.0.log` / Wayland session 启动失败 / 显卡驱动 |
| 桌面卡顿 | GPU 驱动、compositor（KWin / mutter）、swap、IO |
| 应用启动后闪退 | XWayland 兼容、缺失库（`ldd`）、显卡驱动 |
| 字体显示异常 | `etc/fonts/conf.d/`、`fc-cache`、fontconfig |
| 中文输入法失效 | fcitx5/ibus 服务、dbus、environment vars |
| 音频无声 | `pulseaudio --check` / `pipewire` 服务、`alsa` 状态 |
| 屏幕撕裂 | compositor 关闭、vsync、显卡驱动参数 |
| Wayland 黑屏 | `WAYLAND_DEBUG`、`XWayland` 配置 |
| 远程桌面（XRDP / VNC） | `xrdp.log`、`var/log/xrdp-sesman.log` |

## 七、复现建议（让用户提供的信息）

sosreport 不足以定位时，建议用户额外提供：
- 复现时间点（精确到分钟）
- 当时的操作（点了什么）
- `~/.log/` 下的桌面日志
- `journalctl --since "2026-08-03 10:00" --until "2026-08-03 10:30"` 输出
- 必要时：`Xorg.0.log`（桌面环境） / `~/.xsession-errors`（旧的错误汇总）
