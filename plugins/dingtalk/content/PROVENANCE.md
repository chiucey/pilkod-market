# 上游来源

- 官方仓库：https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli
- CLI 与技能来自 npm `dingtalk-workspace-cli@1.0.64` 的同一发布包。
- 发布包： https://registry.npmjs.org/dingtalk-workspace-cli/-/dingtalk-workspace-cli-1.0.64.tgz
- SHA-512：`d324afdd97b311e330618e26dc36fb00438df4371e56bfdd41a4b6973d3b832fdf22534c879d2a6e740decb96a7390790a3b99a14ac12946aca536c93745726b`
- 技能来源：发布包 `assets/dws-skills.zip` 中完整 `multi/`，保留相对引用、脚本和授权文件。
- 本地修改：每个技能入口增加准备说明；新增 MiniMax Code 安装、登录指南与独立二进制安装脚本。

升级时一起更新 CLI 版本、发布包校验值和技能树，重新核对宿主说明；不要仅替换某个产品目录。

兼容目录校验：上游 JSON 数组示例保留原始内容，后缀改为 `.json.example`，同步更新引用：host-action.json.example, agent-run-progress.json.example, data-report.json.example, agent-run.json.example, form-interaction.json.example。

修复 shared/references/recipes/conventions.md 的两个共享技能相对链接，使其指向同包的 dingtalk-shared/SKILL.md。

部分上游文件仅规范化行尾与末尾空白，正文和许可证条款不变。

## 官方图标

- 来源页面：https://www.dingtalk.com/
- 原图：https://gw.alicdn.com/imgextra/i3/O1CN014ZbI6ZTEhdC0ttN2_!!6000000003783-2-tps-444-444.png
- 获取日期：2026-10-18；尺寸 444×444，PNG 原文件，未重绘或放大。
- SHA-256：`b3fb0715857df5d23213b5265166fabcb7f7b4b290890d7b5682a027cf39c85d`。
- 品牌图标权利归原权利人所有，用于标识本插件连接的产品，不代表官方开发或背书。
