---
name: instant-web-generator
description: No-code responsive web page generator expert. Create beautiful, deployable web pages using Tailwind CSS and modern frontend frameworks. Use when users need landing pages, portfolios, product showcases, or business websites. Trigger words include: generate web page, create website, landing page, responsive design, Tailwind CSS, Bootstrap.
---

# Instant Web Generator Expert

## Core Capabilities

Generate beautiful, responsive web pages from simple descriptions without coding knowledge.

## Key Features

- **Requirement Analysis**: Understand topic, style, and functionality
- **Web Generation**: Complete HTML+CSS+JS with Tailwind CSS
- **Responsive Design**: Auto-adapt to mobile/tablet/PC
- **Quick Customization**: Easy modifications after generation
- **Deployment Support**: One-click deploy to hosting platforms

## Workflow

### 1. Receive Requirements

**Required Information**:
- Topic: What is the website about? (e.g., "Pet Hospital", "Coffee Shop")
- Style: What visual style? (Ins / Vintage / Tech / Minimalist / Chinese Trend)
- Core Functions: What features are needed?

**Style Mapping**:

| Style | Color Palette | Design Elements | Font |
|-------|--------------|-----------------|------|
| Ins/Soft | Light pink + cream | Rounded cards, handwritten | Cursive headers |
| Vintage | Brown + beige | Textures, serif | Serif headings |
| Tech | Dark gray + purple | Gradients, geometric | Sans-serif |
| Minimalist | White + black | Clean lines | Sans-serif |
| Chinese Trend | Red + gold | Traditional patterns | Chinese fonts |

**Core Functions**:
- Carousel/Banner
- Product showcase
- Booking form
- Contact form
- Testimonials
- Team introduction
- Pricing table
- FAQ section

**Ask clarifying questions when needed**:
- "Do you prefer Ins style or Vintage style?"
- "Do you need online payment feature?"
- "What's the main purpose of this page?"

### 2. Output Structure

```
# [Topic] Web Page Generated

## Preview Link
[Live Demo URL - deployed and ready]

## Code Structure
```
project/
├── index.html      # Main page
├── styles.css      # Custom styles
├── script.js       # Interactions
└── assets/         # Images
```

## Key Code Sections (with comments)

### Header Section
```html
<!-- Navigation: Logo + Menu -->
<header class="bg-white shadow">
  <nav class="container mx-auto px-4">
    <!-- Responsive menu -->
  </nav>
</header>
```

### Hero/Banner Section
```html
<!-- Full-width carousel -->
<section class="hero-carousel">
  <!-- Responsive images -->
</section>
```

### Features Section
```html
<!-- Product showcase: Grid layout -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
  <!-- Cards -->
</div>
```

## Modification Guide

### Change Primary Color
Find in CSS:
```css
:root {
  --primary-color: #3B82F6; /* Replace this value */
}
```

### Add Video Background
Replace image with video:
```html
<video autoplay loop muted class="w-full h-full object-cover">
  <source src="video.mp4" type="video/mp4">
</video>
```

### Add New Section
Copy template and insert:
```html
<!-- Section Template -->
<section class="py-12 bg-gray-50">
  <div class="container mx-auto px-4">
    <h2 class="text-2xl font-bold mb-6">Section Title</h2>
    <!-- Content -->
  </div>
</section>
```

## Deployment Guide

### Option 1: Vercel (Recommended)
1. Go to vercel.com
2. Sign up with GitHub
3. Drag and drop project folder
4. Done! Get instant URL

### Option 2: Netlify
1. Go to netlify.com
2. Sign up
3. Drag and drop
4. Custom domain available

### Option 3: GitHub Pages
1. Create GitHub repository
2. Upload files
3. Settings → Pages → Deploy
4. Get yourURL.github.io URL

### Option 4: Download ZIP
Download complete package with all assets

## Design Principles

### UI/UX Guidelines

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| Contrast | Visual hierarchy | Dark text on light bg |
| Alignment | Organized layout | Consistent margins |
| Repetition | Brand consistency | Same button style |
| Proximity | Related grouping | Cards grouped together |

### Responsive Breakpoints

| Device | Width | Columns |
|--------|-------|---------|
| Mobile | < 640px | 1 |
| Tablet | 640-1024px | 2 |
| Desktop | > 1024px | 3-4 |

### Visual Hierarchy

```
Above the fold (30%):
├── Hero banner/Carousel
├── Main value proposition
└── Primary CTA

Middle section (40%):
├── Product/Service showcase
├── Features grid
└── Testimonials

Below fold (30%):
├── Contact form
├── Team/About
└── Footer
```

## Code Standards

### Structure
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <!-- Meta tags -->
  <!-- Tailwind CSS CDN -->
  <!-- Custom styles -->
</head>
<body>
  <header><!-- Navigation --></header>
  <main>
    <section id="hero"><!-- Banner --></section>
    <section id="features"><!-- Content --></section>
    <section id="contact"><!-- Form --></section>
  </main>
  <footer><!-- Footer --></footer>
  <!-- Scripts -->
</body>
</html>
```

### Comments
```html
<!-- 轮播图模块 -->
<!-- 产品展示卡片 -->
<!-- 联系表单 -->
<!-- 页脚 -->
```

### Tailwind Classes Order
```html
<!-- Layout: container, mx-auto, px-4 -->
<!-- Display: flex, grid, block -->
<!-- Spacing: py-4, mt-2, mb-6 -->
<!-- Typography: text-xl, font-bold -->
<!-- Colors: bg-white, text-gray-600 -->
<!-- Responsive: md:flex, lg:grid-cols-3 -->
```

## Quality Standards

1. **Completeness**: All required sections present
2. **Responsiveness**: Works on all devices
3. **Accessibility**: Proper alt texts, contrast
4. **Performance**: Optimized images, fast load
5. **Customization**: Easy to modify code

## Common Templates

### Landing Page Structure
```
Header (Logo + Nav)
├── Hero (Banner + CTA)
├── Features (3-4 cards)
├── About/Story
├── Products/Services
├── Testimonials
├── FAQ (optional)
├── Contact Form
└── Footer
```

### Portfolio Structure
```
Header
├── Hero (Photo + Intro)
├── Portfolio Grid
├── Skills
├── Experience Timeline
├── Contact Form
└── Footer
```

### Business Page Structure
```
Header
├── Services Overview
├── Pricing Table
├── Team Introduction
├── Process/Steps
├── Testimonials
├── Contact Form
├── Map/Location
└── Footer
```
