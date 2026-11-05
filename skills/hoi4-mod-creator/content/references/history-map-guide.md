---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: de4632c54999dfda3626785342348d6d
    PropagateID: de4632c54999dfda3626785342348d6d
    ReservedCode1: 3045022100b2f53c71fff11ec2734258ab6678d5ed86f202aaaeac617f6acfda22c7a4e8ec02200b2451db2b3d801e3922485305706b043c38a5e4ac1dddb983506fd7a0e0747d
    ReservedCode2: 30450220229b6d7ce2857dfce7fec80f167ae236fc97ade465a9829c579da7efd275ee460221009c8f11bf6f9205274784b25ad1fc2952b8160a4de8b1160f4705e81bcb175c24
---

# History 与 Map 指南

## history/ 目录

### history/countries/
国家初始设定文件，命名格式：`[TAG] - [国家名].txt`

```
capital = 64

set_oob = "GER_1936"
set_research_slots = 4

set_stability = 0.57
set_war_support = 0.30

set_politics = {
    ruling_party = fascism
    last_election = "1933.3.5"
    election_frequency = 48
    elections_allowed = no
}

set_popularities = {
    democratic = 20
    fascism = 60
    communism = 20
    neutrality = 0
}

add_ideas = {
    GER_mefo_bills_idea
    general_staff
}

recruit_character = GER_adolf_hitler
```

### history/states/
省份初始设定，命名格式：`[ID]-[地区名].txt`

```
state = {
    id = 1
    name = "STATE_1"
    manpower = 322900
    state_category = town
    
    resources = {
        steel = 4
        aluminium = 2
    }
    
    history = {
        owner = FRA
        add_core_of = FRA
        
        victory_points = { 3838 1 }
        
        buildings = {
            infrastructure = 2
            industrial_complex = 1
            dockyard = 1
            3838 = { naval_base = 3 }
        }
    }
    
    provinces = { 3838 9851 11804 }
    local_supplies = 0.0
}
```

关键字段：
- `id`：省份唯一 ID
- `manpower`：人力
- `state_category`：规模分类（metropolis/city/town/rural/wasteland）
- `resources`：资源储量
- `buildings`：建筑等级
- `victory_points`：胜利点 `{ 省份内地块ID 点数 }`
- `provinces`：该州包含的地块 ID 列表

### history/units/
初始军队部署，命名格式：`[TAG]_[年份].txt`

```
division_template = {
    name = "Infanterie-Division"
    regiments = {
        infantry = { x = 0 y = 0 }
        infantry = { x = 0 y = 1 }
        infantry = { x = 0 y = 2 }
        infantry = { x = 1 y = 0 }
        infantry = { x = 1 y = 1 }
        infantry = { x = 1 y = 2 }
        artillery_brigade = { x = 2 y = 0 }
    }
    support = {
        engineer = { x = 0 y = 0 }
        recon = { x = 0 y = 1 }
    }
}

units = {
    division = {
        name = "1. Infanterie-Division"
        location = 6521
        division_template = "Infanterie-Division"
        start_experience_factor = 0.3
        start_equipment_factor = 0.8
    }
}
```

海军和空军部署：
```
units = {
    fleet = {
        name = "Hochseeflotte"
        naval_base = 6389
        task_force = {
            name = "1. Flotte"
            location = 6389
            ship = { name = "Bismarck" definition = battleship equipment = { battleship_1 = { amount = 1 owner = GER } } }
        }
    }
}

air_wings = {
    64 = {
        fighter_equipment_0 = { owner = GER amount = 100 }
        tac_bomber_equipment_0 = { owner = GER amount = 50 }
    }
}
```

## map/ 目录

### 核心文件

| 文件 | 用途 |
|------|------|
| `default.map` | 地图主配置 |
| `definition.csv` | 省份定义（ID,R,G,B,类型,大陆,is_coastal,terrain,continent）|
| `provinces.bmp` | 省份颜色索引图（决定边界，必须 8bit）|
| `terrain.bmp` | 地形类型图 |
| `rivers.bmp` | 河流网络 |
| `heightmap.bmp` | 高度图 |
| `trees.bmp` | 植被分布 |
| `world_normal.bmp` | 法线贴图 |
| `cities.bmp` | 城市位置 |
| `positions.txt` | 建筑/单位位置坐标 |
| `adjacencies.csv` | 省份邻接（含海峡）|
| `adjacency_rules.txt` | 邻接规则（运河通行条件）|
| `railways.txt` | 铁路网络 |
| `supply_nodes.txt` | 补给节点 |
| `buildings.txt` | 地图建筑位置 |
| `ambient_object.txt` | 环境物体 |
| `seasons.txt` | 季节设定 |
| `continent.txt` | 大洲定义 |
| `colors.txt` | 地图颜色 |

### default.map

```
definitions = "definition.csv"
provinces = "provinces.bmp"
positions = "positions.txt"
terrain = "terrain.bmp"
rivers = "rivers.bmp"
heightmap = "heightmap.bmp"
tree = "trees.bmp"

# 可建造省份（排除海洋、湖泊等）
sea_starts = { 1 2 3 ... }
lake = { 4 5 6 ... }

# 战略区域和补给区数量
strategic_region = { ... }
supply_node = { ... }

# 铁路
railways = "railways.txt"
supply_nodes = "supply_nodes.txt"
```

### definition.csv

CSV 格式，每行一个地块：
```
province;red;green;blue;type;coastal;terrain;continent
1;120;40;20;land;1;plains;1
2;120;41;20;sea;0;ocean;1
3;120;42;20;lake;0;lake;1
```

### strategicregions/

战略区域定义，命名：`[ID]-[区域名].txt`

```
strategic_region = {
    id = 1
    name = "STRATEGICREGION_1"
    provinces = { 1 2 3 4 5 ... }
    
    weather = {
        period = {
            between = { 0.0 30.0 }
            temperature = { -10.0 10.0 }
            temperature_day_night = { -2.0 2.0 }
            no_phenomenon = 0.500
            rain_light = 0.200
            rain_heavy = 0.100
            snow = 0.100
            blizzard = 0.050
            arctic_water = 0.000
            mud = 1.000
            sandstorm = 0.000
            min_snow_level = 0.000
        }
    }
}
```

### supplyareas/

补给区域定义：
```
supply_area = {
    id = 1
    name = "SUPPLYAREA_1"
    value = 10
    states = { 1 2 3 }
}
```

## 地图修改建议

1. `provinces.bmp` 必须使用 8-bit 索引色模式
2. 每个省份颜色在 `definition.csv` 中必须唯一
3. 修改省份后必须同步更新 `history/states/` 和 `strategicregions/`
4. 使用官方地图编辑器（`Hearts of Iron IV/tools/`）或第三方工具
5. 修改 `provinces.bmp` 后需要删除 `map/cache/` 让游戏重新生成

## 官方工具

游戏安装目录下的 `tools/` 包含：
- 地图编辑器
- 模型查看器
- 其他开发辅助工具
