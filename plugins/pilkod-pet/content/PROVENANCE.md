# 源码与分发

作者：MiniMax。MiniMax Pet `0.5.8` 的代码、文档、默认薄荷色机器人图集和章鱼图标按 [MIT](LICENSE) 分发。

## 固定来源

- 公开仓库：[MiniMax-AI/MiniMax-Code-MiniApps](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps)。
- 固定提交：[`7cf0b25cd96c21d4be6b284f28dae1e6ac7f058d`](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps/commit/7cf0b25cd96c21d4be6b284f28dae1e6ac7f058d)。
- [完整可编辑源码、测试与构建工具](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps/tree/7cf0b25cd96c21d4be6b284f28dae1e6ac7f058d/sources/minimax-ai/minimax-pet)。
- [上游可安装包](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps/tree/7cf0b25cd96c21d4be6b284f28dae1e6ac7f058d/plugins/minimax-ai/minimax-pet)。

本市场仓库只维护 `plugins/minimax-pet/` 中可直接安装的文件，不保存源码副本、开发依赖、构建脚本、测试或插件专项 CI。安装后不依赖源码仓库或 `node_modules`。

市场包的 manifest、运行代码、Skill、图集、图标和许可证保留上游文件字节。`README.md`、`README.zh-CN.md`、`ARTWORK.md` 和本文件仅调整安装路径、源码链接和本仓库职责说明。运行时不读取上游仓库，也不访问 Host 私有文件。

## 复现

在上述固定提交的 `sources/minimax-ai/minimax-pet/` 中，使用 Node.js 22 及以上版本：

```sh
npm ci --ignore-scripts
npm test
npm run test:smoke
npm run package
npm run check:package
```

上游构建使用明确的运行文件和文档 allowlist，输出 `dist/package`；完整包比较覆盖路径和文件字节，拒绝符号链接。内部市场的文档适配不应改变 manifest、`miniapp/`、`skills/`、图标或许可证。

市场校验与打包使用本仓库现有的 `tools/validate_marketplace.py` 和 `tools/publish_marketplace.py --dry-run`，不修改共享校验器或发布规则。

## 素材与兼容

默认图集由上游 Node 内置模块绘制，紫色章鱼图标由 OpenAI imagegen 根据用户提供的视觉参考生成；参考图和第三方宠物图集不随包分发，详见 [ARTWORK.md](ARTWORK.md)。用户导入的素材保留各自许可。

客户端支持基线、数据访问和已验证／未验证环境见 [README.zh-CN.md](README.zh-CN.md)。自动化校验及发布 dry-run 不等同于正式客户端或官方市场安装验收。
