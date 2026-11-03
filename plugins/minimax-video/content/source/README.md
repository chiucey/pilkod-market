# MiniMax Video 构建源码

MiniMax Video 基于 [OpenChatCut](https://github.com/0xsline/OpenChatCut) v0.2.16，固定提交 `2e6f4a29b784200cfb32b859b16f2561592bc3e8`，遵循 AGPL-3.0-or-later。上游完整源码由该提交提供；`upstream.patch` 是已跟踪文件的全部修改，`overlay/` 是新增源码，`adapter/` 是 Mini App 构建与验证脚本。运行入口和安装脚本以 `plugins/minimax-video/miniapp/node/` 为源文件。对应许可证位于插件的 `LICENSE`。

源码随插件存放在 source/，不放入 miniapp/ 运行目录。插件可以直接复制安装，不需要用户编译。

## 重建

需要 Git、Node.js 24 和 npm。以下命令从仓库根目录执行；目标目录必须不存在。安装依赖和生成渲染资源会访问公共 npm、GitHub 和上游模型资源服务。

```sh
node plugins/minimax-video/source/prepare-source.mjs ../openvideo-build
cd ../openvideo-build/upstream
npm ci
npm run sync:mediapipe
npx tsx desktop/prebuild-remotion.mts
npx vite build --config config/vite.miniapp.config.ts
node scripts/build-miniapp.mjs ../release
```

构建脚本会复制 source/、skills/、中英文说明和许可证到 release/；然后执行下方区域处理命令。生成的 buildId 包含时间戳，不要求产物字节完全相同。字体、音效、AI 浏览器组件的清单与公开 CDN 地址位于 `resource-manifest.json`，下载会验证 SHA-256；更换资源必须同步清单与发布源，不能仅修改 URL。

## 验证

市场检查：在本仓库根目录执行 `python tools/validate_marketplace.py`。检查重建包时使用 `python tools/validate_marketplace.py --help` 查看当前版本支持的目录参数。

运行验证：准备源码后，在构建目录执行 `node verify-runtime.mjs ./release`。该程序启动隔离数据目录并检查服务与依赖恢复；首次运行可能下载当前平台所需的工具。它不能替代 MiniMax Code 内的真实 Agent、权限确认和视频导出测试。

已执行的原生测试与未覆盖平台见插件 README；不发布本机项目、用户对话、私有日志和凭据。

## 国内与海外测试包

此仓库仅发布 国内区域。构建并复制使用说明后，运行 `node plugins/minimax-video/source/package-region.mjs <release目录> cn`。该脚本设置版本、市场介绍、HTML 默认语言和安装错误信息。用户已保存的语言与下载源优先，不根据 IP 猜测位置，不更改项目数据。

相对 GitHub PR #38，本版新增安装页、入门指南、示例工程、AI 助手及设置的英文翻译，复用现有 `t()` / `useT()`。应用包版本 1.1.6；通过独立 MR 发布到 dev 或 main，main 仍须通过生产审批。

首次安装自动检测实际依赖地址连通性，优先使用已保存来源或区域包默认值；单个文件失败自动尝试备用源，两个来源均进行固定摘要校验。完整缓存不发起探测或下载。安装失败可重试，手动选源位于“下载遇到问题？”中。
