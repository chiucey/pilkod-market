---
name: lark-feishu-write-pattern
description: lark-cli 1.0.42+ 把 Markdown 内容写入飞书云文档的**通用**最优模式（不限于 A 股报告）。覆盖 docs +create 一步完成、--markdown @file 避开 shell 转义、bot 模式自动 grant full_access、media-insert + block_move_after 两段式插入任意 block 到文档开头。
---

# 飞书云文档写入最优模式（lark-cli 1.0.42+）

适用场景：把任何 Markdown 内容（报告、笔记、播客脚本、代码 review 等）写入飞书云文档或知识库节点。

## 核心模式：一行命令 = 创建节点 + 写入内容 + 自动授权

```bash
# 通用模板
lark-cli docs +create --api-version v2 \
  --wiki-space <SPACE_ID>      # 或 --folder-token <FOLDER_TOKEN>，或都不传（个人空间）
  --title "节点标题（建议带日期前缀）" \
  --markdown "@/path/to/report.md" \   # ← 用 @file 避免 shell 转义
  --format json                # ← 必加，方便解析返回值
```

返回值从 `data.document` 节点取：
- `document_id`：后续 `media-insert` / `block_move_after` 的锚点
- `url`：飞书链接，附在交付消息末尾
- `permission_grant.status`：`granted` / `skipped` / `failed`（详见下方 §3）

## 1. 为什么必须用 `--markdown @file` 而不是 `--content "..."`

`--content "..."` 的陷阱（lark-cli 1.0.42 实测）：
- 内容里的 `*` `_` `` ` `` `<` `[` `]` `$` 会被 shell 吞
- 多行内容用 `cat > file <<EOF` 也会被 shell security scan 拦下「Confusable Unicode」false positive
- argv 长度有限（macOS 默认 ARG_MAX = 262144，但很多 shell 设更小）

`--markdown @file` 的优势：
- 完整避开 shell 解析
- 字面 `@` 开头用 `@@` 转义
- 文件可重用（调试/重出方便）
- 配合 `cat > /tmp/file.md <<'EOF'`（EOF 带单引号禁用变量展开）写文件即可

```bash
# 写文件（EOF 必须带单引号，否则 $VAR 被 shell 展开）
cat > /tmp/report.md <<'REPORT_EOF'
# 标题
**时间**: $(date)   ← 这是字面量，不会被 shell 展开
REPORT_EOF

# 写入飞书
lark-cli docs +create --api-version v2 \
  --wiki-space 7644627944614169549 \
  --title "$(date +%Y-%m-%d) 报告" \
  --markdown "@/tmp/report.md"
```

## 2. 不要再做的事（lark-cli 1.0.42+ 都已自动处理）

| 旧做法 | 现在 | 原因 |
|---|---|---|
| `curl /open-apis/auth/v3/tenant_access_token/internal` 拿 token | ❌ 不要做 | lark-cli 内置 auth，cron 环境自动注入 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` |
| `POST /drive/v1/permissions/{id}/members?type=docx` 加管理员 | ❌ 不要做（bot 模式） | `docs +create --as bot` 自动给 config.json 里的 `userOpenId` 授权 `full_access`，返回 `permission_grant.status=granted` |
| 先 `wiki +node-create` 再 `docs +update --command overwrite` 两步走 | ❌ 不要做 | `docs +create` 可直接带 `--wiki-space` 一步完成 |
| `--doc-token <id>` | ❌ 错参数名 | 用 `--doc <id>`（所有 `docs +update` / `docs +media-insert` / `docs +fetch` 都用 `--doc`） |
| `--mode overwrite` | ❌ 错参数名 | 用 `--command overwrite`（lark-cli v1.0.42 严格校验，必填 `--command`） |
| `--content "inline text"` | ❌ 转义陷阱 | 用 `--markdown @file` 或 `--content @file` 或 `cat file \| ... --content -` |
| `lark-cli -o /tmp/file.json` | ❌ 不支持 | lark-cli 大部分子命令不支持 `-o`，用 shell `>` 或 `tee` 重定向 |
| `docs +update --command overwrite` 之后又 `media-insert + block_move_after` | ❌ **破坏性顺序** | `--command overwrite` 会清空所有 blocks（音频块会被连根拔起）。**铁律**：所有内容写入 + 所有 media 插入必须在同一次或连续 session 内完成，且**最后一次 `overwrite` 必须在 media-insert 之前** |

## 3. `permission_grant` 自动授权机制详解

lark-cli 在 **bot 模式**（`~/.lark-cli/config.json` 里的 `userOpenId`）下创建文档时，会**自动**给该 open_id 授予 `full_access`（可管理权限）。返回值 `data.permission_grant` 包含：

| `status` 值 | 含义 | 处置 |
|---|---|---|
| `granted` | 成功授权 | 无需任何操作 |
| `skipped` | 本地没有 userOpenId，无法授权 | 用户需先 `lark-cli auth login`，文档创建但 user 没有可管理权限（只读） |
| `failed` | 授权失败（一般是因为 wiki 空间 ACL 限制） | 用户已通过 wiki 空间所有权继承访问权，可直接发 URL |

**核心洞察**：当 cron 任务在 bot 模式下运行时（`config.json` 已配 userOpenId），**完全不需要手动调用 `POST /drive/v1/permissions/.../members`**。旧版 prompt 里那段 `curl` 是多余的（且容易在 member_type / perm 字段上写错）。

## 4. 节点标题：必须用日期前缀

```bash
# ✅ 正确
TITLE="$(date +%Y-%m-%d) 【开盘】A 股分析"

# ❌ 错误（知识库里所有节点长得一样）
TITLE="今日 A 股【开盘】报告"
```

**为什么**：飞书知识库的列表视图按标题排序，日期前缀确保每天的报告节点可区分。

**额外注意**：`--command overwrite` 会把 doc 的 `title` 字段重置为报告的**第一个 H1 文本**。所以报告 H1 也要带日期：
```markdown
# 2026-06-09 今日 A 股【开盘】报告
```
否则 wiki 节点标题是 "2026-06-09 【开盘】A股分析"，但 doc 显示标题会变成 "今日 A 股【开盘】报告"（丢失日期）。

## 5. 把任意 block 插入到文档开头（不限于 mp3）

**两段式插入原理**：`docs +media-insert` 只能追加到文档末尾。要把任意 block 移到任意位置（开头/中间），用 `block_move_after`：

```bash
DOC_ID="<document_id>"

# 5.1 先追加到末尾（拿到新建 block 的 id）
INSERT_JSON=$(lark-cli docs +media-insert \
  --doc "$DOC_ID" \
  --file /path/to/asset \
  --type file \
  --format json)
NEW_BLK_ID=$(echo "$INSERT_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['block_id'])")

# 5.2 移动到文档开头（锚点 DOC_ID 即 page_id）
lark-cli docs +update --api-version v2 \
  --doc "$DOC_ID" \
  --command block_move_after \
  --block-id "$DOC_ID" \
  --src-block-ids "$NEW_BLK_ID"
```

**适用 block 类型**（不仅限 mp3）：
- 音频（`--type file`，飞书用 `audio/mpeg` mime 渲染为可在线播放卡片）
- PDF 附件（`--type file`）
- 图片（`--type image`）
- 任何未来 lark-cli 支持的资源

**坑**：
- `--file` 必须是 **cwd 内的相对路径**（绝对路径会报错）；先 `cd` 到文件所在目录
- 失败时**不要重试** `media-insert`，否则会产生重复 block ——只重试 `block_move_after`
- 两步必须都成功；如 move 失败，block 会被丢在文档末尾（功能上无影响，但不优雅）

## 6. 验证 pipeline 成功

```bash
# 验证文档创建成功
lark-cli docs +fetch --api-version v2 \
  --doc "$DOC_ID" --format json | python3 -c "
import sys, json
d = json.load(sys.stdin)
doc = d['data']['document']
print(f\"doc_id: {doc['document_id']}\")
print(f\"url: {doc['url']}\")
print(f\"title: {doc['title']}\")
print(f\"blocks: {len(d['data'].get('blocks', []))}\")"

# 验证音频/文件在文档开头
lark-cli docs +fetch --api-version v2 \
  --doc "$DOC_ID" --scope range \
  --start-block-id "$DOC_ID" --end-block-id "$DOC_ID" \
  --context-after 3 --format json | python3 -c "
import sys, json
d = json.load(sys.stdin)
blocks = d['data']['blocks']
for i, b in enumerate(blocks[:5]):
    print(f'[{i}] block_id={b[\"block_id\"]} type={b[\"block_type\"]}')"
# 期望: [0]=title, [1]=file (mp3), [2]=p, [3]=p, ...
```

## 7. 完整模板：写报告 + 插音频 + 投递

```bash
#!/bin/bash
set -e

# === 配置 ===
TODAY=$(date +%Y-%m-%d)
REPORT_TYPE="<open|close>"  # 任务类型
SPACE_ID="7644627944614169549"  # 知识库 space
WIKI_LABEL="<开盘|收盘>"  # 中文标签
DURATION_MIN=4  # 播客时长（开盘4/收盘5）

# === 1. 报告内容写到本地文件 ===
cat > /tmp/report_${REPORT_TYPE}_${TODAY}.md <<'REPORT_EOF'
<完整报告 Markdown>
REPORT_EOF

# === 2. 一行命令写入飞书 ===
CREATE_JSON=$(lark-cli docs +create --api-version v2 \
  --wiki-space "$SPACE_ID" \
  --title "${TODAY} 【${WIKI_LABEL}】A股分析" \
  --markdown "@/tmp/report_${REPORT_TYPE}_${TODAY}.md" \
  --format json)

DOC_ID=$(echo "$CREATE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['document']['document_id'])")
DOC_URL=$(echo "$CREATE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['document']['url'])")
PERM_STATUS=$(echo "$CREATE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data', {}).get('permission_grant', {}).get('status', 'unknown'))")

echo "✅ 文档创建: $DOC_URL (permission: $PERM_STATUS)"

# === 3. 合成播客 ===
cat > /tmp/podcast_${REPORT_TYPE}_${TODAY}.txt <<'PODCAST_EOF'
<播客稿>
PODCAST_EOF

mmx speech synthesize \
  --text-file /tmp/podcast_${REPORT_TYPE}_${TODAY}.txt \
  --voice male-qn-jingying \
  --out /Users/taoyi/.hermes/audio_cache/podcast_${REPORT_TYPE}_${TODAY}.mp3 \
  --quiet

# === 4. 插入音频到文档开头 ===
cd /Users/taoyi/.hermes/audio_cache
INSERT_JSON=$(lark-cli docs +media-insert \
  --doc "$DOC_ID" \
  --file "./podcast_${REPORT_TYPE}_${TODAY}.mp3" \
  --type file --format json)
NEW_BLK_ID=$(echo "$INSERT_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['block_id'])")

lark-cli docs +update --api-version v2 \
  --doc "$DOC_ID" \
  --command block_move_after \
  --block-id "$DOC_ID" \
  --src-block-ids "$NEW_BLK_ID"

# === 5. 交付 ===
echo "DOC_URL=$DOC_URL"
echo "MP3=/Users/taoyi/.hermes/audio_cache/podcast_${REPORT_TYPE}_${TODAY}.mp3"
```

## 8. 历史决策记录（避免重蹈覆辙）

| 决策 | 时间 | 来源 |
|---|---|---|
| 用 `docs +create` 一步完成，不再分 wiki +node-create + docs +update | 2026-06-09 | 本会话 |
| 删掉手动 `curl tenant_access_token` | 2026-06-09 | lark-cli 1.0.42 内置 auth |
| 删掉手动 `curl drive/v1/permissions/...` 加管理员 | 2026-06-09 | `docs +create --as bot` 自动 grant full_access |
| 节点标题必须带日期前缀 | 2026-06-04 之前 | 知识库列表按标题排序 |
| 报告首个 H1 必须带日期 | 2026-06-04 | `--command overwrite` 会重置 doc title |
| `block_move_after --block-id <DOC_ID>` = 移到文档开头 | 2026-06-08 | 锚点传 page_id 等同于"开头" |
| 不重试 `media-insert`（只重试 `block_move_after`） | 2026-06-08 | 重复插入会产生多个 file block |
