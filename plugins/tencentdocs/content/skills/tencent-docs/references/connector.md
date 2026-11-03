# Connector 调用约定

本插件只引用 `tencentdocs` App。文档中 `manage.*`、`doc.*`、`sheet.*`、`slide_*` 等名称是业务操作标识，用于匹配工具描述，不代表可以据此拼出运行时工具名。

## 发现、检查、调用

优先使用当前会话已暴露的腾讯文档 Connector 工具。需要命令行编排时，使用宿主提供的 `mcode-tools`：

```bash
mcode-tools connector tools --keyword tencentdocs
mcode-tools connector tool "<从列表复制的完整工具名>"
mcode-tools connector call "<从列表复制的完整工具名>" --args-file "args.json"
```

`tools` 返回名称与描述；`tool` 返回具体参数和响应 Schema。只选择 `connector__tencentdocs__` 开头的实际工具名，不猜测点号、连字符或下划线的转换规则。当前 Schema 优先于包内参考；但其中旧客户端的安装、取凭证或直连代码不适用于本插件。

如某个品类的工具未暴露，明确说明该能力当前不可用；不要注册其他服务、读取客户端凭证或换 HTTP 端点尝试。鉴权失败按 [auth.md](auth.md) 重新连接 App。写操作超时后先读回检查结果，不能盲目重复创建或写入。

## 本地文件与长文本

本地辅助脚本要求 Node.js 18+，以及由当前 MiniMax 会话提供的 `mcode-tools`。所有工具参数通过 JSON stdin 交给 Connector，避免命令行长度限制和在模型上下文中传递大段 Base64。

先把不含大字段的其余参数写入 `args.json`，然后使用以下脚本。脚本路径相对本 Skill 目录；在其他工作目录运行时换成解析得到的绝对路径。工具名称必须来自上一步发现结果。

```bash
# 插入/替换文档或幻灯片图片：args.json 中保留文档 ID、位置和尺寸等字段
node scripts/call_with_file.js "<图片操作工具名>" args.json content base64 image.png

# 上传图片：args.json 包含 file_name，返回 image_id 后供后续操作使用
node scripts/call_with_file.js "<upload_image 工具名>" args.json image_base64 base64 image.png

# 从 Markdown 创建 Word：args.json 可包含 title
node scripts/call_with_file.js "<doc.create_with_markdown 工具名>" args.json base64_markdown base64 report.md

# 持久化 PPT 设计：args.json 包含 file_id 或 file_url
node scripts/call_with_file.js "<slide_set_design 工具名>" args.json design_md text design.md
```

`--args-file` 只解决参数传递方式，不绕过 Connector 或服务的大小限制。超过限制时，使用当前工具支持的图片 URL、已上传的 `image_id`、压缩后的图片或合法分批操作；没有支持的路径就报告限制。不要让用户提供 API Token 或运行工具描述中读取凭证的脚本。
