---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4c7ec52a16c9998c3ef9f2846b0ec158
    PropagateID: 4c7ec52a16c9998c3ef9f2846b0ec158
    ReservedCode1: 304502200d39fffbce88e8a84aa7478e37af1d3bd15afb9033b4f453250b003fb09ee288022100dff2acace63a32f6eda76f6bbaa49e59494f5e5181ee2b05a9220ba9a954e4eb
    ReservedCode2: 3045022100f82da3d7a0ce0338d6299597d0e61b5ea7378c7a446b12bcc46a88f6989bfb3602200c86e82e1f3e16777e9ded7b351ff1f191c1eee6b719af662d3a22b95c4586f3
description: 生成预印本科研动态日报HTML页面。当用户提供bioRxiv/medRxiv预印本文献列表，需要生成格式化的科研日报时使用。自动分类文献（综述/研究/技术）、生成统计、目录、文献卡片和趋势观察。
name: preprint-daily-report
---

# 预印本科研动态日报生成器

## 输入规范

用户提供的原始内容需要包含：
- 标题和日期
- 文献列表（bioRxiv/medRxiv预印本）
- 每篇文献的：标题、作者、摘要、主要发现、方法、标签

## 输出结构

### 1. 页面框架
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>预印本科研动态日报 · 第{期号}期 · {日期}</title>
  <style>/* 使用标准样式 */</style>
</head>
<body>
  <div class="page-wrap">
    <!-- 品牌横幅 -->
    <!-- 期号信息栏 -->
    <!-- 日期区域 -->
    <!-- 统计栏 -->
    <!-- 目录区域 -->
    <!-- 文献分类卡片 -->
    <!-- 趋势观察 -->
    <!-- 页脚 -->
  </div>
</body>
</html>
```

### 2. 分类规则

**综述类** - 包含系统性文献综述、Meta分析或全面评述的研究

**研究类** - 包含原创实验数据、新方法验证、临床研究

**技术类** - 包含软件工具、新算法、数据库、计算框架

### 3. 文献卡片结构

每个文献卡片包含：
1. 序号 + 标题（中英文）
2. 元数据：来源badge、作者、通讯作者、日期
3. 亮点框：创新点一句话概括
4. 摘要：100-200字研究概述
5. 主要发现：3-5个要点列表
6. 方法标签：研究方法简述
7. 主题标签：相关领域关键词

### 4. 颜色规范

```css
:root {
  --primary: #1A5F3C;     /* 主色-深绿 */
  --accent: #E84545;      /* 强调-红色 */
  --accent2: #F59E0B;     /* 次强调-橙色 */
  --bg: #F5F7FA;          /* 背景 */
  --card: #FFFFFF;        /* 卡片背景 */
  --text: #2D3748;        /* 正文 */
  --muted: #718096;       /* 次要文字 */
  --border: #E2E8F0;      /* 边框 */
}
```

### 5. Badge规则
- bioRxiv: 背景#E0F2FE, 文字#0369A1
- medRxiv: 背景#FEF9C3, 文字#92400E

### 6. 趋势观察生成

从本期文献中提取3-4个跨文献主题趋势，每个趋势包含：
- 编号 + 主题标签（加粗）
- 主题解释，关联具体文献

## 执行流程

1. 解析输入的文献数据
2. 按类型分类（综述/研究/技术）
3. 生成统计数字（总文献数、各类数量、覆盖学科数）
4. 生成目录
5. 为每篇文献生成标准卡片
6. 提取并生成趋势观察
7. 组装完整HTML

## 示例

**输入**：提供文献列表和元数据
**输出**：完整HTML日报页面

---

## 文件参考

- `references/template.html` - 完整HTML模板参考
- `references/styles.css` - 样式参考
