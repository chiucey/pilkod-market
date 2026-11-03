---
name: blog-website-generator
description: 创建简洁美观的Blog网站，完美支持移动端。当用户要求开发个人博客、文章展示网站、图片文字展示网站，或需要移动端适配、响应式设计时使用。关键词：blog、网站、博客、个人网站、文章展示、图片展示、移动端、响应式、mobile。
---

# Blog 网站开发技能

基于 React + Vite + Tailwind CSS 的现代化 Blog 网站解决方案，**移动端优先（Mobile-First）** 设计。

## 技术栈选择

| 组件 | 技术方案 | 优势 |
|------|----------|------|
| 框架 | React 18 | 生态成熟、社区庞大 |
| 构建工具 | Vite | 极速启动、HMR热更新 |
| 样式方案 | Tailwind CSS | 原子化CSS、响应式内置 |
| 部署 | 静态部署 | 免服务器、成本低 |

## 网站结构

```
blog-website/
├── src/
│   ├── components/     # 组件
│   │   ├── Header.jsx       # 顶部导航（含汉堡菜单）
│   │   ├── MobileMenu.jsx   # 移动端菜单
│   │   ├── Footer.jsx       # 底部
│   │   ├── PostCard.jsx     # 文章卡片
│   │   └── Layout.jsx       # 布局组件
│   ├── hooks/           # 自定义Hook
│   │   └── useMobile.js    # 移动端检测
│   ├── pages/           # 页面
│   │   ├── Home.jsx        # 首页
│   │   ├── Blog.jsx        # 博客列表
│   │   └── Post.jsx        # 文章详情
│   ├── data/            # 数据
│   │   └── posts.js        # 文章数据
│   ├── App.jsx
│   └── main.jsx
├── public/
├── index.html
├── tailwind.config.js
└── package.json
```

## 响应式断点系统

Tailwind CSS 默认断点：

| 前缀 | 最小宽度 | 典型设备 |
|------|----------|----------|
| 无 | 0px | 手机 (<640px) |
| `sm:` | 640px | 大手机/小平板 |
| `md:` | 768px | 平板 |
| `lg:` | 1024px | 笔记本电脑 |
| `xl:` | 1280px | 桌面显示器 |
| `2xl:` | 1536px | 大屏显示器 |

## 执行流程

### 1. 初始化项目

```bash
npm create vite@latest blog-website -- --template react
cd blog-website
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2. 配置 Tailwind CSS（含移动端优化）

更新 `tailwind.config.js`：

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
      },
    },
  },
  plugins: [],
}
```

添加全局样式到 `src/index.css`：

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 移动端优化 */
@layer base {
  html {
    -webkit-tap-highlight-color: transparent;
  }

  body {
    @apply bg-gray-50 text-gray-800 antialiased;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* 禁用iOS缩放 */
  @media screen and (max-width: 768px) {
    html {
      font-size: 16px;
    }
  }
}

/* 安全区域适配（iPhone刘海屏） */
.safe-area-top {
  padding-top: env(safe-area-inset-top);
}
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}
```

### 3. 添加移动端检测 Hook

创建 `src/hooks/useMobile.js`：

```javascript
import { useState, useEffect } from 'react';

export function useMobile(breakpoint = 768) {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < breakpoint);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [breakpoint]);

  return isMobile;
}
```

### 4. 组件开发顺序（移动端优先）

1. **Layout 组件** - 提供统一页面框架（含安全区域）
2. **MobileMenu 组件** - 移动端抽屉菜单
3. **Header 组件** - 响应式导航栏
4. **Footer 组件** - 页脚
5. **PostCard 组件** - 响应式文章卡片
6. **页面组件** - Home / Blog / Post

### 5. 响应式组件示例

#### Header.jsx（含汉堡菜单）
```jsx
import { useState } from 'react';
import { useMobile } from '../hooks/useMobile';
import MobileMenu from './MobileMenu';

export default function Header() {
  const isMobile = useMobile();
  const [menuOpen, setMenuOpen] = useState(false);

  const navLinks = [
    { name: '首页', href: '/' },
    { name: '博客', href: '/blog' },
    { name: '关于', href: '/about' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100 safe-area-top">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="text-xl font-bold text-gray-900">
          My Blog
        </a>

        {/* 桌面端导航 */}
        {!isMobile && (
          <nav className="flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-gray-600 hover:text-blue-600 transition-colors"
              >
                {link.name}
              </a>
            ))}
          </nav>
        )}

        {/* 移动端汉堡菜单按钮 */}
        {isMobile && (
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-2 -mr-2 text-gray-600 hover:text-gray-900"
            aria-label="菜单"
          >
            {menuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        )}
      </div>

      {/* 移动端菜单 */}
      {isMobile && <MobileMenu links={navLinks} isOpen={menuOpen} onClose={() => setMenuOpen(false)} />}
    </header>
  );
}
```

#### MobileMenu.jsx（移动端抽屉）
```jsx
import { useEffect } from 'react';

export default function MobileMenu({ links, isOpen, onClose }) {
  // 防止背景滚动
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-40">
      {/* 背景遮罩 */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* 菜单面板 */}
      <nav className="absolute top-14 left-0 right-0 bg-white shadow-lg safe-area-bottom">
        <div className="px-4 py-4 space-y-1">
          {links.map((link) => (
            <a
              key={link.name}
              href={link.href}
              onClick={onClose}
              className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg active:bg-gray-100 transition-colors"
            >
              {link.name}
            </a>
          ))}
        </div>
      </nav>
    </div>
  );
}
```

#### PostCard.jsx（响应式卡片）
```jsx
export default function PostCard({ post }) {
  return (
    <article className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden">
      {/* 封面图 - 移动端保持比例 */}
      {post.cover && (
        <div className="aspect-video overflow-hidden">
          <img
            src={post.cover}
            alt={post.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
      )}

      <div className="p-4 sm:p-6">
        {/* 标题 - 移动端字号略小 */}
        <h3 className="text-lg sm:text-xl font-semibold mb-2 text-gray-900 line-clamp-2">
          {post.title}
        </h3>

        {/* 摘要 */}
        <p className="text-gray-600 text-sm sm:text-base mb-4 line-clamp-2 sm:line-clamp-3">
          {post.excerpt}
        </p>

        {/* 元信息 - 移动端垂直排列 */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <span className="text-sm text-gray-500">{post.date}</span>
          <span className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded-full inline-block">
            {post.category}
          </span>
        </div>
      </div>
    </article>
  );
}
```

#### Home.jsx（响应式网格布局）
```jsx
import Layout from '../components/Layout';
import PostCard from '../components/PostCard';
import { useMobile } from '../hooks/useMobile';

export default function Home({ posts }) {
  const isMobile = useMobile();

  return (
    <Layout>
      {/* Hero区域 - 移动端简化 */}
      <section className="mb-8 sm:mb-12 text-center sm:text-left">
        <h1 className="text-2xl sm:text-4xl font-bold text-gray-900 mb-4">
          欢迎访问我的博客
        </h1>
        <p className="text-gray-600 text-sm sm:text-base">
          分享技术与生活，记录成长足迹
        </p>
      </section>

      {/* 文章列表 - 响应式网格 */}
      <section>
        <h2 className="text-lg sm:text-xl font-semibold mb-4">最新文章</h2>

        {/* 移动端单列，桌面端多列 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      </section>
    </Layout>
  );
}
```

#### Post.jsx（文章详情 - 阅读体验优化）
```jsx
import Layout from '../components/Layout';

export default function PostDetail({ post }) {
  return (
    <Layout>
      <article className="bg-white rounded-xl shadow-sm overflow-hidden">
        {/* 封面图 */}
        {post.cover && (
          <div className="aspect-video overflow-hidden">
            <img
              src={post.cover}
              alt={post.title}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        <div className="p-4 sm:p-8 lg:p-12">
          {/* 标题 */}
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            {post.title}
          </h1>

          {/* 元信息 */}
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-8 pb-8 border-b">
            <span>{post.date}</span>
            <span>{post.author}</span>
            <span className="text-blue-600">{post.category}</span>
          </div>

          {/* 文章内容 - 移动端优化阅读宽度 */}
          <div className="prose prose-sm sm:prose-base lg:prose-lg max-w-none
                        prose-headings:text-gray-900
                        prose-p:text-gray-700
                        prose-a:text-blue-600
                        prose-img:rounded-lg
                        prose-li:text-gray-700">
            {post.content}
          </div>

          {/* 底部标签 */}
          {post.tags && (
            <div className="flex flex-wrap gap-2 mt-8 pt-8 border-t">
              {post.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded-full"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </article>
    </Layout>
  );
}
```

### 6. 构建部署

```bash
npm run build
```

构建产物在 `dist/` 目录，可直接部署到静态托管服务。

## 移动端优化清单

### 视口配置
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
```

### 触摸友好设计
| 要求 | 最小尺寸 | 实现方式 |
|------|----------|----------|
| 点击目标 | 44x44px | `min-h-11 min-w-11` |
| 按钮内边距 | 12px | `px-3 py-2` |
| 链接间距 | 8px | `gap-2` |

### 图片优化
```jsx
// 使用懒加载
<img loading="lazy" />

// 使用 srcset 响应式图片
<img
  srcSet="small.jpg 400w, medium.jpg 800w, large.jpg 1200w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
/>
```

### 性能优化
- 使用 `loading="lazy"` 延迟加载图片
- 使用 `content-visibility` 优化长列表
- 启用 Gzip 压缩
- 图片使用 WebP 格式

### iOS 特殊处理
- 安全区域：`env(safe-area-inset-*)`
- 禁用双击缩放：`-webkit-text-size-adjust: none`
- 圆角按钮：`border-radius: 12px` 避免iOS圆角裁剪

## 设计规范

### 配色方案
- 主色：`#3B82F6` (蓝色)
- 背景：`#F9FAFB` (浅灰)
- 卡片：`#FFFFFF` (白色)
- 文字：`#1F2937` (深灰)
- 辅助：`#6B7280` (中灰)

### 字体规范
| 场景 | 桌面端 | 移动端 |
|------|--------|--------|
| 标题H1 | 36-48px | 24-32px |
| 标题H2 | 24-30px | 18-24px |
| 正文 | 16px | 16px |
| 辅助文字 | 14px | 14px |

### 间距系统
| 场景 | 桌面端 | 移动端 |
|------|--------|--------|
| 页面内边距 | 32-64px | 16px |
| 卡片间距 | 24px | 16px |
| 组件内间距 | 24px | 16px |

## 验收标准

- [ ] 移动端导航汉堡菜单正常工作
- [ ] 文章列表在移动端单列、桌面端多列显示
- [ ] 触摸目标尺寸 >= 44x44px
- [ ] iPhone刘海屏安全区域适配
- [ ] 图片懒加载配置
- [ ] 触摸反馈（active状态）
- [ ] 无双击缩放问题
- [ ] 构建产物可正常部署
