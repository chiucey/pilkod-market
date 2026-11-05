#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说人物关系图谱生成器 - 书籍解析模块

功能：
- 解析 epub、pdf、txt 格式的小说文件
- 提取人物信息和关系
- 生成可视化图谱数据
"""

import os
import re
import json
from typing import List, Dict, Tuple, Optional

# EPUB 解析
try:
    from ebooklib import epub
    from bs4 import BeautifulSoup
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False
    print("警告: ebooklib 未安装，EPUB 解析功能不可用")

# PDF 解析 (通过外部工具)
# PDF_CONTENT = ""  # 由 MCP 工具 extract_pdfs_full_content 提供


class Character:
    """人物数据类"""
    def __init__(self, id: str, name: str, emoji: str = "👤", 
                 is_protagonist: bool = False, color: str = "#27ae60",
                 intro: str = "", nationality: str = ""):
        self.id = id
        self.name = name
        self.emoji = emoji
        self.is_protagonist = is_protagonist
        self.color = color
        self.intro = intro
        self.nationality = nationality
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "emoji": self.emoji,
            "isProtagonist": self.is_protagonist,
            "color": self.color,
            "intro": self.intro,
            "nationality": self.nationality,
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy
        }


class Relationship:
    """关系数据类"""
    def __init__(self, from_id: str, to_id: str, 
                 rel_type: str = "work", label: str = "",
                 direction: str = "single", reverse_label: str = ""):
        self.from_id = from_id
        self.to_id = to_id
        self.type = rel_type
        self.label = label
        self.direction = direction
        self.reverse_label = reverse_label
    
    def to_dict(self) -> dict:
        result = {
            "from": self.from_id,
            "to": self.to_id,
            "type": self.type,
            "label": self.label,
            "direction": self.direction
        }
        if self.reverse_label:
            result["reverseLabel"] = self.reverse_label
        return result


def parse_epub(file_path: str) -> str:
    """解析 EPUB 文件，返回纯文本内容"""
    if not EPUB_AVAILABLE:
        return ""
    
    book = epub.read_epub(file_path)
    text_content = []
    
    for item in book.get_items():
        if item.get_type() == 9:  # EPUB_HTML
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator='\n', strip=True)
            if len(text) > 100:
                text_content.append(text)
    
    return '\n'.join(text_content)


def parse_txt(file_path: str) -> str:
    """解析 TXT 文件"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    return ""


def extract_chapters(text: str) -> List[Dict[str, str]]:
    """提取章节信息"""
    chapters = []
    
    # 常见的章节标题模式
    patterns = [
        r'^第[一二三四五六七八九十百千零\d]+章[：:\s]*(.+)$',
        r'^Chapter\s*\d+[：:\s]*(.+)$',
        r'^\d+\.\s+(.+)$',
        r'^(第[一二三四五六七八九十百千零\d]+节[：:\s]*(.+))?$',
    ]
    
    lines = text.split('\n')
    current_chapter = {"title": "序言", "content": ""}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        matched = False
        for pattern in patterns:
            if re.match(pattern, line, re.MULTILINE):
                if current_chapter["content"]:
                    chapters.append(current_chapter)
                current_chapter = {"title": line, "content": ""}
                matched = True
                break
        
        if not matched:
            current_chapter["content"] += line + "\n"
    
    if current_chapter["content"]:
        chapters.append(current_chapter)
    
    return chapters


def analyze_characters(text: str) -> Tuple[List[Character], List[Relationship]]:
    """
    分析文本，提取人物信息和关系
    
    注意：这是一个基础实现。实际使用时，
    AI 会根据具体书籍内容进行更智能的分析。
    
    返回: (人物列表, 关系列表)
    """
    # 这里由 AI 根据具体书籍内容填充
    # 以下是示例数据结构
    characters = []
    relationships = []
    
    return characters, relationships


def generate_html(book_title: str, characters: List[Character], 
                 relationships: List[Relationship], output_path: str):
    """生成 HTML 图谱文件"""
    
    characters_json = json.dumps([c.to_dict() for c in characters], ensure_ascii=False)
    relationships_json = json.dumps([r.to_dict() for r in relationships], ensure_ascii=False)
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title} - 人物关系图谱</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', sans-serif; min-height: 100vh; overflow: hidden; }}
        #canvas {{ position: absolute; top: 0; left: 0; cursor: grab; }}
        #canvas.dragging {{ cursor: grabbing; }}
        .panel {{
position: fixed; background: rgba(255,255,255,0.97);
            border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.25); z-index: 1000;
        }}
        .panel h3 {{ margin-bottom: 12px; color: #1a1a2e; font-size: 14px; border-bottom: 2px solid #4a90d9; padding-bottom: 8px; }}
        .panel button {{
            display: inline-block; padding: 8px 14px; margin: 4px 2px;
            background: #4a90d9; color: white; border: none;
            border-radius: 6px; cursor: pointer; font-size: 12px;
        }}
        .panel button:hover {{ background: #357abd; }}
        .panel button.active {{ background: #2d6aa6; }}
        #toolbar {{ top: 20px; left: 20px; width: 260px; }}
        .char-detail {{
            position: fixed; background: rgba(255,255,255,0.98);
            border-radius: 12px; padding: 15px 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3); z-index: 2000;
            max-width: 300px; display: none; animation: fadeIn 0.2s;
        }}
        .char-detail.show {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        .theme-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px; }}
        .theme-btn {{ padding: 8px 4px; border: 2px solid transparent; border-radius: 8px; cursor: pointer; text-align: center; font-size: 10px; }}
        .theme-btn:hover {{ transform: scale(1.05); }}
        .theme-btn.active {{ border-color: #4a90d9; }}
        .theme-preview {{ width: 100%; height: 30px; border-radius: 4px; margin-bottom: 4px; }}
        .slider-row {{ display: flex; align-items: center; margin: 8px 0; font-size: 12px; }}
        .slider-row input {{ flex: 1; margin: 0 8px; }}
        .slider-row span {{ min-width: 40px; text-align: right; }}
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <div id="toolbar" class="panel">
        <h3>⚙️ 力导向图谱</h3>
        <div style="margin-bottom:12px;">
            <button id="btnSimStart">▶️ 开始模拟</button>
            <button id="btnSimStop">⏸️ 停止</button>
            <button id="btnSimReset">🔄 重置</button>
        </div>
        <label>🔬 物理参数</label>
        <div class="slider-row">斥力 <input type="range" id="repulsion" min="500" max="8000" value="3000"> <span id="repVal">3000</span></div>
        <div class="slider-row">刚度 <input type="range" id="stiffness" min="1" max="100" value="40"> <span id="stiffVal">40</span></div>
        <div class="slider-row">向心 <input type="range" id="centerForce" min="0" max="100" value="8"> <span id="centerVal">8</span></div>
        <div class="slider-row">阻尼 <input type="range" id="damping" min="50" max="990" value="850"> <span id="dampVal">0.85</span></div>
        <hr style="margin:10px 0;border:none;border-top:1px solid #eee;">
        <label>🎨 配色方案</label>
        <div class="theme-grid" id="themeGrid"></div>
    </div>
    <div id="charDetail" class="char-detail">
        <button onclick="document.getElementById('charDetail').classList.remove('show')" style="float:right;background:#ccc;padding:2px 8px;">×</button>
        <h3><span id="detailEmoji"></span> <span id="detailName"></span></h3>
        <div id="detailTag" style="font-size:10px;padding:2px 8px;border-radius:10px;background:#f1c40f;display:none;margin:5px 0;">🌟 主角</div>
        <div id="detailNationality" style="font-size:12px;color:#888;margin:5px 0;"></div>
        <p id="detailIntro" style="font-size:12px;color:#444;line-height:1.6;margin-top:10px;"></p>
    </div>
    <script>
    const themes = [
        {{ name: '深邃星空', bg: '#0d1117', grid: '#21262d', text: '#ffffff', textDim: '#8b949e', nodeBorder: '#f0f6fc', relationLine: '#58a6ff', preview: 'linear-gradient(135deg, #0d1117, #161b22)' }},
        {{ name: '经典蓝白', bg: '#1a365d', grid: '#2c5282', text: '#ffffff', textDim: '#bee3f8', nodeBorder: '#90cdf4', relationLine: '#63b3ed', preview: 'linear-gradient(135deg, #1a365d, #2c5282)' }},
        {{ name: '暗夜紫罗兰', bg: '#1a1a2e', grid: '#2d2d4e', text: '#e0e0ff', textDim: '#9090b0', nodeBorder: '#b0b0ff', relationLine: '#9b59b6', preview: 'linear-gradient(135deg, #1a1a2e, #2d2d4e)' }},
        {{ name: '森林秘境', bg: '#1a2f1a', grid: '#2d4d2d', text: '#e0ffe0', textDim: '#90c090', nodeBorder: '#80d080', relationLine: '#27ae60', preview: 'linear-gradient(135deg, #1a2f1a, #2d4d2d)' }},
        {{ name: '沙漠黄昏', bg: '#2d1f0f', grid: '#4d3f1f', text: '#ffe0c0', textDim: '#c0a080', nodeBorder: '#ffd090', relationLine: '#e67e22', preview: 'linear-gradient(135deg, #2d1f0f, #4d3f1f)' }},
        {{ name: '极简灰白', bg: '#f5f5f5', grid: '#e0e0e0', text: '#1a1a1a', textDim: '#666666', nodeBorder: '#333333', relationLine: '#555555', preview: 'linear-gradient(135deg, #f5f5f5, #e0e0e0)' }},
        {{ name: '复古羊皮', bg: '#f4ecd8', grid: '#e8dcc8', text: '#3d2914', textDim: '#8b7355', nodeBorder: '#5c4033', relationLine: '#8b4513', preview: 'linear-gradient(135deg, #f4ecd8, #e8dcc8)' }},
        {{ name: '薄荷清晨', bg: '#e8f5f0', grid: '#c8e6d8', text: '#1a3a2a', textDim: '#5a8a6a', nodeBorder: '#2d6b4a', relationLine: '#27ae60', preview: 'linear-gradient(135deg, #e8f5f0, #c8e6d8)' }},
        {{ name: '天空蓝调', bg: '#e8f4fc', grid: '#c0dcf0', text: '#1a2a3a', textDim: '#5a7a9a', nodeBorder: '#2a5a8a', relationLine: '#3498db', preview: 'linear-gradient(135deg, #e8f4fc, #c0dcf0)' }}
    ];
    
    let currentTheme = themes[0];
    let offsetX = 0, offsetY = 0, scale = 1;
    let isDragging = false, isDraggingNode = false, draggedNode = null;
    let lastX, lastY, simulationRunning = false;
    let physics = {{ repulsion: 3000, stiffness: 0.04, centerForce: 0.0008, damping: 0.85, idealLength: 220 }};
    
    const characters = {characters_json};
    const relationships = {relationships_json};
    
    const typeColors = {{ work: '#e74c3c', teammate: '#3498db', friend: '#9b59b6', control: '#e67e22', home: '#f1c40f', enemy: '#f39c12', protect: '#2ecc71' }};
    
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    function resize() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; if(characters.every(c=>c.x===0))initPositions(); }}
    function initPositions() {{ const cx=canvas.width/2-offsetX, cy=canvas.height/2-offsetY, r=280; characters.forEach((c,i)=>{{const a=(i/characters.length)*Math.PI*2;c.x=cx+Math.cos(a)*r*(0.7+Math.random()*0.6);c.y=cy+Math.sin(a)*r*(0.7+Math.random()*0.6);c.vx=c.vy=0;}}); }}
    
    function draw() {{
        ctx.clearRect(0,0,canvas.width,canvas.height);
        ctx.fillStyle=currentTheme.bg; ctx.fillRect(0,0,canvas.width,canvas.height);
        drawGrid(); drawRelationships(); drawCharacters();
    }}
    
    function drawGrid() {{
        const gs=50*scale, sx=offsetX%gs, sy=offsetY%gs;
        ctx.strokeStyle=currentTheme.grid; ctx.lineWidth=1; ctx.setLineDash([4,4]);
        for(let x=sx;x<canvas.width;x+=gs){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,canvas.height);ctx.stroke();}}
        for(let y=sy;y<canvas.height;y+=gs){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(canvas.width,y);ctx.stroke();}}
        ctx.setLineDash([]);
    }}
    
    function drawRelationships() {{
        relationships.forEach(rel=>{{
            const a=characters.find(c=>c.id===rel.from), b=characters.find(c=>c.id===rel.to);
            if(!a||!b)return;
            const x1=a.x*scale+offsetX, y1=a.y*scale+offsetY, x2=b.x*scale+offsetX, y2=b.y*scale+offsetY;
            const dx=x2-x1, dy=y2-y1, angle=Math.atan2(dy,dx);
            const r1=(a.isProtagonist?50:40)*scale, r2=(b.isProtagonist?50:40)*scale;
            const sx=x1+Math.cos(angle)*r1, sy=y1+Math.sin(angle)*r1;
            const ex=x2-Math.cos(angle)*(r2+15), ey=y2-Math.sin(angle)*(r2+15);
            ctx.strokeStyle=typeColors[rel.type]||currentTheme.relationLine; ctx.lineWidth=3*scale;
            if(rel.direction==='single'){{
                ctx.setLineDash([8*scale,4*scale]); ctx.beginPath(); ctx.moveTo(sx,sy); ctx.lineTo(ex,ey); ctx.stroke(); ctx.setLineDash([]);
                drawArrow(ex,ey,angle,typeColors[rel.type]);
                ctx.font=`bold ${{11*scale}}px Microsoft YaHei`; ctx.fillStyle=typeColors[rel.type]; ctx.textAlign='center'; ctx.textBaseline='middle';
                ctx.fillText(rel.label,(sx+ex)/2,(sy+ey)/2-8*scale);
            }} else {{
                const off=10*scale, px=-Math.sin(angle)*off, py=Math.cos(angle)*off;
                ctx.setLineDash([8*scale,4*scale]);
                ctx.beginPath(); ctx.moveTo(sx+px,sy+py); ctx.lineTo(ex+px,ey+py); ctx.stroke(); drawArrow(ex+px,ey+py,angle,typeColors[rel.type]);
                ctx.beginPath(); ctx.moveTo(ex-px,ey-py); ctx.lineTo(sx-px,sy-py); ctx.stroke(); drawArrow(sx-px,sy-py,angle+Math.PI,typeColors[rel.type]);
                ctx.setLineDash([]);
                ctx.font=`bold ${{10*scale}}px Microsoft YaHei`; ctx.fillStyle=typeColors[rel.type]; ctx.textAlign='center'; ctx.textBaseline='middle';
                ctx.fillText(rel.label,(sx+ex)/2+px*0.6,(sy+ey)/2+py*0.6-5*scale);
            }}
        }});
    }}
    
    function drawArrow(x,y,angle,color){{const s=12*scale;ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x-s*Math.cos(angle-Math.PI/6),y-s*Math.sin(angle-Math.PI/6));ctx.lineTo(x-s*Math.cos(angle+Math.PI/6),y-s*Math.sin(angle+Math.PI/6));ctx.closePath();ctx.fill();}}
    
    function drawCharacters() {{
        characters.forEach(c=>{{
            const x=c.x*scale+offsetX, y=c.y*scale+offsetY, r=(c.isProtagonist?50:40)*scale;
            if(c.isProtagonist){{const g=ctx.createRadialGradient(x,y,r,x,y,r*2);g.addColorStop(0,c.color+'50');g.addColorStop(1,'transparent');ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r*2,0,Math.PI*2);ctx.fill();}}
            ctx.fillStyle=c.color; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
            ctx.strokeStyle=c.isProtagonist?currentTheme.nodeBorder:currentTheme.nodeBorder+'80'; ctx.lineWidth=c.isProtagonist?4*scale:2*scale; ctx.stroke();
            ctx.font=`${{r*0.85}}px Arial`; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(c.emoji,x,y-3*scale);
            if(c.isProtagonist){{ctx.font=`${{11*scale}}px Microsoft YaHei`;ctx.fillStyle=currentTheme.nodeBorder;ctx.fillText('🌟 主角',x,y-r-12*scale);}}
            ctx.font=`bold ${{13*scale}}px Microsoft YaHei`; ctx.fillStyle=currentTheme.text; ctx.shadowColor=currentTheme.bg; ctx.shadowBlur=6; ctx.fillText(c.name,x,y+r+16*scale); ctx.shadowBlur=0;
            ctx.font=`${{10*scale}}px Microsoft YaHei`; ctx.fillStyle=currentTheme.textDim; ctx.fillText(c.nationality,x,y+r+30*scale);
            const bx=x+r+8*scale, by=y-r+5*scale, bs=24*scale;
            ctx.fillStyle=currentTheme.bg+'dd'; ctx.beginPath(); ctx.arc(bx,by,bs/2,0,Math.PI*2); ctx.fill();
            ctx.strokeStyle=currentTheme.nodeBorder; ctx.lineWidth=2*scale; ctx.stroke();
            ctx.font=`${{bs*0.6}}px Arial`; ctx.fillStyle=currentTheme.nodeBorder; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText('🔍',bx,by);
        }});
    }}
    
    function simulate() {{
        if(!simulationRunning)return;
        const cx=canvas.width/2-offsetX, cy=canvas.height/2-offsetY;
        characters.forEach(c=>{{c.fx=0;c.fy=0;}});
        for(let i=0;i<characters.length;i++)for(let j=i+1;j<characters.length;j++){{
            const a=characters[i],b=characters[j]; const dx=b.x-a.x,dy=b.y-a.y,dist=Math.sqrt(dx*dx+dy*dy)||1;
            const f=physics.repulsion/(dist*dist), ffx=(dx/dist)*f, ffy=(dy/dist)*f;
            a.fx-=ffx;a.fy-=ffy;b.fx+=ffx;b.fy+=ffy;
        }}
        relationships.forEach(rel=>{{
            const a=characters.find(c=>c.id===rel.from),b=characters.find(c=>c.id===rel.to);
            if(!a||!b)return;
            const dx=b.x-a.x,dy=b.y-a.y,dist=Math.sqrt(dx*dx+dy*dy)||1;
            const f=physics.stiffness*(dist-physics.idealLength),ffx=(dx/dist)*f,ffy=(dy/dist)*f;
            a.fx+=ffx;a.fy+=ffy;b.fx-=ffx;b.fy-=ffy;
        }});
        characters.forEach(c=>{{c.fx+=(cx-c.x)*physics.centerForce;c.fy+=(cy-c.y)*physics.centerForce;}});
        characters.forEach(c=>{{
            if(isDraggingNode&&c===draggedNode)return;
            c.vx=(c.vx+c.fx)*physics.damping; c.vy=(c.vy+c.fy)*physics.damping;
            const sp=Math.sqrt(c.vx*c.vx+c.vy*c.vy);
            if(sp>50){{c.vx=c.vx/sp*50;c.vy=c.vy/sp*50;}}
            c.x+=c.vx;c.y+=c.vy;
        }});
        draw(); requestAnimationFrame(simulate);
    }}
    
    function getClicked(mx,my){{for(const c of characters){{
        const x=c.x*scale+offsetX,y=c.y*scale+offsetY,r=(c.isProtagonist?50:40)*scale;
        if(Math.sqrt((mx-x)**2+(my-y)**2)<r)return{{c,type:'node'}};
        const bx=x+r+8*scale,by=y-r+5*scale;
        if(Math.sqrt((mx-bx)**2+(my-by)**2)<14*scale)return{{c,type:'btn'}};
    }}return null;}}
    
    canvas.addEventListener('mousedown',e=>{{
        const mx=e.clientX-offsetX,my=e.clientY-offsetY;
        lastX=e.clientX;lastY=e.clientY;
        const ck=getClicked(mx,my);
        if(ck&&ck.type==='node'){{isDraggingNode=true;draggedNode=ck.c;draggedNode.vx=draggedNode.vy=0;canvas.classList.add('dragging');}}
        else isDragging=true;
    }});
    canvas.addEventListener('mousemove',e=>{{
        if(isDragging){{offsetX+=e.clientX-lastX;offsetY+=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;draw();}}
        else if(isDraggingNode&&draggedNode){{const mx=e.clientX-offsetX,my=e.clientY-offsetY;draggedNode.x=mx/scale;draggedNode.y=my/scale;draw();}}
    }});
    canvas.addEventListener('mouseup',()=>{{isDragging=isDraggingNode=false;draggedNode=null;canvas.classList.remove('dragging');}});
    canvas.addEventListener('click',e=>{{
        const mx=e.clientX-offsetX,my=e.clientY-offsetY;
        const ck=getClicked(mx,my);
        if(ck){{
            const d=document.getElementById('charDetail');
            document.getElementById('detailEmoji').textContent=ck.c.emoji;
            document.getElementById('detailName').textContent=ck.c.name;
            const tag=document.getElementById('detailTag');
            tag.textContent='🌟 主角'; tag.style.display=ck.c.isProtagonist?'inline-block':'none';
            document.getElementById('detailNationality').textContent=ck.c.nationality;
            document.getElementById('detailIntro').textContent=ck.c.intro;
            let l=e.clientX+30,t=e.clientY-50;
            if(l+300>window.innerWidth)l=e.clientX-320;
            if(t+200>window.innerHeight)t=window.innerHeight-220;
            d.style.left=l+'px';d.style.top=t+'px';d.classList.add('show');
        }} else document.getElementById('charDetail').classList.remove('show');
    }});
    canvas.addEventListener('wheel',e=>{{e.preventDefault();scale=Math.max(0.3,Math.min(3,scale*(e.deltaY>0?0.9:1.1)));draw();}});
    
    document.getElementById('btnSimStart').onclick=()=>{{simulationRunning=true;simulate();}};
    document.getElementById('btnSimStop').onclick=()=>{{simulationRunning=false;}};
    document.getElementById('btnSimReset').onclick=()=>{{simulationRunning=false;initPositions();offsetX=offsetY=0;scale=1;draw();}};
    
    themes.forEach((t,i)=>{{
        const btn=document.createElement('div');
        btn.className='theme-btn'+(i===0?' active':'');
        btn.innerHTML=`<div class="theme-preview" style="background:${{t.preview}};border:1px solid ${{t.nodeBorder}};;"></div><div style="color:${{t.text}}">${{t.name}}</div>`;
        btn.onclick=()=>{{currentTheme=t;document.querySelectorAll('.theme-btn').forEach((b,j)=>b.classList.toggle('active',i===j));draw();}};
        document.getElementById('themeGrid').appendChild(btn);
    }});
    
    document.getElementById('repulsion').oninput=function(){{physics.repulsion=+this.value;document.getElementById('repVal').textContent=this.value;}};
    document.getElementById('stiffness').oninput=function(){{physics.stiffness=+this.value/1000;document.getElementById('stiffVal').textContent=this.value;}};
    document.getElementById('centerForce').oninput=function(){{physics.centerForce=+this.value/10000;document.getElementById('centerVal').textContent=this.value;}};
    document.getElementById('damping').oninput=function(){{physics.damping=+this.value/1000;document.getElementById('dampVal').textContent=(this.value/1000).toFixed(2);}};
    
    window.onresize=resize;
    resize(); initPositions(); draw();
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python parser.py <输入文件> <输出HTML> [书名]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    book_title = sys.argv[3] if len(sys.argv) > 3 else "未知书籍"
    
    ext = input_file.lower().split('.')[-1]
    
    if ext == 'epub':
        text = parse_epub(input_file)
    elif ext == 'txt':
        text = parse_txt(input_file)
    else:
        print(f"不支持的文件格式: {ext}")
        sys.exit(1)
    
    if not text:
        print("无法解析文件内容")
        sys.exit(1)
    
    # 提取人物和关系（这里需要 AI 填充）
    characters, relationships = analyze_characters(text)
    
    # 生成 HTML
    generate_html(book_title, characters, relationships, output_file)
    print(f"图谱已生成: {output_file}")
