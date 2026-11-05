#!/usr/bin/env python3
"""
抽奖系统后端服务
使用FastAPI提供抽奖页面的Excel处理功能
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import openpyxl
from io import BytesIO
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os

app = FastAPI(title="抽奖系统", version="1.0.0")

# 允许CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Participant(BaseModel):
    name: str
    department: Optional[str] = ""
    employee_id: Optional[str] = ""


class Prize(BaseModel):
    name: str
    count: int


class LotteryData(BaseModel):
    participants: List[Participant]
    first_prize: Prize
    second_prize: Prize
    third_prize: Prize
    souvenir_prize: Prize


# HTML页面内容
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>幸运大抽奖</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
        }
        .container {
            text-align: center;
            padding: 40px;
        }
        h1 { font-size: 3rem; color: #ffd700; margin-bottom: 30px; }
        .btn {
            display: inline-block;
            padding: 15px 40px;
            margin: 10px;
            border-radius: 50px;
            text-decoration: none;
            font-size: 1.1rem;
            font-weight: bold;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, #4ade80, #22c55e);
            color: white;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .upload-section {
            margin-top: 30px;
        }
        .file-input { display: none; }
        .file-label {
            display: inline-block;
            padding: 15px 40px;
            background: linear-gradient(135deg, #f093fb, #f5576c);
            border-radius: 50px;
            cursor: pointer;
        }
        #result { margin-top: 20px; }
        .data-preview {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 幸运大抽奖 🎉</h1>

        <a href="/template" class="btn btn-primary">📥 下载Excel模板</a>

        <div class="upload-section">
            <label class="file-label">
                📤 上传Excel文件
                <input type="file" class="file-input" accept=".xlsx,.xls" id="fileInput">
            </label>
        </div>

        <div id="result"></div>
    </div>

    <script>
        document.getElementById('fileInput').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/upload/', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    showPreview(data);
                } else {
                    alert('文件上传失败');
                }
            } catch (error) {
                alert('上传出错: ' + error);
            }
        });

        function showPreview(data) {
            const result = document.getElementById('result');
            result.innerHTML = `
                <div class="data-preview">
                    <h3>📋 数据预览</h3>
                    <p>参与人员: <strong>${data.participants.length}</strong> 人</p>
                    <p>一等奖: <strong>${data.first_prize.name}</strong> x ${data.first_prize.count}</p>
                    <p>二等奖: <strong>${data.second_prize.name}</strong> x ${data.second_prize.count}</p>
                    <p>三等奖: <strong>${data.third_prize.name}</strong> x ${data.third_prize.count}</p>
                    <p>纪念奖: <strong>${data.souvenir_prize.name}</strong> x ${data.souvenir_prize.count}</p>
                    <p style="margin-top:15px;color:#4ade80;">✅ 数据加载成功！</p>
                </div>
            `;
        }
    </script>
</body>
</html>
'''


@app.get("/", response_class=HTMLResponse)
async def index():
    """返回抽奖页面"""
    return HTML_PAGE


@app.get("/template")
async def download_template():
    """下载Excel模板"""
    from template_generator import create_lottery_template

    wb = create_lottery_template()
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return FileResponse(
        buffer.getvalue(),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename='抽奖模板.xlsx'
    )


@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...)):
    """上传并解析Excel文件"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="请上传Excel文件")

    try:
        contents = await file.read()
        wb = openpyxl.load_workbook(BytesIO(contents))

        # 解析参与人员 (Sheet1)
        participants = []
        if '参与人员' in wb.sheetnames:
            ws = wb['参与人员']
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:  # 姓名不能为空
                    participants.append({
                        'name': str(row[0]),
                        'department': str(row[1]) if len(row) > 1 and row[1] else '',
                        'employee_id': str(row[2]) if len(row) > 2 and row[2] else ''
                    })

        # 解析一等奖 (Sheet2)
        first_prize = {'name': '', 'count': 0}
        if '一等奖' in wb.sheetnames:
            ws = wb['一等奖']
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:
                    first_prize = {
                        'name': str(row[0]),
                        'count': int(row[1]) if len(row) > 1 and row[1] else 0
                    }
                    break

        # 解析二等奖 (Sheet3)
        second_prize = {'name': '', 'count': 0}
        if '二等奖' in wb.sheetnames:
            ws = wb['二等奖']
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:
                    second_prize = {
                        'name': str(row[0]),
                        'count': int(row[1]) if len(row) > 1 and row[1] else 0
                    }
                    break

        # 解析三等奖 (Sheet4)
        third_prize = {'name': '', 'count': 0}
        if '三等奖' in wb.sheetnames:
            ws = wb['三等奖']
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:
                    third_prize = {
                        'name': str(row[0]),
                        'count': int(row[1]) if len(row) > 1 and row[1] else 0
                    }
                    break

        # 解析纪念奖 (Sheet5)
        souvenir_prize = {'name': '', 'count': 0}
        if '纪念奖' in wb.sheetnames:
            ws = wb['纪念奖']
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:
                    souvenir_prize = {
                        'name': str(row[0]),
                        'count': int(row[1]) if len(row) > 1 and row[1] else 0
                    }
                    break

        return {
            'participants': participants,
            'first_prize': first_prize,
            'second_prize': second_prize,
            'third_prize': third_prize,
            'souvenir_prize': souvenir_prize,
            'total': len(participants)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "lottery-system"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
