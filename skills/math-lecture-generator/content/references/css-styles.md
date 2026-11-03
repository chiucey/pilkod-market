---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502210095ed1a5d950ebcb3f85df98c973b2fd2e358922e72e9a34f248c3a4bd9ff2b6602205360ed1a6e25c0fc7f45ef47b3626ee8b82d48d7c4c153a9da88cd8a7dff7d3f
    ReservedCode2: 304402200732ddcf6ea7b4157aed64bed060fd126162ab04539b5ddc3274f8e78a3c566b022063817b7996d2d338023926f7616574d7884418fe31ab77ad0d8d7036d426ab81
---

# 数学课件 CSS 样式表

## 核心卡片样式

### 1. 概念/定义卡片 (蓝色)

```css
.card-definition {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-left: 4px solid #2196f3;
  border-radius: 8px;
  padding: 1.25rem;
  margin: 1.5rem 0;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);
}

.card-definition::before {
  content: "📘 定义";
  display: block;
  font-weight: 700;
  color: #1565c0;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}
```

### 2. 定理/性质/公式卡片 (紫色)

```css
.card-theorem {
  background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
  border-left: 4px solid #9c27b0;
  border-radius: 8px;
  padding: 1.25rem;
  margin: 1.5rem 0;
  box-shadow: 0 2px 8px rgba(156, 39, 176, 0.15);
}

.card-theorem::before {
  content: "📐 定理";
  display: block;
  font-weight: 700;
  color: #7b1fa2;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}
```

### 3. 例题详解卡片 (绿色)

```css
.card-example {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border-left: 4px solid #4caf50;
  border-radius: 8px;
  padding: 1.25rem;
  margin: 1.5rem 0;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
}

.card-example::before {
  content: "✏️ 例题";
  display: block;
  font-weight: 700;
  color: #2e7d32;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}
```

### 4. 重点/易错点卡片 (红色)

```css
.card-warning {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  border-left: 4px solid #f44336;
  border-radius: 8px;
  padding: 1.25rem;
  margin: 1.5rem 0;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.15);
}

.card-warning::before {
  content: "⚠️ 易错点";
  display: block;
  font-weight: 700;
  color: #c62828;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}
```

### 5. 思考/探究卡片 (橙色)

```css
.card-explore {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-left: 4px solid #ff9800;
  border-radius: 8px;
  padding: 1.25rem;
  margin: 1.5rem 0;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.15);
}

.card-explore::before {
  content: "🤔 思考";
  display: block;
  font-weight: 700;
  color: #e65100;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}
```

## 布局工具类

### 两列布局

```css
.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin: 1.5rem 0;
}

@media (max-width: 768px) {
  .two-columns {
    grid-template-columns: 1fr;
  }
}
```

### 三列布局

```css
.three-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin: 1.5rem 0;
}

@media (max-width: 1024px) {
  .three-columns {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .three-columns {
    grid-template-columns: 1fr;
  }
}
```

## 公式相关样式

### 公式居中显示

```css
.formula-center {
  display: block;
  text-align: center;
  margin: 1.5rem 0;
  padding: 1rem;
  background: #fafafa;
  border-radius: 8px;
}
```

### 步骤推导对齐

```css
.step-align {
  font-family: 'KaTeX_Main', 'Times New Roman', serif;
  line-height: 1.8;
}

.step-align .step-line {
  display: flex;
  align-items: center;
  margin: 0.5rem 0;
}

.step-align .step-number {
  min-width: 2rem;
  font-weight: bold;
  color: #666;
}

.step-align .step-content {
  flex: 1;
}
```

## 表格样式

```css
.math-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  font-size: 0.95rem;
}

.math-table th {
  background: #e3f2fd;
  color: #1565c0;
  font-weight: 600;
  padding: 1rem;
  text-align: left;
  border-bottom: 2px solid #2196f3;
}

.math-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.math-table tr:hover {
  background: #f5f5f5;
}
```

## 标题层级样式

```css
.slide-title {
  color: #1565c0;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  border-bottom: 3px solid #2196f3;
  padding-bottom: 0.5rem;
}

.slide-subtitle {
  color: #424242;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem;
}

.section-title {
  color: #7b1fa2;
  font-size: 1.75rem;
  font-weight: 600;
  margin: 2rem 0 1rem;
}
```

## Marp 兼容样式

```css
/* Marp 幻灯片内使用 */
section {
  font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
}

/* 强调文字 */
strong {
  color: #d32f2f;
}

/* 高亮 */
mark {
  background: #ffeb3b;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
}
```

## Reveal.js 增强样式

```css
/* Reveal.js 幻灯片容器 */
.reveal .slides section {
  text-align: left;
}

/* 代码块 */
.reveal pre {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  font-size: 0.8em;
}

.reveal pre code {
  padding: 1rem 1.25rem;
}

/* 进度条 */
.reveal .progress {
  height: 4px;
  background: rgba(0, 0, 0, 0.1);
}

.reveal .progress span {
  background: linear-gradient(90deg, #2196f3, #9c27b0);
}
```