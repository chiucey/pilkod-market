---
name: md-notes
description: MD格式笔记技能。用户说"记一下"、"写个笔记"、"帮我记录"、"存到笔记"时触发。自动将内容保存为MD文件（本地）并推送到IMA笔记，双重备份。支持标题+正文结构，本地文件存放在~/.openclaw/md_notes/目录。
---

# MD Notes — MD格式笔记技能

## 核心文件

- **CLI脚本**: `/workspace/skills/md-notes/scripts/md_note.py`
- **本地存储**: `~/.openclaw/md_notes/`
- **本地索引**: `~/.openclaw/md_notes/index.json`
- **IMA推送**: 同步保存到微信IMA笔记

## 命令说明

### 保存笔记
```
md_note.py save "<标题>" "<内容>"
```
**示例：**
```bash
python3 md_note.py save "供应链QVL准入流程" "1.供应商资格审查..."
```

### 列出所有笔记
```bash
python3 md_note.py list
```

### 搜索笔记
```bash
python3 md_note.py search "<关键词>"
```

### 读取笔记内容
```bash
python3 md_note.py read "<标题关键词>"
```

## 工作流程

当用户说「记一下这个」「帮我写个笔记」「存到笔记」时：

1. **解析内容** — 提取标题和正文
2. **保存本地** — 生成 MD 文件（以标题为文件名）
3. **推送IMA** — 同步到微信IMA笔记
4. **更新索引** — 记录到 index.json 方便后续搜索

## MD格式模板

```markdown
# {标题}

> 创建时间：{YYYY-MM-DD}

---

{正文内容}

---
*由 AI 助手自动生成 | {YYYY-MM-DD}*
```

## 注意事项

- **标题**：提取用户话语中的核心主题
- **正文**：用户描述的内容，可能分段，需要保留格式
- **自动生成日期**：无需用户指定，自动添加
- **文件名安全**：特殊字符过滤，空格转`-`，截断40字符

## 示例场景

| 用户说法 | 解析 |
|---|---|
| "记一下，今天开会讨论了供应链QVL准入" | 标题：今日会议纪要；正文：供应链QVL准入讨论内容 |
| "帮我写个笔记，关于ECN变更管控流程" | 标题：ECN变更管控流程；正文：完整流程描述 |
| "记一下，供应商来访接待流程" | 标题：供应商来访接待流程；正文：流程要点 |

## IMA API 调用

使用 `import_doc` 接口：
- URL: `https://ima.qq.com/openapi/note/v1/import_doc`
- 本地推送失败不影响本地保存，双重保险
