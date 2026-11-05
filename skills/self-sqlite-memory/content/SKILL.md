---
name: self-sqlite-memory
description: SQLite 三库持久化记忆系统（记忆/知识/物品）。**唯一指定的记忆读写渠道**，所有记忆、知识、物品数据必须通过此 Skill 读写，不使用 memory_search/memory_get 等平台内置工具。
---

# Self-SQLite Memory — 三库架构

> ⚠️ **Exclusivity 规则**
> - ✅ 只使用 `memory_store.py` 读写所有数据
> - ❌ 不使用 `memory_search` / `memory_get` / MEMORY.md
> - 所有数据操作统一走本 Skill

## 三库架构

```
self-sqlite-memory/
├── memory.db      ← 记忆库（个人偏好/上下文/决定）
├── knowledge.db  ← 知识库（客观事实/实体关系/有来源）
└── items.db      ← 物品库（家庭资产管理，含使用人）
```

## 记忆库 (memory.db)

存**你自己**的东西——偏好、习惯、上下文、重要决定。

| 操作 | 命令 |
|------|------|
| 添加记忆 | `mem add <内容> --category <分类> --tags <标签>` |
| 搜索记忆 | `mem search <关键词>` |
| 列出记忆 | `mem list --category --limit <数量>` |
| 统计 | `mem stats` |
| 记录进化（纠正） | `mem evolve <主题> <纠正前> <纠正后> <触发> <教训>` |

**分类**：general / preference / context / decision / habit / session_summary / learned

---

## 知识库 (knowledge.db)

存**客观事实**——有来源、可验证、可持续引用。

| 操作 | 命令 |
|------|------|
| 添加知识 | `kg add <主体> <类型> <描述> --property <属性> --value <值> --source <来源>` |
| 搜索知识 | `kg search <关键词>` |
| 添加关系 | `kg rel <实体A> <关系> <实体B> --source <来源>` |
| 查关系 | `kg rels <实体名>` |
| 统计 | `kg stats` |

**实体类型**：timer / protocol / company / person / concept / band / equipment / other

---

## 物品库 (items.db)

存**家庭所有实体物品**，支持多使用人。

| 操作 | 命令 |
|------|------|
| 添加物品 | `item add <名称> <类别> --owner <使用人> --brand <品牌> --model <型号> --serial <序列号> --value <估值> --location <位置> --condition <状态>` |
| 搜索物品 | `item search <关键词> --owner <使用人> --category <类别>` |
| 列出物品 | `item list --owner <使用人> --category <类别> --limit <数量>` |
| 查看物品详情 | `item get <id>` |
| 更新物品 | `item update <id> --owner <使用人> --value <估值> --location <位置> --condition <状态>` |
| 删除物品 | `item delete <id>` |
| 统计 | `item stats` |

**使用人字段**：`owner` — 记录物品归属谁（如：kirk / 妈妈 / 全局）
**物品类别**：电子产品 / 家具 / 证件 / 文件 / 工具 / 家用电器 / 服装 / 食品药品 / 收藏品 / 其他

---

## 使用示例

```bash
# 记忆
python3 memory_store.py mem add "kirk 偏好安静环境" --category preference --tags kirk,工作
python3 memory_store.py mem search 工作

# 知识
python3 memory_store.py kg add T310 timer "T310定时器在UE检测到物理层问题后启动" --property 章节 --value 5.3.10 --source "TS 36.331"
python3 memory_store.py kg rel T310 触发 RLF --source "TS 36.331 §5.3.10"
python3 memory_store.py kg rel RLF 导致 切换失败

# 物品
python3 memory_store.py item add "MacBook Pro 16寸" 电子产品 --owner kirk --brand Apple --model "MacBook Pro 16 M3 Max" --value 28000 --location 书房 --condition 良好
python3 memory_store.py item add "戴森吸尘器" 家用电器 --owner 全局 --brand 戴森 --value 4000 --location 客厅
python3 memory_store.py item list --owner kirk
python3 memory_store.py item update 2 --owner 全局 --location 储藏室
python3 memory_store.py item stats
```

## 执行确认规则

- ✅ 读取/搜索/查询 → 无需确认，直接执行
- ✅ 简单回答 → 无需确认
- ⏰ 定时任务（cron）→ 自动执行
- ⚠️ 以下**必须先确认**：
  - 添加/修改/删除数据
  - 删除文件
  - 发送外部消息
  - 修改配置
