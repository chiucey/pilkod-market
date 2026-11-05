# ElevenLabs Design System

ElevenLabs 的 AI 语音设计语言。

## 设计理念

ElevenLabs 追求**声音**、**清晰**、**创意**。服务于 AI 语音合成。

## 色彩系统

### 品牌色
- Primary: `#A132E6` (ElevenLabs 紫)
- Primary Light: `#B85AE8`
- Primary Dark: `#8B2BC9`

### 背景色

#### 浅色模式
- Background: `#FAFAFA`
- Background Secondary: `#F0ECF5`
- Background Card: `#FFFFFF`

#### 深色模式
- Background Dark: `#121218`
- Background Dark Secondary: `#1C1C24`
- Background Dark Card: `#262630`

### 文字色

#### 浅色模式
- Text Primary: `#1A1A2E`
- Text Secondary: `#5C5C72`
- Text Tertiary: `#9090A0`

#### 深色模式
- Text Dark Primary: `#EDEDF5`
- Text Dark Secondary: `#A0A0B0`
- Text Dark Tertiary: `#6B6B80`

### 功能色
- Success: `#10B981`
- Warning: `#F5A623`
- Error: `#EF4444`
- Wave: `#A132E6` (波形颜色)

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 32px
- H1: 24px
- H2: 18px
- Body: 15px
- Small: 13px

## 间距系统

基于 8px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

## 圆角

- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px

## 组件样式

### 按钮

**主要按钮**
- Background: `#A132E6`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 40px

**次要按钮**
- Background: `#F0ECF5`
- Color: `#1A1A2E`

### 波形可视化

- 波形颜色: `#A132E6`
- 背景: `#1C1C24`
- 圆角: 8px

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E0E0E8`
- Border Radius: 8px
- Height: 44px
- Focus Border: `#A132E6`

## 适用场景

- 🎙️ 语音合成
- 🎧 音频产品
- 🗣️ 语音克隆
- 📖 有声书

## 组件示例 HTML 结构

```html
<button class="elevenlabs-btn-primary">生成语音</button>
<div class="elevenlabs-waveform">波形可视化</div>
<input class="elevenlabs-input" type="text" placeholder="输入文本">
```
