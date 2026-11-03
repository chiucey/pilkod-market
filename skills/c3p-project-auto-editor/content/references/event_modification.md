# 事件表修改指南

## 事件表结构

Construct3事件表是XML格式，包含以下层级：

```
eventSheet
├── variables (全局变量)
├── groups (事件组)
│   └── events (事件)
│       ├── conditions (条件)
│       └── actions (动作)
└── includes (引用)
```

## 可修改参数

### 数值参数

| 参数类型 | 示例 | 范围 |
|---------|------|------|
| score | 分数 | 0-9999999 |
| speed | 速度 | 0-9999 |
| health | 生命 | 0-9999 |
| timer | 时间 | 0-9999 |

### 触发条件

| 条件类型 | 参数 |
|---------|------|
| On collision | 碰撞对象 |
| On click | 鼠标/触摸 |
| Every X seconds | 间隔时间 |
| Variable comparison | 变量比较 |

### 动作参数

| 动作类型 | 参数 |
|---------|------|
| Set value | 目标值 |
| Add to | 增加量 |
| Subtract from | 减少量 |
| Spawn | 生成位置 |

## 修改示例

### 1. 修改分数倍率

```python
from event_editor import C3PEventEditor

editor = C3PEventEditor('/path/to/c3p')

# 将所有分数值乘以2
editor.update_score_values(
    'eventSheets/MainEvents.uevents',
    score_multiplier=2.0,
    base_score_add=0
)
```

### 2. 更新游戏平衡

```python
from event_editor import C3PEventEditor, GameBalanceConfig

config = GameBalanceConfig(
    click_reward=10,
    difficulty=1.5,
    coin_rate=2,
    ad_frequency=30
)

editor.update_game_balance(config)
```

### 3. 更新广告配置

```python
editor.update_ad_config({
    'tiktok_app_id': 'your_app_id',
    'tiktok_rewarded_id': 'your_unit_id',
    'tiktok_interstitial_id': 'your_unit_id'
})
```

### 4. 添加自定义变量

```python
editor.add_variable(
    'eventSheets/MainEvents.uevents',
    'CustomScore',
    'number',
    0
)
```

## 游戏平衡配置类

```python
@dataclass
class GameBalanceConfig:
    click_reward: int = 1           # 点击收益
    upgrade_cost_base: int = 10    # 升级基础价格
    difficulty: float = 1.0         # 难度系数
    coin_rate: int = 1             # 金币倍率
    ad_frequency: int = 60          # 广告间隔(秒)
    reward_multiplier: float = 1.0  # 奖励倍率
    enemy_speed: float = 100.0     # 敌人速度
    player_speed: float = 200.0    # 玩家速度
```

## 注意事项

1. **保持结构完整**：不要删除必要的事件节点
2. **数值范围**：遵守参数范围限制
3. **备份原文件**：编辑器会自动备份
4. **测试验证**：修改后用Construct3打开测试

## 导出修改日志

```python
editor.export_modifications_log('modifications.json')
```
