---
name: website-builder
description: 创建完整的专业网站和Web应用。当用户要求创建网站、制作网页、开发Web应用、落地页、个人主页、企业网站、电商网站、博客、作品集或任何在线应用时使用。支持响应式设计、现代UI/UX和前后端集成。
---

# Website Builder

全栈网站制作技能 - 从概念到上线的完整解决方案

## 核心能力

### 1. 响应式前端开发
- HTML5 语义化结构
- Tailwind CSS 现代化样式
- Vanilla JavaScript 交互逻辑
- 跨设备兼容（桌面/平板/手机）

### 2. 组件库
| 组件 | 描述 |
|------|------|
| 导航栏 | 固定/响应式顶部导航 |
| 英雄区 | 全屏首屏展示 |
| 卡片网格 | 产品/服务展示 |
| 表单 | 联系/注册/登录 |
| 页脚 | 多栏页脚 |
| 图库 | 图片展示 |
| 定价表 | 价格方案展示 |
| 特性展示 | 特色功能介绍 |

### 3. 设计模式
- 极简主义设计
- 企业官网设计
- 作品集/简历设计
- 电商产品展示
- 博客/内容站
- 落地页高转化设计

## 工作流程

### Phase 1: 需求分析
```
收集信息 → 确定类型 → 制定方案
```

**必问问题**:
1. 网站类型？（企业官网/电商/作品集/博客/落地页）
2. 主要功能？（展示/交易/收集信息/品牌宣传）
3. 目标受众？（年龄/行业/技术背景）
4. 风格偏好？（现代/传统/创意/简约）
5. 是否有参考网站？

### Phase 2: 架构设计
```
选择模板 → 规划页面 → 定义主题
```

**页面规划模板**:
- 首页 + 关于 + 服务/产品 + 联系方式（4页标准）
- 首页 + 关于 + 服务 + 案例 + 博客 + 联系（6页企业）
- 自定义页面结构

### Phase 3: 组件开发
```
页面结构 → 样式设计 → 交互实现
```

**开发优先级**:
1. HTML结构（语义化标签）
2. Tailwind CSS样式（响应式）
3. JavaScript交互（动画/表单）

### Phase 4: 内容填充
```
品牌元素 → 文案内容 → 视觉资源
```

### Phase 5: 测试验证
```
多浏览器测试 → 响应式测试 → 功能测试
```

### Phase 6: 部署上线
```
构建优化 → 部署 → 最终验证
```

## 项目结构模板

```
project/
├── index.html          # 主页面
├── about.html          # 关于页
├── contact.html        # 联系页
├── css/
│   └── custom.css      # 自定义样式
├── js/
│   └── main.js         # 交互逻辑
└── assets/
    ├── images/         # 图片资源
    └── icons/         # SVG图标
```

## 常用技术栈组合

### 方案A: 极简静态站
- HTML5 + Tailwind CSS
- Vanilla JavaScript
- 无需构建工具

### 方案B: 功能型站点
- React + Tailwind CSS
- Vite 构建
- 组件化开发

### 方案C: 内容管理系统
- 静态站点生成
- Markdown 内容
- 自动化部署

## 质量标准

### 视觉质量
- [ ] 所有图片使用 HTTPS URL
- [ ] Tailwind CSS 类名规范
- [ ] 间距/对齐一致性
- [ ] 色彩对比度符合 WCAG

### 功能质量
- [ ] 所有链接可点击
- [ ] 表单有完整验证
- [ ] 动画流畅无卡顿
- [ ] 移动端交互友好

### 性能质量
- [ ] 首屏加载 < 3秒
- [ ] 图片懒加载
- [ ] CSS/JS 最小化
- [ ] 使用 CDN 资源

## 快速启动模板

### 单页网站模板
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网站标题</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <!-- 导航栏 -->
    <nav class="fixed w-full bg-white/90 backdrop-blur-sm z-50 border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="text-xl font-bold">Logo</div>
                <div class="hidden md:flex space-x-8">
                    <a href="#home" class="hover:text-blue-600">首页</a>
                    <a href="#features" class="hover:text-blue-600">功能</a>
                    <a href="#contact" class="hover:text-blue-600">联系</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- 英雄区 -->
    <section id="home" class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div class="text-center px-4">
            <h1 class="text-5xl font-bold mb-6">主标题</h1>
            <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">副标题描述</p>
            <a href="#contact" class="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition">
                立即开始
            </a>
        </div>
    </section>

    <!-- 功能区 -->
    <section id="features" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4">
            <h2 class="text-3xl font-bold text-center mb-12">核心功能</h2>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="p-6 rounded-xl bg-gray-50 hover:shadow-lg transition">
                    <div class="w-12 h-12 bg-blue-100 rounded-lg mb-4"></div>
                    <h3 class="text-xl font-semibold mb-2">功能一</h3>
                    <p class="text-gray-600">功能描述</p>
                </div>
            </div>
        </div>
    </section>

    <!-- 联系区 -->
    <section id="contact" class="py-20 bg-gray-900 text-white">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <h2 class="text-3xl font-bold mb-8">联系我们</h2>
            <p class="text-gray-400 mb-8">准备好开始了吗？</p>
            <a href="mailto:hello@example.com" class="inline-block bg-white text-gray-900 px-8 py-3 rounded-lg hover:bg-gray-100 transition">
                发送邮件
            </a>
        </div>
    </section>

    <!-- 页脚 -->
    <footer class="bg-gray-900 text-gray-400 py-8">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <p>&copy; 2024 公司名称. 保留所有权利.</p>
        </div>
    </footer>

    <script>
        // 平滑滚动
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>
```

## 常用 Tailwind CSS 工具类速查

### 布局
- `container mx-auto` - 居中容器
- `flex items-center justify-between` - 弹性布局
- `grid grid-cols-1 md:grid-cols-3` - 响应式网格

### 间距
- `p-4` / `px-4` / `py-4` - 内边距
- `m-4` / `mx-auto` - 外边距
- `space-y-4` - 子元素间距

### 文字
- `text-xs/sm/base/lg/xl/2xl/3xl/4xl` - 字号
- `font-light/normal/semibold/bold` - 字重
- `text-left/center/right` - 对齐

### 颜色
- `text-gray-500` / `bg-white` / `border-gray-200`
- 完整色系: gray, red, orange, yellow, green, blue, indigo, purple, pink

### 响应式
- `sm:` (640px) - 小屏
- `md:` (768px) - 中屏
- `lg:` (1024px) - 大屏
- `xl:` (1280px) - 超大屏

### 动画
- `transition` - 过渡效果
- `duration-300` - 过渡时长
- `hover:scale-105` - 悬停缩放
- `animate-pulse` - 脉冲动画

## 输出要求

**部署**: 所有网站必须使用 `deploy` 工具部署

**交付格式**:
```xml
<deliver_assets>
<item>
<path>https://deployed-site-url.com</path>
<name>网站名称</name>
<screenshot>https://screenshot-url</screenshot>
</item>
</deliver_assets>
```

## 触发检查

确保以下情况触发本技能：
- 用户说"创建一个网站"
- 用户说"制作一个网页"
- 用户说"开发一个Web应用"
- 用户说"帮我做一个落地页"
- 用户说"做一个个人主页"
- 用户说"搭建企业官网"
- 用户说"做一个电商网站"
- 任何涉及网站/Web开发的需求

**不触发情况**:
- 纯内容写作（无网站结构）
- API开发（无前端界面）
- 移动App开发（非Web）
