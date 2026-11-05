# Style Presets Summary

Quick reference for style + layout preset combinations.

## Single-Command Presets

| Preset | Command | Style | Layout | Best For |
|--------|---------|-------|--------|----------|
| knowledge-card | --preset knowledge-card | notion | dense | 干货知识卡 |
| checklist | --preset checklist | notion | list | 清单排行 |
| tutorial | --preset tutorial | chalkboard | flow | 教程步骤 |
| cute-share | --preset cute-share | cute | balanced | 少女种草 |
| warning | --preset warning | bold | list | 避坑指南 |
| poster | --preset poster | screen-print | sparse | 海报封面 |
| cinematic | --preset cinematic | screen-print | comparison | 电影对比 |

## Usage Examples

```bash
# Auto-select style and layout based on content
/xhs-images posts/article.md

# Specify preset (style + layout in one)
xhs-images posts/article.md --preset knowledge-card

# Specify style only (layout auto-selected)
xhs-images posts/article.md --style notion

# Specify layout only (style auto-selected)
xhs-images posts/article.md --layout dense

# Combine style and layout
xhs-images posts/article.md --style notion --layout dense

# Override preset with specific layout
xhs-images posts/article.md --preset poster --layout quadrant
```

## Auto Selection Matrix

| Content Keywords | Style | Layout | Preset |
|-----------------|-------|--------|--------|
| 美丽/穿搭/少女 | cute | sparse/balanced | cute-share |
| 健康/自然/有机 | fresh | balanced/flow | nature-flow |
| 生活/故事/情感 | warm | balanced | cozy-story |
| 避坑/警告/重要 | bold | list/comparison | warning |
| 专业/商务/简洁 | minimal | sparse/balanced | pro-summary |
| 经典/复古/传统 | retro | balanced | throwback |
| 趣味/好玩/震撼 | pop | sparse/list | hype |
| 知识/概念/效率 | notion | dense/list | knowledge-card |
| 教程/学习/课堂 | chalkboard | balanced/flow | tutorial |
| 笔记/考试/手写 | study-notes | dense/list | study-guide |
| 影评/海报/观点 | screen-print | sparse/comparison | poster |
