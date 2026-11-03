# 区域测试版本 0.2.36

基于 GitHub 社区仓库 `MiniMax-AI/MiniMax-Code-MiniApps` 提交 `26786369a297a7db6eb63213b3764a5958560fe5` 的 `plugins/webguhui/minimax-photo`。保留源码、构建补丁和第三方许可证，未加入用户图片或录屏。

国内使用中文市场文案和默认 README，海外使用英文市场文案、README、用户手册及 Skill。应用运行代码与源提交相同，界面仍按用户保存的语言或浏览器语言选择简体中文、繁体中文、英文、日文，不按部署区域强制覆盖。

两个区域只添加 `minimax-photo` 的 Desktop 目录条目，安装策略沿用默认 USER_MANAGED。不依赖 Connector provider；AI 能力由当前 Host 提供。合入 dev 自动发布到区域测试环境，不代表已进入生产。

本包只同步 metadata、文档、Skill 和版本号；0.2.35 的历史宿主验收不等于 0.2.36 已完成市场安装验收。GitHub 上的社区代码版本独立发布，不由这次 GitLab MR 自动更新。
