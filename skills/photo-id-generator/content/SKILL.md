---
name: photo-id-generator
description: 证件照生成器。当用户上传人像照片时，自动裁切头像、替换背景（蓝底/白底）、生成1寸和2寸证件照，支持轻度美颜，提供4张证件照供选择下载。
---

# 证件照生成器 (Photo ID Generator)

## 1. Concept & Vision

一款轻量级、易用的在线证件照生成工具。用户只需上传一张人像照片，系统自动完成人像识别、背景替换、尺寸裁切和轻度美颜，生成4张标准证件照供选择。整体风格简洁专业，强调"即传即得"的便捷体验。

## 2. Design Language

### Aesthetic Direction
- **风格**: 现代极简主义，参考政府证件服务的专业感
- **情绪**: 可信赖、高效、亲切

### Color Palette
- Primary: `#2563EB` (专业蓝)
- Secondary: `#1E40AF` (深蓝)
- Accent: `#10B981` (成功绿)
- Background: `#F8FAFC` (浅灰白)
- Surface: `#FFFFFF` (纯白)
- Text Primary: `#1E293B` (深灰)
- Text Secondary: `#64748B` (中灰)
- Border: `#E2E8F0` (边框灰)

### Typography
- Font Family: `"Inter", "PingFang SC", "Microsoft YaHei", sans-serif`
- Headings: 600-700 weight
- Body: 400-500 weight
- Scale: 14px base, 1.5 line-height

### Spatial System
- Base unit: 8px
- Padding: 16px / 24px / 32px
- Border radius: 8px (cards), 12px (buttons), 16px (modals)
- Shadows: `0 1px 3px rgba(0,0,0,0.1)`, `0 4px 12px rgba(0,0,0,0.15)`

### Motion Philosophy
- Transitions: 200-300ms ease-out
- Loading states: 脉冲动画
- Success feedback: 轻微弹跳 + checkmark 动画

## 3. Layout & Structure

### Page Structure
```
┌─────────────────────────────────────────┐
│  Header (Logo + Title)                  │
├─────────────────────────────────────────┤
│  Upload Area (拖拽上传 + 点击选择)        │
├─────────────────────────────────────────┤
│  Photo Preview (原始照片预览)            │
│  Background Selection (蓝/白底切换)     │
│  Size Selection (1寸/2寸)               │
│  Beauty Slider (美颜强度)                │
├─────────────────────────────────────────┤
│  Generate Button                        │
├─────────────────────────────────────────┤
│  Result Grid (4张证件照展示)             │
│  Download Options (单张/全部下载)         │
├─────────────────────────────────────────┤
│  Footer (使用说明)                       │
└─────────────────────────────────────────┘
```

### Responsive Strategy
- Desktop: 居中布局，最大宽度 800px
- Tablet: 全宽，padding 调整为 16px
- Mobile: 单列布局，照片 grid 改为 2x2

## 4. Features & Interactions

### Core Features

#### 4.1 Image Upload
- 支持拖拽上传和点击选择
- 支持格式: JPG, PNG, WEBP
- 文件大小限制: 10MB
- 上传后即时预览

#### 4.2 Face Detection & Cropping
- 自动检测人脸位置
- 智能裁切（头部占比约70-80%）
- 保持适当的头顶和肩部空间

#### 4.3 Background Replacement
- **蓝底**: RGB(67, 142, 219) - 标准证件照蓝
- **白底**: RGB(255, 255, 255) - 纯白
- 使用色彩替换算法，自动识别前景和背景

#### 4.4 Size Options
- **1寸**: 25mm × 35mm (295 × 413 px @300dpi)
- **2寸**: 35mm × 53mm (413 × 626 px @300dpi)

#### 4.5 Beauty Enhancement
- 轻度磨皮（柔和处理）
- 轻微亮度调整
- 强度: 0-3档（默认1档）
- **原则**: 自然真实，不过度美颜

#### 4.6 Photo Export
- 生成4张证件照:
  1. 蓝底 1寸
  2. 白底 1寸
  3. 蓝底 2寸
  4. 白底 2寸
- 支持单张下载和全部下载
- 文件命名: `证件照_[尺寸]_[底色].jpg`

### Interaction Details

#### Upload Area
- Default: 虚线边框 + 上传图标 + 提示文字
- Hover: 边框颜色变深，显示"松开上传"
- Dragging: 背景色变蓝，显示拖拽提示
- Error: 红色边框 + 错误提示信息

#### Generate Button
- Default: 蓝色背景 + 白色文字
- Hover: 背景色加深
- Loading: 显示旋转图标 + "处理中..."
- Disabled: 灰色背景，不可点击

#### Result Photos
- Hover: 显示下载图标
- Click: 弹出大图预览
- Download: 点击下载按钮触发下载

### Error Handling
- 文件过大: 提示文件大小限制
- 格式不支持: 提示支持的格式
- 未检测到人脸: 提示上传清晰人像
- 处理失败: 显示具体错误信息

### Edge Cases
- 图片中人脸过小: 提示"请上传更清晰的人像"
- 图片中人脸过多: 提示"请上传单人照片"
- 人脸被遮挡: 提示"请上传无遮挡的人像"

## 5. Component Inventory

### UploadCard
- States: default, hover, dragging, uploading, error, success
- Icon: 上传箭头
- Text: 提示文案

### PhotoPreview
- 显示原图预览
- 支持缩放和拖拽查看

### BackgroundSelector
- Radio group with preview swatches
- States: selected (border + checkmark), unselected

### SizeSelector
- Radio group with size labels
- States: selected, unselected, hover

### BeautySlider
- Range slider (0-3)
- Labels: 关闭, 轻度, 中度, 强效
- Current value indicator

### GenerateButton
- States: default, hover, loading, disabled, success
- Loading: Spinner + "处理中..."
- Success: Checkmark + "完成"

### PhotoCard
- Thumbnail display
- Overlay with download button on hover
- Size and background info label

### DownloadModal
- Large preview image
- Download button
- Close button

## 6. Technical Approach

### Architecture
- 单页应用 (SPA)
- 纯前端实现，无需后端
- 使用 Canvas API 进行图像处理

### Image Processing Pipeline
```
1. Load Image → 2. Face Detection → 3. Smart Crop →
4. Background Replace → 5. Beauty Enhancement →
6. Size Generation → 7. Export
```

### Face Detection Strategy
- 使用浏览器原生功能或简化的肤色/特征检测
- 备选: 简单的人脸定位算法（基于肤色和形状）

### Background Replacement Algorithm
- 基于颜色阈值的前景/背景分离
- 边缘平滑处理避免硬边
- 色彩匹配确保自然过渡

### Beauty Enhancement
- 轻度高斯模糊实现磨皮
- 轻微对比度/亮度调整
- 边缘保持滤波

### Output Format
- JPEG (quality: 0.92)
- 标准证件照分辨率

### Browser Compatibility
- Chrome 80+
- Firefox 75+
- Safari 14+
- Edge 80+
