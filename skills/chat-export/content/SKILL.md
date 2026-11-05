---
name: chat-export
description: |
  Export Mavis conversation/session transcripts into downloadable files — Markdown archive, self-contained HTML, and full-fidelity JSON. Use this skill whenever the user wants to export, save, back up, archive, or share a chat/对话记录: triggers include "导出聊天", "导出对话记录", "把这个聊天导出来", "把历史聊天打包", "export this chat", "save the conversation as markdown/html", "存档一下这段对话". Covers locating a session by title, pulling its message history, converting it, and delivering the files. Do NOT use for exporting documents from other sources (PDF/Word/PPT files → use the docx/pdf/pptx skills), for summarizing what a chat said without producing files, or for reading a single old message (read the session directly instead).
---

# Chat Export

把任意一段 Mavis 会话导出成用户能直接打开的文件。平台本身没有"一键导出"按钮，但消息历史可以完整读出——流程就是"取消息 → 落盘 → 转换 → 交付"。

## Inputs to collect

- **导出哪个会话**：用户通常给标题（"导出神经网络训练那个"）。标题不明确时，先用 `session list` 列出候选让用户挑，不要自己猜。
- **要什么格式**：默认三种（HTML / Markdown / JSON）都出。用户点名只要某一种（比如"给我导个 html"）就只出那一种。
- **是否包含思考过程与工具原始输出**：默认不含（HTML/Markdown 只留对话正文，可读性最好）。用户要"完整原始记录"时加 `--thinking --tool-output`，JSON 本身始终是全量的。

用户没说的不要追问——用默认值往下走。

## 加载失败时的兜底

如果 `skill` 工具在本会话报 `Cloud Host skill not found`（子会话里连内置技能都可能加载不到），不要卡住：直接用 Read 工具读本文件，然后照着下面的流程走，脚本用绝对路径调用 `/workspace/.skills/chat-export/scripts/export-chat.mjs`。文件在 NAS 挂载上，跨会话可见，流程完全一样。

## Procedure

### 1. 定位 session id

```
mavis({ command: "session list", args: { agent_name: "me", limit: 20 } })
```

返回里每项有 `title` / `session_id` / `updated_at`。用 `title` 匹配用户说的那个。
- 命中 → 记下 `session_id`。
- 第一页没有 → 用返回的 `next_cursor` 继续翻 `session list`（`args: { cursor: "..." }`），翻完仍没有再问用户。
- **带 `agent_name: "me"` 过滤的列表可能只返回当前 agent 名下的少数几条，漏掉你想找的会话。** 命中不到就换成不带过滤的全量列表（`args: { limit: 50 }`）再翻 cursor 找。两种列表都会用，取决于会话归属。
- 会话记录里的 `agent_name` 可能带尾随空格（`"Mavis "`）。写进导出文件头时用干净的名字，别把带空格的串原样回传。
- 用户要导当前对话 → `session_id: "me"`。

### 2. 取消息

```
mavis({ command: "session messages", args: { session_id: "<id>", limit: 100 } })
```

返回 `has_more: true` 时说明有翻页：用返回的 `before` 游标再调一次（`args: { before: "<cursor>" }`），直到 `has_more: false`。漏掉这一步会导出残缺的会话。

### 3. 把原始返回落盘（最容易出错的一步）

脚本要读一个**真实存在的文件**，所以必须先把工具返回原样存下来。两种情况：

- **返回体很大**（工具结果末尾出现 `[ToolResult artifact notice]`）：平台已把完整 JSON 转存成磁盘工件，`artifact_dir` 形如 `.mavis/tool-results/<session_id>/<call_id>/`，里面 `chunks/000000.txt` 就是完整原始 JSON。用 `ls` 确认路径后直接把 `--raw` 指向它。
  - 好处：几百 KB 的内容不进上下文，也不会因转录丢失。
- **返回体较小、inline 返回**：内容就在工具结果里，用 Write 工具原样写到 `/workspace/output/chat-export/raw/<session_id>.json`。保持 JSON 结构完整（`{"ok":true,"response":{"messages":[...]}}`），不要只摘 `messages` 之外的部分，也不要手工改写里面的字符串。
  - 写完用 `node -e "JSON.parse(require('fs').readFileSync('<file>','utf8'))"` 验一下能解析，防止转义出错。
  - 文件名必须带 `session_id`：并发导多个会话时同名会互相覆盖，评测里就撞过这个。

两种情况最终都只需保证 `--raw` 指向一个含 `messages` 数组的 JSON 文件。

**只依赖本 skill 里的脚本**：`/workspace/output/chat-export/` 下可能残留别次会话的产物（旧的转换脚本、别的会话的导出文件），那些不是可靠来源，别拿来当工具或当输入。

### 4. 跑转换

```
node .skills/chat-export/scripts/export-chat.mjs \
  --raw <raw.json 路径> \
  --title "<会话标题>" --session-id <id> \
  --agent "<智能体名>" --model "<模型 ID>" \
  --outdir /workspace/output/chat-export --basename "<会话标题>"
```

- 只要 HTML 就加 `--formats html`；只要 md+json 用 `--formats md,json`。
- 完整原始记录用 `--thinking --tool-output`。
- 脚本零依赖（Node 内置模块），`node scripts/export-chat.mjs --help` 有全部参数。
- 脚本路径以**本 skill 的 base directory** 为准（技能加载时会给出，例如 `Base directory for this skill: /workspace/.skills/chat-export`），拼上 `scripts/export-chat.mjs`。装到别的 workspace 根目录下时绝对路径会变，相对 base directory 的拼法不会。

### 5. 交付

把生成的文件用 `<deliver-assets>` 交付给用户，HTML 放第一个（最好读的形态）。格式是工作区绝对路径 + 自闭合标签：

```
<deliver-assets>
<media src="/workspace/output/chat-export/<标题>.html" caption="<标题> · HTML" />
<media src="/workspace/output/chat-export/<标题>.md" caption="<标题> · Markdown" />
<media src="/workspace/output/chat-export/<标题>.json" caption="<标题> · 全量 JSON" />
</deliver-assets>
```

`src` 必须是工作区内的绝对路径，`caption` 可选。不要把 raw 中间件放进交付块，除非用户要。

### 6. 批量导出

多个会话时逐个走完 1–5 步，最后打包：

```
cd /workspace/output/chat-export && zip -j chat-导出.zip *.html *.md
```

`zip` 不可用时用 `tar -czf`，并把产物移出工作区再交付。

## Output contract

每个会话产出（`/workspace/output/chat-export/` 下）：

- `<标题>.html` — 单文件、自带样式、自适应深浅色，浏览器直接打开；正文保留 Markdown 的标题/列表/表格/加粗
- `<标题>.md` — 带会话元信息（标题、ID、智能体、模型、时间范围、消息数）的纯文本归档
- `<标题>.json` — 全量原始数据，含思考过程、工具返回原文、token 用量

三个文件都必须在工作区内，交付前用 `ls` 确认存在。

## Failure handling

- **`session list` 里没有那个标题** → 翻完全部页仍没有，就问用户要会话 ID 或确认标题；不要把最接近的一个当成答案导出。
- **脚本报"输入里找不到 messages 数组"** → `--raw` 指的文件不是 `session messages` 的返回。重新按第 3 步落盘。
- **导出内容明显少于预期** → 多半是第 2 步漏了翻页，回去检查 `has_more`。
- **工件路径读不到（`expires_at_ms` 已过）** → 平台会清理旧工件，重新调一次 `session messages` 拿到新的工件目录。
- **导出是历史快照** → 导出时刻之后的对话不会出现在文件里。交付时说明这一点，别让用户以为拿到了实时副本。
- **会话为空** → 如实告诉用户这个会话没有消息，不要产出空文件充数。

## Examples

Input: "请给我导出'神经网络训练'的html"

1. `session list` → 命中 `title: "神经网络训练"`，`session_id: 452872047558979`
2. `session messages`（`limit: 100`）→ `has_more: false`，6 条消息
3. 返回体不大，inline 落盘到 `raw/452872047558979.json`
4. `node .skills/chat-export/scripts/export-chat.mjs --raw raw/452872047558979.json --title "神经网络训练" --session-id 452872047558979 --outdir /workspace/output/chat-export --basename "神经网络训练" --formats html`
5. 交付 `神经网络训练.html`

Input: "把'中英经济比较'和'具身自动驾驶'都导出来"

两次单会话导出 + `zip` 打包，一次性交付 ZIP。
