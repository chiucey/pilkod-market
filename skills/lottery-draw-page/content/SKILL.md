---
name: lottery-draw-page
description: 年会抽奖页面技能。当用户要求创建抽奖页面、制作年会/组会/展会等场景的抽奖系统、上传Excel进行抽奖、下载抽奖模板时使用。支持一等奖、二等奖、三等奖、纪念奖四个奖项级别。
---

# 抽奖页面技能

## 功能概述

创建精美的抽奖页面，支持年会、组会、展会等场景。用户可下载Excel模板填写参与人员和奖品信息，上传后即可开始抽奖。

## 技能使用流程

### 1. 创建抽奖页面

使用 `lottery_html_generator` 子代理生成完整的抽奖HTML页面：

**输入要求**：
- 技能名称：`lottery-draw-page`
- 语言：简体中文
- 功能需求：
  - 初始页面：显示下载Excel模板按钮
  - Excel模板结构：Sheet1=参与人员（含姓名列），Sheet2=一等奖奖品和数量，Sheet3=二等奖奖品和数量，Sheet4=三等奖奖品和数量，Sheet5=纪念奖奖品和数量
  - 文件上传功能：支持上传Excel文件
  - 抽奖功能：点击开始抽奖按钮进行随机抽取
  - 奖项设置：支持一等奖、二等奖、三等奖、纪念奖四个级别
  - 抽奖动画：滚动名字效果，营造紧张氛围
  - 结果展示：显示中奖名单
  - 领奖功能：显示领奖码或凭证

**输出要求**：
- 完整可运行的HTML文件
- 包含所有CSS样式和JavaScript逻辑
- 无需外部依赖（纯前端实现）
- 使用openpyxl库在Python端处理Excel文件上传和解析

### 2. Python后端处理（可选）

如需服务器端Excel处理，创建 `app.py` 文件：

```python
# 使用FastAPI处理Excel上传和解析
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import openpyxl
from io import BytesIO

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    # 返回抽奖HTML页面

@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...)):
    # 解析Excel文件
    # 返回参与人员和奖品数据
```

### 3. Excel模板生成

使用 `template_generator.py` 生成标准模板：

```python
import openpyxl
from openpyxl import Workbook

def create_template():
    wb = Workbook()

    # Sheet1: 参与人员
    ws1 = wb.active
    ws1.title = "参与人员"
    ws1.append(["姓名", "部门", "工号"])
    ws1.append(["示例人员", "技术部", "EMP001"])

    # Sheet2: 一等奖
    ws2 = wb.create_sheet("一等奖")
    ws2.append(["奖品名称", "数量"])
    ws2.append(["iPhone 15", "3"])

    # Sheet3: 二等奖
    ws3 = wb.create_sheet("二等奖")
    ws3.append(["奖品名称", "数量"])
    ws3.append(["iPad Air", "5"])

    # Sheet4: 三等奖
    ws4 = wb.create_sheet("三等奖")
    ws4.append(["奖品名称", "数量"])
    ws4.append(["蓝牙耳机", "10"])

    # Sheet5: 纪念奖
    ws5 = wb.create_sheet("纪念奖")
    ws5.append(["奖品名称", "数量"])
    ws5.append(["马克杯", "50"])

    return wb
```

## 验收标准

1. ✅ 初始页面显示下载Excel模板按钮
2. ✅ 用户可上传Excel文件
3. ✅ 支持四个奖项级别抽奖
4. ✅ 抽奖动画流畅，有滚动效果
5. ✅ 中奖名单正确记录
6. ✅ 不重复抽奖（已中奖者不再参与）
7. ✅ 响应式设计，适配多种屏幕
8. ✅ 无外部依赖，可离线使用

## 技术要点

### 前端实现
- 使用CSS动画实现名字滚动效果
- 使用localStorage保存抽奖状态
- 纯JavaScript实现，无需框架

### 数据存储
- Excel解析后的数据存储在浏览器localStorage
- 抽奖结果持久化保存
- 防止页面刷新丢失数据

### 抽奖算法
- Fisher-Yates洗牌算法确保公平性
- 随机数生成使用crypto.getRandomValues
- 已中奖者从奖池移除

## 文件结构

```
lottery-draw-page/
├── SKILL.md
├── _meta.json
├── lottery.html          # 完整抽奖页面
├── template_generator.py # Excel模板生成器
└── app.py               # 可选：FastAPI后端
```
