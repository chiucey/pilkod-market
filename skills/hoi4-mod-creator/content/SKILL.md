---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f53bea825d33c0db6bb837b8e7c64526
    PropagateID: f53bea825d33c0db6bb837b8e7c64526
    ReservedCode1: 304402202b850e3e36405a27915cff88fa7ee084389418a151811906da45dcd5e87aa27d022012eb7082edd3e5f33e8f938291a5040c571ce68cbef3ceb14304a6fa378c0e48
    ReservedCode2: 3044022041af50dd6407d33bf6e97b0c45b424267b906605624b07b4d2d4bf0e6e85b59b02206b2b29519604b8dea6a1b811a0778a1db1eac45890f8f41da6dba0f44c475836
description: 创建 Hearts of Iron IV (HOI4) MOD 的全方位技能。用于当用户要求创建 MOD、设计国策、编写事件、定义科技/装备、修改地图、设置本地化，或任何涉及 HOI4 MOD 制作的任务。
name: hoi4-mod-creator
---

# HOI4 MOD 制作技能

本技能帮助用户创建、调试和优化 Hearts of Iron IV MOD。

## 核心能力

- **MOD 基础结构**：创建标准目录结构和 descriptor.mod
- **国家与政治**：定义国家、意识形态、领袖角色
- **国策树 (National Focus)**：设计国策树和持续性国策
- **科技与装备**：定义科技树和装备类型
- **事件系统**：编写事件链、新闻事件、自动触发事件
- **GFX/界面**：定义精灵、GUI 窗口、自定义 UI
- **地图编辑**：编辑省份、地形、战略区域、补给区
- **历史初始设定**：设置国家、军队、建筑初始状态
- **本地化**：创建多语言本地化文件
- **AI 配置**：编写 AI 战略和编制模板

## 工作流程

### 1. 需求确认

确认用户需求：
- 新 MOD 还是已有 MOD 扩展？
- 需要哪些核心系统（国策/事件/科技/地图）？
- 目标国家/时代/主题？

### 2. 结构创建

创建标准 MOD 目录结构：
```
my-mod/
├── descriptor.mod
├── common/
│   ├── countries/
│   ├── national_focus/
│   ├── ideas/
│   ├── technologies/
│   ├── scripted_effects/
│   ├── scripted_triggers/
│   ├── on_actions/
│   └── decisions/
├── events/
├── gfx/interface/
├── history/
│   ├── countries/
│   ├── states/
│   └── units/
├── localisation/
│   ├── english/
│   └── simp_chinese/
└── map/
    ├── strategicregions/
    └── supplyareas/
```

### 3. 实现各系统

根据用户需求实现对应系统，参考 `references/` 中的详细指南。

### 4. 验证与测试

- 检查文件覆盖机制是否正确
- 验证本地化键是否完整
- 确保 descriptor.mod 配置正确

## 关键文件参考

| 指南 | 内容 |
|------|------|
| `common-guide.md` | common/ 目录详解 |
| `events-guide.md` | 事件脚本语法 |
| `gfx-interface-guide.md` | GFX 和 UI 定义 |
| `history-map-guide.md` | 历史设定和地图文件 |
| `localisation-guide.md` | 本地化格式 |
| `mod-structure.md` | MOD 元数据和结构 |

## 常见问题

- 事件/国策不显示？检查本地化键是否定义
- MOD 不加载？检查 descriptor.mod 的 `supported_version`
- 覆盖不生效？确认 `replace_path` 声明或使用正确文件名
- 地图问题？清除 `map/cache/` 缓存
