# XML配置参数表

## project.c3proj 参数

### 基础信息

| 参数 | XPath | 类型 | 说明 |
|-----|-------|------|------|
| game_name | //name | string | 游戏名称 |
| description | //description | string | 游戏描述 |
| author | //author | string | 作者 |
| version | //version | string | 版本号 |

### 画布设置

| 参数 | XPath | 类型 | 默认值 |
|-----|-------|------|--------|
| width | //window/width | number | 540 |
| height | //window/height | number | 960 |
| fps | //fps | number | 60 |
| pixel_rounding | //pixelrounding | boolean | true |

### 导出配置

| 参数 | XPath | 类型 | 说明 |
|-----|-------|------|------|
| package_name | //android/package | string | Android包名 |
| bundle_id | //ios/bundleIdentifier | string | iOS包标识 |
| min_sdk | //android/minSdkVersion | number | 最低Android版本 |
| target_sdk | //android/targetSdkVersion | number | 目标Android版本 |

## *.uilayout 参数

### 场景属性

| 参数 | XPath | 类型 | 说明 |
|-----|-------|------|------|
| name | //name | string | 场景名称 |
| width | //window/width | number | 场景宽度 |
| height | //window/height | number | 场景高度 |
| background_color | //background | color | 背景色 |

## *.uevents 参数

### 变量定义

| 参数 | XPath | 类型 | 说明 |
|-----|-------|------|------|
| variable_name | //variables/variable/@name | string | 变量名 |
| variable_type | //variables/variable/@type | string | 变量类型 |
| initial_value | //variables/variable | any | 初始值 |

### 事件属性

| 参数 | 说明 |
|-----|------|
| event.id | 事件唯一ID |
| event.description | 事件描述 |
| conditions | 条件列表 |
| actions | 动作列表 |

## 广告配置参数

| 参数 | 用途 | 格式 |
|-----|------|------|
| tiktok_app_id | TikTok应用ID | string |
| tiktok_rewarded_id | 激励视频广告位ID | string |
| tiktok_interstitial_id | 插屏广告位ID | string |
| admob_app_id | AdMob应用ID | string |
| admob_rewarded_id | AdMob激励视频ID | string |

## 游戏平衡参数

| 参数 | 范围 | 说明 |
|-----|------|------|
| click_reward | 1-99999 | 点击收益 |
| upgrade_cost_base | 10-9999999 | 基础升级价格 |
| difficulty | 0.1-10.0 | 难度系数 |
| coin_rate | 1-9999 | 金币产出倍率 |
| ad_frequency | 1-999 | 广告触发间隔(秒) |

## 参数修改示例

```python
# 修改项目名称
editor.update_project_property('project.c3proj', 'game_name', 'New Game Name')

# 修改画布尺寸
editor.update_project_property('project.c3proj', 'canvas_width', 1080)
editor.update_project_property('project.c3proj', 'canvas_height', 1920)

# 修改导出配置
editor.update_export_config('project.c3proj', {
    'package_name': 'com.gamestudio.newgame',
    'bundle_id': 'com.gamestudio.newgame'
})
```
