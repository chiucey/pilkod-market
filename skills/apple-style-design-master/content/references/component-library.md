# 组件设计参考库

## 按钮 (Button)

### 主要按钮 (Primary Button)
```html
<button class="btn btn-primary">
  <span>了解更多</span>
</button>
```

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  outline: none;
}

.btn-primary {
  background: #0071e3;
  color: #ffffff;
}

.btn-primary:hover {
  background: #0077ed;
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0);
}
```

### 次要按钮 (Secondary Button)
```html
<button class="btn btn-secondary">了解更多</button>
```

```css
.btn-secondary {
  background: transparent;
  color: #0071e3;
  border: 1px solid #0071e3;
}

.btn-secondary:hover {
  background: rgba(0, 113, 227, 0.05);
}
```

### 文字按钮 (Text Button)
```html
<button class="btn btn-text">
  了解更多
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</button>
```

```css
.btn-text {
  background: transparent;
  color: #0071e3;
  padding: 8px 0;
}

.btn-text:hover {
  text-decoration: underline;
}
```

## 卡片 (Card)

### 标准卡片
```html
<div class="card">
  <div class="card-image">
    <img src="/images/product.jpg" alt="产品图">
  </div>
  <div class="card-content">
    <h3 class="card-title">产品名称</h3>
    <p class="card-description">简洁的产品描述</p>
    <div class="card-footer">
      <span class="card-price">¥999</span>
      <button class="btn btn-primary btn-sm">购买</button>
    </div>
  </div>
</div>
```

```css
.card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-image {
  width: 100%;
  aspect-ratio: 4/3;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.card:hover .card-image img {
  transform: scale(1.02);
}

.card-content {
  padding: 24px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px;
}

.card-description {
  font-size: 14px;
  color: #86868b;
  line-height: 1.5;
  margin: 0 0 16px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-price {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 14px;
}
```

### 悬浮卡片
```css
.floating-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

## 输入框 (Input)

### 文本输入框
```html
<div class="input-group">
  <label class="input-label">邮箱</label>
  <input type="email" class="input" placeholder="请输入邮箱地址">
</div>
```

```css
.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
}

.input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #d2d2d7;
  border-radius: 8px;
  font-size: 16px;
  color: #1d1d1f;
  transition: all 0.2s ease;
  background: #ffffff;
}

.input::placeholder {
  color: #86868b;
}

.input:focus {
  outline: none;
  border-color: #0071e3;
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
}
```

### 搜索框
```html
<div class="search-box">
  <svg class="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16z" stroke="#86868b" stroke-width="1.5"/>
    <path d="M15 15l4 4" stroke="#86868b" stroke-width="1.5" stroke-linecap="round"/>
  </svg>
  <input type="text" class="search-input" placeholder="搜索...">
</div>
```

```css
.search-box {
  position: relative;
  width: 100%;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 48px;
  border: 1px solid #d2d2d7;
  border-radius: 24px;
  font-size: 16px;
  background: #f5f5f7;
  transition: all 0.2s ease;
}

.search-input:focus {
  background: #ffffff;
  border-color: #0071e3;
  outline: none;
}
```

## 导航栏 (Navbar)

### 透明导航栏
```html
<nav class="navbar navbar-transparent">
  <div class="navbar-container">
    <a href="/" class="navbar-logo">
      <img src="/logo.svg" alt="Logo" height="24">
    </a>
    <div class="navbar-links">
      <a href="#" class="nav-link">产品</a>
      <a href="#" class="nav-link">特点</a>
      <a href="#" class="nav-link">支持</a>
    </div>
    <a href="#" class="btn btn-primary btn-sm">购买</a>
  </div>
</nav>
```

```css
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 16px 0;
  transition: all 0.3s ease;
}

.navbar-transparent {
  background: transparent;
}

.navbar-scrolled {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.05);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-logo {
  display: flex;
  align-items: center;
}

.nav-link {
  padding: 8px 16px;
  color: #1d1d1f;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: #0071e3;
}
```

## 特性列表 (Feature List)

### 特性项
```html
<div class="feature-item">
  <div class="feature-icon">
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
      <path d="M16 2L2 16l14 14 14-14L16 2z" stroke="#0071e3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M16 10v12M10 16h12" stroke="#0071e3" stroke-width="2" stroke-linecap="round"/>
    </svg>
  </div>
  <h3 class="feature-title">极简设计</h3>
  <p class="feature-description">删繁就简，每一个元素都有其存在的意义</p>
</div>
```

```css
.feature-item {
  text-align: center;
  padding: 48px 24px;
}

.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(0, 113, 227, 0.05);
  margin-bottom: 24px;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 12px;
}

.feature-description {
  font-size: 15px;
  color: #86868b;
  line-height: 1.6;
  margin: 0;
}
```

## 模态框 (Modal)

```html
<div class="modal-overlay">
  <div class="modal">
    <div class="modal-header">
      <h2 class="modal-title">标题</h2>
      <button class="modal-close">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
    <div class="modal-body">
      模态框内容
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary">取消</button>
      <button class="btn btn-primary">确认</button>
    </div>
  </div>
</div>
```

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 2000;
}

.modal {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f5f5f7;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #86868b;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: #1d1d1f;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f5f5f7;
}
```

## 标签页 (Tabs)

```html
<div class="tabs">
  <div class="tab-list">
    <button class="tab-btn active">概述</button>
    <button class="tab-btn">特性</button>
    <button class="tab-btn">规格</button>
  </div>
  <div class="tab-content">
    标签页内容区域
  </div>
</div>
```

```css
.tabs {
  width: 100%;
}

.tab-list {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid #d2d2d7;
  padding-bottom: -1px;
}

.tab-btn {
  padding: 12px 24px;
  background: transparent;
  border: none;
  font-size: 16px;
  color: #86868b;
  cursor: pointer;
  position: relative;
  transition: color 0.2s ease;
}

.tab-btn::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #0071e3;
  transform: scaleX(0);
  transition: transform 0.2s ease;
}

.tab-btn:hover {
  color: #1d1d1f;
}

.tab-btn.active {
  color: #0071e3;
}

.tab-btn.active::after {
  transform: scaleX(1);
}

.tab-content {
  padding: 32px 0;
}
```

## 图片展示 (Image Showcase)

### 轮播图
```css
.carousel {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 16px;
}

.carousel-track {
  display: flex;
  transition: transform 0.5s ease;
}

.carousel-slide {
  flex-shrink: 0;
  width: 100%;
}

.carousel-slide img {
  width: 100%;
  height: auto;
}
```

### 画廊网格
```css
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.gallery-item {
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 4/3;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.gallery-item:hover img {
  transform: scale(1.05);
}
```
