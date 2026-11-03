#!/usr/bin/env python3
"""
Universal Mind Map Generator
Convert various data sources to interactive mind map visualization
Supports drag-drop editing and multiple style themes
"""

import os
import json
import re
import base64
from pathlib import Path
from typing import Optional, Dict, List, Any
import subprocess

# Content Extraction Module
class ContentExtractor:
    """Data source content extractor"""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """Universal text extraction"""
        ext = Path(file_path).suffix.lower()

        if ext == '.txt' or ext == '.log':
            return ContentExtractor._read_text(file_path)
        elif ext == '.md':
            return ContentExtractor._read_markdown(file_path)
        elif ext in ['.json']:
            return ContentExtractor._read_json(file_path)
        elif ext == '.xml':
            return ContentExtractor._read_xml(file_path)
        elif ext in ['.yaml', '.yml']:
            return ContentExtractor._read_yaml(file_path)
        elif ext in ['.sql']:
            return ContentExtractor._read_sql(file_path)
        elif ext in ['.ini', '.conf', '.cfg']:
            return ContentExtractor._read_config(file_path)
        else:
            return ContentExtractor._read_text(file_path)

    @staticmethod
    def _read_text(file_path: str) -> str:
        """Read plain text file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    @staticmethod
    def _read_markdown(file_path: str) -> str:
        """Read Markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove Markdown formatting symbols
        content = re.sub(r'#+ ', '', content)
        return content

    @staticmethod
    def _read_json(file_path: str) -> str:
        """Read JSON file and convert to readable text"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def _read_xml(file_path: str) -> str:
        """Read XML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove XML tags
        text = re.sub(r'<[^>]+>', '', content)
        return text

    @staticmethod
    def _read_yaml(file_path: str) -> str:
        """Read YAML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def _read_sql(file_path: str) -> str:
        """Read SQL file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Extract table names and key info
        tables = re.findall(r'CREATE TABLE (\w+)', content, re.IGNORECASE)
        return f"SQL Schema: {', '.join(tables)}\n\n{content[:2000]}"

    @staticmethod
    def _read_config(file_path: str) -> str:
        """Read config file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class MindMapGenerator:
    """Mind map generator with drag-drop and theme support"""

    # Theme definitions
    THEMES = {
        'purple': {
            'name': '紫色渐变',
            'bgGradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',
            'text': '#fff',
            'cardBg': '#fff',
            'darkText': '#333'
        },
        'blue': {
            'name': '蓝色科技',
            'bgGradient': 'linear-gradient(135deg, #0c3483 0%, #a2b6df 100%)',
            'primary': '#0c3483',
            'secondary': '#537895',
            'accent': '#00d4ff',
            'text': '#fff',
            'cardBg': '#fff',
            'darkText': '#1a1a2e'
        },
        'green': {
            'name': '绿色自然',
            'bgGradient': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
            'primary': '#11998e',
            'secondary': '#38ef7d',
            'accent': '#ccff90',
            'text': '#fff',
            'cardBg': '#fff',
            'darkText': '#1b4332'
        },
        'orange': {
            'name': '橙色活力',
            'bgGradient': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'primary': '#f5576c',
            'secondary': '#ff9a44',
            'accent': '#fddb92',
            'text': '#fff',
            'cardBg': '#fff',
            'darkText': '#4a2c0a'
        },
        'dark': {
            'name': '暗黑模式',
            'bgGradient': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            'primary': '#0f3460',
            'secondary': '#533483',
            'accent': '#e94560',
            'text': '#eaeaea',
            'cardBg': '#1a1a2e',
            'darkText': '#fff'
        }
    }

    def __init__(self):
        self.nodes = []
        self.root = ""

    def generate_html(self, title: str, mermaid_code: str, theme: str = 'purple') -> str:
        """Generate interactive HTML mind map with drag-drop and themes"""
        # Escape special characters but preserve Chinese characters
        mermaid_escaped = mermaid_code.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

        # Get theme colors
        theme_colors = self.THEMES.get(theme, self.THEMES['purple'])
        themes_json = json.dumps(self.THEMES, ensure_ascii=False)

        html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Mind Map</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Microsoft YaHei', 'PingFang SC', sans-serif;
            background: {bgGradient};
            min-height: 100vh;
            transition: background 0.5s ease;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        h1 {{
            color: {text};
            font-size: 1.8rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .toolbar {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .toolbar-group {{
            display: flex;
            gap: 8px;
            background: rgba(255,255,255,0.2);
            padding: 8px 12px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }}
        .btn {{
            background: {primary};
            color: {text};
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            background: {secondary};
        }}
        .btn:active {{
            transform: translateY(0);
        }}
        .theme-btn {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border: 3px solid transparent;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .theme-btn:hover {{
            transform: scale(1.2);
        }}
        .theme-btn.active {{
            border-color: {text};
            box-shadow: 0 0 10px rgba(255,255,255,0.5);
        }}
        .mindmap-container {{
            background: {cardBg};
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            min-height: 600px;
            position: relative;
            overflow: hidden;
        }}
        .mindmap-wrapper {{
            position: relative;
            width: 100%;
            height: 500px;
            overflow: hidden;
            cursor: grab;
        }}
        .mindmap-wrapper:active {{
            cursor: grabbing;
        }}
        .mindmap-wrapper svg {{
            display: block;
        }}
        .zoom-controls {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 100;
        }}
        .zoom-btn {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: {primary};
            color: {text};
            border: none;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .zoom-btn:hover {{
            background: {secondary};
            transform: scale(1.1);
        }}
        .code-section {{
            margin-top: 30px;
            background: #1e1e1e;
            border-radius: 16px;
            padding: 20px;
        }}
        .code-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .code-section h3 {{
            color: #fff;
            margin: 0;
        }}
        pre {{
            background: #2d2d2d;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            color: #abb2bf;
            max-height: 300px;
        }}
        code {{
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 13px;
        }}
        .edit-modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        .edit-modal.active {{
            display: flex;
        }}
        .edit-modal-content {{
            background: {cardBg};
            padding: 30px;
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
        }}
        .edit-modal h3 {{
            margin-bottom: 20px;
            color: {darkText};
        }}
        .edit-modal input, .edit-modal textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
            font-family: inherit;
        }}
        .edit-modal textarea {{
            min-height: 100px;
            resize: vertical;
        }}
        .edit-modal-buttons {{
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }}
        .instructions {{
            color: {text};
            font-size: 14px;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .theme-selector {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .theme-selector span {{
            color: {text};
            font-size: 14px;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="toolbar">
                <div class="theme-selector">
                    <span>主题:</span>
                    <button class="theme-btn" style="background: linear-gradient(135deg, #667eea, #764ba2);" data-theme="purple" title="紫色渐变"></button>
                    <button class="theme-btn" style="background: linear-gradient(135deg, #0c3483, #537895);" data-theme="blue" title="蓝色科技"></button>
                    <button class="theme-btn" style="background: linear-gradient(135deg, #11998e, #38ef7d);" data-theme="green" title="绿色自然"></button>
                    <button class="theme-btn" style="background: linear-gradient(135deg, #f5576c, #ff9a44);" data-theme="orange" title="橙色活力"></button>
                    <button class="theme-btn" style="background: linear-gradient(135deg, #1a1a2e, #16213e);" data-theme="dark" title="暗黑模式"></button>
                </div>
            </div>
        </div>
        <p class="instructions">提示: 鼠标滚轮缩放 | 拖拽画布平移 | 点击节点双击编辑</p>
        <div class="mindmap-container">
            <div class="mindmap-wrapper" id="mindmapWrapper">
                <pre class="mermaid" id="mermaidDiagram">
{mermaid_code}
                </pre>
            </div>
            <div class="zoom-controls">
                <button class="zoom-btn" id="zoomIn" title="放大">+</button>
                <button class="zoom-btn" id="zoomOut" title="缩小">-</button>
                <button class="zoom-btn" id="resetView" title="重置视图">⟲</button>
            </div>
        </div>
        <div class="code-section">
            <div class="code-header">
                <h3>Mermaid 代码</h3>
                <button class="btn" onclick="downloadMermaid()">下载代码</button>
            </div>
            <pre><code id="mermaidCode">{mermaid_escaped}</code></pre>
        </div>
    </div>

    <!-- Edit Modal -->
    <div class="edit-modal" id="editModal">
        <div class="edit-modal-content">
            <h3>编辑节点</h3>
            <input type="text" id="editInput" placeholder="输入节点文本...">
            <div class="edit-modal-buttons">
                <button class="btn" onclick="closeEditModal()" style="background: #999;">取消</button>
                <button class="btn" onclick="saveEdit()">保存</button>
            </div>
        </div>
    </div>

    <script>
        const themes = {themes_json};
        let currentTheme = '{theme}';
        let scale = 1;
        let panX = 0;
        let panY = 0;
        let isDragging = false;
        let startX, startY;
        let currentEditNode = null;

        // Initialize Mermaid
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'base',
            themeVariables: {{
                primaryColor: themes[currentTheme].primary,
                primaryTextColor: themes[currentTheme].darkText,
                primaryBorderColor: themes[currentTheme].secondary,
                lineColor: themes[currentTheme].secondary,
                secondaryColor: themes[currentTheme].accent,
                tertiaryColor: themes[currentTheme].accent
            }},
            mindmap: {{
                useMaxWidth: true,
                padding: 16
            }}
        }});

        // Theme switching
        document.querySelectorAll('.theme-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const theme = btn.dataset.theme;
                if (theme === currentTheme) return;

                currentTheme = theme;
                const themeColors = themes[theme];

                // Update CSS variables
                document.body.style.background = themeColors.bgGradient;
                document.querySelectorAll('.btn, .zoom-btn').forEach(el => {{
                    el.style.background = themeColors.primary;
                    el.style.color = themeColors.text;
                }});
                document.querySelector('.mindmap-container').style.background = themeColors.cardBg;
                document.querySelector('.theme-btn.active')?.classList.remove('active');
                btn.classList.add('active');

                // Update modal
                document.querySelector('.edit-modal-content').style.background = themeColors.cardBg;
                document.querySelector('.edit-modal h3').style.color = themeColors.darkText;

                // Re-render mermaid with new theme
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'base',
                    themeVariables: {{
                        primaryColor: themeColors.primary,
                        primaryTextColor: themeColors.darkText,
                        primaryBorderColor: themeColors.secondary,
                        lineColor: themeColors.secondary,
                        secondaryColor: themeColors.accent,
                        tertiaryColor: themeColors.accent
                    }}
                }});
                mermaid.init('.mermaid');
            }});
        }});

        // Set initial active theme
        document.querySelector(`[data-theme="{theme}"]`).classList.add('active');

        // Zoom controls
        document.getElementById('zoomIn').addEventListener('click', () => {{
            scale = Math.min(scale + 0.2, 3);
            applyTransform();
        }});

        document.getElementById('zoomOut').addEventListener('click', () => {{
            scale = Math.max(scale - 0.2, 0.3);
            applyTransform();
        }});

        document.getElementById('resetView').addEventListener('click', () => {{
            scale = 1;
            panX = 0;
            panY = 0;
            applyTransform();
        }});

        function applyTransform() {{
            const wrapper = document.getElementById('mindmapWrapper');
            wrapper.querySelector('svg')?.style.setProperty('transform', `translate(${{panX}}px, ${{panY}}px) scale(${{scale}})`);
        }}

        // Pan functionality
        const wrapper = document.getElementById('mindmapWrapper');
        wrapper.addEventListener('mousedown', (e) => {{
            if (e.target.closest('.mermaid svg')) {{
                isDragging = true;
                startX = e.clientX - panX;
                startY = e.clientY - panY;
                wrapper.style.cursor = 'grabbing';
            }}
        }});

        wrapper.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                panX = e.clientX - startX;
                panY = e.clientY - startY;
                applyTransform();
            }}
        }});

        wrapper.addEventListener('mouseup', () => {{
            isDragging = false;
            wrapper.style.cursor = 'grab';
        }});

        wrapper.addEventListener('mouseleave', () => {{
            isDragging = false;
            wrapper.style.cursor = 'grab';
        }});

        // Mouse wheel zoom
        wrapper.addEventListener('wheel', (e) => {{
            e.preventDefault();
            if (e.deltaY < 0) {{
                scale = Math.min(scale + 0.1, 3);
            }} else {{
                scale = Math.max(scale - 0.1, 0.3);
            }}
            applyTransform();
        }});

        // Double-click to edit
        wrapper.addEventListener('dblclick', (e) => {{
            const svg = wrapper.querySelector('svg');
            if (svg && svg.contains(e.target)) {{
                currentEditNode = e.target;
                const modal = document.getElementById('editModal');
                const input = document.getElementById('editInput');
                input.value = e.target.textContent || '';
                modal.classList.add('active');
                input.focus();
            }}
        }});

        function closeEditModal() {{
            document.getElementById('editModal').classList.remove('active');
            currentEditNode = null;
        }}

        function saveEdit() {{
            if (currentEditNode) {{
                currentEditNode.textContent = document.getElementById('editInput').value;
            }}
            closeEditModal();
        }}

        // Enter key to save
        document.getElementById('editInput').addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') saveEdit();
        }});

        // Download Mermaid code
        function downloadMermaid() {{
            const code = document.getElementById('mermaidCode').textContent;
            const blob = new Blob([code], {{ type: 'text/plain', encoding: 'utf-8' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mindmap.mmd';
            a.click();
            URL.revokeObjectURL(url);
        }}

        // Download as PNG
        function downloadPNG() {{
            const svg = document.querySelector('.mermaid svg');
            if (!svg) return;

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const svgData = new XMLSerializer().serializeToString(svg);
            const img = new Image();

            img.onload = () => {{
                canvas.width = svg.width.baseVal.value * 2;
                canvas.height = svg.height.baseVal.value * 2;
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                const a = document.createElement('a');
                a.download = 'mindmap.png';
                a.href = canvas.toDataURL('image/png');
                a.click();
            }};
            img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
        }}
    </script>
</body>
</html>'''

        return html_template.format(
            title=title,
            mermaid_code=mermaid_code,
            mermaid_escaped=mermaid_escaped,
            themes_json=themes_json,
            theme=theme,
            bgGradient=theme_colors['bgGradient'],
            primary=theme_colors['primary'],
            secondary=theme_colors['secondary'],
            text=theme_colors['text'],
            cardBg=theme_colors['cardBg'],
            darkText=theme_colors['darkText']
        )

    def build_tree_structure(self, content: str) -> Dict:
        """Build tree structure from content"""
        lines = content.strip().split('\n')
        lines = [l.strip() for l in lines if l.strip()]

        if not lines:
            return {"root": "Empty Content", "children": []}

        # Extract title as root node
        root = lines[0][:50] if lines else "Main Topic"

        # Intelligent grouping
        topics = self._group_content(lines)

        return {
            "root": root,
            "children": topics
        }

    def _group_content(self, lines: List[str]) -> List[Dict]:
        """Group content into topics"""
        groups = []
        current_group = None

        # Keywords for categorization (supports both Chinese and English)
        keywords = {
            'concept': ['概念', '定义', 'definition', 'concept'],
            'feature': ['功能', '特性', '特点', 'feature', 'function'],
            'step': ['步骤', '流程', '过程', 'step', 'process'],
            'type': ['类型', '分类', '种类', 'type', 'category'],
            'example': ['例子', '示例', 'example', 'instance'],
            'note': ['注意', '提示', 'note', 'tip', 'warning'],
        }

        for line in lines[1:20]:  # Process first 20 lines
            line = re.sub(r'[#*`\[\]]', '', line).strip()
            if len(line) < 2:
                continue

            # Categorization
            category = 'general'
            for cat, kws in keywords.items():
                if any(kw in line.lower() for kw in kws):
                    category = cat
                    break

            groups.append({
                "text": line[:80],  # Limit length
                "category": category
            })

        return groups[:12]  # Max 12 child nodes

    def generate_mermaid(self, tree: Dict) -> str:
        """Generate Mermaid mind map code"""
        lines = ["mindmap"]
        lines.append("  root(({}))".format(self._escape_mermaid(tree['root'])))

        children = tree.get('children', [])
        for i, child in enumerate(children):
            indent = "    "
            text = child.get('text', 'Topic')[:40]
            lines.append("{}{}".format(indent, self._escape_mermaid(text)))

            # Add grandchild nodes
            sub_children = children[i:i+3] if i < len(children) - 1 else []
            for sub in sub_children[:2]:
                sub_text = sub.get('text', '')[:30]
                lines.append("{}  {}".format(indent, self._escape_mermaid(sub_text)))

        return '\n'.join(lines)

    def _escape_mermaid(self, text: str) -> str:
        """Escape special characters for Mermaid while preserving Chinese"""
        # Mermaid mindmap only needs basic escaping
        return text.replace('(', '\\(').replace(')', '\\)').replace('[', '\\[').replace(']', '\\]')


def process_file(file_path: str, output_dir: str = '/workspace/mindmap_output', theme: str = 'purple') -> Dict[str, Any]:
    """Process file and generate mind map"""
    os.makedirs(output_dir, exist_ok=True)

    # Extract content
    content = ContentExtractor.extract_text(file_path)

    # Generate mind map
    generator = MindMapGenerator()
    tree = generator.build_tree_structure(content)
    mermaid_code = generator.generate_mermaid(tree)

    # Generate HTML
    title = Path(file_path).stem
    html_content = generator.generate_html(title, mermaid_code, theme)

    # Save files
    output_path = os.path.join(output_dir, f"{title}_mindmap.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Save mermaid code
    mmd_path = os.path.join(output_dir, f"{title}_mindmap.mmd")
    with open(mmd_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_code)

    return {
        'success': True,
        'output_html': output_path,
        'output_mmd': mmd_path,
        'mermaid_code': mermaid_code,
        'content_preview': content[:500]
    }


def generate_demo_mindmap() -> str:
    """Generate a demo mind map with Chinese content and themes"""
    demo_content = """人工智能基础知识
机器学习是人工智能的核心分支
监督学习使用标注数据进行训练
无监督学习从无标注数据中发现模式
深度学习通过神经网络处理复杂任务
卷积神经网络用于图像识别
循环神经网络处理序列数据
自然语言处理使机器理解人类语言
计算机视觉让机器看懂图片和视频
强化学习通过试错优化决策
机器人技术结合多种AI能力
AI伦理与安全日益受到关注"""

    generator = MindMapGenerator()
    tree = generator.build_tree_structure(demo_content)
    mermaid_code = generator.generate_mermaid(tree)
    html_content = generator.generate_html("AI基础知识演示", mermaid_code, 'purple')

    output_path = '/workspace/mindmap_output/demo_chinese_mindmap.html'
    os.makedirs('/workspace/mindmap_output', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        theme = sys.argv[2] if len(sys.argv) > 2 else 'purple'
        result = process_file(sys.argv[1], theme=theme)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Generate demo with Chinese content
        demo_path = generate_demo_mindmap()
        print(f"Demo Chinese mind map generated: {demo_path}")
