---
name: 表情包自由
description: 基于参考图生成一套16格“手残鼠标画”风格的聊天表情包。当用户想要制作表情包、贴纸、搞怪头像，提供角色照片或描述并要求配上吐槽文案时调用。擅长处理“丑萌”、“荒诞”、“手写感”的极简视觉创作。
metadata:
  tools:
    - gpt_image_2_draw
---

# 表情包自由：手残党鼠标画生成指南

## 1. 核心任务：模拟“深夜发疯”的乱画过程
这个技能的核心不是“设计”，而是“发泄”。必须模拟一个不会画画的人，用鼠标在电脑画板（MS Paint）上，一边乱涂一边顺手写字的过程。

### 核心视觉哲学：错误一致性
- **禁止美化**：严禁比例协调、线条流畅、光影细腻。如果画面看起来“好看”，即为失败。
- **一致性定义**：不是“长得像”，而是“画得像同一个人乱画的”。
- **视觉特征**：
  - 锯齿状（Aliased）线条，边缘粗糙，像低分辨率像素图。
  - 线条抖动（Shaky lines），像鼠标没拿稳或手抖。
  - 极度简化：火柴人、符号脸、五官错位、比例严重失调。
  - 颜色：纯色填充，甚至故意涂出界或留白。

## 2. 16宫格版式与文案系统
- **结构**：固定为 4x4 格排列（Grid Layout），每格一个独立表情。
- **文字融入（关键）**：文字必须像“画”上去的，而不是排版出来的。
  - 风格：歪歪扭扭、大小不一、重叠在角色身上或边缘。
  - 形式：允许拉长音（啊——）、重复字（烦烦烦）、乱用标点（？！）。
- **文案生成机制**：
  - 模拟16次“独立、随机、临时”的吐槽表达。
  - 语感：摆烂、吐槽、打工人崩溃、敷衍、荒诞。
  - 补全原则：若用户文案不足16条，补全具备互联网张力的短语（如：哈？、溜了、想死、没救了、我不理解）。

## 3. 生图指令强制要求 (Prompt Engineering)
调用生图工具时，必须在 prompt 中融入以下英文关键词以强制降级：
- **Style Keywords**: MS Paint drawing style, crude mouse art, pixelated aliased brush, Microsoft Paint aesthetic, low-fidelity digital art, shaky digital lines, intentionally bad drawing, minimalist sketch.
- **Composition**: 4x4 stickers sheet, white background, distinct individual squares, no professional framing.
- **Character Consistency**: Preserve only minimum recognizable features (hair shape, key color, distinct accessory) but allow anatomy failure.
- **Text Implementation**: Scribbled text by mouse, handwritten captions integrated into the drawing, messy handwriting, chaotic placement.

## 4. 交付标准
如果生成的图看起来“可爱”、“精致”或“像插画师的作品”，必须重新通过增加“混乱度”来修正。
成功标准：用户看到图的第一反应是“哈哈哈哈这画得好烂，好真实”。

## 5. 输出结构示例
<example>
[一张 4x4 的大图，背景白色]
格子(1,1): 一个扭曲的圆头，旁边写着“寄了” (文字歪斜)
格子(1,2): 只有一双大眼睛占据画面，写着“？！？！”
格子(2,3): 角色全身缩成一团，文字叠在身上“不想上班啊啊”
格子(4,4): 角色几乎消失，只剩一团乱线和文字“没救了”
...以此类推，共16格独立内容。
</example>
