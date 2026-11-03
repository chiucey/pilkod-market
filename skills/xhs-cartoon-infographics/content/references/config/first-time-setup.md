# First-Time Setup Guide

## Setup Flow

When EXTEND.md is not found, run first-time setup before any other questions.

## Questions (Single AskUserQuestion Call)

### All Questions Combined

```
请完成初始设置（将一次性询问以下偏好）：

1. 语言偏好
   - 中文 (中文内容优先)
   - English (English content preferred)
   - Auto (根据内容自动检测)

2. 水印设置
   - 否 (不添加水印)
   - 是 (添加文字水印)

3. 偏好的视觉风格
   - 自动推荐
   - 甜美可爱 (cute)
   - 清新自然 (fresh)
   - 温馨友好 (warm)
   - 强视觉冲击 (bold)
   - 极简高级 (minimal)
   - 复古怀旧 (retro)
   - 活力潮流 (pop)
   - 知性手绘 (notion)
   - 黑板粉笔 (chalkboard)
   - 手写笔记 (study-notes)
   - 丝网印刷 (screen-print)

4. 偏好的布局模式
   - 自动推荐
   - 稀疏留白 (sparse)
   - 平衡布局 (balanced)
   - 密集信息 (dense)
   - 清单枚举 (list)
   - 对比布局 (comparison)
   - 流程时间线 (flow)
   - 思维导图 (mindmap)
   - 四象限 (quadrant)
```

## Configuration Storage

Save to: `.baoyu-skills/baoyu-xhs-images/EXTEND.md`

## Non-Interactive Mode (--yes flag)

When `--yes` flag is provided:
- If EXTEND.md found → load preferences
- If EXTEND.md not found → use built-in defaults
  - No watermark
  - Auto style/layout selection
  - Language from content
- Do NOT run first-time setup
- Do NOT ask any questions
- Proceed directly to content analysis
