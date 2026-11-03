# 输出格式说明

## 触发条件速查

| 用户关键词 | 输出格式 | 使用工具/Skill |
|-----------|---------|--------------|
| 默认无指定 | Markdown 纯文本 | 直接输出 |
| "导出Word" / "生成Word" | .docx 文件 | minimax-docx skill |
| "同步到飞书" / "写入飞书" | 飞书云文档 | feishu-doc skill |
| "同步到企微" / "写入企微文档" | 企业微信文档 | wecom-doc-manager skill |
| "发给我" / "发送到微信" | 微信消息 | message tool |

---

## Markdown 文本（默认）

直接输出 Markdown 格式，用户可复制。
微信/WhatsApp 场景下自动转换表格为列表。

---

## Word 文档（.docx）

使用 minimax-docx skill，流程：
1. 整理好 Markdown 内容
2. 调用 minimax-docx skill 的 write_docx 功能
3. 生成 .docx 文件并发送给用户

文档样式：专业商务风格，标题加粗、层次分明。

---

## 飞书云文档

使用 feishu-doc skill，流程：
1. 整理好内容后调用 feishu-doc skill
2. 创建飞书文档并写入内容
3. 返回文档链接给用户

---

## 企业微信文档

使用 wecom-doc-manager skill，流程：
1. 整理好内容后调用 skill
2. 在企业微信侧边栏创建文档
3. 返回文档链接或确认消息

---

## 微信直接发送

使用 message tool，action=send，media 可附带文件：
- 语音：AMR/MP3 文件，max 2MB
- 图片：PNG/JPEG，max 10MB
- 文件：任意格式，max 20MB