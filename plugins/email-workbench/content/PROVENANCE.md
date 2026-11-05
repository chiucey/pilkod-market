# 邮箱插件源码与构建来源

邮箱核心与 MiniApp 最初复用自本地开发快照：
`matrix/agent-archon` HEAD `1d6c7b34b77169a76cccd9a5ef65e6144e19c704`
及该会话当时已有的本地改动。当前独立插件的源码在
`sources/email-workbench`，运行、测试、构建均不依赖原仓库。

## 富文本编辑器与 PDF 预览

可编辑源码已经收录到本仓库的 `editor/rich-editor.js` 和
`editor/pdf-preview.js`。导入时的原文件路径、SHA-256、旧构建脚本与
原依赖锁哈希、原来三个发布资产的哈希记录在
`editor/import-provenance.json`。这些哈希标识包含当时本地改动的准确内容，
不能把上述 HEAD 当作所有导入文件的唯一来源。

浏览器依赖继续使用原快照版本，不在恢复构建链路时升级：

| 组件 | 版本 | 上游 |
| --- | --- | --- |
| Tiptap React / Starter Kit / PM | 3.22.3 | https://github.com/ueberdosis/tiptap |
| React / React DOM | 18.3.1 | https://github.com/facebook/react |
| PDF.js (`pdfjs-dist`) | 6.3.289 | https://github.com/mozilla/pdf.js |
| esbuild | 0.25.12 | https://github.com/evanw/esbuild |

Tiptap、ProseMirror 及编辑器依赖树按原快照锁定，精确依赖版本和下载完整性
由 `package-lock.json` 保存。浏览器实际打包依赖的名称、版本、许可证类型和
许可证正文由构建生成到 `miniapp/client/licenses/`，PDF 字体/CMap/WASM
原有许可证也随 `pdf-assets` 保留。QuickJS 资产仍不打包，PDF 脚本保持禁用。
PDF.js 的 Node 可选依赖只可能存在于构建机 `node_modules`，不复制进插件。

## 独立重建与发布一致性

需要 Node.js 22.13 或更新的兼容版本、npm 和 Python 3。在本目录执行：

```sh
npm ci --ignore-scripts
npm run typecheck
npm test
npm run test:packaging
npm run build
npm run package
npm run check:package
```

`build` 先从 `editor/` 重建富文本与 PDF 浏览器入口，再打包 Node 后端；
PDF worker、字体和映射数据直接取自锁定的 npm 包。生成文件头只引用本仓库
脚本。不要手工修改 `miniapp/client/rich-editor.js`、`pdf-preview.js` 或
`pdf.worker.min.mjs`。

`package` 生成 `dist/package` 与 ZIP；`check:package` 将整个
`dist/package` 与仓库 `plugins/email-workbench` 按路径及文件字节比较，
包含执行代码、图标、二进制资源、元数据和许可证。它拒绝缺失、多余、不一致
文件和符号链接；不以 ZIP 时间戳比较，也没有忽略运行文件的规则。

邮箱相关文件或 CI 配置变动会触发 `email-workbench-check`，运行上述全套
检查；市场发布必须等待该检查成功。未涉及邮箱时该 job 可以不创建，现有
市场校验与发布预检继续执行。市场 V1 对 `.node` 原生模块的独立限制没有放宽。

## 过渡版系统凭证适配

1.1.2-test.20260924 移除 `@napi-rs/keyring` 的四个平台原生二进制及其 vendor 目录。
macOS 使用系统自带 `/usr/bin/security -i`，不分发、下载或运行额外原生模块。
命令仅从 stdin 传入；`-X` 写入原始32字节主密钥，`-g` 读取带明确格式的结果，
兼容旧 service/account 命名。程序不修改钥匙串全局配置或现有条目的访问控制。

实现依据：Apple SecurityTool 的
[keychain_add.c](https://github.com/apple-oss-distributions/Security/blob/main/SecurityTool/macOS/keychain_add.c)、
[keychain_find.c](https://github.com/apple-oss-distributions/Security/blob/main/SecurityTool/macOS/keychain_find.c)、
[keychain_utilities.c](https://github.com/apple-oss-distributions/Security/blob/main/SecurityTool/macOS/keychain_utilities.c)
和 [security.c](https://github.com/apple-oss-distributions/Security/blob/main/SecurityTool/macOS/security.c)。
这些系统源码没有复制到插件中。

`test/credential-system-smoke.test.ts` 默认跳过，设置 `EMAIL_KEYCHAIN_SMOKE=1` 可在 macOS
创建唯一命名的临时测试条目，验证二进制/可打印密钥的写读更新与清除；不读取现有邮箱密钥。
1.2.7 增加 Windows Credential Manager 适配，使用系统 Windows PowerShell 5.1 加载固定的
C# P/Invoke 声明；主密钥在编译后才从 stdin 读取，不写入编译源、命令行或临时文件。
`CredReadW`、`CredWriteW` 和 `CredDeleteW` 来自 Windows 的 `advapi32.dll`，无新增 npm
依赖或分发二进制，不修改 PowerShell 执行策略或系统凭据权限。Windows 原生 smoke 由
`EMAIL_WINDOWS_CREDENTIAL_SMOKE=1` 显式启用；Linux 仍无系统凭据适配。

新增实现按 [Microsoft WinCred API 文档](https://learn.microsoft.com/en-us/windows/win32/api/wincred/)
编写，未复制第三方实现。

Windows helper 使用系统 .NET Framework 的 `System.Runtime.Serialization` 与 `System.Xml` 解析 stdin JSON。固定 C# 无参入口处理请求和响应，避免将主密钥绑定到 PowerShell `ConvertFrom-Json.InputObject`；不关闭模块日志或其他审计策略。

## 1.2.8 图标透明背景修复

图标沿用原有 MiniMax 生成的蓝色信封素材（原文件 SHA-256：
`af0df753fb65f20d0b0283f850b1359b66561d76c54def85bd053cff945a4871`）。
以确定性像素处理移除与画布外部连通的近黑背景，并恢复轮廓抗锯齿像素的透明度及颜色，
未重绘主体。输出保持 2048×2048，改为 RGBA PNG；3,952,359 个不透明主体像素
的 RGB 与原图逐像素一致。国内、海外使用同一图标文件。
