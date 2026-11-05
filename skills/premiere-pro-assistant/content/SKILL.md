---
name: premiere-pro-assistant
description: 当用户询问 Adobe Premiere Pro（PR）软件的使用方法、剪辑技巧、调色操作、特效制作、音频处理、导出设置、快捷键、常见问题解决等问题时使用。也适用于"如何用 PR 做..."、"Premiere Pro 怎么..."、"PR 剪辑教程"、"PR 调色技巧"等类型的查询。
---

# Adobe Premiere Pro 助手

专门服务于 Adobe Premiere Pro 专业视频编辑软件的智能助手技能。

## 核心能力

### 1. 面板导航
Premiere Pro 包含以下核心面板，根据用户问题识别对应功能：

| 面板 | 功能 | 触发关键词 |
|------|------|------------|
| **Project** | 素材管理、项目面板 | 导入素材、项目、媒体 |
| **Source Monitor** | 源监视器、预览素材 | 源监视器、预览 |
| **Program Monitor** | 时间线监视器、回放 | 节目监视器、回放 |
| **Timeline** | 时间线、剪辑轨道 | 时间线、轨道、剪辑 |
| **Effect Controls** | 效果控制、运动属性 | 效果控制、运动、关键帧 |
| **Essential Graphics** | 字幕、图形 | 字幕、标题、图形 |
| **Lumetri Color** | 调色板 | 调色、颜色、Lumetri |

### 2. 常用操作指南

#### 基础剪辑
- **创建项目**：File → New → Project → 命名 → OK
- **导入媒体**：File → Import 或快捷键 Ctrl+I
- **双击素材**：在 Source Monitor 打开预览
- **设置入点**：按 I 键设置入点
- **设置出点**：按 O 键设置出点
- **插入编辑**：按 , (逗号) 插入到时间线
- **覆盖编辑**：按 . (句号) 覆盖时间线内容
- **波纹编辑**：选中片段边缘拖拽自动调整后续片段

#### 高级剪辑技术
- **多机位编辑**：Sequence → Multi-Camera
- **嵌套序列**：选中序列 → 右键 → Nest
- **匹配帧**：按 F 键找到源素材对应位置
- **提升/提取**：Shift+Delete 执行提升，Alt+Shift+Delete 执行提取

#### 音频处理
- **音频轨道**：右键 Track → Add Tracks
- **增益调整**：Clip → Audio Options → Audio Gain
- **标准化音量**：Effect → Audio Adjustments → Normalize
- **关键帧**：在 Effect Controls 面板调整音量关键帧
- **淡入淡出**：拖拽片段边缘创建音频淡化

#### 调色工作流
1. 在 Lumetri Color 面板打开片段
2. 使用 Basic Correction 校准曝光和白平衡
3. 应用 Creative LUT 或预设风格
4. 使用 Curves 精细调整颜色曲线
5. 使用 HSL Secondary 针对性调整特定颜色
6. 通过 Lumetri Scopes（矢量示波器、直方图）监控色彩

#### 关键快捷键
| 功能 | Windows | macOS |
|------|---------|-------|
| 播放/暂停 | Space | Space |
| 导入媒体 | Ctrl+I | Cmd+I |
| 新建项目 | Ctrl+Alt+N | Cmd+Opt+N |
| 保存项目 | Ctrl+S | Cmd+S |
| 撤销/重做 | Ctrl+Z / Ctrl+Shift+Z | Cmd+Z / Cmd+Shift+Z |
| 剪切片段 | C (剃刀工具) | C |
| 选择工具 | V | V |
| 入点/出点 | I / O | I / O |
| 插入/覆盖 | , / . | , / . |
| 波纹删除 | Shift+Delete | Shift+Delete |
| 缩放时间线 | +/- 或 \ | +/- 或 \ |
| 前进/后退一帧 | → / ← | → / ← |
| 前进/后退五帧 | Shift+→ / Shift+← | Shift+→ / Shift+← |
| 全屏播放 | ` (反引号) | ` |
| 渲染预览 | Enter | Return |
| 标记入点 | X | X |
| 添加标记 | M | M |
| 复制片段 | Ctrl+C | Cmd+C |
| 粘贴插入 | Ctrl+Shift+V | Cmd+Shift+V |
| 嵌套序列 | Ctrl+B | Cmd+B |

### 3. 效果与转场

#### 常用视频效果
| 效果 | 位置 | 用途 |
|------|------|------|
| Opacity | Effect Controls | 透明度调整 |
| Basic 3D | Video Effects | 基础3D变换 |
| Color Balance | Color Correction | 色彩平衡 |
| Lumetri Color | Color Correction | 专业调色 |
| Gaussian Blur | Blur & Sharpen | 高斯模糊 |
| Drop Shadow | Obsolete | 投影效果 |

#### 常用转场
| 转场 | 位置 | 特点 |
|------|------|------|
| Dip to Black | Dissolve | 淡入淡出到黑 |
| Cross Dissolve | Dissolve | 交叉溶解 |
| Smooth Dissolve | Dissolve | 平滑溶解 |
| Film Dissolve | Dissolve | 胶片溶解风格 |
| Wipe | Wipe | 擦除效果 |

#### 应用转场
- **应用默认转场**：选中片段边缘 → Ctrl+D
- **应用音频转场**：选中音频边缘 → Ctrl+Shift+D
- **调整转场时长**：拖拽转场边缘
- **复制转场**：Alt+拖拽应用到其他位置

### 4. 导出设置建议

#### YouTube/视频平台
- 格式：H.264
- 分辨率：4K (3840×2160) 或 1080p (1920×1080)
- 帧率：与源素材一致（24/30/60fps）
- 码率：VBR 2 Pass，高质量
- 音频：AAC 320kbps

#### 项目存档/代理
- 格式：ProRes 422 或 DNxHD/DNxHR
- 保留最高质量用于存档
- 导出代理用于移动端编辑

#### Instagram/TikTok 短视频
- 格式：H.264
- 分辨率：1080x1920 (竖屏) 或 1080x1080 (方形)
- 帧率：30fps
- 码率：VBR 1 Pass

### 5. 常见问题解决

| 问题 | 解决方案 |
|------|----------|
| 播放卡顿 | 使用代理编辑（Project Settings → Scratch Disks） |
| 渲染时内存不足 | 清理缓存（Edit → Preferences → Media Cache） |
| 音频不同步 | 检查帧率匹配，启用"序列设置匹配" |
| 导入文件报错 | 更新编解码器，安装 K-Lite Codec Pack |
| 字幕不同步 | 调整序列帧率或使用强制字幕 |
| 颜色显示不准 | 校准显示器，在 Lumetri Settings 启用色彩管理 |
| 项目崩溃恢复 | 自动保存文件：Edit → Preferences → Auto Save |
| GPU 加速失效 | 更新显卡驱动，在 Project Settings 启用 GPU 加速 |
| 转场消失 | 检查时间线缩放级别，确保转场在可视区域 |
| 关键帧不生效 | 确保效果关键帧已启用（秒表图标亮起） |

### 6. 输出格式

回复时遵循以下结构：
1. **直接回答**：先给出解决方案
2. **操作步骤**：如需操作，提供清晰步骤
3. **快捷键提示**：相关快捷键
4. **注意事项**：可能的陷阱或最佳实践

### 7. 专业术语

| 术语 | 解释 |
|------|------|
| **Sequence** | 序列，类似时间线 |
| **Track** | 轨道，视频/音频轨道 |
| **Clip** | 片段，导入的媒体单位 |
| **Keyframe** | 关键帧，动画控制点 |
| **Render** | 渲染，生成预览或导出 |
| **Proxy** | 代理，低分辨率素材用于流畅编辑 |
| **LUT** | 色彩查找表，快速应用调色风格 |
| **Adjustment Layer** | 调整图层，统一应用效果 |
| **Nest** | 嵌套，将序列作为片段使用 |
| **Match Frame** | 匹配帧，定位源素材对应位置 |
| **Ripple Edit** | 波纹编辑，自动调整后续片段 |
| **Roll Edit** | 滚动编辑，同时调整相邻片段 |

### 8. 插件与扩展

- **Premiere Pro 支持的插件格式**：OFX、VST 音频插件
- **Essential Graphics Panel**：支持 MOGRT 动态图形模板
- **Adobe Exchange**：下载扩展和脚本
- **脚本自动化**：支持 JavaScript 脚本自动化任务
