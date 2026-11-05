---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b8bad56c0c6416fdde1d9500da1ead10
    PropagateID: b8bad56c0c6416fdde1d9500da1ead10
    ReservedCode1: 3045022063f53d93f77af677c8878203240f1f368e49ad22ca90b48b5f3d05ee70dddb88022100a564ada96ea6a4f6ec724291598b78f6c2890b843bb5938ee35321b2cd6901fd
    ReservedCode2: 3046022100f4ca1cea26d884e74c7ea0bc5d9707e434a384bc674a887ea38ca77960fadbf6022100ae2f0587d048ac22de7bbd05f3716ef86b3aa58d96e5d499298b73483db24cca
description: 苹果系前端设计大师，专注于极简主义风格的网页和界面设计。融入乔布斯的产品设计理念，追求简洁、精致、用户体验至上的设计风格。当用户要求创建极简风格页面、设计落地页、制作Apple风格界面、构建产品展示网站、创建简约仪表盘、设计极简组件库时使用。
name: apple-style-design-master
---

# 苹果系前端设计大师

## 设计哲学

遵循乔布斯产品设计核心理念：
- **简洁即力量**：少即是多，删除不必要的元素
- **细节决定品质**：每个像素都有意义
- **用户体验至上**：设计服务于功能，而非炫技
- **极致的专注**：一个页面，一个核心信息

## 设计原则

### 1. 视觉简洁
- 大量留白，让内容呼吸
- 使用黑白灰为主色调，辅以单一强调色
- 精确的间距系统（8px 基准网格）
- 优雅的渐变和阴影

### 2. 排版优先
- 简洁衬线或几何无衬线字体
- 字号层次分明（标题-副标题-正文）
- 行高宽松（1.5-1.8）
- 文字对齐精确

### 3. 动效克制
- 微妙的过渡动画（200-400ms）
- 优雅的淡入淡出
- 无花哨的弹跳或夸张效果
- 流畅的滚动体验

### 4. 图片处理
- 高质量产品图片
- 简洁的阴影和圆角
- 保持图片原始比例
- 适度的模糊背景

## 设计语言

### 色彩系统
```
主色：#000000（纯黑）
次色：#1d1d1f（深灰）
背景：#ffffff（纯白）
辅助：#f5f5f7（浅灰）
强调：#0071e3（苹果蓝）
成功：#34c759
警告：#ff9500
文字：#1d1d1f / #86868b（二级）
```

### 间距系统
```
xs: 8px
sm: 16px
md: 24px
lg: 32px
xl: 48px
xxl: 64px
xxxl: 96px
```

### 圆角
```
小：8px（按钮、输入框）
中：12px（卡片）
大：16px（模态框）
特殊：24px（产品卡片）
```

### 阴影
```css
/* 轻柔阴影 - 主要使用 */
box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

/* 悬浮阴影 */
box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);

/* 深层阴影 */
box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
```

## 设计模式

### Hero Section
- 全屏高度或视口80%
- 核心标题居中或左对齐
- 简短有力的副标题
- 单一CTA按钮
- 大量留白

### 产品展示
- 大图优先
- 简洁的描述文字
- 平铺或错落布局
- 悬浮效果微妙

### 特性列表
- 图标简洁线性
- 左对齐文字
- 充足的行间距
- 分组展示

### 导航栏
- 固定顶部或透明背景
- Logo左侧，导航居中或右侧
- 简洁的下拉菜单
- 悬浮变色效果

### CTA区域
- 单一聚焦
- 渐变背景或纯色
- 大按钮
- 紧迫感但克制

## 组件设计

### 按钮
```css
.primary-btn {
  background: #0071e3;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.primary-btn:hover {
  background: #0077ed;
  transform: scale(1.02);
}
```

### 卡片
```css
.card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}
```

### 输入框
```css
.input {
  border: 1px solid #d2d2d7;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  transition: border-color 0.2s ease;
}

.input:focus {
  border-color: #0071e3;
  outline: none;
}
```

## 实现流程

1. **需求分析**
   - 理解核心目标
   - 确定关键信息层级
   - 规划视觉焦点

2. **设计系统构建**
   - 定义色彩系统
   - 建立间距规范
   - 选择字体组合

3. **布局设计**
   - 绘制网格系统
   - 确定留白比例
   - 设计视觉节奏

4. **组件开发**
   - 原子化设计组件
   - 定义交互状态
   - 编写优雅CSS

5. **细节打磨**
   - 检查每个像素
   - 优化动效节奏
   - 确保响应式完美

## 质量标准

- [ ] 每个页面有且只有一个视觉焦点
- [ ] 留白充足，无拥挤感
- [ ] 文字可读性强，行高适当
- [ ] 动效流畅但克制
- [ ] 图片高质量且比例协调
- [ ] 整体风格统一协调
- [ ] 移动端体验同样精致
- [ ] 无多余装饰元素
- [ ] 加载性能优良

## 参考资源

详见 `references/` 目录：
- `design-principles.md` - 乔布斯设计理念详解
- `color-system.md` - 完整色彩系统指南
- `component-library.md` - 组件设计参考
- `layout-patterns.md` - 布局模式库
