# Construct3事件系统完全指南

## 事件系统概述

Construct3的事件系统（Event Sheet）采用可视化编程方式，无需编写代码即可实现复杂游戏逻辑。

### 事件结构

```
+-- 事件表
|   +-- 事件组（可选）
|   |   +-- 事件（Event）
|   |   |   +-- 条件（Conditions）
|   |   |   |   +-- 条件1
|   |   |   |   +-- 条件2
|   |   |   +-- 动作（Actions）
|   |   |   |   +-- 动作1
|   |   |   |   +-- 动作2
```

### 执行顺序

1. 从上到下检查事件条件
2. 所有条件满足时执行动作
3. 下一帧重复此过程

---

## 常用条件详解

### 键盘/输入条件

| 条件 | 说明 | 示例 |
|-----|------|------|
| On key pressed | 键被按下（仅触发一次） | On Space pressed |
| Is key down | 键被按住（持续触发） | While D is down |
| On key released | 键释放 | On Space released |

### 触摸/鼠标条件

| 条件 | 说明 | 示例 |
|-----|------|------|
| On tap gesture | 点击手势 | On Tap on Button |
| On swipe gesture | 滑动手势 | On Swipe Left |
| On touched object | 触摸对象 | On Touched Sprite |
| Cursor is over | 光标悬停 | Cursor is over Button |

### 对象条件

| 条件 | 说明 | 示例 |
|-----|------|------|
| Is visible | 对象可见 | Player is visible |
| On collision with | 碰撞检测 | Player on collision with Enemy |
| Overlapping | 重叠检测 | Bullet overlapping Enemy |
| Pick by comparison | 按条件筛选 | score > 100 |

### 系统条件

| 条件 | 说明 | 示例 |
|-----|------|------|
| Every X seconds | 定时触发 | Every 1 second |
| On start of layout | 场景开始 | On start of Game |
| On end of layout | 场景结束 | On end of Game |
| Compare variable | 变量比较 | score >= target |

---

## 常用动作详解

### 对象动作

| 动作 | 说明 | 参数 |
|-----|------|------|
| Destroy | 销毁对象 | 无 |
| Set position | 设置位置 | X, Y坐标 |
| Set size | 设置尺寸 | Width, Height |
| Set angle | 设置角度 | 度数 |
| Set visible | 设置可见性 | true/false |
| Spawn another object | 生成对象 | 对象类型, 位置 |

### 运动动作

| 动作 | 说明 | 参数 |
|-----|------|------|
| Set velocity | 设置速度 | X, Y速度值 |
| Set acceleration | 设置加速度 | 加速度值 |
| Apply force | 施加力 | X, Y力值 |
| Simulate control | 模拟控制 | Left/Right/Jump |

### 变量动作

| 动作 | 说明 | 示例 |
|-----|------|------|
| Set value | 设置变量值 | Set score to 0 |
| Add to | 变量增加 | Add 1 to score |
| Subtract from | 变量减少 | Subtract 1 from lives |
| Set text | 设置文本 | Set ScoreText to score |

### 场景动作

| 动作 | 说明 | 参数 |
|-----|------|------|
| Go to layout | 跳转场景 | 场景名称 |
| Restart layout | 重启场景 | 无 |
| Close | 关闭游戏 | 无 |

---

## 事件逻辑模板

### 玩家移动

```
// 键盘控制
Event: Keyboard - On key pressed (D)
Action: Player - Set velocity X to 200

Event: Keyboard - On key pressed (A)
Action: Player - Set velocity X to -200

Event: Keyboard - On key released (D or A)
Action: Player - Set velocity X to 0
```

### 跳跃控制

```
Event: On key pressed (Space)
Condition: Player is on floor
Action: Player - Set velocity Y to -500
Action: Player - Set animation (Jump)
```

### 碰撞检测

```
Event: Player - On collision with Enemy
Action: Player - Set animation (Hurt)
Action: Subtract 1 from Lives
Action: Player - Set position to spawn point
Action: Wait 1 second
Action: Player - Set animation (Idle)
```

### 计分系统

```
Event: Player - On collision with Coin
Action: Add 10 to Score
Action: Destroy Coin
Action: Play sound (Coin)
Action: Spawn Particle at Coin.X, Coin.Y
```

### 敌人AI

```
Event: Every 2 seconds
Action: Enemy - Spawn bullet at Enemy.X, Enemy.Y

Event: System - Every tick
Action: Enemy - Move toward Player (speed 100)
```

---

## 高级事件技巧

### OR事件（任一条件满足）

```
+-- Event (OR block)
|   +-- Condition: Player on collision with Spike
|   +-- Condition: Player on collision with Enemy
|   +-- Condition: Player.Y > LayoutHeight
|   +-- Action: Game Over
```

### ELSE事件（条件不满足时）

```
+-- Event: Cursor is over Button
|   +-- Action: Button - Set animation (Hover)

+-- Event: Else
|   +-- Action: Button - Set animation (Normal)
```

### For Each循环

```
Event: System - For each Sprite
Condition: Sprite.Value > 10
Action: Sprite - Set color to Red
```

### 等待和定时

```
Event: On start of layout
Action: Wait 3 seconds
Action: Show TutorialPopup
```

### 函数调用

```
// 定义函数
Event: On function "CalculateScore"
Condition: Stars = 3
Action: Set return value to 1000

// 调用函数
Event: On button clicked
Action: Call function "CalculateScore"
Action: Add function return to Score
```

---

## 性能优化建议

### 减少事件检查

```python
# 使用"Once while true"避免重复触发
Event: Player - On collision with Coin (trigger once)
Action: Add 1 to Score

# 使用条件筛选减少检查对象
Event: Sprite (pick by comparison: Sprite.type = "enemy")
Action: Sprite - Set health to 0
```

### 对象池复用

```python
// 预创建对象池
Event: On start of layout
Action: Loop 20 times
Action: Create Bullet (set to variable)
Action: Bullet - Set visible false

// 从池中取对象
Event: On space pressed
Condition: Bullet (pick nearest: Bullet.visible = false)
Action: Bullet - Set position to Player
Action: Bullet - Set visible true
Action: Bullet - Set velocity 0, -500
```

### 碰撞组优化

```python
// 使用碰撞组
Collision group: "hazards"
- Player
- Enemy
- Spike

Event: Player - On collision with group "hazards"
Action: Player hurt
```

---

## 常见问题解决方案

### 事件不触发
- 检查条件是否正确
- 确认对象存在
- 检查事件顺序

### 动作执行错误
- 确认目标对象正确
- 检查变量类型
- 查看控制台错误

### 性能卡顿
- 减少每帧事件数量
- 使用对象池
- 优化碰撞检测

---

## 事件系统速查表

| 场景 | 条件 | 动作 |
|-----|------|------|
| 键盘移动 | On key pressed | Set velocity |
| 跳跃 | On key pressed + On floor | Set velocity Y |
| 碰撞伤害 | On collision | Subtract from lives |
| 收集物品 | On collision | Add to score + Destroy |
| 场景切换 | On clicked | Go to layout |
| 敌人巡逻 | Every X seconds | Move to waypoint |
| 射击 | On clicked | Spawn bullet |
| 游戏结束 | Lives = 0 | Show game over |
