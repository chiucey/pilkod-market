---
name: wechat-smart-formatter
description: 微信公众号智能排版配图工具。当用户需要将文章进行公众号排版、智能配图、去除水印、布局优化时使用。支持从Unsplash/Pexels搜索版权图片、AI生图、自动去水印、高级配色方案、智能图文混排。
---

# 微信公众号智能排版配图系统

## 核心功能

### 1. 智能配图系统

#### 1.1 图片搜索优先级
```
优先级流程：
┌─────────────────────────────────────────────────────┐
│  1. 搜索 Unsplash/Pexels 版权免费图片              │
│     → 关键词提取 + 语义匹配                        │
│     → 优先选择无水印、高清、大图                   │
│                                                      │
│  2. 如未找到合适图片 → 调用 AI 生图                │
│     → 使用 MiniMax Image API                       │
│     → 生成符合文章语境的图片                       │
│                                                      │
│  3. 本地 Stable Diffusion 接口（可选）             │
│     → 可配置本地 SD API 地址                       │
│     → 支持自定义模型和参数                        │
└─────────────────────────────────────────────────────┘
```

#### 1.2 图片处理流程
```
图片获取 → 水印检测 → 去水印处理 → 尺寸适配 → 智能裁剪 → 最终输出
    ↓
[智能识别水印位置] → [OpenCV/LaMa算法去除] → [16:9/4:3/1:1比例]
```

### 2. 高级排版系统

#### 2.1 配色方案（拒绝蓝紫配色）

**主推配色方案：**

| 方案名称 | 主色 | 辅色 | 适用场景 |
|---------|------|------|---------|
| **经典商务** | #2D3436 深灰 | #636E72 炭灰 | 商务资讯、企业公告 |
| **温暖人文** | #B85C38 赭红 | #EAB543 琥珀 | 情感随笔、生活分享 |
| **清新自然** | #2D6A4F 森绿 | #95D5B2 薄荷 | 旅行游记、自然主题 |
| **极简黑白** | #1A1A1A 墨黑 | #F5F5F5 素白 | 专业评测、干货分享 |
| **活力橙黄** | #E76F51 珊瑚橙 | #F4A261 暖黄 | 活动宣传、促销推广 |
| **文艺复古** | #6D4C41 咖啡 | #D7CCC8 米灰 | 书评影评、文艺专栏 |

#### 2.2 排版规范

**字体设置：**
- 正文：`"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`
- 标题：`"PingFang SC", "Microsoft YaHei", sans-serif` 加粗
- 代码：`"SF Mono", "Menlo", "Monaco", monospace`

**字号规范：**
- 文章标题：24px-28px，加粗
- 小标题：18px-20px，加粗
- 正文：15px-16px，行高 1.8
- 引用：14px-15px，斜体
- 图片说明：12px，灰色

**间距规范：**
- 段落间距：1.5em
- 标题上下间距：1.2em
- 图片上下间距：1em
- 引用缩进：1.5em

#### 2.3 布局规则

```
┌────────────────────────────────────────┐
│           封面图（900x383px）          │
│                                        │
│  [如提供Logo，自动嵌入右下角/左下角]    │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│              文章标题                   │
│         （可添加装饰线）                │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  [智能配图]   图左文右 / 图右文左 / 图上文下  │
│  根据图片数量自动选择最优布局          │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  [引用块]     左侧装饰线 + 灰色背景     │
│  [代码块]     深色背景 + 等宽字体       │
│  [列表]       自定义符号或序号         │
└────────────────────────────────────────┘
```

### 3. Logo/企业标识集成

如用户提供Logo或企业VI色，将自动：
- 封面图右下角嵌入Logo（水印级别）
- 章节分隔符使用品牌色
- 全文色调向品牌色靠拢
- 底部生成专属签名模块

---

## 执行流程

### 第一步：内容分析

```
输入文章 → 提取关键词 → 识别文章类型 → 确定配色方案 → 规划配图位置
```

**关键词提取：**
- 提取3-5个核心名词
- 识别文章情感基调（专业/温暖/活泼/文艺）
- 判断内容类型（资讯/评测/故事/教程/推广）

### 第二步：图片处理

```
for each 需要配图的位置:
    1. 搜索版权图片（Unsplash/Pexels API）
    2. 如未找到 → AI生成图片
    3. 检测水印（OpenCV 边缘检测）
    4. 如有水印 → 自动去水印处理
    5. 适配尺寸（900px宽度，质量85%）
    6. 裁剪优化（保持主体居中）
```

**去水印算法：**
- 边缘检测定位水印区域
- LaMa/DeepFill算法填充
- 色彩一致性修正
- 人工微调（如必要）

### 第三步：排版生成

```
文章结构 → 应用模板 → 插入配图 → 优化布局 → 输出HTML
```

**输出格式：**
- HTML代码（可直接粘贴到公众号编辑器）
- CSS内联样式（确保微信显示一致）
- Markdown源文件备份

---

## 配置选项

### 可选配置项

```yaml
# 图片搜索API配置
image_search:
  provider: "unsplash"  # unsplash / pexels
  per_page: 10
  orientation: "landscape"  # landscape / portrait / squarish

# AI生图配置
ai_generation:
  enabled: true
  api: "minimax"  # minimax / openai / stability
  style: "photorealistic"  # photorealistic / illustration / flat

# 本地SD配置（可选）
local_sd:
  enabled: false
  api_url: "http://localhost:7860"
  model: "AnythingV5"
  steps: 30

# 水印处理配置
watermark_removal:
  enabled: true
  auto_detect: true
  strength: "medium"  # low / medium / high

# 品牌配置
brand:
  logo_path: null  # 本地Logo路径，如用户提供
  primary_color: null  # 品牌主色
  secondary_color: null  # 品牌辅色
```

---

## 技术实现

### 使用的工具

| 工具 | 用途 |
|-----|------|
| Unsplash API | 高质量版权图片搜索 |
| Pexels API | 备用图片源 |
| MiniMax Image API | AI图片生成 |
| OpenCV | 水印检测与处理 |
| PIL/Pillow | 图片处理与裁剪 |

### 图片搜索策略

```python
# 搜索关键词组合
search_keywords = [
    main_topic,  # 核心主题
    article_type,  # 文章类型
    visual_style,  # 视觉风格
    color_scheme,  # 配色关键词
    "no people",  # 排除人物
    "high resolution",  # 高清优先
]
```

### 水印检测算法

```python
# 水印检测流程
1. 边缘检测（Canny）→ 找出高对比度区域
2. 角点检测（Harris）→ 定位矩形区域
3. 颜色分析 → 识别半透明白色/灰色区域
4. 区域合并 → 确定完整水印边界
5. 去水印处理 → 基于内容填充
```

---

## 使用示例

### 基础用法

```
用户：请将以下文章进行公众号排版配图

[粘贴文章内容]

Skill将自动：
1. 分析文章结构和主题
2. 生成3-5个配图方案
3. 应用高级排版模板
4. 输出可直接发布的HTML
```

### 高级用法

```
用户：请用温暖人文配色，为这篇企业新闻排版
      Logo文件：/path/to/logo.png
      品牌色：#1E3A5F

Skill将：
1. 应用温暖人文配色方案
2. 在封面嵌入Logo
3. 使用品牌色作为点缀
4. 生成企业级排版效果
```

---

## 输出规范

### HTML输出标准

```html
<!-- 微信文章容器 -->
<div class="wechat-article">
    <!-- 封面图 -->
    <figure class="cover-image">
        <img src="..." alt="...">
        <figcaption>配图说明</figcaption>
    </figure>

    <!-- 文章标题 -->
    <h1 class="article-title">...</h1>

    <!-- 正文内容 -->
    <article class="article-body">
        <p>...</p>
        <figure class="inline-image">...</figure>
        <blockquote>...</blockquote>
        <h2>...</h2>
    </article>

    <!-- 底部签名 -->
    <footer class="article-footer">
        <div class="author-info">...</div>
        <div class="qr-code">...</div>
    </footer>
</div>
```

### CSS样式标准

```css
/* 微信文章CSS - 高级配色方案 */
.wechat-article {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #2D3436;
    line-height: 1.8;
}

.article-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin: 1.2em 0;
}

.article-body p {
    font-size: 15px;
    text-indent: 2em;
    margin: 0.8em 0;
}

.inline-image {
    margin: 1em auto;
    max-width: 100%;
}

blockquote {
    background: #F8F9FA;
    border-left: 4px solid #B85C38;
    padding: 1em 1.5em;
    margin: 1em 0;
}
```

---

## 注意事项

1. **图片版权**：优先使用Unsplash/Pexels无版权图片，AI生成图片可商用
2. **水印处理**：自动处理后的图片需人工复核，确保去水印效果自然
3. **排版预览**：建议在手机端预览最终效果，确保阅读体验
4. **格式兼容**：输出的HTML可直接粘贴到微信公众号编辑器
5. **本地SD**：如需使用本地Stable Diffusion，需自行部署并配置API

---

## 错误处理

| 错误情况 | 处理方案 |
|---------|---------|
| 图片搜索失败 | 切换到AI生图 |
| AI生图失败 | 使用预设占位图 |
| 去水印失败 | 提供原图+水印位置提示 |
| 排版异常 | 回退到基础模板 |
| API超时 | 重试3次后跳过 |

---

## 版本更新

- **v1.0.0** (2026-04-02)
  - 初始版本
  - 支持Unsplash/Pexels图片搜索
  - 集成MiniMax AI生图
  - 6种高级配色方案
  - 自动去水印功能
  - Logo嵌入支持
