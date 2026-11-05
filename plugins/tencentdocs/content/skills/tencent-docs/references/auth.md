# 腾讯文档 Connector 鉴权

本插件通过 MiniMax Connector 连接腾讯文档。首次使用时，在客户端完成 `tencentdocs` App 的授权；Token、端点和会话状态由 Connector 管理，Skill 不读取、打印或写入凭证。

如果调用返回未授权或 Token 过期：

1. 打开插件或连接器设置，重新连接 `tencentdocs`。
2. 在授权页面完成 QQ 或微信登录。
3. 回到原任务，重新调用失败的 Connector 工具。

不要把腾讯文档 Connector URL、Authorization header 或 Token 写入本地配置。需要确认工具名称时，使用客户端提供的 Connector 工具发现能力，并以当前返回的 `connector__tencentdocs__...` 工具名为准。
