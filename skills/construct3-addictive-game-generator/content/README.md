# Construct3高成瘾性游戏生成插件

专为Claw智能体打造的全自动Construct3高质量成瘾游戏生成引擎，让智能体自主完成从游戏策划、Construct3制作、调试优化到成品导出的完整工作流。

## 插件概述

### 核心能力

| 功能 | 说明 |
|-----|------|
| **游戏智能策划** | 自动定位商业化爆款品类，植入成瘾机制，生成完整策划方案 |
| **Construct3制作** | 自动创建项目、搭建场景、编写事件逻辑、调试优化 |
| **成品自动导出** | 生成可直接发布的HTML5游戏包 |

### 支持游戏品类

- 解压闯关类（Flappy Bird类型）
- 合成养成类（2048类型）
- 敏捷挑战类（俄罗斯方块类型）
- 趣味竞技类
- 放置收集类

## 文件目录结构

```
construct3-addictive-game-generator/
├── SKILL.md                          # 插件主定义文件
├── _meta.json                        # 元数据配置
├── skill.json                        # 插件配置文件
├── README.md                         # 使用说明文档
├── scripts/
│   ├── game_generator.py             # 主执行脚本（游戏生成引擎）
│   ├── event_logic_generator.py       # 事件逻辑生成器
│   ├── game_planner.py               # 游戏策划生成器
│   └── export_config.py              # 导出配置脚本
├── references/
│   ├── event_system_guide.md         # Construct3事件系统指南
│   ├── addiction_design_manual.md    # 高成瘾性游戏设计手册
│   ├── export_guide.md               # 导出配置指南
│   └── quality_checklist.md          # 质量检验清单
└── templates/                        # 游戏模板
```

## Claw智能体部署命令

### 方法1：Git克隆安装
```bash
# 克隆插件仓库
git clone https://github.com/your-repo/construct3-addictive-game-generator.git ~/.claw/skills/construct3-addictive-game-generator

# 重启Claw使插件生效
claw restart
```

### 方法2：手动复制安装
```bash
# 复制插件目录到Claw skills目录
cp -r /path/to/construct3-addictive-game-generator ~/.claw/skills/

# 重启Claw
claw restart
```

## 插件调用指令

### 基础指令

| 指令 | 功能 |
|-----|------|
| `/generate-game flappy` | 生成Flappy Bird类跑酷游戏 |
| `/generate-game 2048` | 生成2048类合成游戏 |
| `/generate-game candy` | 生成Candy Crush类消除游戏 |
| `/generate-game tetris` | 生成俄罗斯方块类游戏 |
| `/generate-game idle` | 生成放置挂机类游戏 |
| `/plan-game` | 生成游戏策划方案 |
| `/events [游戏类型]` | 生成事件逻辑代码 |
| `/export` | 导出游戏成品 |

### 进阶指令

| 指令 | 功能 |
|-----|------|
| `/generate-game custom --name "我的游戏" --category "闯关"` | 自定义参数生成游戏 |
| `/generate-game --add-reward --add-achievement` | 添加奖励和成就系统 |
| `/plan-game --category "合成" --level-count 100` | 自定义策划方案 |

## 使用示例

### 示例1：生成Flappy Bird游戏

```
用户: /generate-game flappy

Claw响应:
正在为您生成Flappy Bird类跑酷游戏...

✓ 游戏品类定位：敏捷挑战
✓ 成瘾机制植入：即时反馈、排行榜、高分挑战
✓ 场景配置：Menu、Game、GameOver
✓ 素材配置：Bird、Pipe、Background
✓ 事件逻辑：跳跃、重力、碰撞、计分
✓ 游戏策划方案已生成

游戏生成完成！
配置文件路径: /tmp/generated_games/flappy_game/
```

### 示例2：生成游戏策划方案

```
用户: /plan-game --category "合成" --level-count 50

Claw响应:
正在为您生成合成游戏策划方案...

✓ 游戏品类：合成养成
✓ 核心机制：滑动操作、相同合成、数值积累
✓ 成瘾循环设计完成
✓ 50个关卡设计已完成
✓ 奖励系统配置完成

策划方案已生成，保存在 references/design_doc.md
```

### 示例3：导出游戏成品

```
用户: /export --format html5 --optimize

Claw响应:
正在导出游戏...

✓ 项目配置完成
✓ 资源优化完成（包体：2.3MB）
✓ HTML5包生成完成
✓ 发布说明已生成

导出完成！
游戏包路径: /tmp/games/export/game.html5
```

## 游戏模板库

### 1. Flappy Bird模板
- 核心机制：单指操作+即时反馈+无限重复
- 成瘾设计：排行榜+好友对战
- 预计生成时间：5分钟

### 2. 2048模板
- 核心机制：滑动合并+数值积累
- 成瘾设计：全合成成就+排名竞争
- 预计生成时间：8分钟

### 3. Candy Crush模板
- 核心机制：交换匹配+连锁反应
- 成瘾设计：关卡进度+星数评价
- 预计生成时间：10分钟

### 4. 俄罗斯方块模板
- 核心机制：空间布局+速度挑战
- 成瘾设计：无尽模式+成就收集
- 预计生成时间：6分钟

### 5. 放置挂机模板
- 核心机制：点击收集+升级强化
- 成瘾设计：离线收益+长期目标
- 预计生成时间：5分钟

## 输出产物

### 必选产出
- Construct3项目配置文件（JSON）
- 事件逻辑表（可导入Construct3）
- 游戏策划文档（Markdown）

### 可选产出
- 完整游戏资源包
- 发布说明文档
- 广告变现接入指南

## 性能指标

| 指标 | 目标值 | 说明 |
|-----|-------|------|
| 生成速度 | < 5分钟 | 从指令到配置完成 |
| 包体大小 | < 5MB | 优化后游戏包 |
| 运行帧率 | 稳定60FPS | 游戏流畅度 |
| 加载时间 | < 3秒 | 首屏加载速度 |

## 注意事项

1. **素材准备**：生成的代码需要配合实际素材使用
2. **广告变现**：游戏导出后可接入TikTok/FB广告变现
3. **平台适配**：导出前请确认目标平台要求
4. **版权合规**：使用原创素材，避免侵权

## 常见问题

### Q1：生成的游戏无法运行？
- 检查Construct3版本是否最新
- 确认素材是否正确导入
- 查看控制台错误信息

### Q2：如何修改游戏难度？
- 编辑事件逻辑中的数值参数
- 调整关卡配置中的难度曲线

### Q3：如何添加新功能？
- 在game_generator.py中添加新模板
- 或使用自定义参数生成

## 技术支持

- 文档：references/ 目录
- 代码：scripts/ 目录
- 模板：templates/ 目录

---

**版本**: 1.0.0
**作者**: MiniMax Agent
**更新**: 2026-04-09
