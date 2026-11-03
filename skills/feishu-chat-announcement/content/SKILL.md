---
name: feishu-chat-announcement
description: Read and update Feishu/Lark docx-style group announcements. Use when the user wants to inspect, replace, or maintain a Feishu 群公告 for a chat, especially when the announcement is the newer docx-backed type. Helpful for: (1) reading announcement metadata, (2) listing announcement blocks, (3) replacing the full announcement with prepared content, (4) maintaining onboarding notices, team rules, or public group notices in a Feishu group announcement, and (5) operating the official docx chat announcement API through a reusable local script.
---

# Feishu Chat Announcement

Use this skill for **docx-type 飞书群公告**.

## What this skill includes

Bundled script:
- `scripts/update_chat_announcement.py`

Supported actions:
- `get-meta` — get docx announcement metadata
- `list-blocks` — inspect top-level announcement blocks
- `set` — replace announcement content by deleting current children under the root block and creating new children

## Official API family used

This skill intentionally uses the docx announcement APIs:
- `GET /open-apis/docx/v1/chats/:chat_id/announcement`
- `GET /open-apis/docx/v1/chats/:chat_id/announcement/blocks`
- `GET /open-apis/docx/v1/chats/:chat_id/announcement/blocks/:block_id/children`
- `DELETE /open-apis/docx/v1/chats/:chat_id/announcement/blocks/:block_id/children/batch_delete`
- `POST /open-apis/docx/v1/chats/:chat_id/announcement/blocks/:block_id/children`

## Recommended workflow

### 1. Inspect first

When working on a new group announcement, start with:
- `get-meta`
- `list-blocks`

This confirms the announcement exists and helps verify the root block structure.

### 2. Replace safely

For straightforward announcement maintenance, treat the root announcement block as a container:
1. list root block
2. list existing children
3. delete existing children
4. create new children from the desired content

This skill is optimized for **full replacement**, not surgical partial edits.

### 3. Confirm write intent

Updating a live group announcement is an external group-management action. Confirm the target content before running `set` unless the user has already clearly approved it.

## Script usage

### Read metadata

```bash
python3 scripts/update_chat_announcement.py get-meta \
  --chat-id oc_xxx \
  --app-id "$FEISHU_APP_ID" \
  --app-secret "$FEISHU_APP_SECRET"
```

### List root blocks

```bash
python3 scripts/update_chat_announcement.py list-blocks \
  --chat-id oc_xxx \
  --app-id "$FEISHU_APP_ID" \
  --app-secret "$FEISHU_APP_SECRET"
```

### Set from raw text

Rule:
- first non-empty line → heading1
- remaining non-empty lines → paragraph blocks

```bash
python3 scripts/update_chat_announcement.py set \
  --chat-id oc_xxx \
  --content $'📢 群公告标题\n第一段内容\n第二段内容' \
  --app-id "$FEISHU_APP_ID" \
  --app-secret "$FEISHU_APP_SECRET"
```

### Set from file

```bash
python3 scripts/update_chat_announcement.py set \
  --chat-id oc_xxx \
  --file ./announcement.txt \
  --app-id "$FEISHU_APP_ID" \
  --app-secret "$FEISHU_APP_SECRET"
```

## Content model

Current script maps content to docx blocks like this:
- first line → `heading1`
- each later non-empty line → `text` paragraph block

This is intentionally simple and reliable.

## Credentials

Prefer environment variables:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

Or pass:
- `--app-id`
- `--app-secret`

## Failure modes

Common blockers:
- app lacks announcement/docx scopes
- caller is not in the group
- caller lacks group management permission
- malformed block payload

If `set` fails, report the returned code/message exactly and do not claim success.

## Scope of this skill

This skill is intentionally narrow:
- supports docx-style group announcement inspection
- supports full replacement of announcement body
- does not yet implement rich inline styling, mentions, links, or partial block patching

If the user needs rich structured edits, extend the block payloads instead of switching back to the older IM announcement API.
