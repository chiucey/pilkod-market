---
name: outfit-occasion-searcher
description: 个人穿搭助手，根据不同场合搜索合适的衣服搭配风格图片。当用户询问约会穿搭、通勤装扮、旅行穿着、派对服装、聚会穿搭、商务场合等特定场合的穿衣建议时使用。触发词：约会穿什么、通勤穿搭、旅行穿什么、派对服装、聚会打扮、商务装、面试穿搭、婚礼着装等。
---

# Outfit Occasion Searcher

个人穿搭图片搜索助手，根据用户指定的不同场合，智能搜索并展示合适的穿搭风格参考图片。

## 使用场景

| 场合类型 | 搜索关键词示例 | 风格特点 |
|---------|---------------|---------|
| 约会 (Date) | date night outfit, romantic dinner look | 优雅、时尚、有点小性感 |
| 通勤 (Work/Commute) | office outfit, business casual, work wear | 干练、专业、舒适 |
| 旅行 (Travel) | travel outfit, vacation look, trip fashion | 轻便、百搭、上镜 |
| 派对 (Party) | party outfit, clubbing look, cocktail dress | 亮眼、个性、时尚 |
| 聚会 (Gathering) | dinner party outfit, family gathering look | 得体、温馨、不过分隆重 |
| 商务 (Business) | business meeting, formal business wear | 正统、专业、高质感 |
| 面试 (Interview) | interview outfit, professional look | 稳重、干练、得体 |
| 婚礼 (Wedding) | wedding guest outfit, ceremony attire | 正式、优雅、符合礼仪 |

## 搜索策略

### 第一步：理解用户需求
- 提取用户描述的**场合类型**
- 识别用户的**风格偏好**（如：休闲、正式、甜美、酷帅）
- 确认**季节/天气**（如已知）
- 了解**性别**倾向（如需要）

### 第二步：构建搜索查询
根据场合组合多个关键词：

```
// 基础查询结构
{场合} outfit fashion {年份}
{场合} style {风格} look
{场合} what to wear {季节}

 // 常见组合示例
date night outfit romantic elegant
office work outfit business casual women spring
beach vacation outfit summer dress
party outfit clubbing stylish
wedding guest outfit women elegant spring
 ```

### 第三步：执行搜索
使用 `images_search_and_download` 工具，每次最多搜索5组关键词。

### 第四步：结果展示
- 优先展示与用户需求**匹配度最高**的图片
- 每张图片标注**场合标签**
- 提供**穿搭要点提示**（可选）

## 输出格式

```
## {场合}穿搭推荐

[展示搜索到的图片]

## 穿搭要点
- [要点1]
- [要点2]
- [要点3]

## 搭配建议
[根据场合给出实用的搭配建议]
```

## 注意事项

1. **搜索量控制**：每次搜索控制在 3-5 组关键词，避免搜索过多结果
2. **图片质量**：优先选择清晰、专业的穿搭图片
3. **风格多样性**：提供 2-3 种不同风格供用户选择
4. **季节适配**：考虑搜索结果与用户所在季节的匹配度
5. **适度建议**：穿搭建议要实用，不要过于极端或夸张

## 示例对话

**用户**: "下周末要去参加朋友的生日派对，穿什么好？"

**助手**:
1. 识别场合：生日派对 → Party/Gathering
2. 搜索关键词：party outfit stylish, birthday celebration look, cocktail dress elegant
3. 展示结果并给出搭配建议

## 错误处理

- **搜索无结果**：尝试变换关键词或扩大搜索范围
- **图片加载失败**：使用备选搜索词重新搜索
- **场合不明确**：询问用户更多细节（场合正式程度、风格偏好等）
