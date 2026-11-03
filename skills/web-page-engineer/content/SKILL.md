---
name: web-page-engineer
description: 网页工程师技能。当用户要求创建网页、生成HTML页面、创建带特效的页面、设计网页时使用。触发短语：做网页、创建网页、生成网页、网页设计、HTML页面、带特效的页面、网页主题。
---

# 网页工程师

网页工程师技能用于根据用户输入的网页主题，快速生成精美、带有丰富特效的HTML页面。

## 核心能力

- 响应式布局设计，适配各种屏幕尺寸
- CSS动画特效（渐变、阴影、过渡、变换等）
- 交互效果（悬停、点击、滚动触发）
- 现代UI组件（卡片、导航栏、按钮、表单等）
- 渐变色和玻璃态设计
- 动态粒子背景或波浪效果
- 平滑滚动和视差效果
- 专业配色方案

## 工作流程

### 第一步：收集需求
- 确认网页主题（如：个人简历、作品集、产品展示、公司官网、活动页面等）
- 询问风格偏好（现代简约、科技感、活泼清新、商务专业等）
- 确认页面数量（单页/多页）
- 确认是否需要特定功能（表单、轮播图、动画等）

### 第二步：生成代码
使用纯 HTML + CSS + JavaScript 实现，确保：
- 所有样式内联或内嵌（单文件即可运行）
- 使用 CSS 变量管理主题色
- 添加适量的 CSS 动画特效
- 实现响应式设计
- 代码结构清晰，注释完善

### 第三步：测试验证
- 检查 HTML 结构完整性
- 验证 CSS 语法正确性
- 确保所有外部资源可用
- 测试响应式布局

### 第四步：部署上线
- 使用 deploy 工具部署页面
- 提供在线访问链接

## 技能约束

- 必须使用 deploy 工具部署，不允许使用本地服务器
- 生成纯静态页面，不涉及后端逻辑
- 优先使用 CSS 动画而非 JavaScript 动画
- 确保代码可读性和可维护性
- 所有特效应有意义，避免过度装饰

## 代码模板

### 基础结构
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题</title>
    <style>
        /* CSS 变量定义 */
        :root {
            --primary-color: #6366f1;
            --secondary-color: #8b5cf6;
            --text-color: #1f2937;
            --bg-color: #ffffff;
            --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            /* 移动端适配 */
        }

        /* 动画定义 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }

        /* 组件样式 */
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }

        /* 按钮样式 */
        .btn {
            background: var(--gradient);
            border-radius: 50px;
            padding: 12px 32px;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
        }
    </style>
</head>
<body>
    <!-- 页面内容 -->

    <script>
        // JavaScript 交互逻辑
        document.addEventListener('DOMContentLoaded', () => {
            // 页面加载动画
            // 滚动监听
            // 交互效果
        });
    </script>
</body>
</html>
```

### 常用特效库

**粒子背景**
```javascript
function createParticles() {
    const canvas = document.getElementById('particles');
    const ctx = canvas.getContext('2d');
    const particles = [];

    for (let i = 0; i < 50; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 3 + 1
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
}
```

**平滑滚动导航**
```javascript
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});
```

**滚动渐入动画**
```javascript
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

document.querySelectorAll('.animate-on-scroll').forEach(el => {
    observer.observe(el);
});
```

## 输出格式

完成页面生成后，提供：
1. **技能执行结果**：简述生成的页面特点
2. **文件路径**：HTML 文件的完整路径
3. **部署链接**：在线访问地址
4. **功能说明**：页面包含的主要功能和特效
