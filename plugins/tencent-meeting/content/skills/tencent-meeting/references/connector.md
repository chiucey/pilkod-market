# Connector 调用约定

## 连接

本插件引用腾讯会议 App（provider `tencentmeeting`）。客户端负责连接状态、凭据输入、MCP 传输与请求头；Skill 只选择工具并提供业务参数。

通常 Connector 工具名形如 `connector__tencentmeeting__<业务工具>`；这是命名约定而不是可猜测的固定清单，实际名称必须从当前工具发现结果复制。

- 先确认 App 已连接并启用。若未连接，引导用户在客户端的 App/Connector 页面完成连接。
- 需要更新凭据时，在同一连接页面完成。不要在对话中索取 Token，不设置本地环境变量，也不把凭据放入工具参数。
- 不执行原项目的 Python 代理，不安装或调用 `tmeet`，不直接请求远程 MCP endpoint。
- 连接页面显示成功、或能够获取工具列表，只能说明连接检查通过。实际业务结果仍要检查错误对象与文本中的状态。

## 发现和调用

1. 使用当前运行环境的 Connector 工具发现能力，限定 `tencentmeeting` provider；如果宿主已经列出该 App 的工具，直接读取这份实时清单。
2. 找到与本技能业务标识匹配的工具，阅读完整 Schema。若完整名称带客户端命名空间，复制发现结果中的名称，不自行拼接。
3. 直接调用该工具，传入 Schema 定义的参数对象。不要在业务参数外再套 `jsonrpc`、`method`、`name` 或 `arguments`，除非当前调用工具的 Schema 明确要求该包装。
4. `api_references.md` 中的业务名称用于路由，JSON 仅是业务参数示例；参数类型、必填项、枚举和上限以当前工具 Schema 为准。
5. `meeting_id`、`record_file_id`、`meeting_record_id`、`minute_id`、`open_id` 等不相互替代。只使用用户明确提供或前序工具实际返回的标识；`meeting_id` 和成员内部 ID 仅在工具参数间透传，面向用户优先展示会议号和昵称。
6. `_client_info` 由 Connector 注入时不覆盖；若 Schema 要求调用方提供，则按实际运行环境填写 `os`、`agent`、`model`。不能假造环境值，也不为此向用户索取业务无关信息。

本文档不规定某个客户端专属的工具发现名称或命名空间；以当前会话提供的接口为准。未发现某个业务工具时，明确说明当前连接未提供该能力，不尝试调用猜测出的名称。

## 结果解析

Connector 可能直接返回结构化业务数据，也可能保留 MCP 的 `content` 数组。按当前返回形态读取：

- 检查传输层失败、`isError`、`error` 对象。
- 若 `content[].text` 是 JSON 文本，解析其中的业务状态、错误码、数据与追踪字段；不要只看最外层成功标记。
- `token not exit`、Token 无效等鉴权错误按错误字典引导更新 App 凭据。
- `has_more=true` 时将 `next_page_token` 原样用于下一页，不计算或猜测游标。滚动纪要按主文件要求拉取完整内容。
- 写操作超时或结果不明时，先查询当前状态确认是否已经生效，再决定是否重试，避免重复创建、邀请、呼叫或提交权限申请。
- 仅展示实际返回的追踪字段，不编造 `X-Tc-Trace` 或 `rpcUuid`。

## 旧项目中不由 Connector 提供的部分

原项目在本地代理中注入了 `get_skill_update_preference` 和 `set_skill_update_preference`，并读写本地更新状态。本插件没有这些本地工具和状态文件。

`convert_timestamp`、`check_skill_version` 不能仅凭旧 SKILL 的工具索引就视为当前 Connector 可用。相对时间使用当前运行环境的可信时间来源；版本更新遵循 [version_management.md](version_management.md)。
