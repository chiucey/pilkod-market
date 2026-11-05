# GFX 与 Interface 指南

## GFX 目录结构

```
gfx/
├── interface/          # UI 纹理（.dds）
├── flags/              # 国家旗帜（.dds/.tga）
├── event_pictures/     # 事件图片（.dds）
├── leaders/            # 领袖肖像（.dds）
├── models/             # 3D 模型
├── fonts/              # 字体
├── loadingscreens/     # 加载画面
├── texticons/          # 文本内嵌图标
├── aces/               # 王牌飞行员肖像
├── achievements/       # 成就图标
└── ...
```

## 图像格式

- **.dds**：DirectDraw Surface，带 MipMap 的纹理格式
- **.tga**：Targa，用于旗帜等需要透明通道的图像
- 推荐尺寸：事件图片 400x300 或 400x400，旗帜 82x52，领袖 156x210

## .gfx 文件

定义游戏中的精灵（sprite），位于 `interface/` 或 `gfx/`：

```
spriteTypes = {
    # 静态精灵
    spriteType = {
        name = "GFX_my_mod_icon"
        texturefile = "gfx/interface/my_mod_icon.dds"
    }
    
    # 动画精灵
    frameAnimatedSpriteType = {
        name = "GFX_my_mod_glow"
        texturefile = "gfx/interface/my_mod_glow.dds"
        noOfFrames = 2
        animation_rate_fps = 0.5
        looping = yes
    }
    
    # 进度条
    progressbartype = {
        name = "GFX_my_mod_progress"
        textureFile1 = "gfx/interface/my_mod_progress_bg.dds"
        textureFile2 = "gfx/interface/my_mod_progress_fill.dds"
        size = { x = 200 y = 20 }
    }
    
    # 遮罩进度条
    maskedShieldType = {
        name = "GFX_my_mod_shield"
        textureFile1 = "gfx/interface/shield.dds"
        textureFile2 = "gfx/interface/shield_mask.dds"
    }
}
```

常用 sprite 类型：
- `spriteType`：静态图片
- `frameAnimatedSpriteType`：帧动画
- `progressbartype`：进度条
- `pieChartType`：饼图
- `maskedShieldType`：遮罩

## .gui 文件

定义 UI 窗口布局和控件：

```
guiTypes = {
    containerWindowType = {
        name = "my_mod_window"
        position = { x = 0 y = 0 }
        size = { width = 400 height = 300 }
        moveable = yes
        
        background = {
            name = "background"
            quadTextureSprite = "GFX_tiled_window"
        }
        
        instantTextBoxType = {
            name = "title"
            position = { x = 20 y = 10 }
            font = "hoi_24header"
            text = "MY_MOD_TITLE"
            maxWidth = 360
            maxHeight = 30
            format = center
        }
        
        buttonType = {
            name = "close_button"
            position = { x = 370 y = 5 }
            quadTextureSprite = "GFX_closebutton"
            shortcut = "ESCAPE"
            clicksound = click_close
        }
        
        iconType = {
            name = "my_icon"
            position = { x = 20 y = 50 }
            spriteType = "GFX_my_mod_icon"
        }
        
        gridboxType = {
            name = "my_list"
            position = { x = 20 y = 100 }
            size = { width = 360 height = 180 }
            slotsize = { width = 180 height = 40 }
            format = "UPPER_LEFT"
            add_horizontal = yes
        }
    }
}
```

常用控件类型：
- `containerWindowType`：容器窗口
- `buttonType`：按钮
- `iconType`：图标
- `instantTextBoxType`：文本框
- `gridboxType`：网格列表
- `checkboxType`：复选框
- `editBoxType`：输入框
- `scrollbarType`：滚动条

## 自定义 GUI（scripted_guis）

在 `common/scripted_guis/` 定义可交互的自定义 UI：

```
scripted_gui = {
    my_mod_gui = {
        context_type = player_context
        
        window_name = my_mod_window
        parent_window_name = top_bar
        
        visible = { has_country_flag = my_mod_gui_open }
        
        effects = {
            close_button_click = { clr_country_flag = my_mod_gui_open }
            my_button_click = { add_political_power = 10 }
        }
        
        triggers = {
            my_button_click_enabled = { has_political_power > 50 }
        }
        
        properties = {
            my_progress_bar = {
                frame = var:my_mod_progress_var
            }
        }
    }
}
```

## 旗帜

每个国家每种意识形态需要一个旗帜：

```
gfx/flags/
├── GER.tga               # 德国法西斯旗帜
├── GER_communism.tga     # 德国共产主义旗帜
├── GER_democratic.tga    # 德国民主旗帜
├── GER_neutrality.tga    # 德国中立旗帜
├── GER_fascism.tga       # 同 GER.tga
└── medium/               # 中型旗帜（43x26）
└── small/                # 小型旗帜（26x16）
```

所有三种尺寸都必须提供。

## 事件图片

```
gfx/event_pictures/
├── report_events/        # 国家事件图片（400x300）
├── news_events/          # 新闻事件图片（400x400）
└── ...
```

在事件中引用：
```
picture = GFX_report_event_generic_factory
```

GFX 定义：
```
spriteType = {
    name = "GFX_report_event_generic_factory"
    texturefile = "gfx/event_pictures/report_events/generic_factory.dds"
}
```

## 领袖肖像

```
gfx/leaders/
├── GER/                  # 按国家分子目录
│   ├── Portrait_Germany_Adolf_Hitler.dds
│   └── ...
└── ...
```

在角色定义中引用：
```
portraits = {
    civilian = { large = GFX_portrait_GER_adolf_hitler }
}
```

对应的 GFX 定义：
```
spriteType = {
    name = "GFX_portrait_GER_adolf_hitler"
    texturefile = "gfx/leaders/GER/Portrait_Germany_Adolf_Hitler.dds"
}
```
