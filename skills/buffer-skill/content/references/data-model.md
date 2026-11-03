# 数据模型

## 核心对象

### Organization（组织）

```json
{
  "id": "org_xxx",
  "name": "My Company",
  "createdAt": "2025-01-01T00:00:00.000Z"
}
```

### Channel（频道）

```json
{
  "id": "ch_xxx",
  "name": "My Twitter",
  "service": "twitter",
  "organizationId": "org_xxx"
}
```

**service 类型：** instagram, threads, linkedin, twitter, facebook, google_business, mastodon, youtube, pinterest, bluesky

### Post（帖子）

```json
{
  "id": "post_xxx",
  "text": "Hello from Buffer!",
  "channelId": "ch_xxx",
  "dueAt": "2026-03-10T15:00:00.000Z",
  "status": "scheduled",
  "assets": [
    { "id": "asset_xxx", "mimeType": "image/jpeg", "url": "https://..." }
  ]
}
```

## 关系图

```
Organization (组织)
    └── Channel (频道)
            └── Post (帖子)
                    └── Asset (资源/图片)
```