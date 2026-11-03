---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502203edbe98469ddb356b33b55230c0ff4456409a15fccd247bb248c29ff22985e31022100c7bf63e3570557feff2ce1a9b8479055caa42633ed95ba19e0ad4818b730cb09
    ReservedCode2: 304502210091dc244de8ed16ee32f408af3d903b9027df6d5ae4fbdabbe1dbcb553ea79b88022035bb0f6f9786b5c7cdd02ed39a739cde1e890f0cdd3569311d0e4d1dd67ac836
description: Creates standard RPM package projects. Use when users request creating RPM packages, generating RPM builds, packaging into RPM, or rpmbuild projects. Supports interactive collection of installation scripts and dependency requirements.
name: rpm-package-builder
---

# RPM 安装包制作技能

本技能帮助用户创建符合标准的RPM安装包工程项目。

## 工作流程

### 步骤 1：收集基础信息

询问用户以下基础信息：

1. **软件包名称** (Name)：软件包的唯一标识符
2. **版本号** (Version)：软件版本
3. **发布号** (Release)：打包发布次数
4. **软件包摘要** (Summary)：一句话描述
5. **许可证** (License)：如 Apache-2.0, MIT, GPL-2.0 等
6. **URL**：项目主页
7. **软件包描述** (Description)：详细描述

### 步骤 2：收集文件信息

询问用户：
- **需要打包的文件或目录路径**：要安装到系统中的文件
- **安装目标路径** (Prefix)：文件安装到系统的哪个位置，默认为 `/usr`

### 步骤 3：收集安装脚本（重要）

**必须逐步询问**，不能跳过：

1. **安装前脚本** (pre)：RPM安装前需要执行的操作
   - 询问用户：安装前是否需要执行任何准备工作？
   - 例如：创建用户、创建目录、停止服务等

2. **安装后脚本** (post)：RPM安装后需要执行的操作
   - 询问用户：安装后是否需要执行任何配置工作？
   - 例如：设置权限、启动服务、注册服务等

3. **卸载前脚本** (preun)：RPM卸载前需要执行的操作
   - 询问用户：卸载前是否需要执行清理工作？
   - 例如：停止服务、备份配置等

4. **卸载后脚本** (postun)：RPM卸载后需要执行的操作
   - 询问用户：卸载后是否需要执行清理工作？
   - 例如：删除用户、清理日志等

### 步骤 4：收集依赖信息

询问用户：
- **运行时依赖** (Requires)：运行时需要哪些其他软件包
- **构建时依赖** (BuildRequires)：编译构建时需要哪些工具和库

### 步骤 5：生成RPM工程

根据收集的信息，生成以下目录结构：

```
<project-name>-rpm/
├── SPECS/
│   └── <package-name>.spec          # RPM SPEC文件
├── SOURCES/
│   └── <package-name>-<version>/    # 源代码目录
│       └── [用户提供的文件]
├── BUILD/                           # 编译构建目录
├── RPMS/                            # 生成的RPM包输出目录
├── SRPMS/                           # 生成的源码包输出目录
└── README.md                        # 使用说明文档
```

### 步骤 6：生成SPEC文件

SPEC文件是RPM包的核心，包含：
- 头部信息（Name, Version, Release, Summary等）
- %description 部分
- %prep 准备阶段
- %build 构建阶段
- %install 安装阶段
- %files 文件清单
- %pre, %post, %preun, %postun 脚本
- %changelog 变更日志

### 步骤 7：生成README.md

README.md包含：
1. 工程目录结构说明
2. 如何修改SPEC文件
3. 如何添加/修改安装脚本
4. 构建命令
5. 常见问题和解决方案

## 输出产物

1. 完整的RPM工程目录
2. 标准化的SPEC文件
3. 详细的使用说明文档

## 注意事项

- 所有脚本必须使用绝对路径
- 脚本执行失败会导致整个安装/卸载失败
- 依赖版本要明确指定
- 文件权限需要在%install阶段正确设置
