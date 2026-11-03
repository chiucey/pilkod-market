# 胶囊形渐变按钮(5 色 × 4 尺寸, 2026-10-14 抽取)

> 来自 4 张 B 端应用门户参考图(General statistics / 大数据可视化分享 / 采购大数据监控平台 / 智能体中心)
> 配合 `bright-portal` 第 4 档配色主题使用

---

## 一、5 种 brand 色

| 名称 | HEX | 渐变 | 阴影 |
|---|---|---|---|
| purple | `#7C3AED` | `linear-gradient(135deg, #7C3AED, #A78BFA)` | `rgba(124, 58, 237, 0.3)` |
| orange | `#F97316` | `linear-gradient(135deg, #F97316, #FDBA74)` | `rgba(249, 115, 22, 0.3)` |
| green  | `#10B981` | `linear-gradient(135deg, #10B981, #6EE7B7)` | `rgba(16, 185, 129, 0.3)` |
| cyan   | `#06B6D4` | `linear-gradient(135deg, #06B6D4, #67E8F9)` | `rgba(6, 182, 212, 0.3)` |
| yellow | `#F59E0B` | `linear-gradient(135deg, #F59E0B, #FCD34D)` | `rgba(245, 158, 11, 0.3)` |

---

## 二、4 种尺寸

| 名称 | 高度 | 字号 | 内边距 | 圆角 | 适用场景 |
|---|---|---|---|---|---|
| `btn-sm`  | 32px | 13px | 0 16px | 9999px | 表格内次要操作、标签 |
| `btn-md`  | 40px | 14px | 0 20px | 9999px | 普通按钮(默认) |
| `btn-lg`  | 48px | 16px | 0 24px | 9999px | 主操作、CTA |
| `btn-xl`  | 56px | 18px | 0 28px | 9999px | 登录按钮、首屏 CTA |

---

## 三、HTML + CSS 完整代码

### 3.1 基础 CSS(直接复制)

```css
/* 胶囊按钮基础 */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: none;
    border-radius: 9999px;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    user-select: none;
    text-decoration: none;
    font-family: inherit;
    line-height: 1;
}

/* 尺寸 */
.btn-sm { height: 32px; padding: 0 16px; font-size: 13px; }
.btn-md { height: 40px; padding: 0 20px; font-size: 14px; }
.btn-lg { height: 48px; padding: 0 24px; font-size: 16px; }
.btn-xl { height: 56px; padding: 0 28px; font-size: 18px; }

/* 5 色主题 */
.btn-purple { background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%);
               box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3); }
.btn-orange { background: linear-gradient(135deg, #F97316 0%, #FDBA74 100%);
               box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3); }
.btn-green  { background: linear-gradient(135deg, #10B981 0%, #6EE7B7 100%);
               box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
.btn-cyan   { background: linear-gradient(135deg, #06B6D4 0%, #67E8F9 100%);
               box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3); }
.btn-yellow { background: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
               box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3); }

/* hover 上浮 + 阴影加深 */
.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px currentColor;
    filter: brightness(1.05);
}
/* 注意: box-shadow 用 currentColor 时要配 fallback */
.btn-purple:hover { box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4); }
.btn-orange:hover { box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4); }
.btn-green:hover  { box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4); }
.btn-cyan:hover   { box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4); }
.btn-yellow:hover { box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4); }

/* active 下沉 */
.btn:active { transform: translateY(0); box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); }

/* 禁用 */
.btn:disabled {
    background: #E2E8F0;
    color: #94A3B8;
    box-shadow: none;
    cursor: not-allowed;
    transform: none;
}

/* 加载中 */
.btn.loading {
    pointer-events: none;
    color: transparent;
}
.btn.loading::after {
    content: '';
    position: absolute;
    width: 16px; height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
```

### 3.2 HTML 用法

```html
<!-- 5 色 × 4 尺寸 全组合 -->
<button class="btn btn-purple btn-sm">小·紫</button>
<button class="btn btn-orange btn-md">中·橙</button>
<button class="btn btn-green btn-lg">大·绿</button>
<button class="btn btn-cyan btn-xl">特大·青</button>
<button class="btn btn-yellow btn-lg">大·黄</button>

<!-- 带图标 -->
<button class="btn btn-purple btn-md">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 5v14M5 12h14"/>
    </svg>
    新建应用
</button>

<!-- 链接形式(<a> 同样适用) -->
<a class="btn btn-cyan btn-md" href="#/consult">立即开始</a>

<!-- 加载中 -->
<button class="btn btn-purple btn-md loading">提交中</button>

<!-- 禁用 -->
<button class="btn btn-orange btn-md" disabled>不可用</button>
```

---

## 四、5 种变体

### 4.1 描边款(Outline)
```css
.btn-outline-purple { background: white; color: #7C3AED; border: 1.5px solid #7C3AED; box-shadow: none; }
.btn-outline-purple:hover { background: #F5F3FF; }
```

### 4.2 浅底款(Soft)
```css
.btn-soft-purple { background: #F5F3FF; color: #7C3AED; box-shadow: none; }
.btn-soft-purple:hover { background: #EDE9FE; }
.btn-soft-orange { background: #FFF7ED; color: #F97316; }
.btn-soft-green  { background: #ECFDF5; color: #10B981; }
.btn-soft-cyan   { background: #ECFEFF; color: #06B6D4; }
.btn-soft-yellow { background: #FFFBEB; color: #F59E0B; }
```

### 4.3 图标按钮(Icon Only)
```css
.btn-icon {
    width: 40px; height: 40px;
    padding: 0;
    border-radius: 50%;
}
.btn-icon.btn-sm { width: 32px; height: 32px; }
.btn-icon.btn-lg { width: 48px; height: 48px; }
```

### 4.4 块按钮(Block)
```css
.btn-block { width: 100%; }
```

### 4.5 圆角矩形款(非胶囊)
```css
.btn-rounded {
    border-radius: 12px;  /* 圆角矩形 */
}
```

---

## 五、与原 cream 主题的兼容

```css
/* 在 cream 主题下, 按钮可以是单色蓝(不用 5 色渐变) */
.theme-cream .btn-primary {
    background: #1E3A6E;
    box-shadow: 0 4px 12px rgba(30, 58, 110, 0.2);
}

/* 但 cream 主题用胶囊按钮也 OK, 只是配色不同 */
.theme-cream .btn-orange { background: #F97316; }
```

**建议**:
- cream 主题:用 btn-primary (单色深蓝) + btn-outline 为主
- bright-portal 主题:用 5 色渐变胶囊按钮为主

---

## 六、避坑 5 条

1. **不要堆 3+ 渐变** — 单屏最多 2-3 个渐变按钮, 其余用单色或 outline
2. **阴影用同色系** — `box-shadow: 0 4px 12px rgba(color, 0.3)`, 不要用纯黑阴影
3. **白色文字 + bold 600+** — 渐变背景对比度低, 字重要够
4. **hover 不要换色** — 换色会跳, 用亮度/阴影/位移代替
5. **加载中状态必加** — fetch/接口请求时不加 loading 状态用户会重复点击

---

## 七、完整 demo HTML

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>胶囊按钮 Demo</title>
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #F5F8FE;
    padding: 40px;
    margin: 0;
}
h2 { color: #0F172A; margin: 32px 0 16px; font-size: 18px; }
.demo-row {
    display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
    background: white; padding: 24px; border-radius: 12px;
    box-shadow: 0 4px 24px rgba(15, 23, 42, 0.04);
}

/* 复制基础 CSS 到这里 */
.btn { ... }
.btn-sm { ... }
.btn-md { ... }
.btn-lg { ... }
.btn-xl { ... }
.btn-purple { ... }
/* ... */
</style>
</head>
<body>
    <h2>5 色 × 4 尺寸 全组合</h2>
    <div class="demo-row">
        <button class="btn btn-purple btn-sm">小·紫</button>
        <button class="btn btn-orange btn-sm">小·橙</button>
        <button class="btn btn-green btn-sm">小·绿</button>
        <button class="btn btn-cyan btn-sm">小·青</button>
        <button class="btn btn-yellow btn-sm">小·黄</button>
        
        <button class="btn btn-purple btn-md">中·紫</button>
        <!-- ... -->
        
        <button class="btn btn-purple btn-lg">大·紫</button>
        <button class="btn btn-orange btn-lg">大·橙</button>
        
        <button class="btn btn-purple btn-xl">特大·紫</button>
        <button class="btn btn-cyan btn-xl">立即开始</button>
    </div>
    
    <h2>变体: Outline / Soft / Icon</h2>
    <div class="demo-row">
        <button class="btn btn-outline-purple btn-md">描边·紫</button>
        <button class="btn btn-soft-orange btn-md">浅底·橙</button>
        <button class="btn btn-cyan btn-icon btn-md">＋</button>
        <button class="btn btn-green btn-icon btn-sm">✓</button>
    </div>
    
    <h2>状态: 加载中 / 禁用</h2>
    <div class="demo-row">
        <button class="btn btn-purple btn-md loading">提交中</button>
        <button class="btn btn-orange btn-md" disabled>不可用</button>
    </div>
</body>
</html>
```