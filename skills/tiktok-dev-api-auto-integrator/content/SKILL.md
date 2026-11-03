---
name: tiktok-dev-api-auto-integrator
description: TikTok开发者API自动集成器。当用户要求自动化TikTok小游戏上线、申请广告位、管理开发者账号、上传游戏包、监控审核状态时使用。与Construct3编辑器插件无缝对接，实现游戏从开发到变现的全链路自动化。
---

# TikTok Developer API Auto-Integrator

专为Claw智能体打造的全自动TikTok开发者API集成器，通过官方OpenAPI完成开发者后台所有操作，与Construct3编辑器形成闭环，实现游戏从生成到变现的全链路自动化。

## 核心功能

### 1. OAuth授权自动化
- 自动完成账号登录授权
- Token自动刷新
- 权限自动校验
- 过期自动重授权

### 2. 应用管理自动化
- 程序化创建MiniGame应用
- 修改应用配置
- 更新基础信息
- 多账号切换

### 3. 游戏包上传自动化
- 大文件断点续传
- 格式自动校验
- 上传进度监控
- 失败自动重试

### 4. 审核状态监控
- 实时轮询审核状态
- 状态变更通知
- 驳回整改报告生成

### 5. 广告位管理
- 激励视频广告位申请
- 插屏广告位申请
- 广告配置自动注入

## 技术架构

```
TikTok Dev API Auto-Integrator
├── OAuth Auth Module      # OAuth2.0授权管理
├── API Client             # TikTok OpenAPI客户端
├── App Manager           # 应用管理
├── Upload Manager         # 文件上传
├── Review Monitor        # 审核监控
└── Config Loader         # 配置管理
```

## 执行流程

### 标准流程（7步完成）

```
① 账号绑定/选择
    ↓
② 创建MiniGame应用
    ↓
③ 上传HTML5游戏包
    ↓
④ 填写应用信息
    ↓
⑤ 申请广告位
    ↓
⑥ 返回AppID和广告位ID
    ↓
⑦ 监控审核状态
```

### 与Construct3编辑器协同

```
Construct3编辑器 → 生成.c3p → TikTok API集成器 → 上传发布 → 广告变现
```

## 配置参数

### 必填参数
| 参数 | 说明 |
|-----|------|
| client_key | TikTok应用Client Key |
| client_secret | TikTok应用Client Secret |
| redirect_uri | OAuth回调地址 |

### 可选参数
| 参数 | 说明 |
|-----|------|
| account_id | 开发者账号ID |
| access_token | 已有访问令牌 |
| refresh_token | 刷新令牌 |

## 使用触发词

- TikTok小游戏上线
- 申请TikTok广告位
- 上传TikTok游戏包
- TikTok开发者API
- 自动申请AppID
- 监控审核状态
- TikTok开发者自动化
- 多账号切换

## API端点覆盖

| 功能 | API端点 |
|-----|--------|
| OAuth授权 | /oauth/authorize |
| 获取Token | /oauth/token |
| 刷新Token | /oauth/refresh_token |
| 创建应用 | /miniapp/v2/app/create |
| 获取应用列表 | /miniapp/v2/app/list |
| 更新应用 | /miniapp/v2/app/update |
| 上传游戏包 | /miniapp/v2/app/upload |
| 申请广告位 | /miniapp/v2/ad/create |
| 获取审核状态 | /miniapp/v2/app/status |

## 输出产物

| 产物 | 说明 |
|-----|------|
| AppID | TikTok MiniGame应用ID |
| AdUnitID (Rewarded) | 激励视频广告位ID |
| AdUnitID (Interstitial) | 插屏广告位ID |
| 执行日志 | 完整操作日志 |
| 审核报告 | 审核状态报告 |

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 授权过期 | 自动刷新Token |
| 上传失败 | 自动重试3次 |
| 审核驳回 | 生成整改报告 |
| API限流 | 等待后重试 |
| 网络异常 | 自动重连 |

## 参考文档

- [API对接指南](references/api_guide.md)
- [OAuth授权教程](references/oauth_tutorial.md)
- [常见错误解决方案](references/troubleshooting.md)
- [配置参数说明](references/config_params.md)
