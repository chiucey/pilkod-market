---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a8beba8dff4a4416b67ef9111219d09c
    PropagateID: a8beba8dff4a4416b67ef9111219d09c
    ReservedCode1: 3045022100cbb6be1ecb07ce3b9f7438b162772d4a1e6aecdb0c6f14f19b9cc658be6ce40802200ce64b4cf1bd246e5f60ea81351fe55b386dcff04fe395dba920a107e04d9dd3
    ReservedCode2: 3045022100a205df4027253e88bd10ec28a5bdb3230d3e7a3d84d53b795405a63b6a4c15b802204c695ec452ff8fcd110c918df84d3fee63a6db1f6dce8b0199b0887cdbe41f33
---

# SKILL.md — MOBI GARDEN 双语进度汇报网页生成器

## Skill Name
`mobi-meeting-deck`

## Version
1.0.0

## Description
从 MOBI GARDEN 北美品牌出海的多源数据（PDP商品文档、品牌语音框架、北美徒步路线研究）中，自动生成双语气进度汇报网页（HTML），支持分享至飞书/微信/CDN链接。

## When to Use
- 跨境独立站进度汇报会议前
- 需要生成 bilingual（中文 + 英文）网页汇报材料
- 品牌故事、产品技术、达人策略、路线匹配需整合展示

## Trigger Keywords
`生成会议网页`、`双语汇报`、`MOBI GARDEN 汇报`、`进度汇报网页`、`meeting deck`、`生成汇报链接`

---

## 工作流程

### Step 0 — 确认需求范围
与用户确认：
- 已有素材：PDP商品文档、品牌语音文件、北美徒步路线研究数据
- 报告结构：四大板块（独立站 / 品牌侧 / 社媒 / 其他）
- 是否需要框架版（先框架，后填细节）

### Step 1 — 读取数据源
按需读取以下文件（优先从 workspace 已有文件读取，勿重复搜索 web）：

```
数据源清单：
├── /workspace/user_input_files/MobiGarden_NA_PDP_Master.docx        # 商品PDP（用Python zipfile读取）
├── /workspace/skills/mobi-garden-brand/SKILL.md                      # 品牌定位框架
├── /workspace/skills/mobi-garden-brand-voice/SKILL.md                 # 品牌语音·语调四柱
├── /workspace/user_input_files/MobiGarden_Brand_Voice_ToV_v1.1.md     # TOV详细文档（含DO/DON'T词汇表）
├── /workspace/user_input_files/pasted-text-*.txt                      # 用户实时粘贴的补充内容
├── /workspace/hiking-research/Product_Trail_Matrix_v1.0.md           # 产品×路线三维矩阵
├── /workspace/hiking-research/data_summary.md                          # 徒步路线象限数据
└── /workspace/hiking-research/quadrant_map.png                        # 北美徒步路线象限图（CDN已上传）
```

**读取 PDP 文件方法**（Python zipfile，不依赖 pandoc）：
```python
python3 << 'EOF'
import zipfile, re
docx_path = '/workspace/user_input_files/MobiGarden_NA_PDP_Master.docx'
with zipfile.ZipFile(docx_path) as z:
    with z.open('word/document.xml') as f:
        xml = f.read().decode('utf-8')
    text = re.sub(r'<[^>]+>', '', xml)
    text = re.sub(r'\s+', ' ', text).strip()
with open('/workspace/pdp_extracted.txt', 'w') as f:
    f.write(text)
print('Extracted length:', len(text))
EOF
```

### Step 2 — 确认内容结构
四大固定板块（不问也可按默认结构处理）：

```html
<!-- SEC1 --> 独立站进度（上线时间 / 下阶段优化 / Phase 2 / 东南亚）
<!-- SEC2 --> 品牌侧确认（故事·冷山传奇·使命 / TOV语调四柱 / DO&DON'T / TA受众 / 定位定价 / 产品设计起源故事）
<!-- SEC3 --> 社媒板块（达人合作 / 账号布局 / GEO策略 / 北美徒步路线+产品矩阵图）
<!-- SEC4 --> 其他进度（Wayfair峰会 / 待确认事项）
```

### Step 3 — 逐段生成 HTML
采用**分块写入 + Python 合并**策略（避免单次大文本写入失败）：

```python
# 分块写入
sections = ['header', 'sec1', 'sec2', 'sec3', 'sec4']
for i, section in enumerate(sections):
    with open(f'/workspace/meeting-deck/part{i}.html', 'w', encoding='utf-8') as f:
        f.write(render_section(section))
    # 每次写入后立即验证大小
    print(f'Part {i}: {os.path.getsize(f"/workspace/meeting-deck/part{i}.html")} bytes')
```

### Step 4 — 关键HTML片段参考

**中英双语标题结构（固定格式）：**
```html
<div class="sh">
  <div class="zh">[中文大标题]</div>
  <div class="en">[English subtitle]</div>
</div>
```

**状态指示灯（固定格式）：**
```html
<div class="sr">
  <div class="dot d-g"></div>  <!-- d-g=green完成 / d-y=yellow进行中 / d-r=red待处理 -->
  <div>内容描述</div>
</div>
```

**双语引用块（品牌故事/产品起源故事）：**
```html
<div class="qt">
  <div class="qtl">小标签</div>
  <p style="font-size:12px;margin-bottom:6px;color:#333"><em>EN:</em><br>英文正文</p>
  <p style="font-size:12px;color:#555"><em>中文：</em><br>中文正文</p>
</div>
```

**价格对比表格：**
```html
<table class="tbl">
  <tr><th>产品</th><th>MOBI GARDEN</th><th>竞品</th><th>竞品价格</th></tr>
  <tr><td>GENNYE PRO R6</td><td><strong>$139.99</strong></td><td>NEMO Tensor All-Season</td><td>$239.95</td></tr>
</table>
```

**产品矩阵Toggle开关：**
```html
<div class="toggle-row">
  <div class="toggle-label">显示产品匹配层 / Show Product Fit Overlay</div>
  <label class="switch"><input type="checkbox" id="matrixToggle" checked onclick="toggleMatrix()"><span class="slider"></span></label>
</div>
<div class="matrix-wrap" id="matrixWrap">
  <img src="[产品匹配矩阵图CDN链接]" alt="...">
</div>
<script>
function toggleMatrix(){
  var img = document.querySelector('#matrixWrap img');
  var isOn = document.getElementById('matrixToggle').checked;
  img.src = isOn ? '[产品叠加图URL]' : '[原始象限图URL]';
}
</script>
```

**Wayfair 专题块：**
```html
<div class="wf-block">
  <div class="wf-grid">
    <div class="wf-stat"><div class="num">$12B+</div><div class="desc">2024年营收</div></div>
    <div class="wf-stat"><div class="num">21.3M+</div><div class="desc">活跃用户</div></div>
    ...
  </div>
</div>
```

### Step 5 — 上传与分享
```python
# 使用 upload_to_cdn() 工具获取公开URL
# CDN URL 可直接粘贴至飞书/微信
```

---

## 样式规范（Design Tokens）

| 元素 | 规范 |
|------|------|
| 主色 | `#dc2626`（红色，左侧边线） |
| 背景 | `#f5f5f5`，卡片 `#fff` |
| 字体 | `-apple-system, BlinkMacSystemFont, 'Segoe UI'` |
| 圆角 | `border-radius: 10px` |
| 间距 | `padding: 16px 18px`，段落间距 `28px` |
| 状态色 | 完成=`#16a34a`，进行中=`#d97706`，待处理=`#dc2626` |
| 标签色 | TA1=`#f0fdf4`，TA2=`#fffbeb`，TA3=`#fef2f2` |

---

## 已验证的文件路径

| 文件 | 路径 |
|------|------|
| 象限图（原始） | `/workspace/hiking-research/quadrant_map.png` |
| 产品×路线矩阵图 | `/workspace/hiking-research/product_trail_matrix_map.png` |
| 北美路线数据 | `/workspace/hiking-research/data_summary.md` |
| 三维匹配矩阵 | `/workspace/hiking-research/Product_Trail_Matrix_v1.0.md` |
| KONGAR报告 | `/workspace/hiking-research/KONGAR_NorthAmerica_Landing_Report.md` |
| 落地页框架 | `/workspace/hiking-research/Landing_Page_Frameworks.md` |

---

## 注意事项
- **不从 web 搜索**数据源，优先复用 workspace 已有文件
- **不修改 openclaw.json**
- **单次写入上限**：建议分块写入，单块不超过 500 行
- **图片 CDN**：先用 `upload_to_cdn()` 获取 URL 再写入 HTML img src
- **中文字符**：在 HTML 内使用 HTML Entities 或纯英文，避免乱码
- **Toggle 开关**：必须在 JS 函数中使用原始 CDN URL，不依赖 workspace 路径
