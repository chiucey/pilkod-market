# 英语词汇大师 - English Vocabulary Master

## 1. Concept & Vision

一款基于"九维深度解析框架"的交互式词汇学习平台，让用户像语言学家一样理解和运用英语单词。设计理念融合学术严谨性与现代交互美学，营造沉浸式学习体验。整体风格：墨绿色主调搭配温暖米色，营造专注而舒适的学术氛围。

## 2. Design Language

### 美学方向
学术期刊风格 + 现代卡片式UI，融合东西方设计美学，营造专业而不沉闷的学习环境。

### 色彩系统
- **Primary**: #1B4332 (深墨绿 - 主色调)
- **Secondary**: #2D6A4F (森林绿 - 次要元素)
- **Accent**: #E07A5F (赤陶橙 - 强调与交互)
- **Background**: #FEFAE0 (暖米色 - 背景)
- **Surface**: #FFFFFF (纯白 - 卡片背景)
- **Text Primary**: #1A1A2E (深墨蓝 - 主文字)
- **Text Secondary**: #6B7280 (灰色 - 辅助文字)
- **Success**: #059669 (翠绿 - 正确反馈)
- **Error**: #DC2626 (红色 - 错误反馈)
- **Warning**: #D97706 (琥珀 - 提示)

### 字体
- **标题**: "Noto Serif SC", serif (中文标题)
- **正文**: "Inter", "Noto Sans SC", sans-serif (中英文正文)
- **代码/标签**: "JetBrains Mono", monospace

### 空间系统
- 基础单位: 8px
- 卡片内边距: 24px (3单位)
- 卡片间距: 24px
- 容器最大宽度: 1200px
- 圆角: 12px (卡片), 8px (按钮), 4px (标签)

### 动效哲学
- 页面切换: 淡入滑动 (opacity 0→1, translateY 20px→0, 400ms ease-out)
- 卡片悬停: 微妙上浮 (translateY -4px, box-shadow加深, 200ms)
- 选项反馈: 缩放脉冲 (scale 0.95→1, 150ms)
- 进度动画: 平滑增长 (width transition, 600ms ease-out)
- 标签切换: 颜色渐变 (300ms)

### 视觉资产
- 图标: Lucide Icons (线性风格, stroke-width: 2)
- 装饰元素: 抽象叶脉纹理作为背景点缀
- 图表: 纯CSS实现的进度环和对比表格

## 3. Layout & Structure

### 页面结构

#### 首页 (Hero)
- 大标题与副标题建立品牌认知
- 输入区域：单词对输入框 + 示例提示
- 快速入口：预设易混词组选择
- 底部：平台特色概览卡片

#### 学习页面 (Learning View)
- 顶部导航：返回、进度指示、收藏
- 九维度内容区：可切换的标签页展示
- 侧边栏：单词对总览与快速跳转
- 底部：继续到练习按钮

#### 练习页面 (Exercise View)
- 进度条与当前题号
- 题目展示区
- 选项区域
- 即时反馈区
- 下一题/结果按钮

#### 结果页面 (Results View)
- 总分与评价
- 详细反馈列表
- 薄弱点分析
- 重新学习/再练一次按钮

### 响应式策略
- Desktop (>1024px): 双栏布局，侧边导航
- Tablet (768-1024px): 单栏，折叠侧边
- Mobile (<768px): 堆叠布局，底部导航

## 4. Features & Interactions

### 核心功能

#### 4.1 单词输入
- 支持输入两个易混词 (用 "vs" 或 "," 分隔)
- 预设词组快速选择
- 实时输入验证
- 按Enter或点击按钮提交

#### 4.2 九维解析展示
标签页切换，动画过渡：

1. **核心定义**
   - 两个单词并排对比卡片
   - 一句话区分本质差异
   - 核心关键词高亮

2. **语境示例**
   - 每个词3个真实语境例句
   - 英文为主，中文注释为辅
   - 关键词在句中加粗

3. **表格提炼**
   - 对比表格：共同点、不同点、使用场景
   - 视觉化差异一目了然

4. **视觉隐喻**
   - 生动比喻帮助你理解抽象含义
   - 配以简洁插图或图标

5. **词语搭配**
   - 常见搭配短语列表
   - 介词/副词搭配高亮
   - 不正确搭配警示

6. **语法功能**
   - 词性标注
   - 句子成分分析
   - 主谓一致说明

7. **语域风格**
   - 正式程度滑块 (1-5)
   - 使用场景描述
   - 近义替换建议

8. **记忆方法**
   - 词根词缀解析
   - 联想记忆法
   - 发音联想

#### 4.3 三级互动练习

**第一级：识别 (Recognition)**
- 题型：给语境选单词
- 考察：能否准确识别语境中的恰当用词
- 难度：基础

**第二级：填空 (Completion)**
- 题型：选词填空
- 考察：能否正确使用词汇
- 难度：进阶

**第三级：创作 (Creation)**
- 题型：用指定单词写句子
- 考察：能否灵活运用
- 难度：挑战

#### 4.4 即时反馈系统
- 选择后立即显示对错
- 正确：绿色高亮 + 解释
- 错误：红色高亮 + 正确答案 + 解释
- AI风格评语（非冰冷标准答案）

### 交互细节
- 标签切换: 点击切换，淡入动画
- 卡片悬停: 上浮+阴影
- 选项点击: 缩放反馈
- 进度更新: 平滑动画
- 表单验证: 实时错误提示

### 边界处理
- 空输入: 显示提示文字
- 无匹配词组: 显示"正在开发中，敬请期待"
- 加载状态: 骨架屏
- 错误状态: 友好提示+重试

## 5. Component Inventory

### 5.1 导航栏 (NavBar)
- Logo + 标题
- 导航链接
- 状态：默认、滚动后（阴影）

### 5.2 单词输入框 (WordInput)
- 双输入框组
- 分隔符显示
- 状态：默认、聚焦、错误、完成

### 5.3 预设词组卡片 (PresetCard)
- 词组名称
- 简短描述
- 状态：默认、悬停、选中

### 5.4 标签切换器 (TabSwitcher)
- 标签列表
- 指示器动画
- 状态：默认、激活、悬停

### 5.5 定义卡片 (DefinitionCard)
- 词性标签
- 释义文字
- 关键词高亮
- 状态：默认、悬停

### 5.6 对比表格 (CompareTable)
- 表头
- 对比行
- 差异高亮
- 状态：静态展示

### 5.7 例句卡片 (ExampleCard)
- 英文例句
- 中文翻译
- 关键词标记
- 状态：默认

### 5.8 练习选项 (ExerciseOption)
- 选项文字
- 标识字母
- 状态：默认、悬停、选中、正确、错误、禁用

### 5.9 进度条 (ProgressBar)
- 百分比显示
- 动画填充
- 状态：进行中、已完成

### 5.10 反馈气泡 (FeedbackBubble)
- 状态图标
- 反馈文字
- 颜色编码

### 5.11 按钮 (Button)
- Primary: 实心墨绿
- Secondary: 边框墨绿
- Accent: 实心赤陶橙
- 状态：默认、悬停、按下、禁用、加载

## 6. Technical Approach

### 架构
- 单页应用 (SPA)
- 纯前端实现 (HTML + CSS + JavaScript)
- 状态管理: 原生JavaScript对象
- 路由: Hash-based (#home, #learn, #exercise, #results)

### 数据结构
```javascript
{
  wordPairs: [
    {
      id: "apathetic-indifferent",
      words: ["apathetic", "indifferent"],
      analysis: {
        definitions: { apathetic: "...", indifferent: "..." },
        examples: { apathetic: [...], indifferent: [...] },
        comparison: { similarities: [...], differences: [...], scenarios: [...] },
        metaphors: { apathetic: "...", indifferent: "..." },
        collocations: { apathetic: [...], indifferent: [...] },
        grammar: { apathetic: {...}, indifferent: {...} },
        register: { apathetic: {...}, indifferent: {...} },
        memory: { apathetic: {...}, indifferent: {...} }
      },
      exercises: {
        level1: [...],
        level2: [...],
        level3: [...]
      }
    }
  ]
}
```

### 预设词组数据
1. apathetic vs indifferent
2. affect vs effect
3. fewer vs less
4. imply vs infer
5. i.e. vs e.g.

### 响应式断点
- Mobile: max-width 767px
- Tablet: 768px - 1023px
- Desktop: min-width 1024px
