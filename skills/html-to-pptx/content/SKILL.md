---
name: html-to-pptx
description: 将HTML幻灯片内容转换为PPTX文件。当用户说"HTML转PPT"、"转换成PPT"、"导出PPTX"时触发。使用pptxgenjs将HTML内容转为PowerPoint，支持多页幻灯片，自动提取标题和正文。
---

# HTML to PPTX Converter

## 核心能力

将 HTML 幻灯片内容转换为 PowerPoint（.pptx）文件，使用 pptxgenjs 生成。

## 支持格式

- HTML 中的 `<hr>` 分隔符 → 每段转为一张幻灯片
- `<br>` → 换行
- 纯文本内容直接处理

## CLI 用法

```bash
node /workspace/skills/html-to-pptx/scripts/html2pptx.js "<标题>" "<幻灯片1内容>" "<幻灯片2内容>" ...
```

## 工作流程

1. 接收 HTML 内容字符串
2. 按 `<hr>` 分隔符拆分为多页
3. 每页提取第一行为标题，其余为正文
4. 生成 PPTX 文件到 `/tmp/`
5. 返回文件路径

## 输出

- PPTX 文件保存至 `/tmp/<标题>.pptx`
- 可通过微信发送给用户

## 示例

输入：标题"测试"，两页内容
输出：测试.pptx（2页幻灯片）

## 依赖

- pptxgenjs 4.0.1（已全局安装于 /usr/local/lib/node_modules/pptxgenjs）
- Node.js 脚本，无需额外依赖
