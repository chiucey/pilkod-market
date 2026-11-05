# 微信读书

通过凭据型 App 连接微信读书。用户从[官方页面](https://weread.qq.com/r/weread-skills)获取 API Key，在 App 连接表单填写；无需把 Key 发给 Agent。

支持搜索、书架、书籍信息、目录、进度、个人划线与想法、笔记概览和阅读统计；不提供写入或整本正文下载。桌面和云端使用相同 Provider。

发布前必须部署独立 [matrix-mcpserver-weread](https://gitlab.xaminim.com/matrix/matrix-mcpserver-weread) 服务并在 Connector 配置 `weread` Provider。仅合并插件清单不会创建在线 App；部署、配置及真实账号验收见[服务部署文档](https://gitlab.xaminim.com/matrix/matrix-mcpserver-weread/-/blob/main/docs/deployment.md)。上游来源见 [PROVENANCE.md](PROVENANCE.md)。
