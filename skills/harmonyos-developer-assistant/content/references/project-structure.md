---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022028bfe97c0927a96913b600ce553f51d7db9526a27b856f8be94dfe2ae9b6471b02204c32dcf9efe45b75dca5640bcc75e6cd11290890732ae51a72652702b7227587
    ReservedCode2: 30440220157cbd63514db4303917675d30eef7e1f2a4d9ece82e8e7a6dce54f27c60b771022025f980a7b8d5de53d73208cdb980ce57419f2628a74364bce20bce7218ac0ab6
---

# HarmonyOS 项目结构指南

## Stage 模型项目结构

```
MyApplication/
├── entry/                           # 主模块
│   ├── src/
│   │   └── main/
│   │       ├── ets/                  # ArkTS 源代码
│   │       │   ├── Application.ets    # 应用入口
│   │       │   ├── MainAbility/       # 主 Ability
│   │       │   │   ├── MainAbility.ets
│   │       │   │   └── pages/         # 页面目录
│   │       │   │       └── Index.ets  # 首页
│   │       │   ├── pages/             # 页面目录
│   │       │   │   ├── Index/
│   │       │   │   │   └── Index.ets
│   │       │   │   └── Detail/
│   │       │   │       └── Detail.ets
│   │       │   ├── components/        # 自定义组件
│   │       │   │   └── MyComponent.ets
│   │       │   └── utils/             # 工具函数
│   │       │       └── logger.ets
│   │       ├── resources/             # 资源文件
│   │       │   ├── base/
│   │       │   │   ├── element/      # 元素资源（颜色、字符串等）
│   │       │   │   │   ├── color.json
│   │       │   │   │   └── string.json
│   │       │   │   ├── media/         # 媒体资源（图片、音频等）
│   │       │   │   │   ├── icon.png
│   │       │   │   │   └── logo.jpg
│   │       │   │   └── profile/      # 配置文件
│   │       │   │       └── rawfile/  # 原始文件
│   │       │   └── zh-cn/             # 中文资源（可选）
│   │       │       └── element/
│   │       │           └── string.json
│   │       └── module.json5           # 模块配置
│   ├── build-profile.json5           # 构建配置
│   └── hvigorfile.ts                 # Hvigor 构建脚本
├── AppScope/                         # 应用范围资源
│   └── resources/
│       └── base/
│           └── element/
│               └── string.json
├── build/                            # 构建产物（自动生成）
├── har/                              # 依赖模块
├── .idea/                            # IDE 配置
├── build-profile.json5               # 构建配置
├── hvigor/                          # Hvigor 配置
├── hvigorw                          # Hvigor 脚本
└── oh-package.json5                 # 包管理配置
```

## 核心配置文件

### module.json5 模块配置

```json5
{
  "module": {
    "name": "entry",
    "type": "entry",
    "description": "$string:module_desc",
    "mainElement": "EntryAbility",
    "deviceTypes": [
      "phone",
      "tablet",
      "2in1"
    ],
    "deliveryWithInstall": true,
    "installationFree": false,
    "pages": "$profile:main_pages",
    "abilities": [
      {
        "name": "EntryAbility",
        "srcEntry": "./ets/MainAbility/EntryAbility.ets",
        "description": "$string:EntryAbility_desc",
        "icon": "$media:icon",
        "label": "$string:EntryAbility_label",
        "startWindowIcon": "$media:icon",
        "startWindowBackground": "$color:start_window_background",
        "exported": true,
        "skills": [
          {
            "entities": ["entity.system.home"],
            "actions": ["action.system.home"]
          }
        ]
      }
    ]
  }
}
```

### main_pages.json 页面配置

```json5
{
  "src": [
    {
      "bundleName": "com.example.app",
      "moduleName": "entry",
      "pages": [
        "pages/Index/Index",
        "pages/Detail/Detail",
        "pages/Settings/Settings"
      ]
    }
  ]
}
```

## 应用入口 Application.ets

```typescript
import UIAbility from '@ohos.app.ability.UIAbility'
import hilog from '@ohos.hilog'
import window from '@ohos.window'

const TAG = 'MyApplication'
const DOMAIN = 0x0001

export default class MyApplication extends UIAbility {
  onCreate(want, launchParam) {
    hilog.info(DOMAIN, TAG, 'Application onCreate')
  }

  onDestroy() {
    hilog.info(DOMAIN, TAG, 'Application onDestroy')
  }

  onWindowStageCreate(windowStage: window.WindowStage) {
    hilog.info(DOMAIN, TAG, 'Application onWindowStageCreate')

    // 加载主页面
    windowStage.loadContent('pages/Index/Index', (err, data) => {
      if (err.code) {
        hilog.error(DOMAIN, TAG, 'Failed to load content: %{public}s', JSON.stringify(err))
        return
      }
      hilog.info(DOMAIN, TAG, 'Succeeded in loading content')
    })
  }

  onWindowStageDestroy() {
    hilog.info(DOMAIN, TAG, 'Application onWindowStageDestroy')
  }
}
```

## Ability 生命周期

### UIAbility.ets

```typescript
import UIAbility from '@ohos.app.ability.UIAbility'
import window from '@ohos.window'

export default class EntryAbility extends UIAbility {
  onCreate(want, launchParam) {
    // Ability 创建时调用
  }

  onDestroy() {
    // Ability 销毁时调用
  }

  onWindowStageCreate(windowStage: window.WindowStage) {
    // 窗口创建时调用
    windowStage.loadContent('pages/Index/Index')
  }

  onWindowStageDestroy() {
    // 窗口销毁时调用
  }

  onForeground() {
    // Ability 进入前台时调用
  }

  onBackground() {
    // Ability 进入后台时调用
  }
}
```

## 资源文件规范

### string.json 字符串资源

```json5
{
  "string": [
    {
      "name": "app_name",
      "value": "我的应用"
    },
    {
      "name": "main_page_title",
      "value": "首页"
    },
    {
      "name": "button_text",
      "value": "点击"
    }
  ]
}
```

### color.json 颜色资源

```json5
{
  "color": [
    {
      "name": "primary_color",
      "value": "#FF007DFF"
    },
    {
      "name": "background_color",
      "value": "#FFF5F5F5"
    }
  ]
}
```

## 常用目录操作

### 创建新页面

1. 在 `entry/src/main/ets/pages/` 下创建页面文件夹
2. 创建 `页面名称/页面名称.ets` 文件
3. 在 `main_pages.json` 中注册页面路由
4. 在 `module.json5` 中配置页面信息

### 添加资源文件

1. 媒体资源：放置到 `resources/base/media/` 目录
2. 字符串资源：在 `resources/base/element/string.json` 中定义
3. 颜色资源：在 `resources/base/element/color.json` 中定义

### 组件目录结构（推荐）

```
entry/src/main/ets/
├── components/           # 公共组件
│   ├── Header.ets
│   ├── Footer.ets
│   └── LoadingView.ets
├── common/              # 常量定义
│   ├── constants.ets
│   └── styles.ets
├── models/              # 数据模型
│   └── UserModel.ets
├── services/           # 服务层
│   ├── HttpService.ets
│   └── StorageService.ets
├── utils/              # 工具函数
│   ├── Logger.ets
│   └── Format.ets
└── pages/              # 页面
    ├── Index/
    ├── Detail/
    └── Settings/
```
