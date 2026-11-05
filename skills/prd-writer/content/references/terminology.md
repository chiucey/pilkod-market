# PRD术语对照表

本文档提供口语化表达与专业PRD术语的对照参考。

## 功能描述类

| 用户口语表达 | 专业PRD表述 |
|-------------|------------|
| 让用户能找到东西 | 搜索功能：支持关键词联想、模糊匹配、高级搜索、搜索历史、热门搜索、结果筛选与排序 |
| 让用户能下单买东西 | 交易功能：商品展示、购物车、订单确认、支付结算、物流跟踪、售后服务 |
| 让用户能支付 | 支付功能：支持支付宝/微信/银行卡/钱包，退款机制，订单对账，风控拦截 |
| 让用户能聊天 | 即时通讯：单聊/群聊、消息类型（文本/图片/语音/文件）、消息状态（已读/未读）、离线消息 |
| 消息能及时收到 | 消息推送：推送到达率≥95%，延迟≤3秒，支持离线消息/APNs，订阅/退订管理 |
| 能看到各种数据 | 数据看板：支持多维度筛选、时间范围选择、数据导出、实时/定期刷新 |
| 能管理各种设置 | 配置管理：支持字段配置、流程配置、规则配置，配置预览与生效 |
| 能上传下载文件 | 文件管理：支持上传（格式/大小限制）、下载、在线预览、版本管理 |

## 用户体验类

| 用户口语表达 | 专业PRD表述 |
|-------------|------------|
| 操作要简单 | UX要求：核心路径≤3步，关键操作一步可达，信息架构扁平化，减少用户决策负担 |
| 页面要好看 | UI要求：符合品牌视觉规范，遵循平台设计语言，组件一致性，交互动效流畅 |
| 要让用户看懂 | 可用性要求：信息层级清晰，关键信息突出，错误提示明确，操作引导直观 |
| 要加载快 | 性能要求：首屏加载≤2秒，页面切换≤1秒，接口响应≤500ms |
| 要适配各种手机 | 兼容性要求：支持iOS/Android主流版本，主流屏幕尺寸适配，安全区域适配 |
| 要能离线用 | 离线能力：本地数据缓存，离线操作队列，网络恢复后自动同步 |

## 技术实现类

| 用户口语表达 | 专业PRD表述 |
|-------------|------------|
| 数据要安全 | 安全要求：传输加密(TLS 1.2+)，存储加密(AES-256)，敏感数据脱敏，密码加密(bcrypt) |
| 要能承受很多人用 | 性能要求：支持X万并发，峰值QPS≥X，响应时间P99≤Xms |
| 要能7*24小时运行 | 可用性要求：系统可用性≥99.9%，故障恢复时间≤30分钟，监控告警覆盖 |
| 要能备份数据 | 数据安全：定期全量/增量备份，备份保留X天，跨机房容灾，数据恢复演练 |
| 要能升级更新 | 升级能力：热更新/灰度发布，支持回滚，更新包校验，版本管理 |
| 要对接其他系统 | 集成能力：OpenAPI/RESTful API，Webhook回调，SSO单点登录，OAuth2.0授权 |

## 业务术语类

| 用户口语表达 | 专业PRD表述 |
|-------------|------------|
| 获客 | 用户获取：新增用户数、获取成本(CAC)、渠道转化率、ROI |
| 留存 | 用户留存：次日/7日/30日留存率，留存曲线，流失用户分析 |
| 促活 | 用户活跃：DAU/MAU，活跃度指标，功能使用率，Push触达率 |
| 转化 | 转化漏斗：曝光→点击→访问→注册→首单→复购，各环节转化率 |
| 变现 | 商业变现：GMV、ARPU、付费率、客单价、LTV |
| 裂变 | 病毒传播：分享率、K因子、裂变系数、邀请转化率 |

## 优先级术语

| 口语表达 | 规范标注 | 含义 |
|---------|---------|------|
| 必须做 | P0 | 阻塞级，MVP必须包含，否则无法发布 |
| 重要做 | P1 | 重要级，核心体验，短期必须实现 |
| 最好做 | P2 | 增强级，体验优化，可分阶段实现 |
| 可以做 | P3 | 观察级，后续版本视情况决定 |

## 指标术语

| 口语表达 | 专业指标 | 定义 |
|---------|---------|------|
| 日活 | DAU | Daily Active Users，日活跃用户数 |
| 月活 | MAU | Monthly Active Users，月活跃用户数 |
| 转化 | CVR | Conversion Rate，转化率 |
| 点击 | CTR | Click Through Rate，点击率 |
| 留存 | Retention | 用户在某时间后回访的比例 |
| 流失 | Churn | 用户停止使用的比例 |
| 推荐 | NPS | Net Promoter Score，净推荐值 |
| 价值 | LTV | Life Time Value，用户生命周期价值 |

## 常用缩略语

| 缩写 | 全称 | 中文含义 |
|-----|------|---------|
| MVP | Minimum Viable Product | 最小可行产品 |
| PRD | Product Requirements Document | 产品需求文档 |
| PM | Product Manager | 产品经理 |
| UX | User Experience | 用户体验 |
| UI | User Interface | 用户界面 |
| KPI | Key Performance Indicator | 关键绩效指标 |
| OKR | Objectives and Key Results | 目标与关键成果 |
| DAU | Daily Active Users | 日活跃用户数 |
| MAU | Monthly Active Users | 月活跃用户数 |
| GMV | Gross Merchandise Volume | 商品交易总额 |
| ARPU | Average Revenue Per User | 每用户平均收入 |
| CAC | Customer Acquisition Cost | 客户获取成本 |
| LTV | Life Time Value | 生命周期价值 |
| ROI | Return on Investment | 投资回报率 |
| CTR | Click Through Rate | 点击率 |
| CVR | Conversion Rate | 转化率 |
| B端 | Business | 企业端/商家端 |
| C端 | Customer | 消费者端/用户端 |
| SDK | Software Development Kit | 软件开发包 |
| API | Application Programming Interface | 应用程序接口 |
| SSO | Single Sign On | 单点登录 |
| ORM | Object-Relational Mapping | 对象关系映射 |
| SaaS | Software as a Service | 软件即服务 |
| PaaS | Platform as a Service | 平台即服务 |
| IaaS | Infrastructure as a Service | 基础设施即服务 |
| DB | Database | 数据库 |
| QA | Quality Assurance | 质量保证 |
| UAT | User Acceptance Test | 用户验收测试 |