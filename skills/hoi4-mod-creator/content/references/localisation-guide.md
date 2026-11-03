---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a8c11b1cda61ea9918c4b2e809762000
    PropagateID: a8c11b1cda61ea9918c4b2e809762000
    ReservedCode1: 304402203ff2ad36a780125304207eb0c65e01a9d16fdfe4fdd71bede746b83cf01262e1022031750962302fb6d8bec4e507965999f4fa8b4521937c8b09c93b6b69da28aa0e
    ReservedCode2: 304502201cc35da8d6e74c642255b098e0984c955ec1fe7391c0c54d855393452fc01620022100a751a84da1f80e3c7ee2be12b7653453d72543b92774991f6384cf0040b2e103
---

# 本地化指南

## 文件位置

```
localisation/
├── english/
│   ├── my_mod_l_english.yml
│   ├── my_mod_events_l_english.yml
│   └── ...
├── simp_chinese/
│   ├── my_mod_l_simp_chinese.yml
│   └── ...
└── ... (其他语言)
```

## 文件格式

YAML 格式，必须使用 **UTF-8-BOM** 编码（带 BOM 的 UTF-8）：

```yaml
l_english:
 my_mod_key_1: "这是文本内容"
 my_mod_key_2: "包含引号的内容: \"你好\""
 my_mod_key_3: "多行内容\n第二行"
 my_mod_key_4:0 "数字前缀是版本号，可选"
```

## 命名规范

| 内容类型 | 键名格式 |
|---------|---------|
| 事件标题 | `namespace.数字.t` |
| 事件描述 | `namespace.数字.d` |
| 事件选项 | `namespace.数字.a` / `.b` / `.c` |
| 国策名称 | `focus_id` |
| 国策描述 | `focus_id_desc` |
| 国家精神 | `idea_id` |
| 国家精神描述 | `idea_id_desc` |
| 决议 | `decision_id` |
| 决议描述 | `decision_id_desc` |
| 角色名称 | `TAG_character_name` |
| 自定义 | `modprefix_任意描述性名称` |

## 动态本地化

使用脚本化变量插入动态内容：

```yaml
my_mod_events.1.d:0 "[ROOT.GetName] 决定向我们宣战。"
my_mod_events.1.d:0 "[FROM.GetNameDef] 的军事实力为 [FROM.GetManpower]。"
```

常用脚本化本地化变量：

| 变量 | 说明 |
|------|------|
| `[ROOT.GetName]` | 当前国家名称 |
| `[ROOT.GetNameDef]` | 带政体的国家名称 |
| `[ROOT.GetLeader]` | 当前领袖名 |
| `[FROM.GetName]` | 来源国家名称 |
| `[THIS.GetName]` | 当前作用域名称 |
| `[?my_var]` | 显示变量值 |
| `[Root.GetTag]` | 国家标签 |

## 脚本化本地化（scripted_localisation）

在 `common/scripted_localisation/` 定义条件性文本：

```
defined_text = {
    name = GetMyModText
    text = {
        trigger = { has_government = fascism }
        localization_key = my_mod_text_fascist
    }
    text = {
        trigger = { has_government = communism }
        localization_key = my_mod_text_communist
    }
    default = my_mod_text_default
}
```

在本地化中引用：
```yaml
my_mod_desc:0 "当前政府是 [GetMyModText]。"
```

## 颜色代码

```yaml
my_mod_text:0 "§R这是红色§! 这是默认色 §G这是绿色§!"
```

| 代码 | 颜色 |
|------|------|
| `§R` | 红色 |
| `§G` | 绿色 |
| `§B` | 蓝色 |
| `§Y` | 黄色 |
| `§O` | 橙色 |
| `§W` | 白色 |
| `§g` | 灰色 |
| `§!` | 恢复默认 |

## 图标代码

```yaml
my_mod_text:0 "£pol_power£ 需要 100 政治点数"
```

常用图标：`£pol_power£`, `£command_power£`, `£manpower£`, `£time£`, `£trigger_no£`, `£trigger_yes£`

## 注意事项

1. 所有脚本中引用的文本键必须在本地化文件中有定义，否则显示为 `KEY_NAME`
2. 中文 MOD 建议同时提供 `english` 和 `simp_chinese` 目录
3. 创意工坊上传时文件名不能含中文
4. 版本号（`:0`）可省略，但建议保留以支持启动器更新
