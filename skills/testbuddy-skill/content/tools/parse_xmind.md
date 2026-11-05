# parse_xmind

解析 XMind 文件为测试节点格式，保持内容完整。

## 使用方式

**重要**：脚本位于 skill 根目录的 `scripts/` 子目录下，不是在 `tools/` 目录下。

```bash
# 输出到文件（推荐）
python <skill_root>/scripts/parse_xmind.py <xmind_file> --output-file <输出文件路径>

# 输出为 YAML 格式
python <skill_root>/scripts/parse_xmind.py <xmind_file> --output yaml --output-file <输出文件路径>

# 保留所有额外信息
python <skill_root>/scripts/parse_xmind.py <xmind_file> --keep-extra --output-file <输出文件路径>
```

**参数说明**：
- `<skill_root>`：skill 的根目录绝对路径（即包含 `scripts/`、`tools/`、`generators/` 等子目录的目录）
- `<xmind_file>`：XMind 文件的绝对路径
- `--output`：输出格式（json/yaml），默认为json
- `--output-file`：输出文件路径（**必需**，避免编码问题）
- `--keep-extra`：保留所有额外信息

**路径示例**：
```
正确的路径：{skill根目录}/scripts/parse_xmind.py
错误的路径：tools/scripts/parse_xmind.py  ❌
```

**执行示例**：
```bash
# 假设 skill 根目录为 /path/to/testbuddy-skill
python /path/to/testbuddy-skill/scripts/parse_xmind.py "C:\Users\XXX\权限管理.xmind" --output-file ".testbuddy/md/xmind_output.json"
```

**注意**：
- 执行脚本前**不要切换目录（不要 cd）**，确保在工作区根目录执行
- **必须使用 `--output-file` 参数**，避免PowerShell编码问题。

---

## 目录结构说明

```
testbuddy-skill/              ← skill 根目录 (<skill_root>)
├── scripts/                  ← 脚本目录
│   ├── parse_xmind.py        ← XMind解析脚本
│   ├── parse_excel.py        ← Excel解析脚本
│   └── ...
├── tools/                    ← 工具文档目录
│   ├── parse_xmind.md        ← 本文档
│   └── ...
└── .testbuddy/
    └── md/                   ← 解析结果保存目录
        └── xmind_*.json      ← 保存的解析结果
```

---

## 注意事项

1. **路径不要混淆**：脚本在 `scripts/` 目录下，不在 `tools/` 目录下
2. **使用绝对路径**：建议使用 skill 根目录的绝对路径
3. **工作目录**：可以在任意目录执行，脚本会自动定位
