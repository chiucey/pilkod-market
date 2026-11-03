# Migration Map (jd-clarify -> jd-clarify-new)

## 迁移目标

在不改动旧技能的前提下，将原 `jd-clarify` 的能力映射到 `jd-clarify-new` 主子模块结构，支持灰度切换。

## 段落级映射

| 旧技能内容块 | 新文件位置 | 迁移状态 | 说明 |
|---|---|---|---|
| Frontmatter 与适用场景 | `SKILL.md` | 已完成 | 主入口保留触发说明与导航 |
| 模式识别与冲突处理 | `master_handler.md` | 已完成 | A/B/C/D/E路由与顺序策略已落地 |
| 全局术语与原则 | `config.md` | 已完成 | 统一术语，降低重复 |
| 画像条数与合规约束 | `common/constraints.md` | 已完成 | 作为唯一约束源 |
| 输入字段定义 | `common/input-schema.md` | 已完成 | 岗位/公司/用工关系拆分 |
| 输出顺序与复盘要求 | `common/output-contract.md` | 已完成 | 通用输出契约 |
| 质量自检清单 | `common/quality-checklist.md` | 已完成 | 通用自检 |
| Step1-6主流程（A） | `sub_skills/profile-sop/workflow.md` | 已完成 | 保留流程骨架 |
| A模式模板 | `sub_skills/profile-sop/templates.md` | 已完成 | 提供简版模板 |
| A模式示例 | `sub_skills/profile-sop/examples.md` | 已完成 | 新增技术岗、写实美术、蓝领快招 |
| B模式规则（顾问简版） | `sub_skills/consultant-brief/rules.md` | 已完成 | 压缩与提问规则 |
| B模式模板 | `sub_skills/consultant-brief/templates.md` | 已完成 | 固定输出结构 |
| B模式示例 | `sub_skills/consultant-brief/examples.md` | 已完成 | 新增顾问速览完整样例 |
| C模式规则（JD重构） | `sub_skills/jd-rewrite/rules.md` | 已完成 | 仅保留JD文案重构，不含话术和AI初面 |
| C模式模板 | `sub_skills/jd-rewrite/templates.md` | 已完成 | 固定JD输出结构 |
| C模式示例 | `sub_skills/jd-rewrite/examples.md` | 已完成 | 仅示例JD文案输出 |
| D模式规则（平台筛选与AI初面包） | `sub_skills/screening-pack/rules.md` | 已完成 | 生成筛选要求、候选人关心信息、话术、AI初面 |
| D模式模板 | `sub_skills/screening-pack/templates.md` | 已完成 | 固定平台筛选包输出结构 |
| D模式示例 | `sub_skills/screening-pack/examples.md` | 已完成 | 新增Java后端筛选包样例 |
| E模式规则（简历匹配分析） | `sub_skills/resume-fit/rules.md` | 已完成 | 明确仅输出合适/不合适点，禁止评分 |
| E模式模板 | `sub_skills/resume-fit/templates.md` | 已完成 | 固定双主块输出结构 |
| E模式示例 | `sub_skills/resume-fit/examples.md` | 已完成 | 新增岗位画像对照简历样例 |

## 字段级对照（灰度切换用）

| 旧字段/要求 | 新位置 | 兼容策略 |
|---|---|---|
| Must Have / Good to Have / Red Flags | `common/constraints.md` + 各子模板 | 保持原命名，不改术语 |
| 待确认标注 | `common/input-schema.md` | 缺失即标注，流程不中断 |
| 三层分流（简历/AI/电话） | `profile-sop/workflow.md` | 保持唯一首要环节原则 |
| RPO/HRO主体口径 | `common/constraints.md` + `screening-pack/templates.md` | 输出中强制保留口径块 |
| AI初面 1->2->3 顺序 | `screening-pack/rules.md` | 固定顺序，不允许调换 |
| 顾问问题双区块（技能验证+引导经验） | `consultant-brief/templates.md` | 保持结构不变 |
| 简历匹配输出形式 | `resume-fit/rules.md` + `resume-fit/templates.md` | 仅“合适的地方/不合适的地方”，不评分 |
| 打招呼话术输出 | `screening-pack/templates.md` | 统一由模式D输出 |

## 切换建议

1. 先在内部试运行 `jd-clarify-new` 一周，记录A/B/C/D/E命中准确率。  
2. 对比旧技能输出一致性，重点检查：用工口径、分流唯一性、模式C与模式D边界、AI初面顺序。  
3. 若稳定，再将旧技能入口逐步替换为新技能入口。
