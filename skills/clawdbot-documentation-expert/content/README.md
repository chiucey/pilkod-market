# Clawdbot Documentation Expert

## 技能简介

基于ClawHub官方Clawddocs完整文档开发的**Minimax Agent专用技能**，无任何OpenClaw依赖、无网络请求、无第三方库，精准解答所有Clawdbot文档相关问题。

## 核心功能

- ✅ Clawdbot功能/配置/安装文档解答
- ✅ Clawddocs文档内容精准查询
- ✅ 常见问题自动匹配官方答案
- ✅ 无编造、无外部信息、纯官方文档

## 适配环境

- Minimax Agent 平台
- Python 3.8+
- 无任何第三方依赖
- 无OpenClaw依赖

## 权限声明

- `network:false`：不访问任何外部网络
- 无文件读写权限
- 无系统权限

## 加载方式

1. 将`clawdbot-documentation-expert`目录完整导入Minimax Agent技能库
2. 加载`SKILL.md`核心配置
3. 触发关键词：Clawdbot、clawddocs、文档、使用指南等

## 测试方法

```bash
cd clawdbot-documentation-expert/tests
python test_main.py
```

## 项目结构

```
clawdbot-documentation-expert/
├── SKILL.md                  # 核心配置文件
├── _meta.json               # 元数据
├── src/
│   └── main.py             # 主逻辑入口
├── instructions/
│   └── system_prompt.md    # 系统提示词
├── config/
│   └── settings.yaml       # 基础配置
├── tests/
│   └── test_main.py        # 单元测试
├── assets/
│   └── .gitkeep            # 静态资源
└── README.md               # 说明文档
```

## 版本信息

- 版本：1.0.0
- 作者：Clawdbot Team
- 更新日期：2026-03-26
