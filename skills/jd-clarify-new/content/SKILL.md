---
name: jd-clarify-new
description: 基于RPO/HRO招聘场景执行JD澄清与筛选SOP。通过主路由识别用户意图并分发到岗位画像与筛选SOP、顾问精简画像、移动端JD重构、平台筛选与AI初面包、简历匹配分析五个子技能。用于用户提到岗位画像、招聘需求澄清、筛选标准、顾问简版画像、JD优化、打招呼话术、AI初面、简历匹配度分析等场景。
---

# JD Clarify New

## 使用说明

这是一个单技能多子模块结构：

1. 主入口负责意图识别与路由，不直接输出长内容。
2. 子模块负责具体执行与输出。
3. 公共规则统一从 `common/` 加载，避免重复定义。

## 执行顺序

1. 读取 `master_handler.md` 做意图识别。
2. 读取 `common/input-schema.md` 做信息完整性检查。
3. 读取 `common/constraints.md` 与 `common/output-contract.md`。
4. 分发到对应子模块执行。
5. 输出前执行 `common/quality-checklist.md` 自检。

## 路由目标

- `sub_skills/profile-sop/`：模式A，岗位画像与筛选SOP（默认）
- `sub_skills/consultant-brief/`：模式B，顾问精简画像与顾问问题
- `sub_skills/jd-rewrite/`：模式C，仅移动端JD文案重构
- `sub_skills/screening-pack/`：模式D，平台筛选与AI初面包（筛选要求 + 候选人关心信息 + 打招呼话术 + AI初面）
- `sub_skills/resume-fit/`：模式E，简历匹配分析（不评分，仅合适/不合适；合适时可推荐语）

## 文件导航

- 主路由：`master_handler.md`
- 全局配置：`config.md`
- 公共规则：`common/`
- 子技能实现：`sub_skills/`
- 版本记录：`changelog.md`
