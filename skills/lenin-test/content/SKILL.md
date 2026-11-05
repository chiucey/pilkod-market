---
name: lenin-test
description: |
  Validate a Mavis skill directory against the official SKILL.md writing rules
  (frontmatter, body, forbidden files, length). Use this skill when the user
  asks to "check my skill", "validate skill", "lint SKILL.md", "audit skill",
  or just finished creating/editing a skill and wants a pre-sync self-check.
  Do NOT use for general code review (route to a code-reviewer agent) or for
  writing the skill from scratch (use the skill-creator skill).
---

# Skill Validator

## Inputs to collect
- 技能目录绝对路径（默认扫描 `.skills/<name>/`，未给就问用户）

## Procedure

1. 校验目标目录存在且包含 `SKILL.md`
   原因：缺主文件的话什么都校验不了
2. 解析 frontmatter（YAML 头用 `---` 包裹）
   原因：触发逻辑全靠 frontmatter，格式错就触发不了
3. 跑规则集，规则在 `references/check-rules.md`
   原因：把规则放正文会让 SKILL.md 变长且每次都加载
4. 输出分级报告（✅ pass / ⚠️ warn / ❌ fail）
   原因：让用户一眼看出"必须修"和"建议改"分开
5. 每条问题给出文件路径 + 行号 + 修复建议
   原因：避免用户猜"我该改哪里"

## Output contract

- 控制台输出文本报告，每行一个检查项
- 退出码：`0` 表示无 fail（有 warn 仍返回 0），`1` 表示有 fail
- 报告末尾一行汇总：`X passed, Y warnings, Z failed`

## Failure handling

- 目录不存在 → 报错并退出码 2，不静默继续
- `SKILL.md` 缺失 → 报错并提示"用 skill-creator 创建一个"
- frontmatter 解析失败 → 输出原始内容片段（前后各 5 行）+ 报错位置
- 校验脚本本身抛异常 → 退出码 3，让上游 CI 看到

## Examples

Input: `node scripts/validate.mjs /workspace/.skills/lenin-test`

Output:
```
✅ name 与目录名匹配（lenin-test）
✅ description 含触发短语（"check my skill" / "lint SKILL.md"）
✅ 必填章节齐全：Procedure / Output contract / Failure handling
⚠️ SKILL.md 行数 87，< 500 上限（建议保留更多 examples）
✅ 无禁止文件（README.md / CHANGELOG.md / .env）
📊 4 passed, 1 warning, 0 failed
```
