# Construct3 C3P文件格式详解

## 概述

Construct3的.c3p文件本质上是**加密ZIP压缩包**，包含游戏项目的所有配置、资源和代码。

## 文件结构

```
game.c3p (ZIP压缩包)
├── project.c3proj              # 主项目配置
├── project.uistate.json         # UI状态
├── layouts/                     # 场景目录
│   ├── Menu.uilayout            # 主菜单场景
│   ├── Game.uilayout            # 游戏场景
│   └── GameOver.uilayout        # 结束场景
├── eventSheets/                 # 事件表目录
│   ├── MainEvents.uevents       # 主事件表
│   └── UIevents.uevents         # UI事件
├── objectTypes/                 # 对象类型
├── animations/                   # 动画配置
├── media/                       # 媒体资源
│   ├── images/                   # 图片
│   ├── audio/                    # 音频
│   └── fonts/                    # 字体
└── icons/                       # 应用图标
```

## 核心文件说明

### project.c3proj

主项目配置文件，XML格式，包含：
- 项目基本信息（名称、版本、作者）
- 画布设置（尺寸、帧率）
- 导出配置（包名、平台设置）
- 全局变量定义

### *.uilayout

场景布局文件，XML格式，包含：
- 场景属性（尺寸、背景色）
- 图层配置
- 对象实例位置
- 视口设置

### *.uevents

事件表文件，XML格式，包含：
- 事件组
- 事件条件
- 事件动作
- 注释

## XML命名空间

```xml
<Constructsc3p xmlns="https://www.construct.net">
  <Project>
    <name>Game Name</name>
    ...
  </Project>
</Constructsc3p>
```

## 版本兼容性

| Construct3版本 | C3P格式 | 兼容性 |
|--------------|---------|--------|
| R280+ | v1.1 | 完整兼容 |
| R290+ | v1.2 | 完整兼容 |
| R300+ | v1.3 | 完整兼容 |

## 加密说明

C3P文件使用标准ZIP加密（Deflate压缩），可通过Python标准库解压：

```python
import zipfile

with zipfile.ZipFile('game.c3p', 'r') as zf:
    zf.extractall('extracted/')
```

## 资源路径

媒体资源路径使用相对于media目录的路径：

```
media/images/background.png
media/audio/bgm.ogg
```

## 导出参数

```xml
<Exporters>
  <Exporter type="html5">
    <package>com.gamestudio.game</package>
    <version>1.0.0</version>
  </Exporter>
</Exporters>
```
