---
phase: tracking
created: {date}
last_updated: {date}
current_phase: {current_phase}
current_chapter: {current_chapter}
---

# 项目状态追踪

## 阶段进度
| 阶段 | 状态 | 最后更新 | 备注 |
|------|------|---------|------|
| Phase 1: Project Setup | {status} | {date} | |
| Phase 2: Core Concept + Title | {status} | {date} | |
| Phase 3: World-Building | {status} | {date} | |
| Phase 4: Character Design | {status} | {date} | |
| Phase 5: Plot Architecture | {status} | {date} | |
| Phase 6: Outline + Pacing | {status} | {date} | |
| Phase 7: Chapter Writing | 进度 {n}/{total} | {date} | 当前：第{n}章 |
| Phase 8: State Extraction | {status} | {date} | |

## 会话历史
| 日期 | 阶段 | 完成事项 |
|------|------|---------|
| {date} | {phase} | {what_was_done} |

## 当前工作焦点
- 正在做：{current_task}
- 下一步：{next_task}
- 待解决问题：{open_issues}

## 文件清单
| 文件 | 路径 | 状态 |
|------|------|------|
| 项目配置 | project-config.md | {status} |
| 核心概念+书名 | title-synopsis.md | {status} |
| 世界观 | world.md | {status} |
| 角色档案 | characters/ | {status} |
| 剧情架构 | plot.md | {status} |
| 大纲 | outline.md | {status} |
| 已写章节 | chapters/ | 第1-{n}章 |

## 活跃伏笔摘要
| ID | 内容 | 类型 | 种植章 | 目标回收 | 紧迫度 |
|----|------|------|--------|---------|--------|
| {id} | {description} | {type} | Ch.{n} | Ch.{target} | {urgency} |

## 术语一致性表
<!-- IR-3 P0 必加载。每章新增术语时更新。详见 consistency-system.md Section 2.3。 -->
| 术语 | 定义 | 首次出现 | 备注 |
|------|------|---------|------|
| {term} | {definition} | Ch.{n} | {notes} |

## 关键数字表
<!-- IR-3 P0 必加载。防止数值矛盾。详见 consistency-system.md Section 2.4。 -->
| 数字 | 含义 | 来源章节 | 备注 |
|------|------|---------|------|
| {number} | {meaning} | Ch.{n} | {notes} |

## 角色状态摘要
| 角色 | 位置 | 状态 | 最近变化 |
|------|------|------|---------|
| {name} | {location} | {status} | {recent_change} |

## 章节摘要
| 章节 | 摘要（≤200字符） | 关键变化 |
|------|---------------|---------|
| Ch.001 | {summary} | {key_change} |

<!-- 注意：章节数超过30时，旧的章摘要应归档为卷级摘要。详见 memory-management.md 长篇归档策略。 -->

## 决策记录
<!-- 通过 Proposal 系统确认的重大创意决策。保留最近20条。 -->
| 日期 | 决策主题 | 选择 | 理由 | 影响文件 |
|------|---------|------|------|---------|
| {date} | {topic} | {choice} | {reason} | {files} |

## 散文基线
<!-- 建立 章节：Ch.01 | 建立日期：{date} -->
<!-- 存储 2-3 段理想散文作为后续章节的风格参考。从已写章节中选取最能代表本书风格的段落。 -->

### 量化指标
| 指标 | 基线值 | Ch.02 | Ch.03 | Ch.04 |
|------|--------|-------|-------|-------|
| 平均句长 | {字} | | | |
| 短句占比(≤10字) | {%} | | | |
| 对话比例 | {%} | | | |
| 段落长度CV | {值} | | | |

### 基线段落 1（来源：Ch.XXX）
{ideal_prose_paragraph}

### 基线段落 2（来源：Ch.XXX）
{ideal_prose_paragraph}

### 风格特征摘要
- 句式特点：{feature}
- 节奏特征：{feature}
- 叙述距离：{feature}
- 感官侧重：{feature}
