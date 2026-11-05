# 第三方来源与许可

## vercel/vercel-plugin

- 上游仓库：https://github.com/vercel/vercel-plugin
- 版本：`0.54.1`
- 固定提交：[`2a1e58dfb63c064c2589c0c21b3e93c53728f8d5`](https://github.com/vercel/vercel-plugin/tree/2a1e58dfb63c064c2589c0c21b3e93c53728f8d5)
- 许可：Apache-2.0，全文随包附于 [LICENSE](LICENSE)。
- 固定提交目录树包含 `LICENSE`，没有单独的 `NOTICE` 文件。

保留上游 LICENSE 中的声明：

```text
Copyright 2026 Vercel, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 适配范围与修改说明

MiniMax Code 将下列上游文件中的工作流精选、中文改写并适配为 MiniMax Plugin V1。每个改写后的 Skill 带有修改声明。来源路径均相对于上述固定提交；表中 SHA256 为上游原文件内容的摘要。

| 上游路径 | SHA256 |
| --- | --- |
| `skills/vercel-cli/SKILL.md` | `6399a7d4f2fc8b7202c46ae4a63380c32ff8a994bd952985ee3f9b0fbf25b756` |
| `skills/deployments-cicd/SKILL.md` | `35a39f8944a878c43fab9bd36ff6f87fee39f8e14a9cdd1aa34addc5430ba9c8` |
| `skills/env-vars/SKILL.md` | `081d79b5b046276631c10b3db6ff07dbff4a59c057fc9bbc64aa364f82bb3045` |
| `skills/vercel-functions/SKILL.md` | `ac162ecba80415929a1c40f65beea13cb25f09baf3bfa87ce6d6e404962040c6` |
| `skills/routing-middleware/SKILL.md` | `521821d60f7af332239ffcf896151e9eb625334c14202430ff60a91af3248165` |
| `skills/vercel-storage/SKILL.md` | `9af1e5d5645cf080a108095076afede10692e040c8cecae8934b122737a76b23` |
| `commands/deploy.md` | `130302d1c3a501f42e539668f9ea013840da3c0963b59f4069423e47f5290a45` |
| `commands/env.md` | `066a9db49480aa0818fead624fb5ef2707c5f6dd4bf38828814c31472082515e` |
| `commands/status.md` | `805ab52452e789c96bbc9084fbd2f97dff82ff12bd63c189c150e0b96767eba9` |
| `LICENSE` | `5c67ad692a469fa14d325db4c1e392f9343a77b9ac82ae87f70cfb47b2387c22` |

`deploy`、`env`、`status` 的内容分别整合进部署、环境变量和 CLI Skills。主要修改为：按需触发、项目与版本核实、宿主权限与确认、上传范围及日志脱敏、首次生产部署识别、环境文件保护、受限查询和不确定结果处理。平台行为还参考各 Skill 链接的 Vercel 当前官方文档，后续执行时按安装版本核实。

本包保留现有技术选型，不携带上游 agents、commands 注册、自动注入 Hooks、遥测与安装器。新增 manifest、共享操作约定及适配文档由 MiniMax Code 维护；本包文本适配内容按 Apache-2.0 分发。

## 图标与名称

- `icon.png` 来自 Vercel 官网提供的 [256×256 PNG 图标](https://assets.vercel.com/image/upload/q_auto/front/favicon/vercel/apple-touch-icon-256x256.png)，原始下载字节未修改。
- SHA256：`004f0e08cdbab6da3f70ae43ebc8353b12320c68e1162337718febcac3c1ee75`。
- Vercel 名称和图标归其权利人所有，用于识别本插件面向的服务。Apache-2.0 的商标条款不授予商标权；本适配包由 MiniMax Code 维护，不表示 Vercel 官方合作、认证或背书。
