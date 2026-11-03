# Linear Design System

Linear 代表极致的开发者体验和产品美学。

## 设计理念

Linear 追求**卓越**、**速度**、**极简**。每个细节都经过精心打磨。

## 色彩系统

### 主色
- Primary: `#5E6AD2` (Linear 紫)
- Primary Hover: `#7B85D3`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F7F7F8`
- Background Tertiary: `#EFEFED`
- Background Hover: `#F0F0EF`

#### 深色模式
- Background Dark: `#0D0D0E`
- Background Dark Secondary: `#17171A`
- Background Dark Tertiary: `#1E1E23`
- Background Dark Hover: `#252529`

### 文字色

#### 浅色模式
- Text Primary: `#1A1A1C`
- Text Secondary: `#5E5E66`
- Text Tertiary: `#8E8E96`

#### 深色模式
- Text Dark Primary: `#EDEDEF`
- Text Dark Secondary: `#8A8A96`
- Text Dark Tertiary: `#5C5C66`

### 边框色

#### 浅色模式
- Border: `#E5E5E7`
- Border Subtle: `#EFEFED`

#### 深色模式
- Border Dark: `#2C2C30`
- Border Dark Subtle: `#222226`

### 语义色

| 用途 | 浅色 | 深色 |
|------|------|------|
| Success | `#26A641` | `#36B237` |
| Warning | `#D4A400` | `#E5B900` |
| Error | `#D83A3A` | `#E54D4D` |
| Info | `#3F8FED` | `#5499F7` |
| Done | `#8A3FFC` | `#A064FF` |
| Cancel | `#8A8A96` | `#6E6E7A` |

### 优先级色

- Urgent: `#E5484D`
- High: `#F76B15`
- Medium: `#FAB12D`
- Low: `#8CD360`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字重
- Regular: 400
- Medium: 500
- Semibold: 600

### 字号
- Title: 13px / 500 / 0.02em tracking
- Body: 13px / 400
- Small: 12px / 400
- Tiny: 11px / 400

### 代码字体
```
'JetBrains Mono', 'SF Mono', Monaco, Consolas, monospace
```

## 间距系统

基于 4px 网格：
- 0.5: 2px
- 1: 4px
- 1.5: 6px
- 2: 8px
- 3: 12px
- 4: 16px
- 5: 20px
- 6: 24px
- 8: 32px
- 10: 40px
- 12: 48px

## 圆角

- none: 0
- sm: 4px
- md: 6px
- lg: 8px
- xl: 10px
- 2xl: 12px
- full: 9999px

## 阴影

### 浅色模式
```css
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
```

### 深色模式
```css
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
```

### 悬停阴影
```css
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
```

## 动效

### 时长
- Fast: 100ms
- Normal: 150ms
- Slow: 200ms
- Slower: 300ms

### 缓动
```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
```

## 组件样式

### 按钮

**主要按钮**
- Background: `#5E6AD2`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 28px
- Padding: 0 12px
- Font Size: 13px
- Font Weight: 500

**次要按钮**
- Background: `#EFEFED`
- Color: `#1A1A1C`
- Hover Background: `#E5E5E7`

**幽灵按钮**
- Background: transparent
- Color: `#5E5E66`
- Hover Background: `#F7F7F8`
- Hover Color: `#1A1A1C`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E5E5E7`
- Border Radius: 6px
- Height: 32px
- Padding: 0 10px
- Font Size: 13px
- Focus Border: `#5E6AD2`

### 侧边栏

- Width: 240px
- Background: `#F7F7F8`
- Item Height: 32px
- Item Padding: 0 12px
- Item Border Radius: 6px

### 模态框

- Border Radius: 12px
- Padding: 24px
- Backdrop: rgba(0, 0, 0, 0.5)

### 状态徽章

- Border Radius: 4px
- Padding: 2px 6px
- Font Size: 11px
- Font Weight: 500

## 设计注意事项

1. **精致细节** - 每个像素都重要
2. **一致性** - 严格的视觉规范
3. **性能感** - 流畅动画、快速响应
4. **键盘优先** - 支持快捷键
5. **暗色优先** - 现代开发者习惯

## 适用场景

- 🏢 项目管理工具
- 💻 开发者工具
- 📊 数据仪表盘
- ⚡ 高端 SaaS 产品
- 🎯 效率工具

## 组件示例 HTML 结构

```html
<!-- 按钮 -->
<button class="linear-btn linear-btn-primary">主要</button>
<button class="linear-btn linear-btn-secondary">次要</button>
<button class="linear-btn linear-btn-ghost">幽灵</button>

<!-- 输入框 -->
<input class="linear-input" type="text" placeholder="输入">

<!-- 侧边栏 -->
<aside class="linear-sidebar">
  <div class="linear-sidebar-item">工作区</div>
  <div class="linear-sidebar-item">项目</div>
</aside>

<!-- 状态徽章 -->
<span class="linear-badge linear-badge-done">完成</span>
<span class="linear-badge linear-badge-cancel">已取消</span>

<!-- 模态框 -->
<div class="linear-modal">
  <div class="linear-modal-header">标题</div>
  <div class="linear-modal-body">内容</div>
</div>
```
