# TikTok Ads API 规格参考

## API 基础信息

### 认证方式
- **OAuth 2.0**：适用于第三方应用授权
- **Access Token**：适用于自建应用

### 基础端点
```
生产环境: https://ads.tiktok.com
沙盒环境: https://sandbox-ads.tiktok.com
```

### 常用API端点

#### 1. 广告账户

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /advertiser/info/ | 获取账户信息 |
| GET | /advertiser/list/ | 获取广告账户列表 |

#### 2. 广告系列

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /campaign/list/ | 获取广告系列列表 |
| POST | /campaign/create/ | 创建广告系列 |
| PUT | /campaign/update/ | 更新广告系列 |
| DELETE | /campaign/delete/ | 删除广告系列 |

#### 3. 广告组

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /adgroup/list/ | 获取广告组列表 |
| POST | /adgroup/create/ | 创建广告组 |
| PUT | /adgroup/update/ | 更新广告组 |
| PUT | /adgroup/status/ | 修改广告组状态 |

#### 4. 广告创意

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /ad/list/ | 获取广告列表 |
| POST | /ad/create/ | 创建广告 |
| PUT | /ad/update/ | 更新广告 |

#### 5. 数据报表

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /report/native/ | 获取原生报表数据 |
| GET | /report/integrated/ | 获取综合报表数据 |

### 请求参数示例

#### 创建广告系列
```json
{
  "advertiser_id": "123456789",
  "campaign_name": "夏季新品推广",
  "objective_type": "CONVERSIONS",
  "budget_mode": "BUDGET_MODE_DAY",
  "budget": 1000,
  "status": "CAMPAIGN_STATUS_ENABLE"
}
```

#### 获取报表数据
```json
{
  "advertiser_id": "123456789",
  "page_size": 20,
  "page": 1,
  "level": "ADGROUP",
  "fields": [
    "campaign_id",
    "adgroup_id",
    "spend",
    "impression",
    "click",
    "conversion",
    "cpm",
    "cpc",
    "ctr",
    "cvr",
    "cpa",
    "roas"
  ],
  "time_increment": 1,
  "start_date": "2026-03-01",
  "end_date": "2026-03-31"
}
```

### 字段映射

| 中文名 | 英文字段 | 数据类型 |
|--------|----------|----------|
| 广告系列ID | campaign_id | String |
| 广告组ID | adgroup_id | String |
| 广告ID | ad_id | String |
| 花费 | spend | Number |
| 展示数 | impression | Integer |
| 点击数 | click | Integer |
| 转化数 | conversion | Integer |
| 千展成本 | cpm | Number |
| 点击成本 | cpc | Number |
| 点击率 | ctr | Number |
| 转化率 | cvr | Number |
| 单成本 | cpa | Number |
| 回报率 | roas | Number |

### 状态枚举

#### 广告系列状态
- `CAMPAIGN_STATUS_ENABLE` - 已启用
- `CAMPAIGN_STATUS_DISABLE` - 已暂停
- `CAMPAIGN_STATUS_DELETED` - 已删除

#### 广告组状态
- `AD_STATUS_ENABLE` - 已启用
- `AD_STATUS_DISABLE` - 已暂停
- `AD_STATUS_DELETE` - 已删除

### 推广目的类型

| 类型 | 说明 |
|------|------|
| APP_INSTALL | 应用安装 |
| LEAD_GENERATION | 线索收集 |
| CONVERSIONS | 网页转化 |
| VIDEO_VIEW | 视频播放量 |
| BRAND_AWARENESS | 品牌认知 |
| TRAFFIC | 网站访问 |

### 出价优化目标

| 目标 | 字段值 |
|------|--------|
| 优化点击 | `click` |
| 优化转化 | `conversion` |
| 优化曝光 | `reach` |
| 优化视频播放 | `video_view` |
| 优化表单提交 | `form` |

### 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 10001 | 参数错误 |
| 10002 | 认证失败 |
| 10003 | 权限不足 |
| 20001 | 账户无效 |
| 20002 | 余额不足 |
| 30001 | 创意审核拒绝 |

### 速率限制

- **QPS限制**：每秒最多20个请求
- **日调用限制**：根据账户等级不同
- **建议重试**：遇到限流时等待60秒后重试

### Webhook 配置

支持的事件类型：
- `campaign_status_changed` - 广告系列状态变更
- `ad_review_result` - 审核结果
- `daily_report_ready` - 日报数据就绪
