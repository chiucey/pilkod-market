---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 738caaee625835e914a5246f550975b3
    PropagateID: 738caaee625835e914a5246f550975b3
    ReservedCode1: 304502204ce20245aa46b7e3c29d084906aa6034ee1e57df480fe389b3b24c16d2654018022100d22926c98ff9f8615861f8599e0e76e6a9fee0ef2326b2e6a9726c9a5072f093
    ReservedCode2: 304402200e8cdfcba88177cfd8f62095f9f9732c2887472b2b5c7b80ff8a3396170d73c6022043de5641e0d56ae60ef92bde392b83bee0eaa201f35fb27e7b1641728867e920
description: 整理和生成错题卡片。当用户提供错题内容时，自动提取题目、错因分析，生成美观的HTML卡片展示。触发场景：整理错题、生成错题卡片、错题本整理、错题本。
name: wrong-answer-cards
---

# Wrong Answer Cards Organizer

## Workflow

### 1. Information Extraction
Automatically identify and extract from user input:
- **Question**: Complete problem description (including options A/B/C/D)
- **User's Answer**: The answer the user selected (marked as wrong)
- **Correct Answer**: The correct answer (marked as right)
- **Note**: Key points to remember, tips, or important reminders for avoiding similar mistakes

### 2. Error Type Classification
Automatically classify based on error characteristics:

| Error Type | Criteria |
|-----------|----------|
| Careless | Calculation mistakes, misreading, missing options |
| Vague Knowledge | Partial understanding, confusing similar concepts |
| Completely Unfamiliar | No understanding, unfamiliar topic |

### 3. Tagging
Automatically tag in output:
- **Subject**: Math, English, Physics, Chemistry, Chinese, History, Geography, etc.
- **Knowledge Point**: Key topics auto-identified from question content

### 4. Output Format Selection

**Primary Format**: Beautiful HTML Cards with Red/Green Feedback (Recommended)
**Fallback Format**: ASCII Box Art

---

## Output Formats

### Format A: Beautiful HTML Cards with Red/Green Feedback (Recommended)

Generate complete, self-contained HTML files with quiz-style feedback design.

**Design Features**:
- 2x2 option grid layout with visual feedback (red for wrong, green for correct)
- √/× symbols for clear status indication
- Left-side colored accent bars for answer feedback cards
- Light background colors with strong text contrast
- Subject-specific gradient header colors
- Error type badges with distinct colors
- Responsive grid layout
- Hover animations for interactivity

**Color Scheme (Red Wrong, Green Correct)**:
| Element | Wrong | Correct |
|---------|-------|---------|
| Option Background | #ffebee (light red) | #e8f5e9 (light green) |
| Option Text | #c62828 (dark red) | #2e7d32 (dark green) |
| Left Accent Bar | #c62828 (dark red) | #2e7d32 (dark green) |
| Answer Label | #757575 (gray) | #757575 (gray) |
| Answer Text | #c62828 bold | #2e7d32 bold |

**Subject Color Themes** (Header Gradient):
| Subject | Gradient Colors |
|---------|----------------|
| Math | #667eea → #764ba2 (Purple-Blue) |
| English | #f093fb → #f5576c (Pink-Red) |
| Physics | #4facfe → #00f2fe (Blue-Cyan) |
| Chemistry | #43e97b → #38f9d7 (Green-Cyan) |
| Chinese | #fa709a → #fee140 (Warm Gradient) |

**Error Type Badges**:
| Type | Background | Text Color |
|------|-----------|------------|
| Careless | #fff3cd | #856404 |
| Vague Knowledge | #ffeaa7 | #d63031 |
| Unfamiliar | #dfe6e9 | #636e72 |

---

## HTML Card Structure

### Upper Section: Option Grid (2x2)

Display all options with visual feedback:
- Wrong option: Light red background (#ffebee), dark red text (#c62828), red × icon
- Correct option: Light green background (#e8f5e9), dark green text (#2e7d32), green √ icon
- Other options: Gray background (#f5f5f5), gray text (#616161)

### Lower Section: Answer Feedback Cards

Two stacked cards with left accent bars:
1. **My Answer Card**: Light pink background, dark red accent bar
2. **Correct Answer Card**: Light green background, dark green accent bar

### Card Structure Example:

```html
<!-- Option Grid -->
<div class="options-grid">
    <div class="option option-correct">
        <span class="option-letter">A</span>
        <span class="option-text">选项内容</span>
        <span class="option-icon correct">✓</span>
    </div>
    <div class="option option-correct">
        <span class="option-letter">B</span>
        <span class="option-text">选项内容</span>
        <span class="option-icon correct">✓</span>
    </div>
    <div class="option option-wrong">
        <span class="option-letter">C</span>
        <span class="option-text">选项内容</span>
        <span class="option-icon wrong">✗</span>
    </div>
    <div class="option">
        <span class="option-letter">D</span>
        <span class="option-text">选项内容</span>
    </div>
</div>

<!-- Answer Feedback -->
<div class="answer-cards">
    <div class="answer-card answer-wrong">
        <div class="answer-accent"></div>
        <div class="answer-content">
            <span class="answer-label">我的答案</span>
            <span class="answer-value wrong">C. 选项内容</span>
        </div>
    </div>
    <div class="answer-card answer-correct">
        <div class="answer-accent"></div>
        <div class="answer-content">
            <span class="answer-label">正确答案</span>
            <span class="answer-value correct">B. 选项内容</span>
        </div>
    </div>
</div>
```

---

### Format B: ASCII Box Art (Fallback)

When HTML is not requested or plain text is preferred:

```
┌─────────────────────────────────────────────┐
│ Wrong Answer Card #{number}
├─────────────────────────────────────────────┤
│ [Subject] [Knowledge Tags]
│ [Error Type: Careless/Vague Knowledge/Unfamiliar]
├─────────────────────────────────────────────┤
│ Options:                                    │
│   A. [Option] [✓/ ]                        │
│   B. [Option] [✓] (Correct)                │
│   C. [Option] [✗] (Your Answer)             │
│   D. [Option] [ ]                           │
├─────────────────────────────────────────────┤
│ My Answer: C. [Answer]                      │
│ Correct Answer: B. [Answer]                 │
├─────────────────────────────────────────────┤
│ [Analysis]                                  │
│ [Note]                                      │
└─────────────────────────────────────────────┘
```

---

## Output Rules

1. **Default to HTML format** - Generate beautiful quiz-style HTML cards as primary output
2. **Red wrong, green correct** - Use the red/green color scheme consistently
3. **Always show both user answer and correct answer** - In separate feedback cards
4. **Display all options in 2x2 grid** - With visual status indicators
5. **ASCII fallback** - Use ASCII box format only when explicitly requested
6. **Auto-detection** of subject and knowledge points from question content
7. **Context-aware** error type classification considering question context
8. **Batch processing** - Multiple cards output in a single HTML file with grid layout
9. **File delivery** - Provide download link for HTML file

---

## Example

**User Input:**
> Question: What are the solutions to x²-5x+6=0?
> Options: A. x=1 B. x=2 C. x=3 D. x=2 or x=3
> My Answer: C
> Correct Answer: D

**HTML Output:**

```html
<div class="wrong-answer-card">
    <div class="card-header math">
        <span class="card-number">错题卡片 #1</span>
        <div class="card-tags">
            <span class="tag">数学</span>
            <span class="tag">一元二次方程</span>
            <span class="error-type careless">粗心大意</span>
        </div>
    </div>
    <div class="card-body">
        <div class="section question">
            <div class="section-label">题目</div>
            <div class="section-content">求解方程 x² - 5x + 6 = 0</div>
        </div>

        <!-- Option Grid -->
        <div class="options-grid">
            <div class="option">
                <span class="option-letter">A</span>
                <span class="option-text">x=1</span>
            </div>
            <div class="option">
                <span class="option-letter">B</span>
                <span class="option-text">x=2</span>
            </div>
            <div class="option option-wrong">
                <span class="option-letter">C</span>
                <span class="option-text">x=3</span>
                <span class="option-icon wrong">✗</span>
            </div>
            <div class="option option-correct">
                <span class="option-letter">D</span>
                <span class="option-text">x=2 or x=3</span>
                <span class="option-icon correct">✓</span>
            </div>
        </div>

        <!-- Answer Feedback Cards -->
        <div class="answer-cards">
            <div class="answer-card answer-wrong">
                <div class="answer-accent"></div>
                <div class="answer-content">
                    <span class="answer-label">我的答案</span>
                    <span class="answer-value wrong">C. x=3</span>
                </div>
            </div>
            <div class="answer-card answer-correct">
                <div class="answer-accent"></div>
                <div class="answer-content">
                    <span class="answer-label">正确答案</span>
                    <span class="answer-value correct">D. x=2 or x=3</span>
                </div>
            </div>
        </div>

        <div class="section analysis">
            <div class="section-label">错因分析</div>
            <div class="section-content">该方程有两个实数根。只写出一个解是不完整的。</div>
        </div>
        <div class="section note">
            <div class="section-label">注意</div>
            <div class="section-content">解一元二次方程时，务必使用求根公式完整求解所有根。</div>
        </div>
    </div>
</div>
```

---

## Trigger Scenarios

- User pastes wrong answer screenshot/text
- User says "help me organize wrong answers", "organize review cards"
- User provides multiple wrong answers for batch processing
- User requests "beautiful cards", "HTML format", "generate cards as HTML"
- User wants to download or print organized wrong answers
- User asks to organize "错题本"

## References

- `references/html-template.md` - Complete HTML template with full styling
- `references/error-types.md` - Detailed error type classification guide
