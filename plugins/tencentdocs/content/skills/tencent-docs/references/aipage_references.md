# 本地 HTML 一键上云（.aipage 导入）

本文档定义「把本地 HTML 打包成 `.aipage` 并上传到腾讯文档」的标准工作流，
适用场景：

- 上游 skill（如 `smart-page`）只产出 HTML 目录 / 单文件，**打包与导入由本 skill 接手完成**。
- 用户直接给出本地 `.html` 路径并要求「上传 / 导入 / 上云 / 发布到腾讯文档」。

> ⚠️ 上游 skill **禁止**自行实现 `prepare-pack` / `pack` / 拼接 `pre_import + async_import`
> 的逻辑；必须改为调用本工作流。

---

## 触发条件

任一满足即触发：

1. 用户输入包含本地 `.html` 文件路径，且语义包含「上传 / 导入 / 上云 / 发布 / 同步到腾讯文档」。
2. 上游 skill（典型为 `smart-page`）显式声明「HTML 已生成，请用 tencentdocs 打包并导入」，
   并提供：
   - 单文件入口：`html_path`（推荐）
   - 或目录入口：`html_dir`（目录内必须有 `index.html`，或唯一一个 `*.html`）
   - 可选：`title`（缺省时自动从 `<title>` 标签或文件名推导）

---

## 标准链路（4 步）

### Step 1：本地打包成 `.aipage`

调用本 skill 自带的脚本 `aipage_pack.js`（**纯 Node.js，零 npm 依赖，跨平台**：macOS / Linux / Windows 原生 cmd / PowerShell 直接可用，不需要 bash / Git Bash / WSL）：

```bash
# 单文件模式（最常见）
node scripts_path/aipage_pack.js --html "<html_path>" [--title "<title>"]

# 目录模式（含 assets/ 等附属资源时）
node scripts_path/aipage_pack.js --dir  "<html_dir>"  [--title "<title>"]
```

> `scripts_path` 为本 SKILL 文件所在目录，例如：
> `<skill_dir>/aipage_pack.js`
>
> 运行环境要求：Node.js >= 18。Windows 上可直接 `node aipage_pack.js ...`。

脚本以稳定格式输出，可直接 `grep` / 正则解析：

```
AIPAGE_PATH=/tmp/xxx.aipage
AIPAGE_SIZE=123456
AIPAGE_MD5=abcd1234...
AIPAGE_TITLE=立项方案
```

退出码：`0` 成功；`1` 参数错；`2` 源 HTML 不合法；`3` 打包失败 / 工具缺失。

### Step 2：调用 `manage.pre_import` 获取 COS 上传链接

```bash
mcode-tools connector call "<PRE_IMPORT_TOOL>" --args \
  '{"file_name": "<basename(AIPAGE_PATH)>", "file_size": <AIPAGE_SIZE>, "file_md5": "<AIPAGE_MD5>"}'
```

返回字段中需要：`upload_url`、`file_key`、`task_id`。

> 也可以直接复用 `import_file.js`（位于本 skill 同目录），它已封装 Step 1 之后的
> 「pre_import + PUT 上传 COS」两步，输出 `IMPORT_READY` + 关键字段。
> 推荐写法：先用 `node aipage_pack.js` 打出 `.aipage`，再 `node import_file.js <AIPAGE_PATH> "<PRE_IMPORT_TOOL>"`。

### Step 3：PUT 上传到 COS

```bash
curl -sS -X PUT \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@<AIPAGE_PATH>" \
  "<upload_url>"
```

HTTP 2xx 视为上传成功。

### Step 4：触发异步导入并轮询

```bash
# 触发
mcode-tools connector call "<ASYNC_IMPORT_TOOL>" --args \
  '{"task_id":"<task_id>","file_key":"<file_key>","file_name":"<file_name>","file_md5":"<AIPAGE_MD5>","file_size":<AIPAGE_SIZE>}'

# 轮询（建议每 3s 一次，最多 60s）
mcode-tools connector call "<IMPORT_PROGRESS_TOOL>" --args '{"task_id":"<task_id>"}'
```

`progress=100` 时视为成功，从返回中拿 `file_id` / `file_url`，必要时用
`?_fid=<file_id>` 拼接到 `file_url`。

---

## 脚本与工具选择

先按本 Skill 的 `references/connector.md` 发现 `manage.pre_import`、`manage.async_import`、`manage.import_progress` 对应的完整工具名。`PRE_IMPORT_TOOL` 等大写占位符均指发现结果，不是字面工具名。

运行 `node import_file.js "<AIPAGE_PATH>" "<PRE_IMPORT_TOOL>"` 可完成预导入和 PUT。将输出的 `file_key`、`file_name`、`file_md5`、`file_size`、`task_id` 用 JSON 序列化写入参数文件，再调用发现到的 async_import 工具；不要把文件名直接插入 shell JSON 字符串。保留 task_id 后轮询 import_progress。

---

## 行为约束

- **必须用 `aipage_pack.js` 打包**：禁止 agent 自己 `zip` / 写 `manifest.json` / 写 `janus.manifest.json`；
  打包脚本是唯一真相源，避免与 aicanvas 后端结构契约漂移。Windows 等无 bash 环境必须使用本 `node aipage_pack.js`，**不要**回退到手写 zip。
- **失败重试**：只读进度查询可有限重试；预导入、上传或触发导入响应不明确时，先按 task_id 查询状态，避免重复提交。失败时报告错误和 trace_id，不自动创建新任务。
- **成功输出**：拿到 `file_url` 后，独立发起一次 `preview_url` 工具调用，
  然后告知用户「已完成，在线地址如下 ↓」。
- **常见错误码** 参见主 SKILL 的「问题定位指南」，鉴权失败优先看 `references/auth.md`。
