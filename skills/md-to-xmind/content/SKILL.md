---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f9e34731afdeeb543612c6df64c52e4f
    PropagateID: f9e34731afdeeb543612c6df64c52e4f
    ReservedCode1: 3045022035655cc688414c9693b730d813f55050aab220dc63b06d485484ea8c10267358022100859daf64399fcc5fcee2a808e4369a66b1c049d8d6f2405f2db09ca8deefa9a8
    ReservedCode2: 3046022100ed5904645b148907244a49dbb986e489845355ce1d80b0a91390a3b214e8248702210083a745a2bdf1cc7f0b34b1d951f8dea40c09c2e16ab5061a1d0bf6ae8f5e4496
description: 将 Markdown 文件转换为 XMind 格式思维导图。当用户要求将 Markdown 转换为 XMind、创建思维导图、md 转 xmind、Markdown 转思维导图时使用。支持 XMind 8/2020/Zen 多种版本格式。
name: md-to-xmind
---

# MD to XMind 转换器

将 Markdown 文档转换为 XMind 格式思维导图，兼容 XMind 8、XMind 2020、XMind Zen 等多种版本。

## 支持的 Markdown 结构

| Markdown 语法 | XMind 结构 |
|-------------|-----------|
| `# 标题` | 中心主题 (Root Topic) |
| `## 二级标题` | 一级分支 |
| `### 三级标题` | 二级分支 |
| `#### 四级标题` | 三级分支 |
| `- 无序列表项` | 子主题节点 |
| `1. 有序列表项` | 子主题节点 |
| `- [ ] 待办项` | 带复选框的节点 |
| `- [x] 已完成项` | 带勾选标记的节点 |
| `> 引用块` | 带标注的节点 |
| `` `代码` `` | 代码格式的节点 |
| `**粗体**` | 粗体文本 |
| `*斜体*` | 斜体文本 |

## 使用方式

用户可以使用以下方式触发转换：

1. **上传 Markdown 文件** - 用户提供 `.md` 文件路径
2. **直接粘贴 Markdown 内容** - 用户粘贴 Markdown 文本
3. **指定 XMind 版本** - 可选：`xmind8`、`xmind2020`、`xmindzen`（默认自动适配）

## 转换流程

### 1. 解析 Markdown

```python
import re

def parse_markdown(content: str) -> dict:
    """解析 Markdown 为层级结构"""
    lines = content.split('\n')
    tree = {'children': [], 'depth': 0}
    stack = [tree]

    for line in lines:
        # 解析标题
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            depth = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            # ... 处理标题
            continue

        # 解析列表
        list_match = re.match(r'^(\s*)[-*+]\s*(?:\[([ xX])\])?\s*(.+)$', line)
        if list_match:
            indent = len(list_match.group(1))
            checked = list_match.group(2)
            text = list_match.group(3).strip()
            # ... 处理列表项
            continue

        # 解析有序列表
        ordered_match = re.match(r'^(\s*)\d+\.\s*(.+)$', line)
        if ordered_match:
            # ... 处理有序列表
            continue

        # 解析引用
        quote_match = re.match(r'^>\s*(.+)$', line)
        if quote_match:
            text = quote_match.group(1).strip()
            # ... 处理引用
            continue
```

### 2. 生成 XMind 格式

#### XMind 8 格式 (XML)

```python
def generate_xmind8_content(tree: dict) -> str:
    """生成 XMind 8 XML 格式"""
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0"
              xmlns:svg="http://www.w3.org/2000/svg"
              xmlns:fo="http://www.w3.org/1999/XSL/Format"
              version="2.0">
  <sheet>
    <title>{title}</title>
    <rootTopic>
      <title>{root_title}</title>
      {children}
    </rootTopic>
  </sheet>
</xmap-content>'''
    return xml
```

#### XMind Zen/2020 格式 (JSON)

```python
def generate_xmind_zen_content(tree: dict) -> dict:
    """生成 XMind Zen JSON 格式"""
    return {
        "schema": "xmind-zen",
        "version": "1.0.0",
        "rootTopic": {
            "id": "root",
            "children": {
                "attached": [],
                "detached": []
            }
        }
    }
```

### 3. 打包为 ZIP 文件

```python
import zipfile
import os

def create_xmind_package(content: str,
                         version: str = 'xmind8',
                         output_path: str = 'output.xmind') -> str:
    """创建 XMind ZIP 包"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if version == 'xmind8':
            zf.writestr('META-INF/manifest.xml', generate_manifest())
            zf.writestr('content.json', content)
            zf.writestr('content.xml', content)
        elif version in ('xmind2020', 'xmindzen'):
            zf.writestr('content.json', content)
    return output_path
```

## XMind 版本兼容性

| 版本 | 文件扩展名 | 内部格式 | 兼容性说明 |
|-----|-----------|---------|-----------|
| XMind 8 | `.xmind` | XML + ZIP | 最广泛兼容 |
| XMind 2020 | `.xmind` | JSON + ZIP | 现代版本 |
| XMind Zen | `.xmind` | JSON | 最新版本 |
| XMind 23+ | `.xmind` | JSON | 当前最新 |

## 样式继承

转换后的 XMind 文件会继承以下 Markdown 样式：

- `#` 标题层级 → 自动分配不同颜色/大小的节点
- `**粗体**` → XMind 粗体格式
- `*斜体*` → XMind 斜体格式
- `` `代码` `` → XMind 代码样式
- `- [ ]` 待办 → 带复选框的节点

## 输出文件

转换完成后，用户将收到：
- `.xmind` 文件，可直接在 XMind 软件中打开
- 预览链接（如适用）

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 文件不存在 | 提示用户上传文件 |
| Markdown 格式错误 | 尝试最佳匹配，跳过无法解析的行 |
| XMind 版本不支持 | 回退到 XMind 8 格式 |
