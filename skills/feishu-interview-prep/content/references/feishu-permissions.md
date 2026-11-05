---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450221009a466187ece8c17fd1f74fea8d1c0f54cc415c36569297d553ee4c415238ca7102202dd74594e9a93138f6bbabce70372e1dd35a62802096b75cc0ae95f41799b412
    ReservedCode2: 304502207573f9b2803a8222d2e00c5e677ee2f9a200e3ace57f60649cb47eeec161c3bc022100e9775222adf1c74d861dfd126da99ec2284f62ba7e7a23c8c164f093628c0aac
---

# 飞书权限配置说明

## 应用权限配置

在使用本技能前，需要在飞书开放平台配置应用权限。

### 配置地址

访问 `https://open.feishu.cn/app/` 并选择您的应用。

### 必需权限清单

#### Tenant 级别权限（应用权限）

```json
{
  "scopes": {
    "tenant": [
      "application:application:self_manage",
      "cardkit:card:read",
      "cardkit:card:write",
      "contact:contact.base:readonly",
      "contact:user.basic_profile:readonly",
      "docx:document",
      "docx:document.block:convert",
      "docx:document:create",
      "docx:document:readonly",
      "docx:document:write_only",
      "drive:drive",
      "im:chat:read",
      "im:chat:update",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:message.pins:read",
      "im:message.pins:write_only",
      "im:message.reactions:read",
      "im:message.reactions:write_only",
      "im:message:readonly",
      "im:message:recall",
      "im:message:send_as_bot",
      "im:message:send_multi_users",
      "im:message:send_sys_msg",
      "im:message:update",
      "im:resource",
      "wiki:space:write_only",
      "wiki:wiki"
    ]
  }
}
```

#### User 级别权限（用户权限）

```json
{
  "scopes": {
    "user": [
      "base:app:copy",
      "base:app:create",
      "base:app:read",
      "base:app:update",
      "base:field:create",
      "base:field:delete",
      "base:field:read",
      "base:field:update",
      "base:record:create",
      "base:record:delete",
      "base:record:retrieve",
      "base:record:update",
      "base:table:create",
      "base:table:delete",
      "base:table:read",
      "base:table:update",
      "base:view:read",
      "base:view:write_only",
      "board:whiteboard:node:create",
      "board:whiteboard:node:read",
      "calendar:calendar.event:create",
      "calendar:calendar.event:delete",
      "calendar:calendar.event:read",
      "calendar:calendar.event:reply",
      "calendar:calendar.event:update",
      "calendar:calendar.free_busy:read",
      "calendar:calendar:read",
      "contact:contact.base:readonly",
      "contact:user.base:readonly",
      "contact:user.basic_profile:readonly",
      "contact:user.employee_id:readonly",
      "contact:user:search",
      "docs:document.comment:create",
      "docs:document.comment:read",
      "docs:document.comment:update",
      "docs:document.comment:write_only",
      "docs:document.media:download",
      "docs:document.media:upload",
      "docs:document:copy",
      "docs:document:export",
      "docs:document:import",
      "docs:permission.member",
      "docx:document.block:convert",
      "docx:document:create",
      "docx:document:readonly",
      "docx:document:write_only",
      "drive:drive",
      "drive:drive.metadata:readonly",
      "drive:drive:version",
      "drive:file:download",
      "drive:file:upload",
      "im:chat.members:read",
      "im:chat:read",
      "im:message",
      "im:message.group_msg:get_as_user",
      "im:message.p2p_msg:get_as_user",
      "im:message:readonly",
      "offline_access",
      "search:docs:read",
      "search:message",
      "sheets:spreadsheet.meta:read",
      "sheets:spreadsheet:create",
      "sheets:spreadsheet:read",
      "sheets:spreadsheet:write_only",
      "space:document:delete",
      "space:document:move",
      "space:document:retrieve",
      "task:comment:read",
      "task:comment:write",
      "task:task:read",
      "task:task:write",
      "task:task:writeonly",
      "task:tasklist:read",
      "task:tasklist:write",
      "wiki:node:copy",
      "wiki:node:create",
      "wiki:node:move",
      "wiki:node:read",
      "wiki:node:retrieve",
      "wiki:space:read",
      "wiki:space:retrieve",
      "wiki:space:write_only"
    ]
  }
}
```

## Wiki 文档编辑权限

### 配置步骤

1. 访问 `https://my.feishu.cn/wiki/`
2. 找到您的文档根目录
3. 打开目标文档
4. 点击右上角「···」菜单
5. 选择「更多」选项
6. 点击「添加应用」
7. 将 MaxClaw 龙虾应用添加进去

### 权限说明

- 添加后，应用将获得该文档的编辑权限
- 可以创建、编辑文档内容
- 可以创建和管理飞书表格
- 可以同步更新面试进度

## 快速检查清单

- [ ] 在开放平台创建了应用
- [ ] 配置了所有必需的 Tenant 权限
- [ ] 配置了所有必需的用户权限
- [ ] 发布了应用版本
- [ ] 在 Wiki 中添加了应用权限
- [ ] 测试了文档读写功能
