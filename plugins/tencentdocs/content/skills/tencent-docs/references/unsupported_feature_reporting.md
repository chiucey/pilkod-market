# 不支持能力上报规范（report_unsupported_feature）

当当前工具集合无法满足用户意图时，先报告具体限制。只有用户明确要求提交反馈，并且当前 tencentdocs Connector 暴露了 `report_unsupported_feature` 对应工具时，才通过该 Connector 上报。

## 可反馈的情况

在用户已授权反馈的前提下，可说明以下情况：

1. 工具列表中找不到可直接完成用户原始意图的工具
2. 虽有相关工具，但 schema/参数能力不满足关键约束（例如用户要求插入图片对象，但工具仅支持文本写入）

## 参数填写规范（强制）

调用 `report_unsupported_feature` 时，使用以下 JSON 结构：

```json
{
  "feature": "<简短动宾短语，描述用户原始意图>",
  "user_prompt": "<用户同意分享的需求摘要>",
  "doc_type": "<涉及文档类型：sheet/doc/smartcanvas/smartsheet/slide/mind/flowchart/form；不涉及则留空字符串>"
}
```

### 字段说明

- `feature`：用简短动宾短语描述用户原始意图（如：`在在线sheet插入图片对象`、`设置文档密码`）
- `user_prompt`：只包含用户同意分享的需求摘要，移除文档内容、凭证和个人敏感信息
- `doc_type`：仅填当前请求涉及的文档类型；不涉及时填空字符串 `""`
