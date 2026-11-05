---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 44211eddee9b21e904f40eecd2603708
    PropagateID: 44211eddee9b21e904f40eecd2603708
    ReservedCode1: 3045022100881c051d8702b02cd6ac3d419af77c0d3aa94b3bffeff85e70a7581ea035fa0502203efca139369fef07edbb204e537198d13f9e83d0661634a3e7856af2f9da3624
    ReservedCode2: 304602210097787ab322855a887facfbfc6b26d339c76d75b5742ac87f578a6fd1f1fed7a30221009fc96e789edeabfb87edebd4b4f6180ff72676befaa7f30a971be4a7c80af06f
---

# common/ 目录详解

`common/` 是 MOD 制作最核心的目录，包含 60+ 子目录。

## 国家与政治

### countries/
国家基础定义，每个国家一个文件：
```
GER = {
    color = { 128 128 128 }
    color_ui = { 115 115 115 }
}
```

### country_tags/
国家标签映射：
```
GER = "countries/Germany.txt"
D01 = "countries/Dynamic.txt"
```

### characters/
角色/将领定义（较新系统），每个国家一个文件如 `GER.txt`：
```
characters = {
    GER_ernst_thalmann = {
        name = GER_ernst_thalmann
        portraits = {
            civilian = { large = GFX_portrait_GER_ernst_thalmann }
        }
        country_leader = {
            ideology = stalinism
            traits = { GER_communist_revolutionary_trait }
        }
    }
}
```

### ideologies/
意识形态定义：
```
ideologies = {
    fascism = {
        types = { nazism fascism_ideology falangism rexism }
        dynamic_faction_names = { ... }
        color = { 110 110 110 }
        rules = { ... }
        can_collaborate = yes
        modifier = { ... }
    }
}
```

### ideas/ 与 idea_tags/
国家精神/法案定义：
```
ideas = {
    country = {
        my_mod_idea = {
            picture = GFX_idea_my_mod
            modifier = {
                political_power_gain = 0.1
                stability_factor = 0.05
            }
        }
    }
}
```

## 国策与焦点

### national_focus/
国策树定义（最复杂的脚本之一）：
```
focus_tree = {
    id = my_mod_german_focus_tree
    country = { factor = 0 modifier = { add = 10 tag = GER } }
    default = no
    
    focus = {
        id = my_mod_focus_industry
        icon = GFX_focus_generic_industry
        cost = 10
        x = 0
        y = 0
        prerequisite = { focus = some_other_focus }
        mutually_exclusive = { focus = another_focus }
        available = { ... }
        completion_reward = { ... }
    }
}
```

关键字段：`id`, `icon`, `cost`（天数/10）, `prerequisite`, `mutually_exclusive`, `available`, `bypass`, `completion_reward`, `allow_branch`。

### continuous_focus/
持续性国策：
```
continuous_focus_palette = {
    id = generic_continuous_focus
    focus = { id = continuous_non_factory_construct }
}
```

## 科技与装备

### technologies/
科技定义：
```
technologies = {
    basic_machine_tools = {
        research_cost = 1.5
        start_year = 1936
        folder = { name = industry_folder position = { x = 0 y = 0 } }
        ai_research_weights = { ... }
        categories = { ... }
        path = { ... }
        allow_branch = { ... }
    }
}
```

### units/ 与 equipment/
单位和装备定义：
```
sub_units = {
    infantry = {
        abbreviation = "INF"
        sprite = infantry
        map_icon_category = infantry
        priority = 600
        combat_width = 2
        manpower = 1000
        need = { infantry_equipment = 100 }
    }
}
```

装备在 `units/equipment/`：
```
equipments = {
    infantry_equipment = {
        year = 1936
        is_archetype = yes
        picture = archetype_infantry_equipment
        is_buildable = no
        type = infantry
        group_by = archetype
        interface_category = interface_category_land
        reliability = 0.9
        maximum_speed = 4
        defense = 3
        breakthrough = 1
        hardness = 0
        armor_value = 0
        soft_attack = 3
        hard_attack = 0.5
    }
}
```

## 决议系统

### decisions/ 与 decisions/categories/
```
categories = {
    my_mod_decision_cat = {
        icon = GFX_decision_category_generic_political_actions
        picture = GFX_decision_cat_picture_generic
        allowed = { always = yes }
        visible = { ... }
        priority = { base = 10 }
    }
}

category = my_mod_decision_cat
my_mod_decision = {
    icon = GFX_decision_generic_form_nation
    allowed = { ... }
    available = { ... }
    visible = { ... }
    cost = 50
    fire_only_once = yes
    days_remove = 30
    complete_effect = { ... }
    remove_effect = { ... }
}
```

## 脚本系统

### scripted_effects/
可复用脚本效果：
```
my_mod_add_war_support = {
    add_war_support = 0.05
    if = { limit = { has_idea = my_mod_idea } add_war_support = 0.05 }
}
```

### scripted_triggers/
可复用脚本条件：
```
my_mod_is_major = {
    OR = {
        tag = GER tag = ENG tag = SOV tag = USA tag = JAP tag = ITA
    }
}
```

### on_actions/
触发器脚本：
```
on_actions = {
    on_daily = { effect = { ... } }
    on_weekly = { random_events = { ... } }
    on_monthly = { ... }
    on_declare_war = { ... }
    on_peaceconference_ended = { ... }
    on_capitulation = { ... }
}
```

## 经济与建设

### buildings/
建筑类型定义：
```
buildings = {
    industrial_complex = {
        base_cost = 10800
        base_cost_conversion = 9000
        military_production = 5
        general_production = 0
        navy_production = 0
        culture_production = 0
        infrastructure_consumption = 0.2
        show_modifier = yes
        damage_factor = 1.0
        value = 5
    }
}
```

### state_category/
省份规模分类：
```
state_categories = {
    metropolis = { local_building_slots = 12 color = { 0 255 255 } }
    city = { local_building_slots = 8 }
    large_town = { local_building_slots = 6 }
    town = { local_building_slots = 4 }
    rural = { local_building_slots = 2 }
    wasteland = { local_building_slots = 0 }
}
```

## AI 配置

### ai_strategy/
AI 战略脚本：
```
GER_unit_production = {
    allowed = { tag = GER }
    enable = { always = yes }
    abort_when_not_enabled = yes
    ai_strategy = { type = unit_ratio id = infantry value = 50 }
    ai_strategy = { type = equipment_production_factor id = infantry value = 10 }
}
```

### ai_strategy_plans/
AI 历史/替代路线策略：
```
GER_historical_plan = {
    name = "Historical Plan"
    desc = "Follow historical path"
    allowed = { tag = GER }
    enable = { has_game_rule = { rule = GER_ai_behavior option = HISTORICAL } }
    abort = { ... }
    ai_national_focuses = {
        GER_rhineland
        GER_anti_comintern_pact
        GER_anschluss
        ...
    }
}
```

### ai_templates/
AI 编制模板：
```
infantry_default = {
    priority = { base = 100 }
    target_width = 20.0
    width_weight = 1.0
    target_template = {
        weight = 0.9
        match_value = 3000.0
        regiments = { infantry = 10 }
        support = { engineer = 1 recon = 1 }
    }
}
```

## 其他重要配置

### defines/
`00_defines.lua`：游戏全局参数，如补给范围、战争分数、外交关系等。

### bookmarks/
开局书签：`the_gathering_storm.txt`（1936）, `blitzkrieg.txt`（1939）。

### game_rules/
游戏规则设定，用于创建剧本选项。

### autonomous_states/
傀儡/自治状态：殖民地、自治领、专员辖区等。

### game_rules/ 与 occupation_laws/
占领政策和游戏规则。
