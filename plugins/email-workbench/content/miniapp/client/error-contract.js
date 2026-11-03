import { t } from './i18n.js';
/** Reviewed, non-secret error contract shared by the page and HTTP boundary.
 * Adding wording does not publish a server code: httpSafe must be explicit.
 * Never interpolate provider responses, credentials, paths or message contents.
 */
export const errorDefinitions = Object.freeze({
  EMAIL_SYNC_UNAVAILABLE: { message: t("邮箱连接配置未同步，请检查网络后刷新重试。当前输入已保留；云端能力尚未启用时请联系管理员。"), httpSafe: true },
  EMAIL_SYNC_AUTH_REQUIRED: { message: t("请重新登录 MCode 后打开邮箱工作台，当前输入已保留。"), httpSafe: true },
  EMAIL_SYNC_ACCOUNT_CHANGED: { message: t("MCode 登录账号已变化，已停止使用原账号的邮箱连接。请重新打开工作台。"), httpSafe: true },
  EMAIL_SYNC_CONFLICT: { message: t("邮箱连接已在另一台设备更新，本次修改未覆盖它。请保留当前输入，刷新配置后核对再保存。"), httpSafe: true },
  EMAIL_SYNC_TOO_LARGE: { message: t("邮箱连接配置超过云端容量（4 KiB），未保存。请减少连接数量后重试。"), httpSafe: true },
  EMAIL_SYNC_INVALID: { message: t("邮箱连接配置格式不正确，未保存。请检查输入后重试。"), httpSafe: true },
  EMAIL_SYNC_CORRUPT: { message: t("云端邮箱连接配置无法验证，已有数据已保留。请联系管理员恢复。"), httpSafe: true },
  MAILBOX_AUTH_FAILED: { message: t("邮箱认证被拒绝，请检查授权码、协议权限和组织策略。"), httpSafe: true },
  MAILBOX_CLIENT_REJECTED: { message: t("邮箱已登录，但服务商拒绝了当前客户端的收信请求（Unsafe Login）。"), httpSafe: true },
  MAILBOX_OPEN_FAILED: { message: t("邮箱已登录，但打开邮件文件夹失败。"), httpSafe: true },
  MAILBOX_QUERY_FAILED: { message: t("邮件文件夹已打开，但服务商未能完成邮件查询。"), httpSafe: true },
  MAILBOX_FETCH_FAILED: { message: t("已查到邮件，但读取邮件列表失败。"), httpSafe: true },
  MAILBOX_NETWORK_FAILED: { message: t("无法连接邮箱服务器，请核对网络或服务器设置。"), httpSafe: true },
  MAILBOX_TLS_FAILED: { message: t("邮箱服务器证书或加密连接未通过验证。"), httpSafe: true },
  MAILBOX_MOVE_UNSUPPORTED: { message: t("服务商未提供原子移动能力，请在服务商网页中移动邮件。"), httpSafe: true },
  MAILBOX_OUTCOME_UNKNOWN: { message: t("移动结果不确定，请刷新原文件夹和目标文件夹核对；不会自动重试。"), httpSafe: true },
  MAILBOX_UNAVAILABLE: { message: t("邮箱暂不可用，请核对连接和服务商状态。"), httpSafe: true },
  BATCH_CONFLICT: { message: t("此请求已有固定清单，请核对原任务。"), httpSafe: true },
  CONFIRMATION_EXPIRED: { message: t("这次发送确认已过期。请重新检查最新草稿并发起确认。"), httpSafe: true },
  DRAFT_LOCKED: { message: t("草稿已进入发送流程，请先查看当前清单。"), httpSafe: true },
  UI_EDIT_BLOCKED: { message: t("页面仍有未保存输入，请先完成保存。"), httpSafe: true },
  UI_CONTEXT_STALE: { message: t("页面状态已变化或已离线，请刷新上下文后重试。"), httpSafe: true },
  CONFIRMATION_INVALID: { message: t("审阅版本已失效，请重新检查最新内容。"), httpSafe: true },
  INVALID_INPUT: { message: t("输入格式不正确，请检查收件地址、正文和附件。"), httpSafe: true },
  OUTCOME_UNKNOWN: { message: t("操作可能已提交。请先核对状态，不要重复提交。"), httpSafe: true },
  REVISION_CONFLICT: { message: t("草稿已被其他操作修改。请保留当前编辑，重新读取后核对。"), httpSafe: true },
  TRANSFER_CONFLICT: { message: t("上传内容或位置不一致，请先检查上传状态。"), httpSafe: true },
  TRANSFER_EXPIRED: { message: t("临时上传已过期。请保留当前编辑，核对草稿列表后再重新保存。"), httpSafe: true },
  STALE_MESSAGE: { message: t("邮箱索引已变化，请刷新列表后重新打开邮件。"), httpSafe: true },
  CONNECTOR_UNAVAILABLE: { message: t("邮箱插件服务暂不可用，请重新打开工作台。"), httpSafe: true },
  VAULT_LOCKED: { message: t("本机邮箱尚未解锁，请允许访问系统凭证后重试。"), httpSafe: true },
  CREDENTIAL_DENIED: { message: t("系统凭证访问未获允许。请允许访问后重试。"), httpSafe: true },
  CREDENTIAL_LOCKED: { message: t("系统凭证库已锁定，请解锁后重试。"), httpSafe: true },
  CREDENTIAL_UNAVAILABLE: { message: t("系统凭证库暂不可用，请检查系统状态后重试。"), httpSafe: true },
  VAULT_KEY_MISSING: { message: t("找不到已有邮箱数据的加密密钥，数据已保留，请恢复原系统凭证。"), httpSafe: true },
  VAULT_INCOMPLETE: { message: t("本机邮箱初始化尚未完成，可重试恢复。已有数据不会被清空。"), httpSafe: true },
  VAULT_CORRUPT: { message: t("本机邮箱数据无法验证，数据已保留，请检查本机存储。"), httpSafe: true },
  VAULT_CLEAR_PENDING: { message: t("上次清除尚未完成，邮箱业务已暂停。请手动重试清除。"), httpSafe: true },
  NEEDS_SETUP: { message: t("请先连接邮箱，再继续此任务。"), httpSafe: true },
  ACCOUNT_REQUIRED: { message: t("请先连接邮箱，再继续此任务。"), httpSafe: true },
  STORAGE_UNAVAILABLE: { message: t("本机邮箱存储暂不可用，请检查磁盘空间和访问权限后重试。"), httpSafe: true },
  STORAGE_CORRUPT: { message: t("本机邮箱文件无法读取，已有数据已保留，请检查存储文件。"), httpSafe: true },
  SETUP_NOT_FOUND: { message: t("本次连接操作已过期，请关闭并重新打开连接表单。"), httpSafe: true },
  CONNECTOR_PROVIDER_ERROR: { message: t("邮箱操作未成功。请核对账号、输入或当前草稿状态后再试。"), httpSafe: true },
  SERVICE_CLOSED: { message: t("登录状态或邮箱服务已变化，请重新打开工作台。"), httpSafe: true },
  STORAGE_FULL: { message: t("本地邮箱空间已达上限，操作未完成。"), httpSafe: true },
  MESSAGE_TOO_LARGE: { message: t("邮件超过当前读取上限（20 MiB）。"), httpSafe: true },
  ATTACHMENT_TOO_LARGE: { message: t("单个附件不能超过 10 MiB。"), httpSafe: true },
  QUOTE_TOO_LARGE: { message: t("原邮件超过当前可编辑长度，尚未生成草稿，正文没有被截断。请新建邮件，明确选择需要摘录的内容，并从原信下载需要的附件。"), httpSafe: false },
  QUOTE_IMAGE_MISSING: { message: t("原邮件内嵌图片未完整取得，尚未生成草稿。请重新读取邮件后再试。"), httpSafe: false },
  QUOTE_ATTACHMENTS_TOO_LARGE: { message: t("原邮件附件超过当前发送上限（单个 10 MiB、最多 10 个），尚未生成转发草稿。请新建邮件，从原信下载并添加需要发送的文件。"), httpSafe: false },
  FORBIDDEN: { message: t("页面请求未通过来源校验，请从工作台入口打开。"), httpSafe: true },
  SESSION_STALE: { message: t("本地服务刚刚重启，连接尚未恢复，请稍后重试。页面中的编辑已保留。"), httpSafe: true },
  UI_OPERATION_NOT_FOUND: { message: t("页面操作已失效，请重新读取当前页面状态。"), httpSafe: true },
  ACCOUNT_NOT_FOUND: { message: t("邮箱连接不存在，请重新选择邮箱或连接账号。"), httpSafe: true },
  DRAFT_NOT_FOUND: { message: t("草稿已不存在，请刷新草稿列表。当前编辑已保留。"), httpSafe: true },
  BATCH_NOT_FOUND: { message: t("发送任务已不存在，请刷新任务列表。"), httpSafe: true },
  ATTACHMENT_NOT_FOUND: { message: t("附件已不存在，请重新选择附件；当前编辑已保留。"), httpSafe: true },
  MESSAGE_NOT_FOUND: { message: t("邮件已不存在或已移走，请刷新当前文件夹。"), httpSafe: true },
  DRAFT_INCOMPLETE: { message: t("草稿信息尚未完整，请核对发件人、收件人和正文。"), httpSafe: true },
  DELIVERY_UNKNOWN: { message: t("发送结果不确定，请先核对发送记录及已发送邮件，不要重复发送。"), httpSafe: true },
  WORKSPACE_UNAVAILABLE: { message: t("工作台暂不可用，请保留当前编辑并重新打开工作台。"), httpSafe: true },
  INVALID_RESPONSE: { message: t("邮箱服务返回异常，请核对当前状态后重试。"), httpSafe: true },
  TOOL_REF_STALE: { message: t("邮箱工具已更新，请重新打开工作台。"), httpSafe: true },
  SERVICE_RESTARTED: { message: t("邮箱服务已重启，请核对当前状态后重试。"), httpSafe: true },
  CONNECTOR_TIMEOUT: { message: t("邮箱服务响应超时，请先核对操作结果再重试。"), httpSafe: true },
  KEY_MISSING: { message: t("找不到本机加密密钥，数据已保留，请恢复原凭证。"), httpSafe: true },
  NEEDS_UNLOCK: { message: t("请先解锁本机邮箱，再继续此任务。"), httpSafe: true },
  VAULT_UNAVAILABLE: { message: t("本机邮箱暂不可用，已有数据已保留。"), httpSafe: true },
  CREDENTIAL_NOT_FOUND: { message: t("找不到邮箱凭证，请重新连接邮箱。"), httpSafe: true },
  SETUP_EXPIRED: { message: t("本次连接操作已过期，请重新打开连接表单。"), httpSafe: true },
  SETUP_BUSY: { message: t("邮箱正在连接，请稍候再试。"), httpSafe: true },
  DEFAULT_ACCOUNT_REQUIRED: { message: t("请选择另一个默认邮箱，再断开当前邮箱。"), httpSafe: true },
  BUSY: { message: t("邮箱正在处理其他操作，请稍候再试。"), httpSafe: true },
  TOOL_NOT_FOUND: { message: t("当前邮箱工具不可用，请重新打开工作台。"), httpSafe: true },
  NOT_FOUND: { message: t("请求的工作台资源不存在。"), httpSafe: true },
  REQUEST_FAILED: { message: t("邮箱操作未成功，请核对当前状态后重试。"), httpSafe: true },
});

export const errorMessages = Object.freeze(Object.fromEntries(
  Object.entries(errorDefinitions).map(([code, definition]) => [code, definition.message]),
));

/** @param {unknown} code */
export function isPublicEmailErrorCode(code) {
  return typeof code === 'string' && Object.hasOwn(errorDefinitions, code) && errorDefinitions[code].httpSafe === true;
}

/** @param {unknown} error */
export function publicEmailError(error) {
  const code = error && typeof error === 'object' && 'code' in error ? error.code : undefined;
  return isPublicEmailErrorCode(code) ? code : 'REQUEST_FAILED';
}
