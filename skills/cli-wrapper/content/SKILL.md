---
name: cli-wrapper
description: 包外部工具（ffmpeg、imagemagick、curl 等）为统一的 CLI 接口，带结构化 JSON 输出和 --help 发现机制。触发场景包括：用户要求包装一个工具、让 agent 调用一个外部程序、构建 tool harness、将命令行工具暴露给 agent。
---

# CLI Wrapper

把任意外部工具包装成 Agent 可控的 CLI 接口——结构化 JSON 输出、一致的参数解析、Unix 约定。

## 核心理念

参考 [CLI-Anything](https://github.com/HKUDS/CLI-Anything) 的原则：
- **Structured Output** — 默认 JSON，human-readable 可选（`--json` flag）
- **Self-Describing** — `--help` 本身就是文档，agent 可发现
- **Composability** — 命令可组合、管道可连接
- **Zero Trade-off** — 不降低功能，只增加接口层

## 目录结构

```
tool-wrapper/
├── SKILL.md
└── references/
    ├── patterns.md    # 模式 + 模板
    └── templates/     # 可复用的代码模板
        ├── click_basic.py    # Click 最小模板
        ├── click_json.py     # JSON 输出模板
        └── shell_wrapper.sh  # Shell 包装模板
```

## 工作流

### 1. 检测目标工具

用 `which` 或 `command -v` 确认工具存在：

```bash
which ffmpeg || echo "not found"
command -v convert && echo "imagemagick found"
```

### 2. 分析工具接口

```
tool --help          # 看基本用法
tool --long-help     # 有些工具用 --long-help 或 -h
man tool             # man page
tool subcommand --help  # 如果是子命令工具
```

### 3. 选择包装方式

| 工具类型 | 推荐方式 |
|---|---|
| 有 CLI 且输出结构化 | Python + Click 包装 |
| 复杂子命令（git/docker） | Shell 包装 + JSON 解析 |
| 简单单命令 | Shell 别名或脚本 |
| 已有 JSON/API 输出 | 直接 proxy + 格式化 |

### 4. 编写包装 CLI

从 `references/templates/` 选模板，原则：
- **必须**：有 `--json` flag（agent 消费）
- **必须**：有 `--help`（自我描述）
- **必须**：正确退出码（0=成功，非0=失败）
- **推荐**：子命令结构（如 `tool image crop`）
- **推荐**：长选项（`--output` 而非 `-o`）

### 5. 注册到 OpenClaw

包装好的 CLI 文件放到 `~/.local/bin/` 或项目 `bin/` 目录，确保可执行。

## 输出格式约定

```bash
# 非 JSON（human-readable）
tool image info input.jpg
# → Width: 1920, Height: 1080, Format: JPEG

# JSON 模式（agent-readable）
tool image info input.jpg --json
# → {"width": 1920, "height": 1080, "format": "JPEG", "file_size": 204800}

# 错误格式（统一）
tool image info missing.jpg --json
# → {"error": "file not found", "path": "missing.jpg", "code": 1}
```

## 常见模式

详见 `references/patterns.md`：
- Click Python CLI 完整模板
- JSON 输出包装器
- Shell 包装器
- 错误处理规范
- 工具检测与回退

## 示例：包装 ffmpeg 的一部分

用户问"帮我把视频转成 gif"，OpenClaw 可以有一个 `cli-ffmpeg` 包装器：

```bash
cli-ffmpeg video to-gif input.mp4 --fps 10 --width 480 -o output.gif --json
```

这样 agent 不需要记忆 ffmpeg 的复杂参数语法，直接调用即可。

## 注意事项

- 不要包装整个工具，只包装常用的几个操作（按需）
- 保持薄层，不重复造轮子
- 测试时同时验证 `--json` 和 human-readable 两种输出
- 退出码必须准确（agent 依赖它判断成功/失败）
