---
name: file-rename-archive
description: 根据文件分类结果（来自 file-classify-tag 技能的 JSON 输出）按国资资料库规范重命名文件并移动到对应的 A~F 类归档子目录。当用户需要批量归档、重命名文件、整理国资资料库、执行文件归档操作时使用。触发短语：归档文件、重命名归档、文件整理入库、执行归档、文件移动归档。
---

# file-rename-archive

接收 `file-classify-tag` 技能的分类结果，按国资资料库规范重命名文件并归档至对应目录。

---

## 输入格式

接受以下两种形式：

1. **JSON 数组**（多文件批量）：Skill 1 输出的 `results` 数组
2. **JSON 单对象**：单文件分类结果

每个对象必须包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `original_path` | string | 原文件完整路径 |
| `category1` | string | 一级分类代码（A~F） |
| `category2` | string | 二级分类代码（如 C01） |
| `category1_name` | string | 一级分类中文名（如 战略规划与改革重组库） |
| `category2_name` | string | 二级分类中文名（如 五年规划） |
| `company` | string | 单位简称（可为空） |
| `year` | string | 四位年份（可为空） |
| `version` | string | 版本标记（可为空，如 正式稿） |
| `subject` | string | 文件核心主题 |

---

## 执行步骤

### Step 1：确认归档根目录

- 若用户在调用时提供了归档根目录参数，直接使用。
- 若未提供，**主动询问用户**：

  > "请提供归档根目录路径（例如：`Z:\国资档案库` 或 `\\192.168.1.100\share\国资档案库`）："

- 将路径保存为 `ARCHIVE_ROOT`。

### Step 2：解析分类结果

- 解析输入的 JSON（数组或单对象均兼容）。
- 若解析失败，提示用户检查输入格式，中止执行。

### Step 3：逐文件处理

对每个分类记录执行以下操作：

#### 3a. 构建目标目录路径

```
一级文件夹名：{category1}类_{category1_name}
二级文件夹名：{category2}_{category2_name}
目标路径：ARCHIVE_ROOT / 一级文件夹名 / 二级文件夹名 /
```

示例：`Z:\国资档案库\C类_战略规划与改革重组库\C01_五年规划\`

若目标目录不存在，自动创建（`os.makedirs(..., exist_ok=True)`）。

#### 3b. 生成新文件名

按命名规范（详见 `references/naming-rules.md`）生成新文件名：

```
格式：YYYYMMDD_单位简称_文件主题_版本标记.扩展名
```

- **日期**：优先用 `year` + 文件修改时间的月日；若 `year` 为空，完全使用文件修改日期。
- **单位简称**：`company` 为空时保留空占位（双下划线）。
- **文件主题**：对 `subject` 执行清洗（去编号前缀、去特殊符号、截断至 15 字）。
- **版本标记**：`version` 为空时省略（同时省略末尾下划线）。

#### 3c. 处理重名冲突

若目标路径已存在同名文件，依次尝试：
`新文件名_1.ext` → `新文件名_2.ext` → ...

#### 3d. 移动文件

使用 `shutil.move(src, dst)` 将原文件移动到目标路径。

- 若路径过长（> 260 字符，Windows），尝试添加 `\\?\` 前缀后重试。
- 若仍失败，记录错误并继续处理下一个文件。

#### 3e. 预留索引更新接口（可选）

归档成功后，若检测到环境变量 `INDEX_UPDATE_URL` 或配置文件中有 `index_update_url`，则向该接口发送如下 JSON 通知：

```json
{
  "action": "archive",
  "original_path": "...",
  "new_path": "...",
  "category1": "...",
  "category2": "..."
}
```

此接口由 Skill 3（检索索引）负责实现，本技能仅预留调用。

### Step 4：汇总结果

所有文件处理完毕后，以 JSON 格式输出归档结果：

```json
{
  "summary": {
    "total": 5,
    "success": 4,
    "failed": 1
  },
  "results": [
    {
      "original_path": "C:/上传/七.五年规划初稿.docx",
      "new_path": "Z:/国资档案库/C类_战略规划与改革重组库/C01_五年规划/20260417_机场集团_十五五发展规划纲要_正式稿.docx",
      "new_filename": "20260417_机场集团_十五五发展规划纲要_正式稿.docx",
      "status": "success",
      "error": null
    },
    {
      "original_path": "C:/上传/附件1：年度报告.pdf",
      "new_path": null,
      "new_filename": null,
      "status": "failed",
      "error": "目标路径不可访问：\\192.168.1.100\share 无法连接"
    }
  ]
}
```

同时以可读的表格或列表形式向用户展示结果摘要。

---

## 执行脚本

可直接调用 `scripts/rename_archive.py` 完成实际文件操作：

```bash
uv run scripts/rename_archive.py \
  --input classification_result.json \
  --archive-root "Z:\国资档案库"
```

脚本支持参数：

| 参数 | 说明 |
|------|------|
| `--input` | 分类结果 JSON 文件路径 |
| `--archive-root` | 归档根目录（优先于环境变量） |
| `--backup-dir` | 可选：备份原文件目录 |
| `--dry-run` | 模拟运行，不实际移动文件 |
| `--index-url` | 可选：索引更新接口 URL |

---

## 注意事项

- 支持 Windows UNC 路径（`\\server\share\...`）和映射盘符（`Z:\...`）。
- 路径超过 260 字符时自动尝试 `\\?\` 前缀（仅 Windows）。
- `subject` 清洗规则详见 `references/naming-rules.md`。
- 本技能通常作为 `file-classify-tag` 的后置步骤调用，可直接传入其输出 JSON。
