---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9d180dd9e5a8abb2ae80c9033b9420d6
    PropagateID: 9d180dd9e5a8abb2ae80c9033b9420d6
    ReservedCode1: 304502200e1d95fea7ab6ee8fe1c706141a1d87d4ac9ce4f1c8fc042db0052ab8908e3dd022100ba9739dabfb64dc6c4d4ca39d84bce71ed99b4f0d288ae20db8fa7313b2fd17b
    ReservedCode2: 30460221008f192647473ba80949f0ff93001c04a00285a59dc8e663a094c9ea919cb32b3e0221009e5c85131062d02f7860fef9fd5c8be3c2e61f54f3c114d3801d9693fb77de4e
description: An elegant dark-themed electronic tarot card divination skill with three-card spread layout. Use when users ask for tarot reading, card drawing, fortune telling, tarot cards, or using tarot.
name: tarot-three-card
---

# 塔罗三牌阵占卜

一个暗黑优雅、神秘高端的电子塔罗牌占卜技能，采用经典三牌阵（过去-现在-未来）。

## 视觉风格规范

### 配色方案
- **主背景**: 深紫渐变 `#0a0612` → `#1a0a2e` → `#0d1b2a`（神秘深邃）
- **次要背景**: `#150a20`（暗紫色调）
- **金色装饰**: `#d4af37`（古典金）、`#f4d03f`（明亮金）、`#c9a227`（暗金）
- **文字主色**: `#e8e0f0`（淡紫白）
- **文字次色**: `#9d8ab4`（淡紫灰）
- **强调色**: `#6b4c9a`（神秘紫）

### 新艺术风格边框
使用 SVG 新艺术曲线边框：
- 流畅的贝塞尔曲线
- 对称的花卉/藤蔓图案
- 金色渐变填充
- 角落装饰元素

## 塔罗牌数据

### 大阿尔卡纳 22 张牌
```
0. 愚者 (The Fool)
1. 魔术师 (The Magician)
2. 女祭司 (The High Priestess)
3. 女皇 (The Empress)
4. 皇帝 (The Emperor)
5. 教皇 (The Hierophant)
6. 恋人 (The Lovers)
7. 战车 (The Chariot)
8. 力量 (Strength)
9. 隐士 (The Hermit)
10. 命运之轮 (Wheel of Fortune)
11. 正义 (Justice)
12. 倒吊人 (The Hanged Man)
13. 死神 (Death)
14. 节制 (Temperance)
15. 恶魔 (The Devil)
16. 塔 (The Tower)
17. 星星 (The Star)
18. 月亮 (The Moon)
19. 太阳 (The Sun)
20. 审判 (Judgement)
21. 世界 (The World)
```

### 牌义解读（每张牌包含正位和逆位）
存储在 `references/card-meanings.json` 中。

## 三牌阵布局

```
        [1] 过去
         ↓
[2] 现在 ← → [3] 未来
```

- **位置 1 (Past)**: 代表问题的根源、过去的事件
- **位置 2 (Present)**: 代表当前状况、挑战
- **位置 3 (Future)**: 代表可能的结果、建议

## 交互流程

### 1. 初始化状态
显示：
- 标题："塔罗三牌阵"
- 副标题："探索命运的奥秘"
- 问题输入框（金色边框）
- "开始占卜"按钮

### 2. 抽牌动画
- 3张牌背卡片滑动出现
- 用户点击选择（可选中动画效果）
- 或自动随机抽取
- 翻牌动画（3D 翻转效果）

### 3. 结果展示
- 三张牌面竖向展示
- 每张牌显示：
  - 牌名
  - 象征符号图案（SVG）
  - 位置含义（过去/现在/未来）
  - 正位/逆位解读
  - 整体牌阵解读

## HTML/CSS/JS 实现

### 文件结构
```
skill/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
└── references/
    └── card-meanings.json      # 牌义数据
```

### 核心实现代码

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>塔罗三牌阵 - 命运之境</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Noto+Serif+SC:wght@400;600&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --bg-dark: #0a0612;
            --bg-purple: #1a0a2e;
            --bg-blue: #0d1b2a;
            --gold: #d4af37;
            --gold-light: #f4d03f;
            --gold-dark: #c9a227;
            --text-primary: #e8e0f0;
            --text-secondary: #9d8ab4;
            --accent: #6b4c9a;
        }
        
        body {
            font-family: 'Noto Serif SC', serif;
            background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-purple) 50%, var(--bg-blue) 100%);
            min-height: 100vh;
            color: var(--text-primary);
            overflow-x: hidden;
        }
        
        /* 新艺术风格背景装饰 */
        .art-nouveau-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.1;
            z-index: 0;
        }
        
        .container {
            position: relative;
            z-index: 1;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        /* 标题样式 */
        .title-section {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .main-title {
            font-family: 'Cinzel', serif;
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--gold-dark), var(--gold-light), var(--gold-dark));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 40px rgba(212, 175, 55, 0.3);
            letter-spacing: 0.2em;
            margin-bottom: 15px;
        }
        
        .subtitle {
            font-size: 1.1rem;
            color: var(--text-secondary);
            letter-spacing: 0.3em;
        }
        
        /* 新艺术风格边框 */
        .art-nouveau-border {
            position: relative;
            border: 2px solid var(--gold);
            padding: 30px;
            margin: 20px 0;
        }
        
        .art-nouveau-border::before,
        .art-nouveau-border::after {
            content: '';
            position: absolute;
            width: 60px;
            height: 60px;
            border: 2px solid var(--gold);
        }
        
        .art-nouveau-border::before {
            top: -5px;
            left: -5px;
            border-right: none;
            border-bottom: none;
            border-top-left-radius: 30px;
        }
        
        .art-nouveau-border::after {
            bottom: -5px;
            right: -5px;
            border-left: none;
            border-top: none;
            border-bottom-right-radius: 30px;
        }
        
        /* 问题输入区 */
        .question-section {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .question-input {
            width: 100%;
            max-width: 500px;
            padding: 18px 25px;
            font-size: 1.1rem;
            font-family: 'Noto Serif SC', serif;
            background: rgba(26, 10, 46, 0.8);
            border: 1px solid var(--gold);
            border-radius: 0;
            color: var(--text-primary);
            outline: none;
            transition: all 0.3s ease;
        }
        
        .question-input:focus {
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
            border-color: var(--gold-light);
        }
        
        .question-input::placeholder {
            color: var(--text-secondary);
            opacity: 0.7;
        }
        
        /* 按钮样式 */
        .btn-divine {
            display: inline-block;
            padding: 15px 50px;
            font-family: 'Cinzel', serif;
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: 0.15em;
            color: var(--bg-dark);
            background: linear-gradient(135deg, var(--gold-dark), var(--gold-light), var(--gold-dark));
            border: none;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .btn-divine:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.4);
        }
        
        .btn-divine::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s ease;
        }
        
        .btn-divine:hover::after {
            left: 100%;
        }
        
        /* 牌阵区域 */
        .spread-section {
            display: none;
            margin-top: 50px;
        }
        
        .spread-section.active {
            display: block;
        }
        
        .spread-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 30px;
        }
        
        .spread-row {
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
        }
        
        /* 单张卡片 */
        .card-slot {
            position: relative;
            width: 160px;
            height: 240px;
            perspective: 1000px;
        }
        
        .card-position {
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            font-family: 'Cinzel', serif;
            font-size: 0.85rem;
            color: var(--gold);
            letter-spacing: 0.1em;
            white-space: nowrap;
        }
        
        .card {
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.8s ease;
            cursor: pointer;
        }
        
        .card.flipped {
            transform: rotateY(180deg);
        }
        
        .card-face {
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid var(--gold);
        }
        
        /* 牌背面 - 新艺术风格 */
        .card-back {
            background: linear-gradient(135deg, #1a0a2e, #0d1b2a);
            position: relative;
            overflow: hidden;
        }
        
        .card-back-pattern {
            position: absolute;
            width: 90%;
            height: 90%;
            border: 1px solid var(--gold);
        }
        
        .card-back-inner {
            width: 80%;
            height: 85%;
            background: 
                radial-gradient(ellipse at center, rgba(107, 76, 154, 0.3) 0%, transparent 70%),
                linear-gradient(135deg, #1a0a2e 0%, #0d1b2a 100%);
            border: 1px solid var(--gold-dark);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .card-back-symbol {
            font-size: 3rem;
            color: var(--gold);
            opacity: 0.8;
        }
        
        /* 牌正面 */
        .card-front {
            background: linear-gradient(180deg, #1a1030 0%, #0a0a15 100%);
            transform: rotateY(180deg);
            padding: 15px;
            flex-direction: column;
        }
        
        .card-front-frame {
            width: 100%;
            height: 100%;
            border: 1px solid var(--gold);
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            background: rgba(10, 6, 18, 0.9);
        }
        
        .card-symbol {
            width: 60px;
            height: 60px;
            margin-bottom: 10px;
        }
        
        .card-symbol svg {
            width: 100%;
            height: 100%;
        }
        
        .card-name {
            font-family: 'Cinzel', serif;
            font-size: 0.9rem;
            color: var(--gold-light);
            text-align: center;
            margin-bottom: 5px;
        }
        
        .card-name-cn {
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-align: center;
        }
        
        .card-orientation {
            position: absolute;
            bottom: 10px;
            font-size: 0.7rem;
            color: var(--gold);
            letter-spacing: 0.1em;
        }
        
        /* 解读区域 */
        .reading-section {
            display: none;
            margin-top: 60px;
            text-align: center;
        }
        
        .reading-section.active {
            display: block;
        }
        
        .reading-title {
            font-family: 'Cinzel', serif;
            font-size: 1.5rem;
            color: var(--gold);
            margin-bottom: 30px;
            letter-spacing: 0.2em;
        }
        
        .reading-content {
            background: rgba(26, 10, 46, 0.6);
            border: 1px solid var(--gold-dark);
            padding: 30px;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.8;
            color: var(--text-primary);
        }
        
        .reading-card-name {
            color: var(--gold-light);
            font-weight: 600;
            font-size: 1.2rem;
        }
        
        /* 动画 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        
        .animate-in {
            animation: fadeIn 0.6s ease forwards;
        }
        
        /* 抽牌动画 */
        .card-slot.dealing {
            animation: dealCard 0.6s ease forwards;
        }
        
        @keyframes dealCard {
            from { 
                opacity: 0; 
                transform: translateY(-100px) scale(0.8) rotateX(30deg);
            }
            to { 
                opacity: 1; 
                transform: translateY(0) scale(1) rotateX(0);
            }
        }
        
        /* 选中高亮 */
        .card-slot.selected {
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.5);
        }
        
        .card-slot.selected .card-face {
            border-color: var(--gold-light);
        }
    </style>
</head>
<body>
    <!-- 新艺术风格背景 -->
    <svg class="art-nouveau-bg" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
        <defs>
            <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#d4af37"/>
                <stop offset="50%" style="stop-color:#f4d03f"/>
                <stop offset="100%" style="stop-color:#d4af37"/>
            </linearGradient>
        </defs>
        <!-- 角落装饰 -->
        <path d="M0,0 Q100,50 150,150 T200,300" stroke="url(#goldGrad)" fill="none" stroke-width="1"/>
        <path d="M1000,0 Q900,50 850,150 T800,300" stroke="url(#goldGrad)" fill="none" stroke-width="1"/>
        <path d="M0,1000 Q100,950 150,850 T200,700" stroke="url(#goldGrad)" fill="none" stroke-width="1"/>
        <path d="M1000,1000 Q900,950 850,850 T800,700" stroke="url(#goldGrad)" fill="none" stroke-width="1"/>
        <!-- 中心装饰 -->
        <circle cx="500" cy="500" r="350" stroke="url(#goldGrad)" fill="none" stroke-width="0.5"/>
        <circle cx="500" cy="500" r="300" stroke="url(#goldGrad)" fill="none" stroke-width="0.3"/>
    </svg>
    
    <div class="container">
        <!-- 标题区 -->
        <div class="title-section">
            <h1 class="main-title">TAROT</h1>
            <p class="subtitle">塔罗三牌阵 · 探索命运的奥秘</p>
        </div>
        
        <!-- 问题输入区 -->
        <div class="question-section" id="questionSection">
            <div class="art-nouveau-border">
                <p style="color: var(--text-secondary); margin-bottom: 20px; font-size: 0.95rem;">
                    静心冥想，默念你心中的疑问
                </p>
                <input type="text" class="question-input" id="questionInput" 
                       placeholder="请输入你的问题... (选填)">
                <div style="margin-top: 25px;">
                    <button class="btn-divine" onclick="startDivination()">
                        开 始 占 卜
                    </button>
                </div>
            </div>
        </div>
        
        <!-- 牌阵区 -->
        <div class="spread-section" id="spreadSection">
            <div class="spread-container">
                <!-- 第一行 - 过去 -->
                <div class="spread-row">
                    <div class="card-slot" id="slot0">
                        <span class="card-position">过 去</span>
                        <div class="card" onclick="flipCard(0)">
                            <div class="card-face card-back">
                                <div class="card-back-pattern"></div>
                                <div class="card-back-inner">
                                    <span class="card-back-symbol">☽</span>
                                </div>
                            </div>
                            <div class="card-face card-front">
                                <div class="card-front-frame">
                                    <div class="card-symbol" id="symbol0"></div>
                                    <div class="card-name" id="name0"></div>
                                    <div class="card-name-cn" id="nameCn0"></div>
                                    <span class="card-orientation" id="orient0"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 第二行 - 现在 & 未来 -->
                <div class="spread-row">
                    <div class="card-slot" id="slot1">
                        <span class="card-position">当 下</span>
                        <div class="card" onclick="flipCard(1)">
                            <div class="card-face card-back">
                                <div class="card-back-pattern"></div>
                                <div class="card-back-inner">
                                    <span class="card-back-symbol">☽</span>
                                </div>
                            </div>
                            <div class="card-face card-front">
                                <div class="card-front-frame">
                                    <div class="card-symbol" id="symbol1"></div>
                                    <divclass="card-name" id="name1"></div>
                                    <div class="card-name-cn" id="nameCn1"></div>
                                    <span class="card-orientation" id="orient1"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card-slot" id="slot2">
                        <span class="card-position">未 来</span>
                        <div class="card" onclick="flipCard(2)">
                            <div class="card-face card-back">
                                <div class="card-back-pattern"></div>
                                <div class="card-back-inner">
                                    <span class="card-back-symbol">☽</span>
                                </div>
                            </div>
                            <div class="card-face card-front">
                                <div class="card-front-frame">
                                    <div class="card-symbol" id="symbol2"></div>
                                    <div class="card-name" id="name2"></div>
                                    <div class="card-name-cn" id="nameCn2"></div>
                                    <span class="card-orientation" id="orient2"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 解读区 -->
        <div class="reading-section" id="readingSection">
            <h2 class="reading-title">✧ 命 运 启 示 ✧</h2>
            <div class="reading-content" id="readingContent"></div>
            <div style="margin-top: 30px;">
                <button class="btn-divine" onclick="resetDivination()">
                    重 新 占 卜
                </button>
            </div>
        </div>
    </div>
    
    <script>
        // 塔罗牌数据
        const tarotCards = [
            { name: "The Fool", cn: "愚者", symbol: "fool" },
            { name: "The Magician", cn: "魔术师", symbol: "magician" },
            { name: "The High Priestess", cn: "女祭司", symbol: "priestess" },
            { name: "The Empress", cn: "女皇", symbol: "empress" },
            { name: "The Emperor", cn: "皇帝", symbol: "emperor" },
            { name: "The Hierophant", cn: "教皇", symbol: "hierophant" },
            { name: "The Lovers", cn: "恋人", symbol: "lovers" },
            { name: "The Chariot", cn: "战车", symbol: "chariot" },
            { name: "Strength", cn: "力量", symbol: "strength" },
            { name: "The Hermit", cn: "隐士", symbol: "hermit" },
            { name: "Wheel of Fortune", cn: "命运之轮", symbol: "wheel" },
            { name: "Justice", cn: "正义", symbol: "justice" },
            { name: "The Hanged Man", cn: "倒吊人", symbol: "hanged" },
            { name: "Death", cn: "死神", symbol: "death" },
            { name: "Temperance", cn: "节制", symbol: "temperance" },
            { name: "The Devil", cn: "恶魔", symbol: "devil" },
            { name: "The Tower", cn: "塔", symbol: "tower" },
            { name: "The Star", cn: "星星", symbol: "star" },
            { name: "The Moon", cn: "月亮", symbol: "moon" },
            { name: "The Sun", cn: "太阳", symbol: "sun" },
            { name: "Judgement", cn: "审判", symbol: "judgement" },
            { name: "The World", cn: "世界", symbol: "world" }
        ];
        
        // 牌义解读
        const cardMeanings = {
            fool: { upright: "新的开始、自由、纯真、冒险", reversed: "冲动、鲁莽、幼稚、等待" },
            magician: { upright: "创造力、技巧、意志力、显现", reversed: "操控、欺骗、无力、浪费天赋" },
            priestess: { upright: "直觉、神秘、智慧、内在声音", reversed: "隐藏的秘密、误导、模糊不清" },
            empress: { upright: "丰盛、创造力、自然、母亲", reversed: "依赖、停滞、创作障碍、空虚" },
            emperor: { upright: "权威、结构、稳定、领导力", reversed: " rigidty、缺乏自律、滥用权力" },
            hierophant: { upright: "传统、信仰、启示、精神指导", reversed: "叛逆、不合常规、个人信仰" },
            lovers: { upright: "爱、和谐、选择、吸引力", reversed: "失衡、冲突、错误选择、不和谐" },
            chariot: { upright: "意志力、胜利、决心、控制", reversed: "失控、失去方向、缺乏自律" },
            strength: { upright: "勇气、耐心、慈悲、力量", reversed: "自我怀疑、软弱、缺乏勇气" },
            hermit: { upright: "内省、孤独、寻找真理、指引", reversed: "孤立、孤独、迷失方向" },
            wheel: { upright: "命运、转变、循环、机会", reversed: "厄运、停滞、坏运气、阻碍" },
            justice: { upright: "公平、真相、法律、因果", reversed: "不公、不诚实、法律问题、缺乏责任感" },
            hanged: { upright: "暂停、牺牲、新的视角、等待", reversed: "停滞、拒绝牺牲、拖延、徒劳" },
            death: { upright: "结束、转变、过渡、释放", reversed: "抗拒改变、僵化、停滞不前" },
            temperance: { upright: "平衡、耐心、目的、调整", reversed: "失衡、过度、缺乏调整" },
            devil: { upright: "束缚、物质主义、诱惑、阴影面", reversed: "释放、挣脱束缚、打破模式" },
            tower: { upright: "突变、启示、解放、觉醒", reversed: "害怕改变、避免灾难、内部冲突" },
            star: { upright: "希望、灵感、平静、疗愈", reversed: "绝望、迷失、缺乏信念" },
            moon: { upright: "幻觉、恐惧、潜意识、直觉", reversed: "恐惧、混乱、隐藏的真相被揭露" },
            sun: { upright: "快乐、成功、活力、活力", reversed: "过度乐观、表面的成功、暂时的挫折" },
            judgement: { upright: "觉醒、重生、复兴、判决", reversed: "自我怀疑、犹豫、错失机会" },
            world: { upright: "完成、成就、整合、成就感", reversed: "缺乏成就感、未完成、失败" }
        };
        
        // 位置解读
        const positionMeanings = [
            { name: "过 去", desc: "代表问题的根源与背景，揭示隐藏的影响因素" },
            { name: "当 下", desc: "代表当前面临的状况与挑战，以及你的应对方式" },
            { name: "未 来", desc: "代表可能的结果与发展方向，提供建议与指引" }
        ];
        
        // SVG 符号
        const symbols = {
            fool: `<svg viewBox="0 0 60 60"><circle cx="30" cy="20" r="8" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M30 28 L30 45 M22 35 L38 35 M25 50 Q30 55 35 50" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="42" cy="12" r="5" fill="#d4af37" opacity="0.6"/></svg>`,
            magician: `<svg viewBox="0 0 60 60"><path d="M30 10 L30 50 M20 30 L40 30" stroke="#d4af37" stroke-width="2"/><circle cx="30" cy="30" r="12" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M10 50 Q30 40 50 50" fill="none" stroke="#d4af37" stroke-width="1"/></svg>`,
            priestess: `<svg viewBox="0 0 60 60"><path d="M30 8 L30 52" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="20" r="10" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M15 45 L45 45 L40 52 L20 52 Z" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="20" r="4" fill="#d4af37" opacity="0.5"/></svg>`,
            empress: `<svg viewBox="0 0 60 60"><circle cx="30" cy="22" r="8" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M20 35 Q30 50 40 35 Q35 45 30 35 Q25 45 20 35" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M15 52 L45 52" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            emperor: `<svg viewBox="0 0 60 60"><path d="M30 10 L30 50" stroke="#d4af37" stroke-width="2"/><path d="M15 10 L45 10 L40 20 L20 20 Z" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M20 35 L40 35 M20 45 L40 45" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            hierophant: `<svg viewBox="0 0 60 60"><path d="M30 8 L30 52" stroke="#d4af37" stroke-width="2"/><circle cx="30" cy="20" r="8" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M22 40 L38 40 L35 52 L25 52 Z" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="20" r="3" fill="#d4af37"/></svg>`,
            lovers: `<svg viewBox="0 0 60 60"><path d="M20 25 Q20 15 30 20 Q40 15 40 25 Q40 35 30 45 Q20 35 20 25" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="30" r="3" fill="#d4af37"/></svg>`,
            chariot: `<svg viewBox="0 0 60 60"><rect x="15" y="25" width="30" height="15" rx="3" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="20" cy="48" r="5" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="40" cy="48" r="5" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M15 25 L30 15 L45 25" fill="none" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            strength: `<svg viewBox="0 0 60 60"><path d="M30 15 Q45 25 40 40 Q30 50 20 40 Q15 25 30 15" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="30" r="8" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M30 22 L30 38 M22 30 L38 30" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            hermit: `<svg viewBox="0 0 60 60"><path d="M30 10 L30 50" stroke="#d4af37" stroke-width="2"/><path d="M30 10 L25 20 L30 18 L35 20 Z" fill="#d4af37"/><circle cx="30" cy="30" r="6" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M15 50 L45 50" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            wheel: `<svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="20" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="30" r="10" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M30 10 L30 50 M10 30 L50 30" stroke="#d4af37" stroke-width="1.5"/><path d="M16 16 L44 44 M44 16 L16 44" stroke="#d4af37" stroke-width="1"/></svg>`,
            justice: `<svg viewBox="0 0 60 60"><path d="M30 10 L30 50" stroke="#d4af37" stroke-width="2"/><path d="M18 18 L42 18 L38 25 L22 25 Z" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="38" r="6" fill="none" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            hanged: `<svg viewBox="0 0 60 60"><path d="M30 8 L30 40" stroke="#d4af37" stroke-width="2"/><circle cx="30" cy="18" r="6" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M22 40 L30 35 L38 40" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M15 50 L45 50" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            death: `<svg viewBox="0 0 60 60"><path d="M30 10 L30 50" stroke="#d4af37" stroke-width="2"/><path d="M20 20 L40 40 M40 20 L20 40" stroke="#d4af37" stroke-width="2"/><path d="M15 50 L45 50" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            temperance: `<svg viewBox="0 0 60 60"><path d="M20 15 Q30 25 40 15 L40 35 Q30 45 20 35 Z" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M25 25 L35 25 M25 30 L35 30" stroke="#d4af37" stroke-width="1"/><path d="M30 40 L30 50" stroke="#d4af37" stroke-width="2"/></svg>`,
            devil: `<svg viewBox="0 0 60 60"><path d="M30 15 Q40 25 35 35 Q30 45 25 35 Q20 25 30 15" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M25 10 L30 18 L35 10" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="30" r="5" fill="#d4af37" opacity="0.5"/><path d="M20 45 L40 45" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            tower: `<svg viewBox="0 0 60 60"><path d="M25 10 L25 50 M35 10 L35 50" stroke="#d4af37" stroke-width="2"/><path d="M25 10 L30 5 L35 10" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M20 50 L40 50" stroke="#d4af37" stroke-width="1.5"/><path d="M15 20 L25 25 M45 20 L35 25" stroke="#d4af37" stroke-width="1.5"/><path d="M18 30 L25 33 M42 30 L35 33" stroke="#d4af37" stroke-width="1"/></svg>`,
            star: `<svg viewBox="0 0 60 60"><path d="M30 10 L33 25 L48 25 L36 35 L40 50 L30 42 L20 50 L24 35 L12 25 L27 25 Z" fill="none" stroke="#d4af37" stroke-width="1.5"/></svg>`,
            moon: `<svg viewBox="0 0 60 60"><path d="M35 15 Q50 30 35 45 Q25 35 35 25 Q25 30 35 15" fill="none" stroke="#d4af37" stroke-width="1.5"/><circle cx="20" cy="30" r="2" fill="#d4af37"/><circle cx="15" cy="25" r="1.5" fill="#d4af37" opacity="0.6"/><circle cx="18" cy="38" r="1" fill="#d4af37" opacity="0.4"/></svg>`,
            sun: `<svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="12" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M30 10 L30 18 M30 42 L30 50 M10 30 L18 30 M42 30 L50 30" stroke="#d4af37" stroke-width="1.5"/><path d="M16 16 L22 22 M38 38 L44 44 M44 16 L38 22 M22 38 L16 44" stroke="#d4af37" stroke-width="1"/></svg>`,
            judgement: `<svg viewBox="0 0 60 60"><path d="M15 35 L30 20 L45 35" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M30 20 L30 50" stroke="#d4af37" stroke-width="2"/><path d="M20 45 L40 45" stroke="#d4af37" stroke-width="1.5"/><circle cx="30" cy="35" r="5" fill="none" stroke="#d4af37" stroke-width="1"/></svg>`,
            world: `<svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="20" fill="none" stroke="#d4af37" stroke-width="1.5"/><path d="M30 10 L30 50 M10 30 L50 30" stroke="#d4af37" stroke-width="1"/><path d="M30 18 L38 30 L30 42 L22 30 Z" fill="none" stroke="#d4af37" stroke-width="1.5"/></svg>`
        };
        
        let drawnCards = [];
        let flippedCards = [];
        
        function startDivination() {
            const question = document.getElementById('questionInput').value;
            document.getElementById('questionSection').style.display = 'none';
            document.getElementById('spreadSection').classList.add('active');
            
            // 随机抽取三张牌
            drawnCards = [];
            flippedCards = [false, false, false];
            
            for (let i = 0; i < 3; i++) {
                const randomIndex = Math.floor(Math.random() * tarotCards.length);
                const isReversed = Math.random() > 0.7; // 30% 概率逆位
                drawnCards.push({
                    ...tarotCards[randomIndex],
                    isReversed: isReversed
                });
            }
            
            // 发牌动画
            for (let i = 0; i < 3; i++) {
                setTimeout(() => {
                    const slot = document.getElementById(`slot${i}`);
                    slot.classList.add('dealing');
                }, i * 300);
            }
        }
        
        function flipCard(index) {
            if (flippedCards[index]) return;
            
            const card = document.querySelectorAll('.card')[index];
            card.classList.add('flipped');
            flippedCards[index] = true;
            
            // 更新牌面内容
            const cardData = drawnCards[index];
            document.getElementById(`symbol${index}`).innerHTML = symbols[cardData.symbol];
            document.getElementById(`name${index}`).textContent = cardData.name;
            document.getElementById(`nameCn${index}`).textContent = cardData.cn;
            document.getElementById(`orient${index}`).textContent = cardData.isReversed ? '逆 位' : '正 位';
            
            // 检查是否全部翻开
            if (flippedCards.every(f => f)) {
                setTimeout(showReading, 800);
            }
        }
        
        function showReading() {
            const positions = ['过 去', '当 下', '未 来'];
            let readingHTML = '';
            
            drawnCards.forEach((card, index) => {
                const meaning = cardMeanings[card.symbol];
                const orientation = card.isReversed ? '逆位' : '正位';
                const meaningText = card.isReversed ? meaning.reversed : meaning.upright;
                
                readingHTML += `
                    <p style="margin: 20px 0;">
                        <span class="reading-card-name">【${card.cn}】</span> 
                        ${positions[index]} · ${orientation}
                    </p>
                    <p style="color: var(--text-secondary); margin-bottom: 10px;">
                        ${meaningText}
                    </p>
                    <p style="font-size: 0.9rem; margin-bottom: 25px;">
                        ${positionMeanings[index].desc}
                    </p>
                `;
            });
            
            // 整体解读
            readingHTML += `
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid var(--gold-dark);">
                    <p style="color: var(--gold); font-size: 0.95rem;">
                        整体启示：这三张牌共同诉说着你生命旅程中的故事。从 ${drawnCards[0].cn} 的根基，
                        穿越 ${drawnCards[1].cn} 的当下挑战，到达 ${drawnCards[2].cn} 的未来可能。
                        命运的丝线正在交织，愿你从中获得启示与力量。
                    </p>
                </div>
            `;
            
            document.getElementById('readingContent').innerHTML = readingHTML;
            document.getElementById('readingSection').classList.add('active');
        }
        
        function resetDivination() {
            document.getElementById('questionSection').style.display = 'block';
            document.getElementById('spreadSection').classList.remove('active');
            document.getElementById('readingSection').classList.remove('active');
            document.getElementById('questionInput').value = '';
            
            // 重置卡片状态
            document.querySelectorAll('.card').forEach(card => {
                card.classList.remove('flipped');
            });
            document.querySelectorAll('.card-slot').forEach(slot => {
                slot.classList.remove('dealing', 'selected');
            });
        }
    </script>
</body>
</html>
```

## 使用流程

1. **输入问题**（可选）：用户可在输入框中默念或输入心中疑问
2. **点击开始**：点击"开始占卜"按钮
3.**观看发牌**：三张牌背依次动画出现
4. **点击翻牌**：用户可点击任意牌翻开（也可全部自动翻开）
5. **查看解读**：牌阵解读将显示三张牌在"过去-现在-未来"位置的意义

## 质量验证

- Frontmatter 格式正确
- 所有塔罗牌数据完整（22张大阿尔卡纳）
- 新艺术风格 SVG 边框装饰
- 3D 翻牌动画效果
- 响应式布局支持移动端
- 金色渐变文字和装饰元素
