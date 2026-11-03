# 设计风格预设参考

本文件包含 10 种精选的视觉风格预设，每种风格都有完整的配色方案、字体建议和 CSS 模板。

---

## 深色主题（Dark Themes）

### 1. Neon Cyber（霓虹赛博）

**风格定位**：未来科技感、数字朋克、粒子效果

**配色方案**：
```css
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --text-primary: #ffffff;
    --text-secondary: #8b8ba0;
    --accent-primary: #00ffff;
    --accent-secondary: #ff00ff;
    --accent-tertiary: #00ff88;
}
```

**适用场景**：科技发布会、AI/区块链产品演示、开发者大会

**设计要点**：
- 使用 CSS 渐变创建霓虹光晕效果
- 添加微妙的网格背景图案
- 霓虹色文字使用 text-shadow 产生发光效果
- 过渡动画使用弹性缓动函数（cubic-bezier）

**代码片段**：
```css
.glow-text {
    color: var(--accent-primary);
    text-shadow:
        0 0 10px var(--accent-primary),
        0 0 20px var(--accent-primary),
        0 0 40px var(--accent-primary);
}

.grid-bg {
    background-image:
        linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}
```

---

### 2. Midnight Executive（午夜 executive）

**风格定位**：高端企业风、专业严谨、可信赖

**配色方案**：
```css
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --text-primary: #f0f6fc;
    --text-secondary: #8b949e;
    --accent: #58a6ff;
    --accent-secondary: #1f6feb;
    --border: rgba(240, 246, 252, 0.1);
}
```

**适用场景**：商务汇报、投资路演、企业培训、正式会议

**设计要点**：
- 干净的线条和微妙的光影效果
- 大量留白，信息层次分明
- 使用微妙的渐变增加深度感
- 保持专业的视觉重量

**代码片段**：
```css
.card {
    background: linear-gradient(145deg, var(--bg-secondary), var(--bg-primary));
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
```

---

### 3. Deep Space（深邃宇宙）

**风格定位**：电影感、浩瀚神秘、引人遐想

**配色方案**：
```css
:root {
    --bg-primary: #050510;
    --bg-secondary: #0a0a1a;
    --text-primary: #e8e8f0;
    --text-secondary: #7070a0;
    --accent: #6366f1;
    --accent-glow: #818cf8;
    --star-color: rgba(255, 255, 255, 0.8);
}
```

**适用场景**：太空主题演讲、品牌故事、产品愿景展示

**设计要点**：
- 添加星星粒子效果（可用 Canvas 或 CSS 实现）
- 使用深蓝到紫的渐变背景
- 文字使用柔和的高对比度
- 动画使用缓慢、流畅的过渡

**代码片段**：
```css
.cosmic-bg {
    background:
        radial-gradient(ellipse at 20% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(129, 140, 248, 0.1) 0%, transparent 50%),
        linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

.fade-in {
    animation: fadeIn 1.5s ease-out forwards;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
```

---

### 4. Terminal Green（终端绿）

**风格定位**：开发者风格、极客美学、技术硬核

**配色方案**：
```css
:root {
    --bg-primary: #0c0c0c;
    --bg-secondary: #1a1a1a;
    --text-primary: #00ff00;
    --text-secondary: #00cc00;
    --text-muted: #008800;
    --cursor: #00ff00;
    --scanline: rgba(0, 255, 0, 0.03);
}
```

**适用场景**：技术分享、代码演示、黑客松展示、开源项目介绍

**设计要点**：
- 添加 CRT 显示器的扫描线效果
- 使用等宽字体（如 JetBrains Mono、Fira Code）
- 文字闪烁的游标效果
- 简洁的边框和分隔线

**代码片段**：
```css
.terminal-text {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    text-shadow: 0 0 5px var(--text-primary);
}

.scanlines::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        var(--scanline) 0px,
        var(--scanline) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
}

.cursor::after {
    content: '█';
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
```

---

## 浅色主题（Light Themes）

### 5. Paper & Ink（纸与墨）

**风格定位**：编辑风格、文学气息、精致典雅

**配色方案**：
```css
:root {
    --bg-primary: #faf9f7;
    --bg-secondary: #ffffff;
    --text-primary: #1a1a1a;
    --text-secondary: #4a4a4a;
    --accent: #c45c3e;
    --accent-secondary: #8b4513;
    --border: #e5e0dc;
}
```

**适用场景**：文学演讲、书籍发布、教育培训、艺术展示

**设计要点**：
- 使用衬线字体（如 Noto Serif SC、Source Serif Pro）
- 添加微妙的纸张纹理
- 精致的边框和装饰线
- 优雅的过渡动画

**代码片段**：
```css
.paper-texture {
    background-color: var(--bg-primary);
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    background-blend-mode: soft-light;
}

blockquote {
    border-left: 3px solid var(--accent);
    padding-left: 1.5rem;
    font-style: italic;
    color: var(--text-secondary);
}
```

---

### 6. Swiss Modern（瑞士现代）

**风格定位**：极简几何、Bauhaus 风格、理性之美

**配色方案**：
```css
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f5;
    --text-primary: #000000;
    --text-secondary: #666666;
    --accent: #e63946;
    --accent-secondary: #1d3557;
    --line: #000000;
}
```

**适用场景**：现代艺术、建筑展示、设计理念演讲

**设计要点**：
- 大量使用几何形状（圆形、方形、三角形）
- 粗体排版，高对比度
- 使用网格系统布局
- 强调线条和边框

**代码片段**：
```css
.geometric-accent {
    position: relative;
}

.geometric-accent::before {
    content: '';
    position: absolute;
    width: 60px;
    height: 60px;
    border: 4px solid var(--accent);
    border-radius: 50%;
    top: -20px;
    left: -20px;
    z-index: -1;
}

.grid-layout {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 20px;
}
```

---

### 7. Soft Pastel（柔和粉彩）

**风格定位**：友好活泼、创意十足、轻松愉悦

**配色方案**：
```css
:root {
    --bg-primary: #fef9f3;
    --bg-secondary: #fffbf5;
    --text-primary: #3d3d3d;
    --text-secondary: #6b6b6b;
    --accent-peach: #ffb5a7;
    --accent-sage: #b8d4c8;
    --accent-lavender: #c9b8e8;
    --accent-sky: #a8dadc;
}
```

**适用场景**：创意工作坊、生活方式分享、儿童教育、产品介绍

**设计要点**：
- 使用柔和的圆角（border-radius: 20px+）
- 添加微妙的阴影增加层次
- 使用多种柔和色彩点缀
- 使用手写或圆润字体

**代码片段**：
```css
.soft-card {
    background: linear-gradient(135deg, var(--bg-secondary) 0%, #fff 100%);
    border-radius: 24px;
    box-shadow:
        0 4px 20px rgba(0, 0, 0, 0.05),
        0 1px 3px rgba(0, 0, 0, 0.08);
    padding: 2rem;
}

.pastel-accent {
    background: linear-gradient(135deg, var(--accent-peach) 0%, var(--accent-lavender) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
```

---

### 8. Warm Editorial（温暖编辑）

**风格定位**：杂志风格、摄影为主、温情叙事

**配色方案**：
```css
:root {
    --bg-primary: #f7f5f2;
    --bg-secondary: #ffffff;
    --text-primary: #2c2c2c;
    --text-secondary: #666666;
    --accent: #c4a35a;
    --accent-dark: #8b7355;
    --photo-overlay: rgba(0, 0, 0, 0.3);
}
```

**适用场景**：品牌故事、旅行分享、摄影展示、个人演讲

**设计要点**：
- 大面积高质量图片展示
- 文字叠加在图片上时使用暗色遮罩
- 使用宽幅图片和满屏布局
- 保持杂志的精致排版感

**代码片段**：
```css
.fullscreen-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.overlay-text {
    position: relative;
    z-index: 2;
}

.overlay-text::before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60%;
    background: linear-gradient(to top, var(--photo-overlay), transparent);
    z-index: -1;
}
```

---

## 特色风格（Specialty）

### 9. Brutalist（粗野主义）

**风格定位**：原始粗犷、反叛传统、引人注目

**配色方案**：
```css
:root {
    --bg-primary: #ffffff;
    --bg-accent: #ffeb3b;
    --text-primary: #000000;
    --text-inverse: #ffffff;
    --border: #000000;
}
```

**适用场景**：创意演讲、艺术展示、反驳常规的演讲、反叛主题

**设计要点**：
- 使用粗体边框（3px+ solid black）
- 强烈对比色块
- 不规则布局，打破网格
- 使用等宽或粗体字体
- 动画使用机械式硬切换

**代码片段**：
```css
.brutalist-box {
    border: 4px solid var(--border);
    background: var(--bg-accent);
    padding: 1.5rem;
    transform: rotate(-2deg);
}

.brutalist-card {
    box-shadow: 8px 8px 0 var(--border);
    transition: transform 0.1s, box-shadow 0.1s;
}

.brutalist-card:hover {
    transform: translate(-4px, -4px);
    box-shadow: 12px 12px 0 var(--border);
}

.jump-in {
    animation: jumpIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

---

### 10. Gradient Wave（渐变波浪）

**风格定位**：现代 SaaS、科技公司、主流审美

**配色方案**：
```css
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --gradient-start: #6366f1;
    --gradient-end: #8b5cf6;
    --gradient-accent: #06b6d4;
}
```

**适用场景**：产品发布会、SaaS 演示、科技公司演讲

**设计要点**：
- 使用流畅的渐变背景
- 文字渐变效果
- 添加微妙的波浪或流动元素
- 使用现代圆润的 UI 元素
- 卡片使用柔和阴影

**代码片段**：
```css
.gradient-bg {
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
}

.gradient-text {
    background: linear-gradient(135deg, var(--gradient-start), var(--gradient-accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.wave-bg {
    position: relative;
    overflow: hidden;
}

.wave-bg::before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 200%;
    height: 200px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%236366f1' fill-opacity='0.1' d='M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,218.7C672,235,768,245,864,234.7C960,224,1056,192,1152,176C1248,160,1344,160,1392,160L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E") no-repeat bottom;
    background-size: 50% 100%;
    animation: wave 10s linear infinite;
}

@keyframes wave {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}
```

---

## 通用动画配置

### 滚动触发动画

```css
.reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}

/* 延迟动画 */
.delay-1 { transition-delay: 0.1s; }
.delay-2 { transition-delay: 0.2s; }
.delay-3 { transition-delay: 0.3s; }
```

### 减少动画支持

```css
@media (prefers-reduced-motion: reduce) {
    .reveal,
    .wave-bg::before,
    .gradient-text,
    * {
        animation: none !important;
        transition-duration: 0.01ms !important;
        opacity: 1 !important;
        transform: none !important;
    }
}
```

### 响应式断点

```css
@media (max-width: 768px) {
    :root {
        --font-size-base: 16px;
        --slide-padding: 1.5rem;
    }

    .slide {
        padding: var(--slide-padding);
    }
}

@media (min-width: 1200px) {
    :root {
        --font-size-base: 18px;
    }
}
```

---

## 字体推荐

**中文：**
- 标题：Noto Serif SC（衬线）、Source Han Sans CN（无衬线）
- 正文：Noto Sans SC

**英文：**
- 标题：Playfair Display、Montserrat
- 正文：Inter、Source Sans Pro
- 代码：JetBrains Mono、Fira Code

**组合建议：**
- 正式风格：Noto Serif SC + Playfair Display
- 现代风格：Noto Sans SC + Montserrat
- 技术风格：Noto Sans SC + JetBrains Mono
