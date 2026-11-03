# Blender 操作

仅在安装/更新扩展、从 Blender 再次导出，或用户要求后台搭白模时读取。

## 安装前置

任何 Blender 侧操作前必须运行随包安装器：

```bash
python3 "<技能目录>/scripts/install_extension.py"
```

必须同时看到 `Installed` 与 `Verified`。如果 Blender 正在运行，安装后请用户完全
退出并重启；重启前不得声称新扩展已生效，也不得用裸 `bpy` 绕过扩展。
当前随包扩展为 1.0.7；新导出 manifest 应为 schema v3 并含 `structure_evidence`。仍出现
schema v1/v2 表示 Blender 尚在使用旧扩展，需重新安装并完全重启。

安装器会从 `extension/minimax_h3-<版本>.zip` 选择最高 SemVer。自动检测不到
Blender 时传 `--blender <可执行文件路径>`；用户提供扩展包时传 `--archive <路径>`。
验证失败就停止 Blender 操作并报告稳定的错误摘要。

重启后，在 3D 视图按 N 打开「Pilkod」。剪贴板仍出现旧 fallback 说明旧模块
仍在内存中，需要重新安装并再次重启。

1.0.7 起，剪贴板只写用户可见的「Blender 白模渲染」触发语和 `preview_video.mp4` 完整路径。
不得写 Skill ID、插件安装目录、SKILL.md 本机路径或 manifest 路径。Skill 被市场运行时加载后，
自行读取视频同目录的 `manifest.json` 作为 preflight 结构侧车；fallback 收件夹也不生成
`instruction.txt` 或 `intent.txt`。

## 用户首次了解插件

简短介绍两种方式：

- Blender 内操作：侧栏「Pilkod」→ 选相机 → 渲染 → 打开 Pilkod 生成。
- 对话式：用户描述主体、动作、运镜和时长，由 M3 后台搭基本白模。

不要展开材质、色温和背景参数问卷；只让用户选择一键渲染或用一句话自定义外观。

## 对话式白模

1. 确认主体、动作、运镜和时长；默认按 24fps。
2. 用 `blender --background --python-expr` 创建基本体、动作关键帧和相机动画。
3. 复用已安装扩展：
   `from bl_ext.user_default.minimax_h3.services import preview_exporter`，调用
   `export_preview(..., export_mode="white_model")`。
4. 产物写入临时目录，先让用户确认白模，再进入主 Skill。

不打开或覆盖用户已有 `.blend`，除非用户明确要求。复杂资产超出基本体表达能力时，
建议用户在 Blender 内搭建后再发送。
