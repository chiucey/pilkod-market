# Construct3 C3P项目自动编辑器

专为Claw智能体打造的全自动Construct3 .c3p项目文件编辑器，实现纯编程方式解析、编辑、重构.c3p项目文件。

## 核心功能

| 功能 | 说明 |
|-----|------|
| **C3P解析器** | 识别.c3p为加密ZIP，自动解压/打包 |
| **XML编辑器** | 程序化修改项目配置 |
| **资源替换器** | 批量替换图片/音效/图标 |
| **事件表编辑器** | 修改游戏逻辑参数 |

## 文件目录结构

```
c3p-project-auto-editor/
├── SKILL.md                          # 技能主定义
├── _meta.json                        # 元数据
├── skill.json                        # 插件配置
├── README.md                         # 使用说明
├── scripts/
│   ├── main.py                       # 主协调脚本
│   ├── c3p_parser.py                  # C3P解析器
│   ├── xml_editor.py                  # XML编辑器
│   ├── resource_manager.py            # 资源管理器
│   ├── event_editor.py                # 事件表编辑器
│   └── config_loader.py              # 配置加载器
└── references/
    ├── c3p_format.md                  # C3P格式详解
    ├── xml_parameters.md               # XML参数表
    ├── resource_replacement.md        # 资源替换指南
    └── event_modification.md          # 事件修改指南
```

## Claw部署命令

```bash
# Git克隆
git clone https://github.com/your-repo/c3p-project-auto-editor.git ~/.claw/skills/c3p-project-auto-editor

# 手动复制
cp -r /path/to/c3p-project-auto-editor ~/.claw/skills/

# 重启Claw
claw restart
```

## 使用指令

### 基础指令

| 指令 | 功能 |
|-----|------|
| `/edit-c3p template.c3p output.c3p --config config.json` | 编辑C3P项目 |
| `/generate-config` | 生成配置模板 |
| `/parse-c3p template.c3p` | 解析C3P结构 |

### 编程调用

```python
from main import C3PAutoEditor

editor = C3PAutoEditor()
editor.load_config('config.json')
result = editor.edit('template.c3p', 'output.c3p')
print(result.success)
```

## 配置文件格式

```json
{
  "basic_info": {
    "game_name": "My Game",
    "version": "1.0.0"
  },
  "assets": {
    "app_icon": "/path/to/icon.png",
    "background": "/path/to/bg.png"
  },
  "game_balance": {
    "click_reward": 10,
    "difficulty": 1.5
  },
  "advertising": {
    "tiktok_app_id": "your_app_id"
  }
}
```

## 完整使用示例

```bash
# 1. 生成配置模板
python scripts/config_loader.py --template config.json

# 2. 编辑配置文件
vim config.json

# 3. 执行编辑
python scripts/main.py template.c3p output.c3p --config config.json

# 4. 查看修改日志
cat output.c3p.log.json
```

---

**版本**: 1.0.0
**作者**: MiniMax Agent
**更新**: 2026-04-09
