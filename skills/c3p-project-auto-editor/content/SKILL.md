---
name: c3p-project-auto-editor
description: Construct3 C3P项目自动编辑器。当用户要求修改.c3p项目文件、批量替换游戏资源、修改游戏数值配置、编辑事件表逻辑、程序化定制Construct3游戏时使用。实现纯编程方式全自动编辑.c3p项目文件，零人工干预完成项目定制化改造。
---

# Construct3 C3P项目自动编辑器

专为Claw智能体打造的全自动Construct3 .c3p项目文件编辑器，实现纯编程方式解析、编辑、重构.c3p项目文件，无需手动打开Construct3软件。

## 核心能力

### 1. .c3p文件解析器
- 识别.c3p为加密ZIP压缩包
- 自动解压/加密打包
- 兼容Construct3 R300+全版本
- 无格式损坏、无导入报错

### 2. XML配置文件编辑器
- 程序化定位核心XML文件
- 增删改查项目全局参数
- 无XML语法错误
- 无节点丢失

### 3. 资源文件替换器
- 自动化匹配资源路径
- 批量替换图片/音效/图标
- 保留原文件层级结构
- 适配游戏加载逻辑

### 4. 事件表修改器
- 精准定位事件表配置区块
- 修改游戏逻辑参数
- 调整数值规则和触发条件
- 不破坏原有事件逻辑结构

## 技术原理

### .c3p文件结构

```
template.c3p (ZIP加密压缩包)
├── project.c3proj          # 主项目配置 (XML)
├── project.uistate.json    # UI状态配置
├── layouts/               # 场景布局目录
│   ├── layout1.uilayout    # 场景配置 (XML)
│   └── ...
├── eventSheets/           # 事件表目录
│   ├── events1.uevents     # 事件逻辑 (XML)
│   └── ...
├── objectTypes/           # 对象类型目录
│   └── *.uot              # 对象类型定义
├── animations/            # 动画配置
├── media/                  # 媒体资源目录
│   ├── images/             # 图片资源
│   ├── audio/              # 音频资源
│   └── fonts/              # 字体资源
└── icons/                  # 应用图标
```

### 处理流程

```
输入模板.c3p → 解压 → 解析XML → 修改配置 → 替换资源 → 重新打包 → 输出定制.c3p
```

## 配置参数

### 基础信息
| 参数 | 说明 | 示例 |
|-----|------|------|
| game_name | 游戏名称 | "My Awesome Game" |
| description | 游戏描述 | "A fun casual game" |
| author | 作者信息 | "Game Studio" |
| version | 版本号 | "1.0.0" |

### 美术资源替换
| 参数 | 说明 | 支持格式 |
|-----|------|---------|
| app_icon | 应用图标 | PNG (512x512) |
| splash_image | 启动画面 | PNG |
| background | 主背景图 | PNG/JPG |
| ui_elements | UI元素 | PNG |
| sprites | 游戏精灵 | PNG |

### 核心数值配置
| 参数 | 说明 | 范围 |
|-----|------|------|
| click_reward | 点击收益 | 1-99999 |
| upgrade_cost | 升级价格 | 10-9999999 |
| difficulty | 难度系数 | 0.1-10.0 |
| coin_rate | 金币产出 | 1-9999 |
| ad_frequency | 广告频次 | 1-999 |

### 广告商业化配置
| 参数 | 说明 | 平台 |
|-----|------|------|
| tiktok_app_id | TikTok应用ID | TikTok |
| tiktok_rewarded_id | 激励视频ID | TikTok |
| tiktok_interstitial_id | 插屏广告ID | TikTok |
| admob_app_id | AdMob应用ID | AdMob |
| admob_rewarded_id | 激励视频ID | AdMob |

### 导出配置
| 参数 | 说明 | 示例 |
|-----|------|------|
| package_name | 包名 | "com.gamestudio.myawesomegame" |
| bundle_id | iOS包标识 | "com.gamestudio.myawesomegame" |
| orientation | 屏幕方向 | "portrait" |
| min_sdk | 最低SDK | 21 |

## 使用触发词

- 修改c3p文件
- 编辑c3p项目
- 替换c3p资源
- 修改游戏数值
- 编辑事件表
- 批量替换游戏素材
- c3p项目定制
- 程序化编辑c3p
- 修改c3p配置

## 执行流程

### 标准流程

```
1. 解析模板.c3p文件
2. 读取项目结构
3. 应用配置参数修改
4. 替换资源文件
5. 更新事件表参数
6. 重新打包输出
7. 生成修改日志
```

### 详细步骤

#### 阶段1：解析
1. 识别.c3p文件类型
2. 解压到临时目录
3. 解析project.c3proj
4. 定位需要修改的文件

#### 阶段2：编辑
1. 修改项目基础信息
2. 更新资源配置路径
3. 调整核心数值参数
4. 更新广告配置ID
5. 修改导出参数

#### 阶段3：打包
1. 验证XML语法
2. 重新压缩打包
3. 应用加密保护
4. 输出标准.c3p文件

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 文件损坏 | 自动检测并提示修复 |
| 格式不兼容 | 尝试兼容适配 |
| 资源路径错误 | 自动修正路径 |
| XML语法错误 | 自动修复 |
| 权限问题 | 提示用户授权 |

## 输出产物

1. **定制.c3p文件** - 可直接导入Construct3
2. **修改日志.json** - 记录所有变更明细
3. **错误报告.txt** - 如有错误，提供详情

## 参考文档

- [C3P文件格式详解](references/c3p_format.md)
- [XML配置参数表](references/xml_parameters.md)
- [资源替换指南](references/resource_replacement.md)
- [事件表修改指南](references/event_modification.md)
