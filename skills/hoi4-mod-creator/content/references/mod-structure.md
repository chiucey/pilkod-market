---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 170fc3f3c17c9cf11237ddf03918fd0a
    PropagateID: 170fc3f3c17c9cf11237ddf03918fd0a
    ReservedCode1: 30440220722acb1605af7b38deb2e64c88e668b38f926a8f3d0132aca7f5041973bb174f0220416de9151e64b06b731eb0afa48127e88ded0745a20593fed80b1e4a9cf25f58
    ReservedCode2: 3044022063e90b46f62c5a0ab0cddf004216eca2dba24550a20caa7f9e8d03532f1561e202203a764189f894233b98fa5456a7ca64a957c30b158d982b8645520200202112cb
---

# HOI4 MOD 结构与元数据

## 目录结构标准

一个完整的 MOD 通常包含以下目录（按重要性排序）：

```
my-mod/
├── descriptor.mod          # MOD 元数据（必需）
├── common/                 # 游戏机制定义
├── events/                 # 事件脚本
├── gfx/                    # 图形资源
├── history/                # 历史初始设定
├── interface/              # UI 定义
├── localisation/           # 本地化文本
├── map/                    # 地图数据（可选）
├── music/                  # 音乐（可选）
├── portraits/              # 肖像（可选）
├── sound/                  # 音效（可选）
└── ...
```

## descriptor.mod

必需文件，定义 MOD 基本信息：

```
name="MOD 显示名称"
version="1.0"
tags={
    "Alternative History"
    "Historical"
    "Events"
    "Balance"
    "Graphics"
    "Gameplay"
    "National Focuses"
    "Technologies"
    "Military"
    "Map"
    "Translation"
    "Fixes"
    "Ideologies"
}
supported_version="1.18.*"
replace_path="history/states"
replace_path="common/national_focus"
```

### 关键字段

| 字段 | 说明 |
|------|------|
| `name` | 显示名称 |
| `version` | MOD 版本 |
| `tags` | 创意工坊标签 |
| `supported_version` | 支持的游戏版本，如 `1.18.*` |
| `replace_path` | 覆盖原版目录路径，可多行 |
| `remote_file_id` | 创意工坊 ID（自动填充）|
| `path` | 开发路径（仅本地开发时使用）|
| `picture` | 缩略图文件名 |

## 文件覆盖机制

HOI4 使用两种加载策略：

### 1. 合并加载（Merge）
多数 `common/` 子目录支持合并：同名文件内条目合并，不同文件共存。
适用目录：`national_focus/`, `ideas/`, `events/`, `decisions/`, `technologies/`, `scripted_effects/`, `scripted_triggers/` 等。

### 2. 完全替换（Replace）
使用 `replace_path = "xxx"` 声明后，该目录下原版文件完全被 MOD 替代。
常用于：`map/`, `history/countries/`, `history/states/`, `history/units/`, `gfx/flags/`, `gfx/loadingscreens/`。

### 3. 同名覆盖（Override）
`gfx/` 下的 `.gfx` 和 `.gui` 文件、interface/ 下的文件：MOD 中同名文件完全覆盖原版。

## 开发路径配置

本地开发时，在 `D:\Documents\Paradox Interactive\Hearts of Iron IV\mod\` 下创建：
- MOD 文件夹（实际文件）
- 同名 `.mod` 文件（指向 descriptor.mod）

示例 `.mod` 文件：
```
name="我的MOD"
supported_version="1.18.*"
path="mod/my-mod"
```

或使用绝对路径：
```
path="D:/Documents/Paradox Interactive/Hearts of Iron IV/mod/my-mod"
```

## 命名规范

- 国家标签：3 位大写字母（GER, SOV, USA, CHI, JAP）
- 动态国家：D01 ~ D75
- 省份 ID：1 ~ 9999
- 文件名建议加 MOD 前缀避免冲突，如 `my_mod_ger_focus.txt`
- 本地化键：使用小写+下划线，如 `my_mod_event.1.t`
