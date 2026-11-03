---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 94b2993861f57833fc7d2007043edd0b
    PropagateID: 94b2993861f57833fc7d2007043edd0b
    ReservedCode1: 30440220550381588a9fde7dfb42eba364b458bc75593e98688b274e46ac0951f561c6f502202bf474aa45e1bafb27cce5917f58c5fea599a580da29eb2f7257176ad1ac7ea7
    ReservedCode2: 3046022100a9c8351a8e4391ebebda5c53a7d09bdd8a9a4a7cbedcbbd09fdf6dcccffcf648022100e0f5f3eb310eef2c24cab8179e43c96d35d682719df92905d172d5cf7ba0d255
description: 创建新的 Agent Skills。当用户要求"创建技能"、"生成技能"、"我想做一个新技能"、"build a skill"、"create a new skill"时使用。此技能会引导用户完成技能的完整创建流程，包括名称、描述、触发短语、工作流程设计和输出。
name: skill-generator
---

# 技能生成器

自动引导用户创建完整的 Agent Skill 结构。

## 工作流程

### 步骤 1：收集技能信息

使用 GenUI 表单向用户收集以下信息：

**必填信息**：
- **技能名称**（name）：使用连字符格式，如 `my-awesome-skill`
- **技能描述**（description）：清晰描述功能，包含触发短语如 "Use when users ask to..."

**可选信息**：
- **功能详情**：技能的主要功能点
- **触发短语**：更详细的触发场景

### 步骤 2：生成技能 ID

调用 `generate_skill_id` 工具获取唯一的技能标识符。

### 步骤 3：创建技能结构

在 `/workspace/temp-skills/` 目录下创建技能文件夹：

```
<skill-name>/
├── SKILL.md          # 技能定义文件
└── _meta.json        # 元数据文件
```

### 步骤 4：生成 SKILL.md

创建包含正确 frontmatter 的 SKILL.md：

```yaml
---
name: <skill-name>
description: <用户提供的描述，包含触发短语>
---

# 技能标题

<技能详细工作流程描述>
```

### 步骤 5：生成 _meta.json

```json
{
  "id": "<generate_skill_id 返回的 ID>",
  "version": "1.0.0"
}
```

### 步骤 6：路径验证

使用 `path-checker` 子代理验证所有路径和名称仅为英文。

### 步骤 7：输出交付

使用 GenUI 技能卡片格式展示生成的技能：

```xml
<genui-skill-card name="skill-name" desc="skill-description" skill-id="skill-id"></genui-skill-card>
```

## 输出格式

完成创建后，提供：
1. 技能已创建的确认消息
2. GenUI 技能卡片组件
3. 技能文件路径信息

## 目录约束

- **必须**使用 `/workspace/temp-skills/` 作为根目录
- **禁止**在其他位置创建技能文件
