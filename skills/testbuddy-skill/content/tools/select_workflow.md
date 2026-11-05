# 工作流选择工具 (select_workflow)

## 工具简介
根据关键词从 `.codebuddy/rules` 目录下智能匹配以"工作流"结尾的文件，并返回工作流文件路径。

## 使用方法

**重要**：脚本位于 skill 根目录的 `scripts/` 子目录下，不是在 `tools/` 目录下。

```bash
python3 <skill_root>/scripts/select_workflow.py <keyword>
```

**参数说明**：
- `<skill_root>`：skill 的根目录绝对路径（即包含 `scripts/`、`tools/`、`generators/` 等子目录的目录）
- `<keyword>`：匹配关键词，如"框架生成"、"用例生成"、"测试点生成"

**路径示例**：
```
正确的路径：{skill根目录}/scripts/select_workflow.py
错误的路径：tools/scripts/select_workflow.py  ❌
```

**执行示例**：
```bash
# 假设 skill 根目录为 /path/to/testbuddy-skill
python3 /path/to/testbuddy-skill/scripts/select_workflow.py "测试点生成"
```

## 输出格式

JSON 格式：
```json
{
  "path": "workflows/testpoint-generation.md"
}
```

- 匹配成功：`path` 为工作流文件路径（相对于 skill 根目录）
- 匹配失败：`path` 为空字符串

## 目录结构说明

```
testbuddy-skill/              ← skill 根目录 (<skill_root>)
├── scripts/                  ← 脚本目录
│   ├── select_workflow.py    ← 工作流选择脚本
│   ├── select_rule.py        ← 规则选择脚本
│   └── ...
├── tools/                    ← 工具文档目录
│   ├── select_workflow.md    ← 本文档
│   └── ...
├── workflows/                ← 工作流目录
│   └── ...
└── generators/               ← 生成器目录
    └── ...
```

## 注意事项

1. **路径不要混淆**：脚本在 `scripts/` 目录下，不在 `tools/` 目录下
2. **使用绝对路径**：建议使用 skill 根目录的绝对路径
3. **工作目录**：可以在任意目录执行，脚本会自动定位
