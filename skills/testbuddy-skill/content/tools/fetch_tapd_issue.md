# fetch_tapd_issue

从 TAPD 获取需求内容及关联需求。

## 使用方式

**重要**：脚本位于 skill 根目录的 `scripts/` 子目录下，不是在 `tools/` 目录下。

```bash
# 获取单个需求并保存
python <skill_root>/scripts/fetch_tapd_issue.py --issue-id <需求ID> --save

# 获取需求及其关联需求并保存
python <skill_root>/scripts/fetch_tapd_issue.py --issue-id <需求ID> --with-linked --save

# 输出为 Markdown 格式并保存
python <skill_root>/scripts/fetch_tapd_issue.py --issue-id <需求ID> --output markdown --save

# 输出为 JSON 格式并保存
python <skill_root>/scripts/fetch_tapd_issue.py --issue-id <需求ID> --output json --save
```

**参数说明**：
- `<skill_root>`：skill 的根目录绝对路径（即包含 `scripts/`、`tools/`、`generators/` 等子目录的目录）
- `<需求ID>`：TAPD需求ID，如 `1167410840001329364`

**路径示例**：
```
正确的路径：{skill根目录}/scripts/fetch_tapd_issue.py
错误的路径：tools/scripts/fetch_tapd_issue.py  ❌
```

**执行示例**：
```bash
# 假设 skill 根目录为 /path/to/testbuddy-skill
python /path/to/testbuddy-skill/scripts/fetch_tapd_issue.py --issue-id 1167410840001329364 --save --output markdown
```

**注意**：
- 执行脚本前**不要切换目录（不要 cd）**，确保在工作区根目录执行
- **建议始终使用 `--save` 参数**，将需求保存到文件，便于后续引用

---

## 配置方式

### 配置文件位置

配置信息存储在 `.testbuddy/env/session.json` 文件中：

```json
{
  "token": "用户token",
  "knowledge_uids": ["知识库UID"],
  "tapd": {
    "base_url": "https://www.tapd.cn",
    "cookie": "your_cookie_string_here",
    "workspace_id": "12345678"
  }
}
```

### 配置字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `base_url` | ❌ | TAPD 地址，默认 `https://www.tapd.cn` |
| `cookie` | ✅ | 通过浏览器抓包获取的 Cookie |
| `workspace_id` | ✅ | TAPD 工作空间 ID |

---

## 目录结构说明

```
testbuddy-skill/                  ← skill 根目录 (<skill_root>)
├── scripts/                      ← 脚本目录
│   ├── fetch_tapd_issue.py       ← TAPD获取脚本
│   ├── select_workflow.py        ← 工作流选择脚本
│   └── ...
├── tools/                        ← 工具文档目录
│   ├── fetch_tapd_issue.md       ← 本文档
│   └── ...
└── .testbuddy/
    └── md/                       ← 需求保存目录
        └── STORY-*.md            ← 保存的需求文件
```

---

## 注意事项

1. **路径不要混淆**：脚本在 `scripts/` 目录下，不在 `tools/` 目录下
2. **使用绝对路径**：建议使用 skill 根目录的绝对路径
3. **工作目录**：可以在任意目录执行，脚本会自动定位
