# 法考错题分析技能 - 使用示例

## 示例1：完整分析流程

### 场景描述
用户上传了一份法考错题集PDF，希望生成完整的知识点总结、思维导图和可视化图表。

### 用户输入
```
请帮我分析这份法考错题集.pdf，生成知识点总结和图表。
```

### 执行步骤

```python
from law_exam_analyzer import main

# 1. 调用主程序进行完整分析
results = main(
    pdf_path='./法考错题集.pdf',
    output_dir='./output'
)

# 2. 查看生成的文件
print("生成的文档：", results['docx'])
# 输出: ./output/法考错题知识点总结.docx

print("生成的思维导图：", results['mindmap'])
# 输出: ./output/法考错题知识点思维导图.md

print("生成的图表：")
for chart in results['pie_charts']:
    print("  -", chart)
# 输出:
#   - ./output/图1-法律科目错题分布.png
#   - ./output/图2-错误原因分布.png
#   - ./output/图3-知识点掌握程度分布.png
```

### 输出结果
生成的文件列表：
- `法考错题知识点总结.docx` - 包含统计概览、科目分布、详细知识点
- `法考错题知识点思维导图.md` - 树形结构思维导图
- 三张PNG饼状图 - 可视化数据展示

---

## 示例2：仅提取题目信息

### 场景描述
用户只想要提取PDF中的题目，不生成文档。

### 执行代码

```python
from law_exam_analyzer import extract_questions_from_pdf

# 提取题目
questions = extract_questions_from_pdf('./法考错题集.pdf')

# 查看结果
print(f"共提取 {len(questions)} 道题目")

for i, q in enumerate(questions[:3], 1):
    print(f"\n题目 {i}:")
    print(f"  题目: {q['question']}")
    print(f"  选项: {q['options']}")
    print(f"  答案: {q['answer']}")
```

### 输出示例
```
共提取 50 道题目

题目 1:
  题目: 关于民事法律行为的效力，下列说法正确的是：
  选项: {'A': '无民事行为能力人实施的民事法律行为无效', ...}
  答案: B
```

---

## 示例3：仅生成Word文档

### 场景描述
用户已有题目数据，只需要生成格式化的Word文档。

### 执行代码

```python
from law_exam_analyzer import extract_questions_from_pdf, extract_knowledge_points, create_summary_document

# 1. 提取题目
questions = extract_questions_from_pdf('./法考错题集.pdf')

# 2. 分析知识点
knowledge_data = extract_knowledge_points(questions)

# 3. 生成Word文档
docx_path = './output/错题总结.docx'
create_summary_document(knowledge_data, docx_path)
print(f"文档已生成: {docx_path}")
```

---

## 示例4：仅生成思维导图

### 场景描述
用户只需要Markdown格式的思维导图。

### 执行代码

```python
from law_exam_analyzer import extract_questions_from_pdf, extract_knowledge_points, generate_mindmap_markdown

# 1. 提取并分析
questions = extract_questions_from_pdf('./法考错题集.pdf')
knowledge_data = extract_knowledge_points(questions)

# 2. 生成思维导图
mindmap = generate_mindmap_markdown(knowledge_data)

# 3. 保存到文件
with open('./output/思维导图.md', 'w', encoding='utf-8') as f:
    f.write(mindmap)

# 或者直接在控制台输出
print(mindmap)
```

### 输出示例（部分）

```markdown
# 法考错题知识点思维导图

## 概览
- 总错题数：50
- 涉及科目：8个

## 法律科目分类

### 民法 (15题, 30.0%)

#### 概念混淆 (8题)
- 物权与债权的区别
- 民事法律行为的有效要件
```

---

## 示例5：仅生成饼状图表

### 场景描述
用户只需要可视化图表。

### 执行代码

```python
from law_exam_analyzer import extract_questions_from_pdf, extract_knowledge_points, generate_pie_charts
import os

# 确保输出目录存在
os.makedirs('./charts', exist_ok=True)

# 1. 分析数据
questions = extract_questions_from_pdf('./法考错题集.pdf')
knowledge_data = extract_knowledge_points(questions)

# 2. 生成图表
charts = generate_pie_charts(knowledge_data, './charts')

print("生成的图表文件:")
for chart in charts:
    print(f"  - {chart}")
```

---

## 示例6：批量处理多个PDF

### 场景描述
用户有多个错题集PDF需要批量分析。

### 执行代码

```python
from law_exam_analyzer import main
import os

# PDF文件列表
pdf_files = [
    './data/民法错题集.pdf',
    './data/刑法错题集.pdf',
    './data/商法错题集.pdf'
]

# 批量处理
for pdf_path in pdf_files:
    if os.path.exists(pdf_path):
        # 使用PDF文件名作为输出目录名
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = f'./output/{pdf_name}'

        print(f"\n正在分析: {pdf_path}")
        results = main(pdf_path, output_dir)
        print(f"完成: {output_dir}")
```

---

## 示例7：自定义科目分类

### 场景描述
用户想要添加自定义的法律科目分类。

### 执行代码

```python
from law_exam_analyzer import LEGAL_SUBJECTS, classify_subject

# 添加新科目
LEGAL_SUBJECTS['知识产权法'] = [
    '著作权', '专利权', '商标权', '反不正当竞争',
    '软件著作权', '商业秘密'  # 添加自定义关键词
]

# 使用新的分类进行识别
subject = classify_subject(
    question_text="关于软件著作权保护范围的说法，正确的是：",
    analysis="本题考察软件著作权的保护对象..."
)

print(f"识别科目: {subject}")
# 输出: 知识产权法
```

---

## 示例8：OCR扫描版PDF分析（新增）

### 场景描述
用户上传的是扫描版PDF（无法复制文本），需要使用OCR识别。

### 执行代码

```python
from law_exam_analyzer import main

# 方法1：自动检测（推荐）
# 如果普通提取失败，会自动切换到OCR模式
results = main(
    pdf_path='./扫描版错题集.pdf',
    output_dir='./output'
)

# 方法2：强制使用OCR
results = main(
    pdf_path='./扫描版错题集.pdf',
    output_dir='./output',
    use_ocr=True,
    dpi=300
)

# 方法3：使用更高的DPI提高识别率
results = main(
    pdf_path='./扫描版错题集.pdf',
    output_dir='./output',
    use_ocr=True,
    dpi=400  # 更高的DPI，但处理更慢
)
```

### 命令行方式

```bash
# 自动检测模式
python law_exam_analyzer.py ./扫描版错题集.pdf

# 强制OCR模式
python law_exam_analyzer.py ./扫描版错题集.pdf --ocr

# 高分辨率OCR
python law_exam_analyzer.py ./扫描版错题集.pdf --ocr --dpi=400
```

---

## 示例9：仅使用OCR提取文本

### 场景描述
用户只想使用OCR从PDF中提取文本，不进行后续分析。

### 执行代码

```python
from law_exam_analyzer import ocr_pdf_to_text

# 提取所有页面的文本
ocr_results = ocr_pdf_to_text('./扫描版错题集.pdf', dpi=300)

print(f"共识别 {len(ocr_results)} 页")
for result in ocr_results:
    print(f"\n--- 第 {result['page']} 页 ---")
    print(result['text'])
```

---

## 示例10：单个图像OCR识别

### 场景描述
用户有一张包含法考题目的截图，需要识别文字。

### 执行代码

```python
from law_exam_analyzer import ocr_single_image

# 识别图像中的文字
text = ocr_single_image('./题目截图.png')
print("识别的文字：")
print(text)
```

---

## 常见问题排查

### Q1: PDF解析结果为空
**原因**: PDF可能是扫描图像而非文本。

**解决**:
1. 技能会自动检测并切换到OCR模式
2. 或手动指定 `--ocr` 参数强制使用OCR
3. 确保已安装Tesseract OCR及中文语言包

### Q2: OCR识别率低
**原因**: 图像质量差或DPI过低。

**解决**:
1. 提高DPI参数（推荐300-400）
2. 确保Tesseract中文语言包已安装
3. 预处理图像可以提高识别率

### Q3: 法律科目识别不准确
**原因**: 题目内容不包含预定义的关键词。

**解决**: 在 `LEGAL_SUBJECTS` 字典中添加更多关键词。

### Q4: 中文字体显示异常
**原因**: 系统缺少中文字体。

**解决**: 在生成图表前设置字体：
```python
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
```

### Q5: Word文档格式不正确
**原因**: 字体安装问题。

**解决**: 确保系统安装了宋体、黑体等中文字体。

### Q6: OCR库未安装错误
**原因**: pytesseract、Pillow或pdf2image未安装。

**解决**: 运行以下命令安装依赖：
```bash
pip install pytesseract Pillow pdf2image

# Ubuntu/Debian 额外安装
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS 额外安装
brew install tesseract tesseract-lang
```
