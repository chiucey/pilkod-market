# 大厂设计规范核心要素

## 设计系统三层架构

### Foundation（基础层）
定义视觉基调，解决"长什么样"的问题。

#### 色彩系统
- **主色（Primary）**：品牌核心色，用于主按钮、关键操作、导航高亮
- **功能色（Functional）**：
  - 成功 Success: #52C41A（Ant）/ #4CAF50（Material）
  - 警告 Warning: #FAAD14 / #FF9800
  - 错误 Error: #F5222D / #F44336
  - 信息 Info: #1890FF / #2196F3
- **中性色（Neutral）**：
  - 标题文字 #262626 / #212121
  - 正文文字 #595959 / #616161
  - 次要文字 #8C8C8C / #9E9E9E
  - 禁用文字 #BFBFBF / #BDBDBD
  - 边框 #D9D9D9 / #E0E0E0
  - 分割线 #F0F0F0 / #EEEEEE
  - 背景 #F5F5F5 / #F5F5F5
- **扩展色板**：按 50-100-200-300-400-500-600-700-800-900 梯度生成

#### 字体系统
- **字体栈**：
  - 中文：-apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei"
  - 英文/数字："SF Pro Display", "Segoe UI", Roboto, "Helvetica Neue"
- **字号阶梯**（以 14px 为基准）：
  - 展示级：56px/64px/72px（hero区域、大标题）
  - 标题级：38px/30px/24px/20px（页面标题、模块标题）
  - 正文级：16px/14px/13px（正文、表单、表格）
  - 辅助级：12px/11px（标签、时间戳、角标）
- **字重**：Regular(400), Medium(500), Semibold(600), Bold(700)
- **行高**：标题 1.4x，正文 1.5x-1.6x，紧凑场景 1.2x

#### 间距系统
基于 4px/8px 原子单位：
- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, xxl: 48px
- 模块间距：24-32-48px
- 卡片内边距：16-20-24px
- 表单间距：16-24px

#### 圆角系统
- 0px：直角，用于表格、数据面板
- 2px/4px：微圆角，按钮、输入框
- 6px/8px：标准圆角，卡片、弹窗
- 12px/16px：大圆角，图片、特殊卡片
- 999px：全圆角，标签、胶囊按钮

#### 阴影系统
- 阴影1（静态）：0 1px 2px rgba(0,0,0,0.05) - 卡片默认
- 阴影2（悬停）：0 4px 12px rgba(0,0,0,0.1) - 卡片悬停
- 阴影3（浮层）：0 8px 24px rgba(0,0,0,0.12) - 下拉菜单、弹窗
- 阴影4（模态）：0 16px 48px rgba(0,0,0,0.15) - 模态框

#### 动效规范
- 时长：快速 150ms，标准 200-250ms，缓慢 300-400ms
- 缓动：ease-out（入场），ease-in（退场），ease-in-out（状态切换）
- 变换：opacity + transform(translate/scale) 组合

### Component（组件层）
解决"单点操作怎么做"的问题。

见 component-library.md 完整组件定义。

### Pattern（模式层）
解决"场景化怎么做"的问题。

见 layout-patterns.md 完整模式定义。

## 大厂设计系统参考

| 设计系统 | 特点 | 适用场景 |
|---------|------|---------|
| Ant Design | 企业级中后台，组件丰富，中文生态完善 | B端管理后台、数据中台、表单密集 |
| Material Design | 拟物隐喻， elevation 层级，动效丰富 | C端应用、移动端、现代化界面 |
| Apple HIG | 简洁优雅，留白多，注重内容 | iOS/macOS 应用、内容展示型 |
| Microsoft Fluent | 深度感，亚克力材质，光线效果 | Windows 应用、生产力工具 |
| IBM Carbon | 理性克制，数据驱动，可访问性强 | 企业级应用、数据密集型 |
