# OpenClaw 导出器使用指南

## 功能概述

OpenClaw 导出器是一个用于完整备份和迁移 MaxClaw/OpenClaw 环境的工具。它可以：

1. **导出所有技能** - 包括 SKILL.md、_meta.json、scripts、references
2. **导出所有记忆** - /memories 目录下的所有文件
3. **导出配置摘要** - 非敏感配置信息
4. **生成导入脚本** - 一键恢复的 bash 脚本

## 使用场景

### 场景 1：完整备份
```
用户：帮我备份所有技能和记忆
助手：使用 openclaw-exporter 技能执行完整导出
```

### 场景 2：迁移到新设备
```
用户：我要把现在的配置迁移到新电脑
助手：使用导出器生成备份包，然后在新设备导入
```

### 场景 3：同步多实例
```
用户：我在多台机器上用 OpenClaw，想保持一致
助手：定期导出/导入确保配置同步
```

## 技术细节

### 扫描的目录
- `.claude/skills/` - 用户自定义技能
- `.expert/skills/` - 系统内置技能
- `temp-skills/` - 临时技能目录
- `/memories/` - 持久记忆存储

### 排除的文件
- `node_modules/` - npm 包
- `.git/` - Git 仓库
- `*.log` - 日志文件
- `.env` - 环境变量
- `secrets/` - 密钥目录

### 输出结构
```
openclaw-backup-20260404_123456/
├── skills/           # 技能目录
│   ├── skill-1/
│   │   ├── SKILL.md
│   │   ├── _meta.json
│   │   └── ...
│   └── skill-2/
├── memories/         # 记忆文件
│   ├── notes.md
│   └── project/
├── config/          # 配置摘要
│   └── openclaw-export.json
├── manifest.json    # 导出清单
└── import.sh       # 导入脚本
```

## 与 clawhub 的配合

clawhub 是 OpenClaw 的技能市场工具，导出器可以生成能被 clawhub 使用的格式：

```bash
# 使用导出器生成备份
python scripts/export_openclaw.py -o my-backup

# 如果需要发布到 clawhub，先打包
cd my-backup
tar -czf skills-backup.tar.gz skills/

# 分享给其他人
# 接收方解压后使用 import.sh 或手动复制
```

## 注意事项

1. **敏感信息** - 导出器会自动排除 .env、secrets 等敏感文件
2. **API 密钥** - 不会导出 openclaw.json 中的 API 密钥
3. **插件列表** - 会导出但需要在新环境重新安装插件
4. **记忆文件** - 完整导出，包括会话笔记和项目状态
