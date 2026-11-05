---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 6752e5d7eef2195bfd83f5473ae5f87e
    PropagateID: 6752e5d7eef2195bfd83f5473ae5f87e
    ReservedCode1: 30450220053e0bb400edff5977066b4f0b4e34968997f70beacd724705b441268d968c2c022100f98c6564e478cd6a8af09756f82ab9db134580966a6aee747e6bfcd5b1175637
    ReservedCode2: 304502201e85c8a5a3d98be2b9af27ed82f69312d09083da816967d81d588e44a500304f022100aafc4eba832e74a1d81ddcced21f1a404a0d052bac34d12b1030bdd169a2d688
---

# 错题卡片HTML模板参考（新样式）

本文档提供类似答题反馈界面的错题卡片HTML输出模板参考。

## 新设计特点

根据用户上传的图片样式，新设计包含：

- **上方2x2选项网格**：红绿配色，√/×符号
- **下方答案反馈卡片**：左侧彩色装饰条
- **"红错绿对"配色方案**：经典的红绿灯色彩心理学
- **圆角卡片设计**：现代简约风

## 颜色方案

| 元素 | 错误状态 | 正确状态 |
|------|----------|----------|
| 选项背景 | #ffebee (淡红) | #e8f5e9 (淡绿) |
| 选项文字 | #c62828 (深红) | #2e7d32 (深绿) |
| 左侧装饰条 | #c62828 (深红) | #2e7d32 (深绿) |
| 图标颜色 | #c62828 (深红) | #2e7d32 (深绿) |

## HTML模板代码

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>错题卡片集</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .header h1 {
            font-size: 2rem;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }

        .header .subtitle {
            color: #7f8c8d;
            font-size: 0.9rem;
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
        }

        .wrong-answer-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .wrong-answer-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }

        .card-header {
            padding: 1.25rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Subject gradient headers */
        .card-header.math { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-header.english { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .card-header.physics { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .card-header.chemistry { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .card-header.chinese { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

        .card-number {
            color: white;
            font-weight: 600;
            font-size: 1.1rem;
        }

        .card-tags {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .tag {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            color: white;
            background: rgba(255, 255, 255, 0.25);
        }

        .error-type {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .error-type.careless { background: #fff3cd; color: #856404; }
        .error-type.vague { background: #ffeaa7; color: #d63031; }
        .error-type.unfamiliar { background: #dfe6e9; color: #636e72; }

        .card-body {
            padding: 1.5rem;
        }

        .section {
            margin-bottom: 1.25rem;
        }

        .section:last-child {
            margin-bottom: 0;
        }

        .section-label {
            font-size: 0.8rem;
            color: #95a5a6;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .section-content {
            color: #2c3e50;
            line-height: 1.6;
            font-size: 0.95rem;
        }

        /* ==================== NEW STYLE: OPTIONS GRID ==================== */
        .options-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
            margin-bottom: 1.25rem;
        }

        .option {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.875rem 1rem;
            border-radius: 12px;
            background: #f5f5f5;
            color: #616161;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }

        .option-letter {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.08);
            font-weight: 600;
            font-size: 0.8rem;
            flex-shrink: 0;
        }

        .option-text {
            flex: 1;
            line-height: 1.4;
        }

        .option-icon {
            font-size: 1rem;
            font-weight: bold;
            flex-shrink: 0;
            margin-left: auto;
        }

        /* Correct option style */
        .option.option-correct {
            background: #e8f5e9;
            color: #2e7d32;
        }

        .option.option-correct .option-letter {
            background: #2e7d32;
            color: white;
        }

        .option-icon.correct {
            color: #2e7d32;
        }

        /* Wrong option style */
        .option.option-wrong {
            background: #ffebee;
            color: #c62828;
        }

        .option.option-wrong .option-letter {
            background: #c62828;
            color: white;
        }

        .option-icon.wrong {
            color: #c62828;
        }

        /* User selected wrong option (highlighted) */
        .option.option-user-wrong {
            background: #ffcdd2;
            color: #b71c1c;
            border: 2px solid #c62828;
        }

        .option.option-user-wrong .option-letter {
            background: #c62828;
            color: white;
        }

        /* ==================== NEW STYLE: ANSWER CARDS ==================== */
        .answer-cards {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-bottom: 1.25rem;
        }

        .answer-card {
            display: flex;
            align-items: center;
            border-radius: 10px;
            overflow: hidden;
            transition: transform 0.2s ease;
        }

        .answer-card:hover {
            transform: scale(1.01);
        }

        .answer-accent {
            width: 5px;
            align-self: stretch;
            flex-shrink: 0;
        }

        .answer-content {
            flex: 1;
            padding: 0.875rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .answer-label {
            font-size: 0.8rem;
            color: #757575;
            font-weight: 500;
            flex-shrink: 0;
        }

        .answer-value {
            font-size: 0.95rem;
            font-weight: 600;
            flex: 1;
        }

        /* Wrong answer card */
        .answer-card.answer-wrong {
            background: #fff5f5;
        }

        .answer-card.answer-wrong .answer-accent {
            background: #c62828;
        }

        .answer-value.wrong {
            color: #c62828;
        }

        /* Correct answer card */
        .answer-card.answer-correct {
            background: #f1f8e9;
        }

        .answer-card.answer-correct .answer-accent {
            background: #2e7d32;
        }

        .answer-value.correct {
            color: #2e7d32;
        }

        /* ==================== ANALYSIS & NOTE SECTIONS ==================== */
        .analysis .section-content {
            background: #f0f7ff;
            padding: 1rem;
            border-radius: 8px;
            border-left: 3px solid #4facfe;
        }

        .note {
            background: #fff9e6;
            padding: 1rem;
            border-radius: 8px;
            border-left: 3px solid #f0ad4e;
        }

        .note .section-content {
            color: #856404;
        }

        /* ==================== RESPONSIVE ==================== */
        @media (max-width: 480px) {
            body {
                padding: 1rem;
            }

            .cards-grid {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 1.5rem;
            }

            .card-number {
                font-size: 1rem;
            }

            .options-grid {
                grid-template-columns: 1fr;
            }

            .section-content {
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>错题卡片集</h1>
            <p class="subtitle">共计 <span id="card-count">0</span> 张错题卡片</p>
        </div>

        <div class="cards-grid" id="cards-container">
            <!-- Dynamic card generation -->
        </div>
    </div>

    <script>
        const wrongAnswers = [
            {
                id: 1,
                subject: 'math',
                subjectName: '数学',
                tags: ['一元二次方程', '求根公式'],
                errorType: 'careless',
                errorTypeName: '粗心大意',
                question: '求解方程 x² - 5x + 6 = 0',
                options: [
                    { letter: 'A', text: 'x=1', isCorrect: false, isUserAnswer: false },
                    { letter: 'B', text: 'x=2', isCorrect: false, isUserAnswer: false },
                    { letter: 'C', text: 'x=3', isCorrect: false, isUserAnswer: true },
                    { letter: 'D', text: 'x=2 or x=3', isCorrect: true, isUserAnswer: false }
                ],
                userAnswer: 'C',
                correctAnswer: 'D',
                analysis: '该方程有两个实数根。只写出一个解是不完整的。对于一元二次方程，务必使用求根公式完整求解所有根。',
                note: '解一元二次方程时，使用求根公式后需要检查是否所有根都满足原方程条件。'
            }
        ];

        function renderCards() {
            const container = document.getElementById('cards-container');
            document.getElementById('card-count').textContent = wrongAnswers.length;

            container.innerHTML = wrongAnswers.map(card => {
                // Determine user answer option and correct answer option
                const userAnswerOpt = card.options.find(o => o.letter === card.userAnswer);
                const correctAnswerOpt = card.options.find(o => o.letter === card.correctAnswer);

                const optionsHTML = card.options.map(opt => {
                    let className = 'option';
                    let iconHTML = '';

                    if (opt.isCorrect && opt.isUserAnswer) {
                        // User selected correct answer - should not happen in wrong answer cards
                        className += ' option-correct option-user-correct';
                        iconHTML = '<span class="option-icon correct">✓</span>';
                    } else if (opt.isCorrect) {
                        // Correct answer
                        className += ' option-correct';
                        iconHTML = '<span class="option-icon correct">✓</span>';
                    } else if (opt.isUserAnswer) {
                        // User's wrong answer
                        className += ' option-wrong';
                        iconHTML = '<span class="option-icon wrong">✗</span>';
                    }

                    return `
                        <div class="${className}">
                            <span class="option-letter">${opt.letter}</span>
                            <span class="option-text">${opt.text}</span>
                            ${iconHTML}
                        </div>
                    `;
                }).join('');

                const answerCardsHTML = `
                    <div class="answer-card answer-wrong">
                        <div class="answer-accent"></div>
                        <div class="answer-content">
                            <span class="answer-label">我的答案</span>
                            <span class="answer-value wrong">${card.userAnswer}. ${userAnswerOpt ? userAnswerOpt.text : ''}</span>
                        </div>
                    </div>
                    <div class="answer-card answer-correct">
                        <div class="answer-accent"></div>
                        <div class="answer-content">
                            <span class="answer-label">正确答案</span>
                            <span class="answer-value correct">${card.correctAnswer}. ${correctAnswerOpt ? correctAnswerOpt.text : ''}</span>
                        </div>
                    </div>
                `;

                return `
                    <div class="wrong-answer-card">
                        <div class="card-header ${card.subject}">
                            <span class="card-number">错题卡片 #${card.id}</span>
                            <div class="card-tags">
                                <span class="tag">${card.subjectName}</span>
                                ${card.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                                <span class="error-type ${card.errorType}">${card.errorTypeName}</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="section question">
                                <div class="section-label">题目</div>
                                <div class="section-content">${card.question}</div>
                            </div>

                            <div class="options-grid">
                                ${optionsHTML}
                            </div>

                            <div class="answer-cards">
                                ${answerCardsHTML}
                            </div>

                            <div class="section analysis">
                                <div class="section-label">错因分析</div>
                                <div class="section-content">${card.analysis}</div>
                            </div>
                            ${card.note ? `
                            <div class="section note">
                                <div class="section-label">注意</div>
                                <div class="section-content">${card.note}</div>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        renderCards();
    </script>
</body>
</html>
```

## 数据结构说明

```javascript
{
    id: 1,
    subject: 'math',           // 科目标识
    subjectName: '数学',        // 科目显示名
    tags: ['一元二次方程'],     // 知识点标签
    errorType: 'careless',     // 错误类型
    errorTypeName: '粗心大意',  // 错误类型显示名
    question: '求解方程 x² - 5x + 6 = 0',  // 题目
    options: [                  // 选项数组（最多4个）
        { letter: 'A', text: 'x=1', isCorrect: false, isUserAnswer: false },
        { letter: 'B', text: 'x=2', isCorrect: false, isUserAnswer: false },
        { letter: 'C', text: 'x=3', isCorrect: false, isUserAnswer: true },  // 用户选择
        { letter: 'D', text: 'x=2 or x=3', isCorrect: true, isUserAnswer: false }  // 正确答案
    ],
    userAnswer: 'C',            // 用户答案字母
    correctAnswer: 'D',         // 正确答案字母
    analysis: '错因分析内容',    // 错因分析
    note: '注意事项'            // 注意点
}
```

## 主题颜色映射

| 科目 | 渐变色 |
|------|--------|
| 数学 (math) | #667eea → #764ba2 |
| 英语 (english) | #f093fb → #f5576c |
| 物理 (physics) | #4facfe → #00f2fe |
| 化学 (chemistry) | #43e97b → #38f9d7 |
| 语文 (chinese) | #fa709a → #fee140 |

## 错误类型样式

| 类型 | 背景色 | 文字色 |
|------|--------|--------|
| 粗心大意 (careless) | #fff3cd | #856404 |
| 知识模糊 (vague) | #ffeaa7 | #d63031 |
| 完全陌生 (unfamiliar) | #dfe6e9 | #636e72 |

## 输出方式

- 生成完整HTML文件供用户下载
- 直接在对话中渲染HTML预览
- 提供可复制的HTML代码块
