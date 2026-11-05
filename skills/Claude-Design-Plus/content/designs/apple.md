# Apple Human Interface Guidelines (HIG)

Apple 的设计系统，代表极致的用户体验和设计品质。

## 设计理念

Apple HIG 代表**清晰**、**功能**、**美学**的统一。设计应让用户感到自然和愉悦。

## 色彩系统

### 系统色

#### 蓝色 (System Blue)
- Primary: `#007AFF`
-适用: 链接、操作按钮、交互元素

#### 绿色 (System Green)
- Primary: `#34C759`
- 适用: 成功、确认、完成

#### 橙色 (System Orange)
- Primary: `#FF9500`
- 适用: 警告、提醒

#### 红色 (System Red)
- Primary: `#FF3B30`
- 适用: 危险、错误、删除

#### 靛色 (System Indigo)
- Primary: `#5856D6`
- 适用: 创意功能

#### 紫色 (System Purple)
- Primary: `#AF52DE`
- 适用: 特殊功能

#### 粉色 (System Pink)
- Primary: `#FF2D55`
- 适用: 社交、媒体

#### 棕色 (System Brown)
- Primary: `#A2845E`
- 适用: 高级、优雅

### 灰色系

#### Label 颜色
- Primary Label: `rgba(0, 0, 0, 1)` (0.87 opacity)
- Secondary Label: `rgba(0, 0, 0, 0.6)` (0.6 opacity)
- Tertiary Label: `rgba(0, 0, 0, 0.3)` (0.3 opacity)
- Quaternary Label: `rgba(0, 0, 0, 0.18)` (0.18 opacity)

#### 填充色
- System Fill: `rgba(120, 120, 128, 0.2)`
- Secondary Fill: `rgba(120, 120, 128, 0.16)`
- Tertiary Fill: `rgba(118, 118, 128, 0.12)`
- Quaternary Fill: `rgba(116, 116, 128, 0.08)`

### 背景色

#### 浅色模式
- System Background: `#FFFFFF`
- Secondary Background: `#F2F2F7`
- Tertiary Background: `#FFFFFF`
- Grouped Background: `#F2F2F7`

#### 深色模式
- System Background: `#000000`
- Secondary Background: `#1C1C1E`
- Tertiary Background: `#2C2C2E`
- Grouped Background: `#000000`

### 分隔线

- Separator: `rgba(60, 60, 67, 0.29)` (0.29 opacity)
- Opaque Separator: `#C6C6C8`

## 字体

### SF Pro (San Francisco)

这是 Apple 的专用字体，iOS 和 macOS 系统字体。

### 字号 (iOS)

#### 大标题
- Size: 34pt
- Weight: Bold
- Usage: 屏幕标题

#### 标题 1
- Size: 28pt
- Weight: Bold

#### 标题 2
- Size: 22pt
- Weight: Bold

#### 标题 3
- Size: 20pt
- Weight: Semibold

#### Headline
- Size: 17pt
- Weight: Semibold
- Usage: 表格标题、重要内容

#### Body
- Size: 17pt
- Weight: Regular
- Usage: 正文内容

#### Callout
- Size: 16pt
- Weight: Regular

#### Subheadline
- Size: 15pt
- Weight: Regular

#### Footnote
- Size: 13pt
- Weight: Regular
- Usage: 脚注、说明

#### Caption 1
- Size: 12pt
- Weight: Regular

#### Caption 2
- Size: 11pt
- Weight: Regular

### 字号 (macOS)

- Title 1: 28pt Bold
- Title 2: 22pt Bold
- Title 3: 20pt Semibold
- Headline: 13pt Semibold
- Body: 13pt Regular
- Callout: 12pt Regular
- Subhead: 11pt Regular
- Footnote: 10pt Regular
- Caption 1: 10pt Regular
- Caption 2: 9pt Regular

## 间距系统

### 边距 (iOS)

- 页面边距: 16pt
- 安全区域: 自动适配
- 列表项高度: 44pt (最小点击目标)

### 网格

- 基础单位: 4pt
- 标准间距: 8pt / 16pt / 24pt / 32pt

## 圆角

### iOS
- 小型元素: 8pt
- 中型元素: 12pt
- 大型元素 (卡片): 16pt
- 超大元素 (弹窗): 20pt

### macOS
- 按钮: 6pt
- 文本框: 4pt
- 面板: 8pt

## 阴影

### iOS 卡片阴影
```css
/* 轻阴影 */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);

/* 中阴影 */
box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15), 0 6px 6px rgba(0, 0, 0, 0.1);
```

### macOS 阴影
```css
/* 弹出层 */
box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12);

/* 模态框 */
box-shadow: 0 19px 38px rgba(0, 0, 0, 0.3), 0 15px 12px rgba(0, 0, 0, 0.22);
```

## 组件样式

### 按钮

#### 主要按钮 (Filled)
- Background: `#007AFF`
- Color: `#FFFFFF`
- Border Radius: 12pt
- Padding: 16pt 20pt
- Font: 17pt Semibold

#### 次要按钮 (Gray)
- Background: `#8E8E93`
- Color: `#FFFFFF`

#### 边框按钮 (Tinted)
- Background: `rgba(0, 122, 255, 0.15)`
- Color: `#007AFF`
- Border Radius: 12pt

#### 文字按钮
- Color: `#007AFF`
- 无背景

### 输入框

- Background: `rgba(118, 118, 128, 0.12)`
- Border Radius: 10pt
- Height: 44pt (iOS)
- Padding: 12pt 16pt
- Placeholder Color: `rgba(60, 60, 67, 0.3)`

### 卡片 (iOS)
- Background: `#FFFFFF`
- Border Radius: 16pt
- Padding: 16pt
- Shadow: 轻阴影

### 列表

- Background: `#FFFFFF` (grouped)
- Row Height: 44pt minimum
- Separator: 0.5pt 左边距 16pt
- Accessory: 右侧箭头 10pt

### 导航栏

- Background: blur effect (毛玻璃)
- Height: 44pt (iPhone) / 52pt (iPad)
- Title: 17pt Semibold
- Tint Color: `#007AFF`

### Tab Bar

- Background: blur effect
- Height: 49pt (iPhone) / 50pt (iPad)
- Icon Size: 25pt
- Label Size: 10pt

## SF Symbols

Apple 官方图标库，推荐使用：
- 大小比例: small / medium / large
- 权重: regular / medium / bold
- 填充: symbol variant (circle.fill vs circle)

## 设计注意事项

1. **内容优先** - 内容是核心，UI 是辅助
2. **一致性** - 遵循 Apple 平台惯例
3. **清晰层次** - 明确的视觉层级
4. **颜色用法** - 语义化用色，不要随意
5. **深色模式** - 必须支持深色模式
6. **无障碍** - 符合 Apple 无障碍标准
7. **安全区域** - 适配刘海和 Home Indicator

## 适用场景

- 📱 iOS/macOS 应用
- 📺 Apple TV 应用
- ⌚ Apple Watch 应用
- 🌐 Apple 风格网页
- 🎨 高端消费品展示

## 组件示例 HTML 结构

```html
<!-- iOS 风格按钮 -->
<button class="apple-btn apple-btn-filled">主要操作</button>
<button class="apple-btn apple-btn-tinted">次要操作</button>
<button class="apple-btn apple-btn-text">文字按钮</button>

<!-- iOS 输入框 -->
<input class="apple-input" type="text" placeholder="输入内容">

<!-- iOS 卡片 -->
<div class="apple-card">
  <div class="apple-card-header">标题</div>
  <div class="apple-card-content">内容</div>
</div>

<!-- iOS 列表 -->
<div class="apple-list">
  <div class="apple-list-row">
    <span>标题</span>
    <span class="apple-chevron">›</span>
  </div>
</div>

<!-- iOS 导航栏 -->
<nav class="apple-nav-bar">
  <span class="apple-nav-title">标题</span>
</nav>
```
