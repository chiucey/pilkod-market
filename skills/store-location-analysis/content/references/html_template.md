---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450220541bc59050bf4306d2872fb1e6f57d97a7dfd57c56afed6c4a8671779947f57f022100967b4143aa3ef6da36a01cb8d04abac1d85e74a276ac819dee886755ae5d14de
    ReservedCode2: 3045022100dd910155b4e921fad73fd0612d3a6231065c0c4d7ad1e196b780304e956f268002205a29256fe20afaf021b9850794ad175e1e6c0ffa51c2b373cd612b2ee2278377
---

# HTML报告模板规格

## 模板结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>门店选址分析报告 - {城市}{商圈}</title>

    <!-- 字体设置 -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">

    <style>
        /* 核心样式 */
        :root {
            --primary: #1976D2;
            --secondary: #424242;
            --success: #388E3C;
            --danger: #D32F2F;
            --warning: #F57C00;
            --background: #FAFAFA;
            --card-bg: #FFFFFF;
            --text-primary: #212121;
            --text-secondary: #757575;
            --border: #E0E0E0;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Noto Sans', 'Noto Sans SC', 'DejaVu Sans', sans-serif;
            background: var(--background);
            color: var(--text-primary);
            line-height: 1.6;
        }

        /* 响应式容器 */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        /* 封面 */
        .cover {
            background: linear-gradient(135deg, var(--primary) 0%, #1565C0 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 16px;
            margin-bottom: 30px;
            text-align: center;
        }

        .cover h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
        }

        .decision-badge {
            display: inline-block;
            padding: 12px 40px;
            border-radius: 50px;
            font-size: 1.3rem;
            font-weight: bold;
            margin: 20px 0;
        }

        .decision-enter {
            background: var(--success);
        }

        .decision-reject {
            background: var(--danger);
        }

        /* 浮动目录 */
        .toc {
            position: sticky;
            top: 20px;
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            z-index: 100;
        }

        .toc-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--primary);
        }

        .toc-list {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 10px;
        }

        .toc-list a {
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.9rem;
            padding: 8px 12px;
            border-radius: 6px;
            transition: all 0.2s;
        }

        .toc-list a:hover {
            background: var(--primary);
            color: white;
        }

        /* 折叠章节 */
        .section {
            background: var(--card-bg);
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            overflow: hidden;
        }

        .section-header {
            padding: 20px 25px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid transparent;
            transition: all 0.3s;
        }

        .section-header:hover {
            background: #F5F5F5;
        }

        .section.active .section-header {
            border-bottom: 1px solid var(--border);
        }

        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .section-icon {
            width: 32px;
            height: 32px;
            background: var(--primary);
            color: white;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        .section-content {
            padding: 25px;
            display: none;
        }

        .section.active .section-content {
            display: block;
        }

        .toggle-icon {
            transition: transform 0.3s;
            font-size: 1.5rem;
            color: var(--text-secondary);
        }

        .section.active .toggle-icon {
            transform: rotate(180deg);
        }

        /* 卡片网格 */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .card {
            background: var(--background);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid var(--border);
        }

        .card-title {
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .card-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }

        .card-unit {
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        /* 表格样式 */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.95rem;
        }

        .data-table th {
            background: var(--primary);
            color: white;
            padding: 14px 16px;
            text-align: left;
            font-weight: 500;
        }

        .data-table td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
        }

        .data-table tr:hover {
            background: #F5F5F5;
        }

        /* 图表容器 */
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }

        .chart-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--text-primary);
        }

        /* SWOT矩阵 */
        .swot-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }

        .swot-item {
            padding: 20px;
            border-radius: 10px;
        }

        .swot-strengths {
            background: #E8F5E9;
            border-left: 4px solid var(--success);
        }

        .swot-weaknesses {
            background: #FFEBEE;
            border-left: 4px solid var(--danger);
        }

        .swot-opportunities {
            background: #E3F2FD;
            border-left: 4px solid var(--primary);
        }

        .swot-threats {
            background: #FFF3E0;
            border-left: 4px solid var(--warning);
        }

        .swot-label {
            font-weight: 600;
            margin-bottom: 10px;
            font-size: 1rem;
        }

        /* 决策摘要 */
        .decision-summary {
            background: var(--background);
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
        }

        .confidence-badge {
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-left: 15px;
        }

        /* 假设清单 */
        .assumption-table {
            width: 100%;
        }

        .assumption-high {
            color: var(--danger);
            font-weight: 600;
        }

        .assumption-medium {
            color: var(--warning);
            font-weight: 600;
        }

        .assumption-low {
            color: var(--success);
            font-weight: 600;
        }

        /* 页脚 */
        .footer {
            margin-top: 40px;
            padding: 25px;
            background: var(--secondary);
            color: white;
            border-radius: 12px;
        }

        .footer-title {
            font-weight: 600;
            margin-bottom: 15px;
        }

        .source-list {
            list-style: none;
            font-size: 0.9rem;
            color: #BDBDBD;
        }

        .source-list li {
            margin: 8px 0;
        }

        .source-list a {
            color: #90CAF9;
        }

        /* 代码块 */
        .code-block {
            background: #263238;
            color: #ECEFF1;
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            margin: 15px 0;
        }

        /* 响应式 */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            .cover {
                padding: 40px 20px;
            }

            .cover h1 {
                font-size: 1.8rem;
            }

            .swot-grid {
                grid-template-columns: 1fr;
            }

            .toc-list {
                grid-template-columns: 1fr;
            }
        }

        /* 打印样式 */
        @media print {
            .toc {
                display: none;
            }

            .section {
                break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <!-- 报告内容将动态生成 -->
</body>
</html>
```

## 图表嵌入规范

### 图片格式
- 导出格式: PNG/SVG
- 分辨率: 150 DPI (屏幕) / 300 DPI (打印)
- 背景: 白色 (#FFFFFF)
- 字体: DejaVu Sans, 12-14pt

### 中英双语表头

```html
<table class="data-table">
    <thead>
        <tr>
            <th>Indicator (指标)</th>
            <th>Value (数值)</th>
            <th>Trend (趋势)</th>
        </tr>
    </thead>
    <tbody>
        <!-- 数据行 -->
    </tbody>
</table>
```

---

## JavaScript交互逻辑

```javascript
// 折叠章节
document.querySelectorAll('.section-header').forEach(header => {
    header.addEventListener('click', () => {
        const section = header.parentElement;
        section.classList.toggle('active');
    });
});

// 平滑滚动
document.querySelectorAll('.toc-list a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href').slice(1);
        document.getElementById(targetId).scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
});
```

---

*模板版本: 1.0.0 | 更新日期: 2026-04-25*
