---
name: deb-package-builder
description: 创建标准DEB安装包工程。当用户要求创建DEB包、制作Debian/Ubuntu安装包、打包.deb文件、创建deb安装包工程时使用。
---

# DEB安装包制作技能

本技能用于创建符合Debian/Ubuntu标准规范的DEB安装包工程。

## 使用场景

当用户提供以下任一需求时触发：
- 创建DEB安装包
- 制作.deb包
- 打包应用到Debian/Ubuntu系统
- 构建deb安装包工程

## 工作流程

### 步骤1：收集基础信息

使用GenUI表单逐步收集以下信息：

**第1页 - 基础信息**
- 包名称 (Package Name): DEB包的标准名称，如 `myapp`
- 包版本 (Version): 语义化版本，如 `1.0.0`
- 维护者 (Maintainer): 姓名和邮箱，格式 `Name <email@example.com>`
- 描述 (Description): 一行简短描述

**第2页 - 文件结构**
- 需要安装的文件路径列表
- 目标安装目录

**第3页 - 脚本配置**
- preinst脚本内容（如需要）
- postinst脚本内容（如需要）
- prerm脚本内容（如需要）
- postrm脚本内容（如需要）

**第4页 - 依赖与平台**
- 运行时依赖包列表
- 目标操作系统版本

### 步骤2：生成DEB工程

根据收集的信息，在 `/workspace/output/deb-projects/{package-name}/` 创建标准DEB工程结构：

```
{package-name}/
├── DEBIAN/
│   ├── control          # 包控制信息
│   ├── preinst          # 安装前脚本 (可选)
│   ├── postinst         # 安装后脚本 (可选)
│   ├── prerm            # 移除前脚本 (可选)
│   ├── postrm           # 移除后脚本 (可选)
│   └── md5sums          # 文件校验和 (自动生成)
├── etc/
│   └── {app}/
│       └── config.conf  # 配置文件示例
├── usr/
│   ├── bin/
│   │   └── {app}       # 可执行文件
│   └── share/
│       └── {app}/
│           └── ...     # 应用资源
└── README.md            # 工程使用说明
```

### 步骤3：生成README.md

创建详细的工程使用文档，包含：
- DEB包结构说明
- 各目录用途
- 打包命令说明
- 测试安装方法
- 常见问题

### 步骤4：自动打包

使用 `dpkg-deb` 命令构建最终的 .deb 文件：
```bash
dpkg-deb --build {package-name}
```

## 输出产物

1. **DEB工程目录**: `/workspace/output/deb-projects/{package-name}/`
2. **生成的DEB包**: `/workspace/output/deb-projects/{package-name}.deb`
3. **README文档**: 工程目录中的 README.md

## DEB规范要点

### control文件必需字段
- Package: 包名
- Version: 版本号
- Architecture: 架构 (amd64, i386, all)
- Maintainer: 维护者信息
- Description: 包描述

### 常用字段
- Depends: 运行时依赖
- Pre-Depends: 预依赖
- Recommends: 推荐依赖
- Suggests: 建议依赖
- Section: 分类
- Priority: 优先级

### 脚本执行时机
- preinst: 文件解压前
- postinst: 文件解压后
- prerm: 文件删除前
- postrm: 文件删除后

## 脚本模板参考

脚本必须以 `#!/bin/bash` 开头，并在开始时设置错误处理：
```bash
#!/bin/bash
set -e

case "$1" in
    configure)
        # 配置操作
        ;;
    abort-upgrade|abort-remove|abort-deconfigure)
        # 回滚操作
        exit 0
        ;;
esac

exit 0
```

## 常见问题处理

1. **权限问题**: 确保DEBIAN目录权限为755
2. **依赖缺失**: 使用 `dpkg-checkbuilddeps` 检查构建依赖
3. **文件冲突**: 使用 `--force-overwrite` 标志（谨慎使用）
