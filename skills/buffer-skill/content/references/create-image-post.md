# 创建图片帖子

## 基本流程

图片帖子需要先通过 Buffer 的 `createPost` mutation 上传图片。

## GraphQL Mutation

```graphql
mutation CreateImagePost {
  createPost(input: {
    text: "Check out this image!",
    channelId: "your_channel_id",
    schedulingType: automatic,
    mode: addToQueue,
    assets: [{
      mimeType: "image/jpeg",
      data: "base64_encoded_image_data"
    }]
  }) {
    ... on PostActionSuccess {
      post {
        id
        text
        dueAt
        assets {
          id
          mimeType
          url
        }
      }
    }
    ... on MutationError {
      message
    }
  }
}
```

## 支持的图片格式

- `image/jpeg`
- `image/png`
- `image/gif`

## 注意事项

1. 图片需要 base64 编码后传递
2. 文件大小建议不超过 10MB
3. 部分平台对图片尺寸有要求