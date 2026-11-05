---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: eabe8c67ca74e4accd436c53c66dbfd7
    PropagateID: eabe8c67ca74e4accd436c53c66dbfd7
    ReservedCode1: 304402206934470ccb2cf7a05198dec4e90bb437479b121306a11c5c2ed25ada600b69a2022049cfc9fa2a7cc25a3aabcc1ac94e3987d65af8433cdcc30bc3488c472ea2680e
    ReservedCode2: 304602210084e148f271933f8a815519a7e0d58d534e713230ca03eb10482a771579dcd28d022100ea381cbf6096411df3217a4e593bb8b737c56565ecfd125814700dccecad8933
description: GameMaker GML编程开发助手。当用户请求GML代码开发、GameMaker项目辅助、gm_cli工具操作、编写游戏逻辑、调试GML代码或使用GameMaker进行任何开发工作时使用。首次触发时自动安装并加载gm_cli工具。
name: gml-developer
---

# GML Developer

GameMaker GML编程开发技能，自动管理gm_cli工具。

## 核心能力

- GML代码编写与调试
- GameMaker项目结构辅助
- gm_cli工具集成
- 游戏逻辑开发支持

## 首次使用流程

**自动加载gm_cli工具链：**

```python
# 首次触发时自动执行
import subprocess
import os

def ensure_gmcli():
    """确保gm_cli已安装并可用"""
    try:
        result = subprocess.run(['npm', 'list', '-g', '@gamemaker/gm-cli'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            subprocess.run(['npm', 'install', '-g', '@gamemaker/gm-cli'], check=True)
    except FileNotFoundError:
        print("需要安装Node.js和npm")
```

## GML开发工作流

1. **项目初始化**：使用gm_cli创建/打开GameMaker项目
2. **代码开发**：编写GML脚本和对象逻辑
3. **编译测试**：使用gm_cli编译并测试游戏
4. **调试优化**：调试并优化代码性能

## gm_cli常用命令

| 命令 | 功能 |
|------|------|
| `gm-cli init` | 初始化新项目 |
| `gm-cli build` | 编译项目 |
| `gm-cli run` | 运行游戏 |
| `gm-cli check` | 代码检查 |

## 参考资料（交叉验证）

技能包含从GameMaker官方教程提取的9份PDF参考文档，覆盖GML完整知识体系：

| 教程文档 | 内容范围 |
|----------|----------|
| 1类型、变量与标准I_O | 数据类型、变量声明、作用域、宏定义、枚举常量 |
| 2真值、分支与游戏循环 | 布尔值、关系运算符、if/else/switch分支语句 |
| 3for循环、字符串和数组 | for循环、字符串函数（string_char_at等）、数组创建与遍历 |
| 4数据结构 | ds_list、ds_map等数据结构的使用与内存管理 |
| 5函数 | 函数定义、参数传递、返回值、局部变量与封装 |
| 6引用 | 引用类型、按引用传递、variable_clone()复制 |
| 7结构体和对象 | struct定义、constructor构造器、对象资产创建 |
| 8高级类与垃圾回收 | 聚合体、method()绑定、toString、GC垃圾回收机制 |
| 9继承与多态 | 构造函数继承、event_inherited()、回调函数重写、多态实现 |

**使用方式**：当用户提供GML编程问题时，可交叉引用这些资料提供准确的语法示例和最佳实践。

## 文件结构

```
skill-name/
├── SKILL.md
├── _meta.json
├── scripts/
│   ├── init_gmcli.py      # gm_cli初始化脚本
│   └── quick_validate.py   # 验证脚本
└── references/
    └── gml_guide.md       # GML参考文档
```