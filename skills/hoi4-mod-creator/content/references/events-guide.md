# 事件脚本指南

## 基本结构

事件文件位于 `events/` 目录，按国家或主题分文件：

```
add_namespace = my_mod_events

country_event = {
    id = my_mod_events.1
    title = my_mod_events.1.t
    desc = my_mod_events.1.d
    picture = GFX_report_event_generic_factory
    
    is_triggered_only = yes
    fire_only_once = yes
    
    option = {
        name = my_mod_events.1.a
        ai_chance = { factor = 70 }
        add_political_power = 100
    }
    
    option = {
        name = my_mod_events.1.b
        ai_chance = { factor = 30 }
        add_stability = -0.05
    }
}
```

## 事件类型

| 类型 | 说明 |
|------|------|
| `country_event` | 国家事件，发给单个国家 |
| `news_event` | 新闻事件，全球广播 |
| `state_event` | 省份事件 |
| `unit_leader_event` | 将领事件 |

## 关键字段

| 字段 | 说明 |
|------|------|
| `id` | 唯一标识，格式 `namespace.数字` |
| `title` / `desc` | 标题/描述，引用本地化键 |
| `picture` | 事件图片，引用 GFX 定义 |
| `is_triggered_only` | 仅由脚本触发（非自动触发）|
| `fire_only_once` | 全局仅触发一次 |
| `hidden` | 隐藏事件（无 UI）|
| `major` | 标记为重大事件 |
| `timeout_days` | 选项超时天数 |
| `trigger` | 自动触发条件（与 mean_time_to_happen 配合）|
| `mean_time_to_happen` | 平均触发时间 |

## 自动触发事件

```
country_event = {
    id = my_mod_events.10
    title = my_mod_events.10.t
    desc = my_mod_events.10.d
    
    trigger = {
        tag = GER
        date > 1936.3.1
        has_government = fascism
    }
    
    mean_time_to_happen = {
        days = 30
        modifier = { factor = 0.5 has_war = yes }
    }
    
    option = { name = my_mod_events.10.a }
}
```

## mean_time_to_happen 语法

```
mean_time_to_happen = {
    days = 30
    months = 6
    years = 1
    modifier = {
        factor = 0.5
        has_war = yes
    }
    modifier = {
        factor = 2.0
        is_in_faction = yes
    }
}
```

`factor < 1` 加速，`factor > 1` 减速。

## 事件选项

```
option = {
    name = my_mod_events.1.a
    ai_chance = {
        factor = 50
        modifier = { factor = 2 has_government = fascism }
    }
    trigger = { has_political_power > 50 }
    custom_effect_tooltip = my_mod_tooltip_key
    
    add_political_power = -50
    add_stability = 0.05
    hidden_effect = { ... }
}
```

## 触发事件

```
# 直接触发
country_event = { id = my_mod_events.1 days = 3 }

# 触发给特定国家
target_country = { country_event = { id = my_mod_events.1 } }

# 随机国家
random_country = {
    limit = { is_major = yes }
    country_event = { id = my_mod_events.1 }
}
```

## 事件链

通过选项的 `hidden_effect` 或外部 `on_actions` 连接多个事件：

```
option = {
    name = my_mod_events.1.a
    hidden_effect = {
        country_event = { id = my_mod_events.2 days = 7 }
    }
}
```

## 新闻事件

```
news_event = {
    id = my_mod_news.1
    title = my_mod_news.1.t
    desc = my_mod_news.1.d
    picture = GFX_news_event_generic_rally
    
    major = yes
    
    trigger = {
        tag = GER
        has_completed_focus = GER_rhineland
    }
    
    mean_time_to_happen = { days = 1 }
    
    option = {
        name = my_mod_news.1.a
        trigger = { NOT = { tag = GER } }
    }
    option = {
        name = my_mod_news.1.b
        trigger = { tag = GER }
    }
}
```

## 常用效果（Effects）

| 效果 | 语法 |
|------|------|
| 增加政治点数 | `add_political_power = 100` |
| 增加稳定度 | `add_stability = 0.05` |
| 增加战争支持度 | `add_war_support = 0.1` |
| 添加国家精神 | `add_ideas = my_idea` |
| 移除国家精神 | `remove_ideas = my_idea` |
| 交换国家精神 | `swap_ideas = { remove = old add = new }` |
| 添加国策 | `unlock_national_focus = my_focus` |
| 完成国策 | `complete_national_focus = my_focus` |
| 添加科技 | `add_tech_bonus = { bonus = 0.5 uses = 1 category = land_doctrine }` |
| 添加装备 | `add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1000 }` |
| 添加军队经验 | `army_experience = 50` |
| 创建阵营 | `create_faction = my_faction` |
| 加入阵营 | `add_to_faction = [TAG]` |
| 宣战 | `declare_war_on = { target = [TAG] type = annex_everything }` |
| 吞并 | `annex_country = { target = [TAG] transfer_troops = yes }` |
| 释放国家 | `release = [TAG]` |
| 设置傀儡 | `set_autonomy = { target = [TAG] autonomy_state = autonomy_puppet }` |
| 转移省份 | `transfer_state = [ID]` |
| 添加核心 | `add_core_of = [TAG]` |
| 设置变量 | `set_variable = { var = my_var value = 10 }` |
| 修改变量 | `add_to_variable = { var = my_var value = 5 }` |
| 触发国家事件 | `country_event = { id = xxx.y }` |
| 触发新闻事件 | `news_event = { id = xxx.y }` |

## 常用条件（Triggers）

| 条件 | 语法 |
|------|------|
| 标签检查 | `tag = GER` |
| 日期检查 | `date > 1939.1.1` |
| 拥有政府 | `has_government = fascism` |
| 拥有国家精神 | `has_idea = my_idea` |
| 完成国策 | `has_completed_focus = my_focus` |
| 拥有科技 | `has_tech = my_tech` |
| 处于战争 | `has_war = yes` |
| 处于阵营 | `is_in_faction = yes` |
| 是主要国家 | `is_major = yes` |
| 存在国家 | `exists = yes` / `GER = { exists = yes }` |
| 拥有省份 | `owns_state = 1` |
| 控制省份 | `controls_state = 1` |
| 省份有核心 | `has_core_of = GER` |
| 检查变量 | `check_variable = { var = my_var value = 10 compare = equals }` |
| 随机概率 | `random = 0.5` |
| AND/OR/NOT | `AND = { ... }`, `OR = { ... }`, `NOT = { ... }` |

## 变量系统

```
# 设置变量
set_variable = { var = my_mod_var value = 0 }
set_variable = { var = my_mod_var value = random }

# 修改
add_to_variable = { var = my_mod_var value = 1 }
subtract_from_variable = { var = my_mod_var value = 1 }
multiply_variable = { var = my_mod_var value = 2 }
divide_variable = { var = my_mod_var value = 2 }

# 条件
if = {
    limit = { check_variable = { var = my_mod_var value = 10 compare = greater_than } }
    ...
}

# 在事件中引用
set_country_flag = my_flag
country_event = { id = my_mod_events.1 }
clr_country_flag = my_flag
```

## 标志（Flags）

```
set_country_flag = my_flag        # 国家标志
set_global_flag = my_flag         # 全局标志
set_state_flag = { flag = my_flag state = 1 }  # 省份标志
clr_country_flag = my_flag        # 清除
has_country_flag = my_flag        # 检查
```
