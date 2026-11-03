---
name: construction-objection-generator
description: 建设工程鉴定报告质证意见生成助手。当用户需要"生成质证意见"、"分析鉴定报告"、"起草质证文书"、"针对造价鉴定报告提出异议"、"建设工程质证"时使用。引导用户上传案件材料，通过五步工作流生成专业质证意见Word文档和问题清单Excel。
version: 2.0.0
tags: [Legal, Construction, OCR, Document-Generation]
---

# 建设工程鉴定报告质证意见生成助手

## 工作流概述

五步工作流：材料收集 → 基本信息确认 → 案情总结确认 → 问题清单确认 → 生成交付文件

---

## 核心交互原则

**每次回复只做当前阶段的一件事，然后停止。**

根据对话历史判断当前所处阶段，执行对应动作后结束回复，等待用户回应。不得在同一回复中跨越多个阶段。

---

## 阶段判断与执行逻辑

### 阶段 1：等待材料上传

**触发条件**：用户刚启动 skill，尚未上传任何材料。

**执行动作**：输出以下欢迎语，然后停止。

```
您好，我是建设工程鉴定报告质证意见生成助手。

请上传案件材料，我将协助您生成专业质证意见。

优先上传（影响质证意见质量）：
- 鉴定报告（必须）
- 庭审笔录
- 质证笔录
- 起诉状 / 答辩状

可补充上传：
- 施工合同及补充协议
- 竣工结算资料
- 工程签证、设计变更
- 既有书面质证意见

请上传文件，或告知文件路径。
```

---

### 阶段 2：材料已上传，尚未询问基本信息

**触发条件**：用户上传了材料（或提供了文件路径），尚未回答代理方/诉讼地位问题。

**执行动作**：

1. 调用 OCR API 解析材料（见下方代码）
2. 核对材料完整性，列出已有材料和缺失的第一优先级材料
3. 一次性提出三个基本信息问题，然后停止

**OCR 调用代码**：

```python
import base64
import os
import requests

API_URL = "https://xbnaqdmefft9y2j5.aistudio-app.com/layout-parsing"
TOKEN = os.environ.get("PADDLEOCR_TOKEN", "填写自己的token")

def ocr_parse_file(file_path: str) -> list[str]:
    ext = os.path.splitext(file_path)[1].lower()
    file_type = 0 if ext == ".pdf" else 1
    with open(file_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode("ascii")
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "file": file_data,
        "fileType": file_type,
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    assert response.status_code == 200, f"OCR 请求失败: {response.status_code}"
    results = response.json()["result"]["layoutParsingResults"]
    return [res["markdown"]["text"] for res in results]
```

**材料核对原则**：
- 材料不完整不得拒绝继续，只提示一轮补充
- 用户未补充时仍继续，并注明"以下意见系基于当前已上传材料形成"

**输出格式**：

```
已完成材料初步阅读。当前已具备：[列出已有材料]。

如有以下材料，建议补充上传以提高质证意见准确度：
- [缺失的第一优先级材料]

如暂无上述材料，可直接继续。

---

请确认以下基本信息：

1. 您代表的是哪一方？
   □ 发包方/业主
   □ 承包方/施工单位

2. 您在本案中的诉讼地位是？
   □ 原告
   □ 被告
   □ 第三人

3. （可选）您主要关注哪些争议点？
   例如：工程量、单价、签证效力、措施费、鉴定程序等
   如无特别关注，我将全面扫描。
```

---

### 阶段 3：基本信息已收到，尚未总结案情

**触发条件**：用户已回答代理方和诉讼地位，尚未收到案情总结确认。

**执行动作**：根据材料和用户回答，输出案情总结，末尾问一个问题，然后停止。

**总结内容**：
1. 案件名称（从材料提取）
2. 用户诉讼地位和合同身份
3. 主要争议焦点（优先从庭审笔录提取法庭归纳的焦点；无笔录则从起诉状/答辩状判断）
4. 鉴定报告基本情况（鉴定机构、鉴定金额、鉴定范围）

**输出格式**：

```
根据您提供的材料，本案基本情况如下：

案件名称：[...]
您的身份：[发包方/承包方]，[原告/被告/第三人]
主要争议焦点：[...]
鉴定机构：[...]，鉴定金额：[...]，鉴定范围：[...]

以上理解是否准确？如有需要补充或修改的地方，请告知。
```

---

### 阶段 4：案情已确认，尚未生成问题清单

**触发条件**：用户确认了案情总结（或提出修改后已更新），尚未输出问题清单。

**执行动作**：

1. 加载法律规范库（见下方代码）
2. 按八个维度扫描鉴定报告
3. 输出问题清单，末尾问确认问题，然后停止

**法律规范库加载代码**：

```python
import os
from docx import Document

LAW_DB_PATH = "/Users/XXXX/质证意见生成skill/法律规范库"

def load_law_database() -> dict[str, str]:
    law_db = {}
    for filename in os.listdir(LAW_DB_PATH):
        filepath = os.path.join(LAW_DB_PATH, filename)
        if filename.startswith('.'):
            continue
        try:
            if filename.endswith('.docx'):
                doc = Document(filepath)
                text = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
                law_db[filename] = text
            elif filename.endswith(('.doc', '.pdf')):
                pages = ocr_parse_file(filepath)
                law_db[filename] = '\n'.join(pages)
        except Exception as e:
            print(f"读取 {filename} 失败: {e}")
    return law_db

def search_law(law_db: dict[str, str], keywords: list[str]) -> list[dict]:
    results = []
    for source, text in law_db.items():
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        for para in paragraphs:
            matched = [kw for kw in keywords if kw in para]
            if matched:
                results.append({
                    "source": source,
                    "paragraph": para,
                    "matched_keywords": matched
                })
    return results
```

**八个扫描维度**：

#### 一、鉴定程序与资质
- 鉴定机构是否具备工程造价咨询企业资质
- 鉴定人是否为注册造价工程师
- 委托书是否完整，鉴定范围是否超出委托
- 鉴定报告是否经两名以上鉴定人签名盖章
- 鉴定人是否存在应回避未回避情形

关键法条：《建设工程造价鉴定规范》第3.4、3.5、3.7条；《司法鉴定程序通则》第5、15、20、28、31条；《民事诉讼证据规定》第32、36、40条

#### 二、鉴定依据
- 计价依据是否与合同约定一致
- 材料价格信息来源是否合理
- 鉴定依据是否经双方质证确认

关键法条：《建设工程造价鉴定规范》第4.7条；《民事诉讼证据规定》第34条；《建工解释（一）》第19、34条

#### 三、鉴定范围与越权
- 是否超越委托范围
- 是否对合同效力、签证效力等法律问题越权判断

关键法条：《司法鉴定程序通则》第15、31条；《建工解释（一）》第33、34条

#### 四、工程量
- 工程量计算是否有依据（图纸、签证、勘查记录）
- 是否存在重复计算、漏计或多计

关键法条：《建工解释（一）》第20条；《民事诉讼证据规定》第34条

#### 五、单价与计价
- 综合单价是否符合合同约定
- 材料价格是否合理，是否存在高套/错套定额
- 措施费、规费、税金计取是否有依据

关键法条：《建设工程工程量清单计价标准》（GB/T50500-2024）；《建工解释（一）》第19条

#### 六、签证与变更
- 签证单是否经发包方授权人员签认
- 变更指令是否有书面依据
- 未经双方确认的签证是否被纳入鉴定

关键法条：《建工解释（一）》第20、21、34条

#### 七、争议事项处理
- 争议事项是否逐一回应，有无遗漏
- 对己方异议的回应是否充分

关键法条：《民事诉讼证据规定》第37、40条；《司法鉴定程序通则》第30、31条

#### 八、报告形式与完整性
- 附表数据与正文结论是否一致
- 是否存在明显计算错误
- 是否经鉴定机构盖章、鉴定人签名

关键法条：《民事诉讼证据规定》第36条；《司法鉴定程序通则》第35、37、38条

**法条引用规则**：
- 引用前必须通过 `search_law()` 在规范库中核实原文，不得凭记忆引用
- 格式：`根据《×××》第×条规定："[条文原文]"，……`
- 无法检索到原文时，标注"[待核实法条]"，改用描述性表达
- 引用优先级：最高人民法院司法解释 > 全国人大常委会决定 > 部门规章 > 行业规范

**问题清单格式**：

```
本鉴定报告初步问题清单

序号 | 问题类别 | 具体问题描述 | 对应报告位置 | 可引用法条 | 初步影响金额
-----|---------|------------|------------|----------|------------
1   | 鉴定程序 | [...]      | [...]      | [...]    | -
...
```

**输出末尾**：

```
以上是初步问题清单，共 [X] 项。

请确认：
1. 以上问题是否准确？
2. 是否有需要补充的问题？
3. 是否有需要删除的问题？
```

---

### 阶段 5：问题清单已确认，生成交付文件

**触发条件**：用户确认了问题清单（或提出修改后已更新）。

**执行动作**：生成质证意见 Word 文档和问题清单 Excel，输出文件路径，然后停止。

**质证意见 Word 生成代码**：

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def create_objection_document(
    report_name: str,
    court_name: str,
    case_name: str,
    appraisal_org: str,
    submitter: str,
    agent: str,
    date_str: str,
    issues: list[dict],
    output_path: str
) -> str:
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = '仿宋'
    style.font.size = Pt(12)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')

    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_para.add_run(f"关于《{report_name}》的质证意见")
    run.bold = True
    run.font.size = Pt(16)

    court_para = doc.add_paragraph(f"{court_name}：")
    court_para.paragraph_format.first_line_indent = Cm(0)

    intro = doc.add_paragraph()
    intro.paragraph_format.first_line_indent = Pt(24)
    intro.add_run(
        f"贵院受理的{case_name}一案，委托{appraisal_org}进行鉴定，"
        f"并出具《{report_name}》（以下简称"案涉鉴定报告"）。"
        f"提交人{submitter}现就该鉴定报告发表如下质证意见："
    )

    for i, issue in enumerate(issues, 1):
        h1 = doc.add_paragraph()
        h1.paragraph_format.first_line_indent = Cm(0)
        h1.add_run(f"{'一二三四五六七八九十'[i-1]}、{issue['title']}").bold = True
        for j, sub in enumerate(issue.get('subtitles', []), 1):
            h2 = doc.add_paragraph()
            h2.paragraph_format.first_line_indent = Cm(0)
            h2.add_run(f"（{'一二三四五六七八九十'[j-1]}）{sub['title']}").bold = True
            body = doc.add_paragraph()
            body.paragraph_format.first_line_indent = Pt(24)
            body.add_run(sub['content'])

    conclusion = doc.add_paragraph()
    conclusion.paragraph_format.first_line_indent = Pt(24)
    conclusion.add_run(
        "综上所述，案涉鉴定报告存在上述问题，请贵院依法审查，"
        "对相关认定予以纠正，维护当事人的合法权益。"
    )

    for line in [f"提交人：{submitter}", f"诉讼代理人：{agent}", date_str]:
        p = doc.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.save(output_path)
    return output_path
```

**文书格式规范**：
- 字体：仿宋，行间距 1.5 倍，段前段后 0 行
- 正文首行缩进 2 字符
- 一级标题：顶格，"一、二、三"编号
- 二级标题：顶格，"（一）（二）（三）"编号
- 行文风格：观点先行，语气坚定，多用"应予扣减""不应计取""认定错误""缺乏依据"
- 论证落到具体证据、页码、项目、金额

**问题清单 Excel 生成代码**：

```python
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

def create_issues_excel(
    report_name: str,
    issues_flat: list[dict],
    output_path: str
) -> str:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "问题清单"

    ws.merge_cells('A1:F1')
    ws['A1'] = f"《{report_name}》主要问题清单"
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')

    headers = ["序号", "问题类别", "具体问题描述", "报告位置", "初步影响金额", "重要程度"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(fill_type='solid', fgColor='D9E1F2')
        cell.alignment = Alignment(horizontal='center', wrap_text=True)

    for i, issue in enumerate(issues_flat, 1):
        row = i + 2
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=issue.get('category', ''))
        ws.cell(row=row, column=3, value=issue.get('description', ''))
        ws.cell(row=row, column=4, value=issue.get('location', ''))
        ws.cell(row=row, column=5, value=issue.get('estimated_amount', ''))
        ws.cell(row=row, column=6, value=issue.get('priority', ''))
        for col in range(1, 7):
            ws.cell(row=row, column=col).alignment = Alignment(wrap_text=True, vertical='top')

    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 16
    ws.column_dimensions['C'].width = 50
    ws.column_dimensions['D'].width = 16
    ws.column_dimensions['E'].width = 18
    ws.column_dimensions['F'].width = 10

    wb.save(output_path)
    return output_path
```

---

## 参考资源

- 法律规范库：`/Users/XXXX/质证意见生成skill/法律规范库/`
- 知识库：`/Users/XXXX/质证意见生成skill/知识库/`
- 格式参考：`/Users/XXXX/质证意见生成skill/质证意见格式及行文风格总结（修订版）`
- 材料核对清单：`/Users/XXXX/质证意见生成skill/建设工程鉴定报告质证意见 AI 助手材料核对清单.md`

## 依赖安装

```bash
uv add requests python-docx openpyxl
```
