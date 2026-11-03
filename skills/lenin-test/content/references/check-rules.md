# Skill 检查规则集

> 本文件是 `scripts/validate.mjs` 的规则来源。每个规则有 ID、严重级别、判定逻辑和修复建议。校验脚本按此表实现。

## 规则分级

| 级别 | 含义 | 退出码影响 |
|------|------|------------|
| ❌ fail | 违反硬约束，skill 不可用 | 退出码 1 |
| ⚠️ warn | 不符合最佳实践但能用 | 不影响退出码 |
| ✅ pass | 通过 | — |

## 规则列表

### R001 — 目录存在 `SKILL.md` [fail]
- 判定：目标目录含 `SKILL.md` 文件
- 修复：用 `skill-creator` 起草一份

### R002 — frontmatter 以 `---` 起止 [fail]
- 判定：文件前 3 行内出现 `---`，且在第 1-30 行内出现第二个 `---`
- 修复：在文件最前面加 `---` 包裹的 YAML 头

### R003 — `name` 字段必填且 kebab-case [fail]
- 判定：frontmatter 解析出 `name`，且匹配 `^[a-z0-9][a-z0-9-]{0,63}$`
- 修复：改名到 kebab-case

### R004 — `name` 与目录名一致 [fail]
- 判定：`name` 字段 === 目录 basename
- 修复：改 `name` 或改目录名

### R005 — `description` 必填 [fail]
- 判定：frontmatter 解析出 `description` 且长度 ≥ 20 字符
- 修复：参考 `skill-creator/references/description-rubric.md` 写 4 要素

### R006 — `description` 含触发短语 [warn]
- 判定：含 "use" / "load" / "when" / "trigger" / "适用于" / "触发" 等关键词
- 修复：在 description 末尾加 "Use this skill when..." 一句

### R007 — `description` 含 near miss 提示 [warn]
- 判定：含 "do not" / "不要" / "not use" / "avoid" 等
- 修复：显式列相邻 skill / 场景

### R008 — 必填章节齐全 [fail]
- 判定：正文含 `## Procedure`、`## Output contract`、`## Failure handling`
  - 任一缺失 → fail
- 修复：从 `skill-creator/references/skill-template.md` 抄结构

### R009 — 正文行数 ≤ 500 [warn]
- 判定：`## Procedure` 之后到文件末尾的行数 ≤ 500
- 修复：把详细参考拆到 `references/<topic>.md`

### R010 — 无禁止文件 [fail]
- 判定：目录内不出现 `README.md` / `CHANGELOG.md` / `INSTALLATION.md` / `install.sh` / `.env` / `.env.example` / `requirements.txt`
- 修复：删除这些文件

### R011 — `references/` 引用解析 [warn]
- 判定：正文中 `references/<file>.md` 的链接都对应真实文件
- 修复：创建缺失的引用文件或修正链接

### R012 — 无 `When to use this skill` 章节 [warn]
- 判定：正文不含此标题（触发条件应在 frontmatter）
- 修复：删章节，把要点并入 `description`

## 校验脚本输出格式

每条规则一行：
```
[LEVEL] R<NNN> <message>（<file>:<line>，如适用）
```

末尾汇总：
```
📊 X passed, Y warnings, Z failed
```
