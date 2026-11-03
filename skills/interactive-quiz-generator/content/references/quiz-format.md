# 交互式测验生成器 - 参考文档

## 模板变量

所有 HTML 模板使用双花括号 `{{VARIABLE}}` 作为占位符：

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{QUIZ_TITLE}}` | 测验标题 | "Python 基础测验" |
| `{{QUESTION_COUNT}}` | 题目总数 | "10" |
| `{{QUIZ_DATA}}` | 题目 JSON 数据 | 见下方格式 |

## 题目数据格式

```json
[
  {
    "question": "以下关于 Python 的说法正确的是？",
    "type": "single",
    "options": ["A选项", "B选项", "C选项", "D选项"],
    "correct": 0,
    "points": 10,
    "explanation": "正确答案是 A，因为..."
  },
  {
    "question": "以下哪些是 Python 的数据类型？（多选）",
    "type": "multiple",
    "options": ["int", "float", "string", "char"],
    "correct": [0, 1, 2],
    "points": 15,
    "explanation": "Python 没有 char 类型"
  },
  {
    "question": "Python 是一种编译型语言。",
    "type": "boolean",
    "options": ["正确", "错误"],
    "correct": 1,
    "points": 5,
    "explanation": "Python 是解释型语言"
  }
]
```

## 题型说明

| 类型 | 值 | 说明 | 正确答案格式 |
|------|-----|------|-------------|
| 单选题 | `single` | 四选一 | `correct: 0-3` |
| 多选题 | `multiple` | 多选 | `correct: [0, 2]` |
| 判断题 | `boolean` | 对/错 | `correct: 0或1` |

## 模板对比

### Study（童趣探索版）
- 适用：儿童教育、亲子学习
- 特点：
  - 柔和渐变背景
  - 圆角卡片设计
  - 积分星星奖励
  - 正确答案动画庆祝
  - 彩色进度条

### Elegant（优雅极简版）
- 适用：正式考试、知识考核
- 特点：
  - 网格布局
  - 精准阴影效果
  - 清晰数据可视化
  - 高对比度文字
  - 专业配色

### Game（活力游戏版）
- 适用：年轻用户、培训活动
- 特点：
  - 暗色主题
  - 进度条动画
  - 连击积分系统
  - 键盘快捷键支持 (A/S/D/F)
  - 粒子动效背景
  - Combo 连击提示

## 使用示例

### Python 示例

```python
from quiz_generator import QuizGenerator

generator = QuizGenerator()

# 方式1: 从文本内容生成
html = generator.generate_from_file(
    content="Python 的基础语法...",
    title="Python 入门测验",
    style="elegant",
    question_count=10
)

# 方式2: 从题目 JSON 生成
questions = [
    {
        "question": "Python 的创始人是谁？",
        "type": "single",
        "options": ["Guido van Rossum", "Linus Torvalds", "Bill Gates", "Steve Jobs"],
        "correct": 0,
        "points": 10,
        "explanation": "Python 由 Guido van Rossum 创造"
    }
]
html = generator.generate_from_json(questions, "Python 历史", "game")

# 保存
generator.save_html(html, "output/quiz.html")
```

### 命令行使用

```bash
# 从文本生成
python quiz_generator.py -c "内容文本..." -t "测验标题" -s elegant -o output.html

# 从文件生成
python quiz_generator.py -f content.txt -t "测验标题" -s game -q 15 -o output.html
```

## 自定义模板

如需修改模板样式，可编辑 `/templates/` 目录下的 HTML 文件。

### CSS 变量说明

```css
:root {
    --primary: #6C5CE7;     /* 主色调 */
    --secondary: #A29BFE;  /* 次要色 */
    --accent: #FD79A8;     /* 强调色 */
    --success: #00CEC9;     /* 正确颜色 */
    --error: #FF7675;      /* 错误颜色 */
    --background: #...;    /* 背景色 */
    --text: #...;          /* 文字颜色 */
}
```

## 部署说明

生成的 HTML 文件是完全独立的单文件应用：
- 无需服务器端支持
- 无需外部依赖
- 可直接在浏览器打开
- 可通过 GitHub Pages、Netlify 等免费托管
