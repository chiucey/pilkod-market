---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450221008bb8fc847cf3b3e3b2de844251a3a2b5330a9c437c09a16ef6e33952fa67602c0220607b4c5757ef8dc3075baa2f6141fe0cb7818df82c8b8bbfa679e14480c1215b
    ReservedCode2: 304502205d1ac13e27e4deb23d2e67c7dd1701a27e8b4e309aee2c1fa430e12ef5ffbff1022100bf124fc456e79b2f3d687267a13c1bf2ee2e5d2bc60fbe3db6ebe6595e5e2283
---

# {{PROJECT_NAME}} RPM 安装包工程

本目录是一个标准的 RPM 安装包构建工程，用于打包和分发 {{PROJECT_NAME}} 软件。

## 目录结构

```
{{PROJECT_NAME}}-rpm/
├── SPECS/                      # SPEC 文件目录
│   └── {{PROJECT_NAME}}.spec    # RPM SPEC 配置文件
├── SOURCES/                    # 源代码目录
│   └── {{PROJECT_NAME}}-{{VERSION}}/   # 源代码和资源文件
│       ├── bin/                # 可执行文件
│       ├── config/             # 配置文件
│       ├── lib/                # 库文件
│       └── scripts/            # 安装脚本
├── BUILD/                      # 构建过程临时目录
├── RPMS/                       # 生成的 RPM 包输出目录
│   └── x86_64/                 # 架构特定目录
├── SRPMS/                      # 源码包输出目录
└── README.md                   # 本说明文档
```

## 快速开始

### 前提条件

确保已安装必要的构建工具：

```bash
# CentOS/RHEL
sudo yum install -y rpm-build rpmdevtools rpmlint

# Fedora
sudo dnf install -y rpm-build rpmdevtools rpmlint

# Debian/Ubuntu
sudo apt-get install -y rpm
```

### 构建 RPM 包

1. **完整构建（二进制 RPM + 源码包）**：

```bash
rpmbuild -ba SPECS/{{PROJECT_NAME}}.spec
```

2. **仅构建二进制 RPM**：

```bash
rpmbuild -bb SPECS/{{PROJECT_NAME}}.spec
```

3. **仅构建源码包**：

```bash
rpmbuild -bs SPECS/{{PROJECT_NAME}}.spec
```

### 构建产物

构建完成后，RPM 包位于：

- **二进制 RPM**：`RPMS/x86_64/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.x86_64.rpm`
- **源码包**：`SRPMS/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.src.rpm`

## SPEC 文件说明

### 修改基本信息

编辑 `SPECS/{{PROJECT_NAME}}.spec` 文件的头部：

```specfile
Name:           {{PROJECT_NAME}}          # 软件包名称
Version:        {{VERSION}}               # 版本号
Release:        {{RELEASE}}%{?dist}      # 发布号
Summary:        {{SUMMARY}}              # 一句话描述
License:        {{LICENSE}}              # 许可证
URL:            {{URL}}                  # 项目主页
Source0:        {{SOURCE_URL}}           # 源代码地址
```

### 修改依赖

```specfile
Requires:       bash >= 4.0              # 运行时依赖
BuildRequires:  gcc >= 4.8               # 构建时依赖
```

### 修改安装路径

在 `%install` 部分修改文件安装位置：

```specfile
%install
# 修改安装目标路径
install -m 0755 myapp %{buildroot}%{_bindir}/
```

### 修改文件清单

在 `%files` 部分定义要打包的文件：

```specfile
%files
%attr(0755,root,root) %{_bindir}/{{PROJECT_NAME}}
%config(noreplace) %{_sysconfdir}/{{PROJECT_NAME}}/config.yml
```

## 安装脚本说明

本 RPM 包包含以下安装/卸载脚本：

### %pre（安装前脚本）

在文件安装前执行，用于：
- 创建系统用户
- 检查环境
- 停止旧服务

### %post（安装后脚本）

在文件安装后执行，用于：
- 设置文件权限
- 启用/启动服务
- 注册 systemd 服务

### %preun（卸载前脚本）

在文件删除前执行，用于：
- 停止服务
- 备份配置

### %preun（卸载后脚本）

在文件删除后执行，用于：
- 清理用户
- 删除数据目录

### 修改脚本

编辑 SPEC 文件中的对应部分：

```specfile
%pre
#!/bin/bash
# 安装前脚本内容
if [ $1 -eq 1 ]; then
    echo "首次安装..."
fi

%post
#!/bin/bash
# 安装后脚本内容
systemctl daemon-reload 2>/dev/null || true

%preun
#!/bin/bash
# 卸载前脚本内容
if [ $1 -eq 0 ]; then
    systemctl stop {{PROJECT_NAME}} 2>/dev/null || true
fi

%postun
#!/bin/bash
# 卸载后脚本内容
if [ $1 -eq 0 ]; then
    userdel {{PROJECT_NAME}} 2>/dev/null || true
fi
```

## 添加新文件

### 方法 1：直接复制到 SOURCES 目录

```bash
# 将文件复制到源代码目录
cp /path/to/newfile SOURCES/{{PROJECT_NAME}}-{{VERSION}}/
```

### 方法 2：在 SPEC 中指定源文件

```specfile
Source1:        config.ini
Source2:        init-script.sh
```

### 方法 3：在 %install 中创建

```specfile
%install
# 创建新的配置目录
install -d %{buildroot}%{_sysconfdir}/{{PROJECT_NAME}}/conf.d
```

## 常见问题

### Q: 构建失败，提示缺少依赖？

```bash
# 安装缺失的依赖
sudo yum install -y <missing-package>
```

### Q: 文件未被打包？

检查 `%files` 部分是否包含该文件：

```specfile
%files
%{_bindir}/*          # 包含所有二进制文件
```

### Q: 权限不正确？

使用 `%attr` 显式指定权限：

```specfile
%files
%attr(0755,root,root) %{_bindir}/myapp
```

### Q: 如何验证 RPM 包？

```bash
# 使用 rpmlint 检查
rpmlint RPMS/x86_64/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.x86_64.rpm

# 查看包内容
rpm -qlp RPMS/x86_64/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.x86_64.rpm

# 测试安装
sudo rpm -ivh RPMS/x86_64/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.x86_64.rpm
```

## 高级用法

### 从源码包重新构建

```bash
rpmbuild --rebuild SRPMS/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.src.rpm
```

### 仅重新安装（不重新构建）

```bash
rpm -ivh --force RPMS/x86_64/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.x86_64.rpm
```

### 升级安装

```bash
sudo rpm -Uvh RPMS/x86_64/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.x86_64.rpm
```

### 查看脚本执行日志

```bash
sudo rpm -ivh --test RPMS/x86_64/{{PROJECT_NAME}}-{{VERSION}}-{{RELEASE}}.x86_64.rpm
```

## 参考资料

- [RPM 官方文档](https://rpm.org/documentation.html)
- [Fedora RPM 指南](https://docs.fedoraproject.org/en-US/package-maintainers/Packaging/)
- SPEC 文件参考：`references/rpm-spec-reference.md`
