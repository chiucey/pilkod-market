# Construct3游戏导出配置指南

## 导出格式概述

Construct3支持多种导出格式，适用于不同平台发布需求。

### 主流导出格式对比

| 格式 | 适用平台 | 包体大小 | 加载速度 | 变现支持 |
|-----|---------|---------|---------|---------|
| **HTML5** | TikTok、FB、Web | 中等 | 快 | 优秀 |
| **Android (APK)** | Google Play | 较大 | 中等 | 良好 |
| **iOS** | App Store | 较大 | 中等 | 良好 |
| **Windows** | Steam、itch.io | 大 | 快 | 一般 |
| **Nintendo Switch** | Nintendo | 大 | 中等 | 优秀 |

---

## HTML5导出配置

### 推荐配置

```javascript
{
    "exportFormat": "html5",
    "minify": true,
    "debugMode": false,
    "compression": {
        "enabled": true,
        "level": 9
    },
    "inlineScripts": true,
    "inlineManifest": true,
    "preloadSounds": true,
    "pixelRounding": true,
    "highDPI": true,
    "deviceOrientation": "portrait"  // 竖屏优先
}
```

### 导出步骤

1. 打开Construct3编辑器
2. 点击菜单 File → Export project
3. 选择 HTML5 网站
4. 配置导出选项
5. 选择导出目录
6. 等待导出完成

### 优化设置

#### 图像优化

| 设置 | 推荐值 | 说明 |
|-----|-------|------|
| 纹理格式 | WebP (如果支持) / PNG | WebP更小 |
| 图像质量 | 85-90% | 平衡质量与大小 |
| 缩放模式 | Low quality scaling | 性能优先 |
| 精灵表 | 合并小图像 | 减少HTTP请求 |

#### 音频优化

| 设置 | 推荐值 | 说明 |
|-----|-------|------|
| 音频格式 | OGG + AAC | 跨浏览器支持 |
| 比特率 | 128kbps | 平衡质量与大小 |
| 流式播放 | 仅BGM | 音效预加载 |
| 单声道 | 仅音效 | 减少文件大小 |

---

## TikTok小游戏导出

### TikTok特定配置

```javascript
{
    "platform": "TikTok",
    "appId": "YOUR_APP_ID",
    "gameConfig": {
        "title": "游戏名称",
        "description": "游戏描述",
        "icon": "512x512 icon.png",
        "category": "休闲游戏",
        "tags": ["跑酷", "休闲", "解压"],
        "orientation": "portrait",
        "permissions": ["score", "leaderboard"]
    },
    "adConfig": {
        "rewardedVideo": true,
        "interstitial": true,
        "banner": false,
        "adUnitIds": {
            "rewarded": "YOUR_REWARDED_UNIT_ID",
            "interstitial": "YOUR_INTERSTITIAL_UNIT_ID"
        }
    }
}
```

### TikTok导出清单

- [ ] 游戏包体 < 10MB
- [ ] 竖屏适配（9:16）
- [ ] 触控操作优化
- [ ] 激励视频广告位集成
- [ ] 插屏广告位集成
- [ ] 排行榜功能（可选）
- [ ] 分享功能

---

## Facebook Instant Games导出

### FB特定配置

```javascript
{
    "platform": "Facebook",
    "gameConfig": {
        "appId": "YOUR_FB_APP_ID",
        "appSecret": "YOUR_SECRET",
        "canvasSize": {
            "width": 640,
            "height": 1136
        },
        "orientation": "portrait",
        "version": "v2.0"
    },
    "permissions": ["public_profile", "friends"]
}
```

### FB导出清单

- [ ] 640x1136画布尺寸
- [ ] FB SDK集成
- [ ] 玩家数据保存
- [ ] 分享功能
- [ ] 排行榜功能

---

## 移动端导出配置

### Android (APK) 配置

```javascript
{
    "platform": "Android",
    "packageName": "com.yourcompany.yourgame",
    "versionCode": 1,
    "versionName": "1.0.0",
    "minSdkVersion": 21,
    "targetSdkVersion": 30,
    "permissions": [
        "INTERNET",
        "ACCESS_NETWORK_STATE",
        "VIBRATE"
    ],
    "orientation": "portrait",
    "screenOrientation": "portrait",
    "resizeMode": "letterbox",
    "keyStore": "your-keystore.jks",
    "keyAlias": "your-key-alias"
}
```

### iOS配置

```javascript
{
    "platform": "iOS",
    "bundleId": "com.yourcompany.yourgame",
    "version": "1.0.0",
    "buildNumber": "1",
    "minIOSVersion": "10.0",
    "deviceFamily": "iPhone,iPad",
    "orientation": "Portrait",
    "requiredCapabilities": ["armv7"],
    "permissions": [
        "NSAppTransportSecurity"
    ]
}
```

---

## 发布检查清单

### 发布前必检项

#### 功能测试
- [ ] 游戏可正常开始
- [ ] 所有关卡可正常游玩
- [ ] 计分系统准确
- [ ] 保存/读取功能正常
- [ ] 广告正常显示

#### 性能测试
- [ ] 加载时间 < 5秒
- [ ] 运行帧率 > 55 FPS
- [ ] 无内存泄漏
- [ ] 无崩溃/卡死

#### 平台特定
- [ ] 触控操作流畅
- [ ] 横竖屏切换正常（如果支持）
- [ ] 音频正常播放
- [ ] 设备兼容测试

### 文件清单

| 文件类型 | 要求 | 检查 |
|---------|------|------|
| 游戏包 | ZIP格式 | □ |
| 图标 | 512x512 PNG | □ |
| 截图 | 至少3张 | □ |
| 描述文案 | 中英文 | □ |
| 隐私政策 | 合规链接 | □ |

---

## 平台特定要求

### TikTok Mini Game

```yaml
游戏要求:
  - 包体限制: 10MB以内
  - 画布尺寸: 540x960 (推荐)
  - 支持格式: HTML5
  - 触控支持: 必须
  - 网络请求: HTTPS

内容要求:
  - 无政治敏感内容
  - 无色情暴力内容
  - 无赌博元素
  - 适合全年龄段

广告要求:
  - 必须接入TikTok广告SDK
  - 支持激励视频
  - 支持插屏广告
```

### Google Play

```yaml
技术要求:
  - APK/AAB格式
  - 签名配置
  - 64位支持
  - Google Play服务

内容要求:
  - 隐私政策
  - 年龄分级
  - 内容分级
  - 广告标识

商店配置:
  - 应用名称
  - 简短描述
  - 完整描述
  - 截图
  - 图标
```

### App Store

```yaml
技术要求:
  - IPA格式
  - Xcode配置
  - 64位支持
  - App Transport Security

审核要求:
  - 演示账号
  - 详细描述
  - 隐私政策
  - 年龄分级

商店配置:
  - 应用名称
  - 关键词
  - 描述
  - 截图
  - 预览视频
```

---

## 常见导出问题

### HTML5导出问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| 加载白屏 | 跨域问题 | 使用相对路径 |
| 音频不播放 | 格式不支持 | 转换OGG格式 |
| 内存占用高 | 未压缩纹理 | 使用压缩纹理 |
| 帧率低 | 复杂逻辑 | 优化事件表 |

### 移动端导出问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| APK过大 | 包含未使用资源 | 清理资源 |
| 安装失败 | 签名问题 | 重新签名 |
| 崩溃 | 内存溢出 | 减少内存占用 |
| 黑屏 | 兼容性问题 | 检查设备要求 |

---

## 导出后处理

### 1. 文件压缩

```bash
# 压缩游戏包
zip -r game.zip dist/

# 进一步压缩（可选）
# 使用gzip压缩
gzip -9 game.zip
```

### 2. CDN部署

```javascript
// CDN配置建议
const cdnConfig = {
    baseUrl: "https://cdn.yourgame.com/",
    versions: ["v1", "v2"],
    fallback: "https://backup.cdn.com/",
    cacheTime: 3600 * 24 * 30 // 30天缓存
};
```

### 3. 版本管理

```javascript
const version = {
    major: 1,  // 大版本更新
    minor: 0,  // 新功能
    patch: 0,  // Bug修复
    build: 123 // 构建号
};
```

---

## 持续优化

### 发布后监控

| 指标 | 监控内容 |
|-----|---------|
| 加载时间 | 首屏加载、关卡加载 |
| 性能 | FPS、内存、CPU |
| 错误 | 控制台错误、崩溃报告 |
| 用户行为 | 流失点、停留时长 |

### 迭代优化

1. 根据数据反馈调整难度曲线
2. 优化卡顿关卡的性能
3. 修复用户反馈的问题
4. 持续更新内容和活动
