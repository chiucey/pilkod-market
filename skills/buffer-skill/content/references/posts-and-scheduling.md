# 帖子与排程

## 排程类型

### addToQueue（自动排队）

自动安排到下一个可用时间槽：

```graphql
mutation {
  createPost(input: {
    text: "Automatically scheduled post",
    channelId: "your_channel_id",
    schedulingType: automatic,
    mode: addToQueue
  }) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}
```

### customScheduled（定时发布）

指定精确发布时间：

```graphql
mutation {
  createPost(input: {
    text: "Scheduled for a specific time",
    channelId: "your_channel_id",
    schedulingType: automatic,
    mode: customScheduled,
    dueAt: "2026-03-10T15:00:00.000Z"
  }) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}
```

## 帖子状态

- **scheduled** - 在队列中等待发布
- **sent** - 已成功发布
- **error** - 发布失败（如频道断开）

## 查询帖子

```graphql
query {
  posts(
    first: 20,
    input: {
      organizationId: "your_org_id",
      filter: {
        status: [sent],
        channelIds: ["your_channel_id"]
      }
    }
  ) {
    edges {
      node {
        id
        text
        dueAt
        channelId
        status
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## 分页

使用 `first` 和 `after` 进行游标分页：

```graphql
query {
  posts(
    first: 10,
    after: "cursor_value",
    input: { organizationId: "your_org_id" }
  ) {
    edges { node { id text } }
    pageInfo { hasNextPage endCursor }
  }
}
```