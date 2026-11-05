---
name: book-character-mapper
description: 从小说文件中提取人物信息，自动生成力导向关系图谱可视化白板。当用户要求分析小说人物关系、生成角色关系图、可视化书中人物、提取书中人物信息时使用。关键词：人物图谱、关系图谱、角色关系、小说分析、人物关系图、character map、novel analysis、relationship graph。
---

# 小说人物关系图谱生成器

## 简介

这是一个用于分析小说中人物关系并生成可视化图谱的技能。通过读取 epub、pdf、txt 格式的小说文件，自动提取人物信息，分析人物之间的关系，并以力导向图谱的形式展示。

## 功能特性

- **智能解析**: 支持 epub、pdf、txt 等多种电子书格式
- **人物提取**: 自动识别并提取人物姓名、性别、身份信息
- **关系分析**: 分析人物之间的各种关系（工作、友情、敌对等）
- **可视化展示**: 力导向图谱，支持物理模拟
- **交互功能**: 拖拽节点、切换配色、查看详情
- **9 套配色**: 深邃星空、经典蓝白、暗夜紫罗兰、森林秘境等

## 使用方式

在对话中输入以下关键词即可触发：

```
分析《书名》的人物关系图谱
生成角色关系图
小说人物图谱
```

## 触发条件

当用户请求以下内容时激活此技能：

1. 分析小说中的人物关系
2. 生成书中角色的关系图
3. 可视化书中人物
4. 提取书中人物信息

## 工作流程

### 1. 读取书籍文件

使用 Python 解析 epub/txt 文件，或使用 MCP 工具解析 PDF：

```python
# EPUB 解析示例
from ebooklib import epub
from bs4 import BeautifulSoup

def parse_epub(file_path):
    book = epub.read_epub(file_path)
    text_content = []
    for item in book.get_items():
        if item.get_type() == 9:  # EPUB_HTML
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            if len(text) > 100:
                text_content.append(text)
    return '\n'.join(text_content)
```

### 2. 分析人物和关系

通过分析文本内容，提取：
- 人物姓名
- 性别（通过代词、称呼判断）
- 身份/国籍
- 人物之间的关系

### 3. 生成图谱 HTML

将人物和关系数据注入到图谱模板，生成可交互的 HTML 文件：

```javascript
// 人物数据结构
const characters = [
    {
        id: 'unique_id',
        name: '人物姓名',
        emoji: '👤',  // 👩 女性, 👽 外星生物
        isProtagonist: true,
        color: '#27ae60',
        intro: '人物简介',
        nationality: '身份/国籍'
    }
];

// 关系数据结构
const relationships = [
    {
        from: 'person_a_id',
        to: 'person_b_id',
        type: 'work',  // work/teammate/friend/enemy
        label: '关系描述',
        direction: 'single'  // single/bidirectional
    }
];
```

### 4. 部署图谱

使用 deploy 工具将生成的 HTML 部署到线上，生成可访问的链接。

## 输出示例

部署后生成包含以下功能的在线图谱：

- 🌟 主角高亮显示，带光晕效果
- 👤👩👽 Emoji 标识性别/物种
- 📊 力导向布局，节点自动排列
- 🔄 物理模拟，节点可拖拽
- 🎨 9 套配色方案可选
- 📝 点击节点查看人物详情

## 技术实现

### 物理模拟参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 斥力 | 节点之间的排斥力 | 3000 |
| 刚度 | 弹簧弹力系数 | 40 |
| 向心 | 指向中心的引力 | 8 |
| 阻尼 | 运动衰减系数 | 850 |

### 配色方案

| 主题 | 背景色 | 适用场景 |
|------|--------|----------|
| 深邃星空 | #0d1117 | 夜间使用 |
| 经典蓝白 | #1a365d | 商务演示 |
| 暗夜紫罗兰 | #1a1a2e | 神秘氛围 |
| 森林秘境 | #1a2f1a | 自然风格 |
| 沙漠黄昏 | #2d1f0f | 复古风格 |
| 极简灰白 | #f5f5f5 | 明亮简约 |
| 复古羊皮 | #f4ecd8 | 古典文学 |
| 薄荷清晨 | #e8f5f0 | 清爽舒适 |
| 天空蓝调 | #e8f4fc | 清新明亮 |

## 示例输出

针对《挽救计划》(Project Hail Mary) 生成的图谱包含：

**人物**: 瑞恩·格雷斯（主角）、Rocky（外星友人）、斯特拉特、国正、杜博等 12 个角色

**关系**: 工作上下级、国际合作、跨种族友谊等 13 条关系线

## 依赖工具

- `extract_pdfs_full_content`: PDF 文件解析
- `mcp__matrix__bash`: 执行 Python 脚本
- `Write`: 生成 HTML 文件
- `deploy`: 部署图谱到线上

## 扩展建议

1. **添加更多关系类型**: 亲情、爱情、师徒等
2. **支持批量处理**: 一次分析多本书
3. **导出功能**: 支持导出为图片、JSON 等格式
4. **个性化设置**: 自定义节点颜色、大小等
