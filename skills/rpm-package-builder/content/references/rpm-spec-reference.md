---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100db57c1cdc5c39ba2026dd0e402b8576b1848f352e774f10b68a352930f92906002200a8df897f952ae75523e27d7182ea35518d1ff29fba8a8b2e037148f2cf43005
    ReservedCode2: 304502200848bbea87ca02536c09c81546c59790763cf0e9842a732d7645a041b13e5479022100c50082f2d991c2c5977d00ddb79014bd8e2d84cedc8aa8827ff2387213ef3513
---

# RPM SPEC 文件完整参考指南

## 1. SPEC 文件结构概述

RPM SPEC 文件是 RPM 包构建的核心，它定义了软件包的元数据、构建过程、安装行为等。一个完整的 SPEC 文件通常包含以下部分：

```
Name:          软件包名称
Version:       版本号
Release:       发布号
Summary:       一句话描述
License:       许可证
URL:           项目主页
Source0:       源代码压缩包
Patch0:        补丁文件
BuildArch:     目标架构
BuildRoot:     构建根目录
Requires:      运行时依赖
BuildRequires: 构建时依赖

%description
软件包详细描述

%prep
准备阶段，解压源码包

%build
构建阶段，编译源码

%install
安装阶段，将文件复制到构建目录

%files
文件清单，定义哪些文件会被包含到 RPM 包中

%pre
安装前脚本

%post
安装后脚本

%preun
卸载前脚本

%postun
卸载后脚本

%changelog
变更日志
```

## 2. 必需标签详解

### 2.1 基础标签

**Name（名称）**

- 软件包的唯一标识符
- 必须唯一，不能与已有软件包冲突
- 建议使用小写字母和连字符
- 不能包含空格或特殊字符（除了连字符）

```specfile
Name:           my-application
```

**Version（版本号）**

- 原始软件的版本号
- 应该与上游发布版本一致
- 推荐使用语义化版本格式（如 1.2.3）
- 不允许包含连字符（如果需要，使用 Release 字段）

```specfile
Version:        1.2.3
```

**Release（发布号）**

- RPM 包自己的发布版本
- 格式：数字[.描述]
- 每次重新打包时递增
- 可以包含平台标识

```specfile
Release:        1%{?dist}
# 或
Release:        2.el7
```

**Summary（摘要）**

- 一句话描述软件包功能
- 应该简洁明了
- 首字母大写
- 长度建议在 50-80 字符

```specfile
Summary:        A high-performance web server
```

### 2.2 源代码和补丁

**Source0, Source1, ...（源代码）**

- 指向源代码压缩包或相关文件的 URL 或本地路径
- 可以是本地文件（相对于当前目录）或远程 URL
- 支持多个源文件

```specfile
Source0:        %{name}-%{version}.tar.gz
Source1:        config.ini
Source2:        %{name}-init.sh
```

**Patch0, Patch1, ...（补丁）**

- 指向需要应用的补丁文件
- 与 Source 类似，可以使用编号区分多个补丁

```specfile
Patch0:         %{name}-fix-build.patch
Patch1:         %{name}-enable-feature.patch
```

### 2.3 构建信息

**BuildArch（目标架构）**

- 指定构建的目标系统架构
- 常用值：x86_64, i686, noarch, aarch64
- 如果不指定，则支持所有架构

```specfile
BuildArch:      x86_64
# 或
BuildArch:      noarch  # 无需编译的包
```

**BuildRoot（构建根目录）**

- 定义构建时的虚拟根目录
- 通常使用 %{_topdir}/BUILDROOT
- 在 %install 阶段使用

```specfile
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
```

**ExclusiveArch（独占架构）**

- 限制软件包只能在特定架构上构建

```specfile
ExclusiveArch: x86_64 aarch64
```

**ExcludeArch（排除架构）**

- 排除不支持的架构

```specfile
ExcludeArch:   s390x
```

### 2.4 依赖管理

**Requires（运行时依赖）**

- 指定软件包运行时需要的其他软件包
- 支持版本比较运算符：=, <, >, <=, >=, !=
- 支持虚拟提供（Provides）

```specfile
Requires:       bash >= 4.0
Requires:       libssl >= 1.1.0
Requires:       python3 >= 3.6
Requires:       %{name}-core = %{version}-%{release}
```

**BuildRequires（构建时依赖）**

- 编译构建时需要的工具和库
- 在构建环境中必须安装

```specfile
BuildRequires:  gcc >= 4.8
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  pkgconfig(glib-2.0)
```

**Provides（提供的功能）**

- 声明软件包提供的虚拟包名
- 其他软件包可以依赖这个虚拟名称

```specfile
Provides:       webserver
Provides:       %{name}-cli = %{version}-%{release}
```

**Obsoletes（替换）**

- 声明该软件包替换的其他软件包
- 安装时自动移除被替换的包

```specfile
Obsoletes:      old-package-name < 2.0
```

**Conflicts（冲突）**

- 声明与该软件包冲突的其他软件包

```specfile
Conflicts:      conflicting-package
```

### 2.5 其他重要标签

**License（许可证）**

- 软件包的许可证类型
- 常用值：GPL-2.0, GPL-3.0, Apache-2.0, MIT, BSD, Proprietary

```specfile
License:        Apache-2.0
```

**URL（项目主页）**

- 软件包的项目主页或源码仓库地址

```specfile
URL:            https://github.com/example/my-application
```

**Vendor（供应商）**

- 软件包的发布厂商

```specfile
Vendor:         My Company Inc.
```

**Packager（打包者）**

- 打包者的联系信息

```specfile
Packager:       developer@example.com
```

## 3. SPEC 文件各部分详解

### 3.1 %description（描述部分）

详细描述软件包的功能、用途和特点。允许使用多行文本，可以包含空白行。

```specfile
%description
This is a high-performance web server designed for modern applications.

Features:
- Supports HTTP/2 and HTTP/3 protocols
- Built-in load balancing
- TLS 1.3 encryption
- Advanced caching mechanisms
```

### 3.2 %prep（准备阶段）

准备阶段负责解压源代码和应用补丁。通常使用 %setup 和 %patch 宏。

**%setup 宏**

```specfile
# 基本用法 - 解压默认源码
%prep
%setup

# 解压并指定目录名
%setup -n %{name}-%{version}-custom

# 清理后重新解压
%setup -c

# 不解压（适用于单文件或已解压的源码）
%setup -T -D

# 应用多个补丁
%setup
%patch0 -p1
%patch1 -p1 -b .orig
```

**%patch 宏**

```specfile
%patch0 -p1    # 应用 Patch0，剥离一层目录
%patch1 -p0    # 应用 Patch1，不剥离目录
```

**自定义准备脚本**

```specfile
%prep
# 检查源码是否存在
if [ ! -f %{SOURCE0} ]; then
    echo "Error: Source file not found"
    exit 1
fi

# 解压并进入目录
%setup -q

# 应用补丁
%patch0

# 进行其他准备工作
chmod +x configure
```

### 3.3 %build（构建阶段）

执行软件的编译构建过程。

**基本构建示例**

```specfile
%build
# 配置
./configure --prefix=%{_prefix} \
            --sysconfdir=%{_sysconfdir} \
            --localstatedir=%{_localstatedir} \
            --enable-shared

# 编译
make %{?_smp_mflags}

# 测试（可选）
make test || true
```

**使用 make 的标准构建**

```specfile
%build
%configure
make %{?_smp_mflags}
```

**Python 包构建**

```specfile
%build
python3 setup.py build

# 或使用 pybuild
%py3_build
```

**CMake 构建**

```specfile
%build
mkdir -p build
cd build
%cmake ..
make %{?_smp_mflags}
cd ..
```

### 3.4 %install（安装阶段）

将构建产物和必要文件安装到构建根目录。这个阶段不执行真正的系统安装，而是将文件复制到虚拟的构建目录中。

**基本安装示例**

```specfile
%install
# 清理旧的构建目录
rm -rf %{buildroot}

# 安装二进制文件
make install DESTDIR=%{buildroot}

# 安装配置文件
install -d %{buildroot}%{_sysconfdir}/%{name}
install -m 0644 config.yml %{buildroot}%{_sysconfdir}/%{name}/

# 安装 systemd 服务文件
install -d %{buildroot}%{_unitdir}
install -m 0644 %{name}.service %{buildroot}%{_unitdir}/

# 安装脚本
install -d %{buildroot}%{_sbindir}
install -m 0755 init.sh %{buildroot}%{_sbindir}/%{name}-init
```

**使用 %makeinstall**

```specfile
%install
%makeinstall
```

**手动复制文件**

```specfile
%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_mandir}/man1

install -m 0755 myapp %{buildroot}%{_bindir}/
install -m 0644 libmyapp.so* %{buildroot}%{_libdir}/
install -m 0644 myapp.1 %{buildroot}%{_mandir}/man1/
```

**创建目录**

```specfile
%install
install -d %{buildroot}%{_localstatedir}/lib/%{name}
install -d %{buildroot}%{_localstatedir}/log/%{name}
install -d %{buildroot}%{_tmpfilesdir}
```

### 3.5 %files（文件清单）

定义哪些文件会被包含到 RPM 包中。这是 RPM 包构建中最关键的部分之一。

**基本语法**

```specfile
%files
%defattr(-,root,root,-)    # 默认权限
%attr(0755,root,root) %{_bindir}/myapp
%attr(0644,root,root) %{_sysconfdir}/%{name}/config.yml
```

**使用通配符**

```specfile
%files
%{_bindir}/*                # 所有二进制文件
%{_libdir}/lib*.so*         # 所有共享库
%{_mandir}/man1/*           # 所有 man 页面
```

**目录声明**

```specfile
%files
%dir %{_sysconfdir}/%{name}           # 声明目录本身
%{_sysconfdir}/%{name}/*              # 目录中的文件
%dir %attr(0755,root,root) %{_localstatedir}/data
```

**文档和配置标记**

```specfile
%files
%doc README.md LICENSE         # 文档文件
%docdir %{_docdir}/%{name}     # 文档目录
%config(noreplace) %{_sysconfdir}/%{name}/app.conf   # 配置文件（不替换用户修改）
%config(missingok) %{_sysconfdir}/%{name}/default.conf  # 可选配置文件
```

**文件权限标记**

```specfile
%files
%attr(0644,root,root) %{_bindir}/myapp
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(-,root,root) %{_libdir}/%{name}/*.so
```

### 3.6 脚本部分

RPM 包支持四种脚本，分别在安装和卸载的不同阶段执行。

#### %pre（安装前脚本）

在软件包文件安装到系统之前执行。

```specfile
%pre
# 检查是否已存在旧版本
if [ $1 -eq 2 ]; then
    # 升级安装（$1=2 表示升级）
    echo "Upgrading from previous version..."
fi

# 创建必要的系统用户
if ! getent passwd myapp > /dev/null 2>&1; then
    groupadd -r myapp 2>/dev/null || true
    useradd -r -g myapp -d %{_localstatedir}/lib/%{name} -s /sbin/nologin \
        -c "MyApp Service" myapp 2>/dev/null || true
fi

# 停止旧服务（如果存在）
if [ -f /etc/init.d/myapp ]; then
    service myapp stop 2>/dev/null || true
fi

exit 0
```

#### %post（安装后脚本）

在软件包文件安装到系统之后执行。

```specfile
%post
# 重新加载 systemd（如果安装了 systemd 服务）
if [ $1 -eq 1 ]; then
    # 首次安装（$1=1 表示安装，$1=2 表示升级）
    systemctl daemon-reload 2>/dev/null || true
    systemd-tmpfiles --create %{name}.conf 2>/dev/null || true
fi

# 启动服务
systemctl enable %{name}.service > /dev/null 2>&1 || true

# 设置文件权限
chown -R myapp:myapp %{_localstatedir}/lib/%{name} 2>/dev/null || true
chown -R myapp:myapp %{_localstatedir}/log/%{name} 2>/dev/null || true

echo "Installation completed successfully!"
```

#### %preun（卸载前脚本）

在软件包文件从系统删除之前执行。

```specfile
%preun
# 停止服务
if [ $1 -eq 0 ]; then
    # 完全卸载（$1=0 表示卸载，$1=1 表示升级）
    systemctl stop %{name}.service 2>/dev/null || true
    systemctl disable %{name}.service 2>/dev/null || true
fi

# 升级时只停止服务，不删除用户和数据
if [ $1 -eq 1 ]; then
    systemctl stop %{name}.service 2>/dev/null || true
fi

exit 0
```

#### %postun（卸载后脚本）

在软件包文件从系统删除之后执行。

```specfile
%postun
# 重新加载 systemd
systemctl daemon-reload 2>/dev/null || true

# 完全卸载时清理
if [ $1 -eq 0 ]; then
    # 删除用户和组（可选）
    userdel myapp 2>/dev/null || true
    groupdel myapp 2>/dev/null || true

    # 清理数据目录（谨慎使用）
    rm -rf %{_localstatedir}/lib/%{name} 2>/dev/null || true

    # 清理日志（可选）
    rm -rf %{_localstatedir}/log/%{name} 2>/dev/null || true
fi

# 升级后重启服务
if [ $1 -ge 1 ]; then
    systemctl start %{name}.service 2>/dev/null || true
fi

exit 0
```

#### 脚本变量说明

| 变量 | 值 | 含义 |
|------|-----|------|
| `$1` | 0 | 卸载软件包 |
| `$1` | 1 | 首次安装 |
| `$1` | 2 | 升级软件包 |

#### 脚本最佳实践

```specfile
# 脚本头部 - 设置环境
%pre
%{?_fontfontdir: echo "Font directory: %{_fontfontdir}"}

# 始终以 exit 0 结束，除非是致命错误
# 使用 set -e 捕获错误
%pre
set -e

# 清理工作
# ...

set +e
exit 0
```

### 3.7 %changelog（变更日志）

记录软件包的变更历史。

```specfile
%changelog
* Tue Apr 09 2026 Your Name <your@email.com> - 1.2.3-1
- Added new feature for load balancing
- Fixed memory leak in connection handler
- Updated documentation

* Mon Jan 15 2026 Your Name <your@email.com> - 1.2.2-1
- Security update: patched CVE-2024-XXXX
- Improved performance by 20%

* Wed Dec 20 2025 Your Name <your@email.com> - 1.2.1-1
- Initial package release
```

## 4. RPM 宏参考

### 4.1 常用宏

| 宏 | 展开路径 | 说明 |
|----|---------|------|
| %{_bindir} | /usr/bin | 用户二进制文件目录 |
| %{_sbindir} | /usr/sbin | 系统管理二进制文件目录 |
| %{_libdir} | /usr/lib64 或 /usr/lib | 库文件目录 |
| %{_lib} | /lib 或 /usr/lib | 32 位库目录 |
| %{_datadir} | /usr/share | 共享数据目录 |
| %{_sysconfdir} | /etc | 配置文件目录 |
| %{_localstatedir} | /var | 本地状态目录 |
| %{_prefix} | /usr | 安装前缀 |
| %{_docdir} | /usr/share/doc | 文档目录 |
| %{_mandir} | /usr/share/man | man 页面目录 |
| %{_unitdir} | /usr/lib/systemd/system | systemd 服务目录 |
| %{_initrddir} | /etc/rc.d/init.d | 初始化脚本目录 |
| %{_tmppath} | /var/tmp | 临时文件目录 |
| %{_builddir} | %{_topdir}/BUILD | 构建目录 |
| %{_rpmdir} | %{_topdir}/RPMS | RPM 输出目录 |
| %{_srcrpmdir} | %{_topdir}/SRPMS | 源码包输出目录 |
| %{_topdir} | ~/rpmbuild | rpmbuild 顶级目录 |

### 4.2 条件宏

```specfile
# 发行版特定条件
%if 0%{?rhel} == 7
# RHEL 7 特定的配置
%endif

%if 0%{?fedora} >= 28
# Fedora 28+ 特定的配置
%endif

# 架构特定条件
%ifarch x86_64
# x86_64 特定的配置
%endif

%ifnarch x86_64
# 非 x86_64 架构的处理
%endif
```

### 4.3 算术和字符串宏

```specfile
# 数值运算
%global major_version %(echo %{version} | cut -d. -f1)
%global minor_version %(echo %{version} | cut -d. -f2)

# 字符串操作
%global name_upper %(echo %{name} | tr '[:lower:]' '[:upper:]')
```

## 5. 完整示例

### 5.1 简单服务类 RPM

```specfile
Name:           myapp-service
Version:        1.2.3
Release:        1%{?dist}
Summary:        MyApp High-Performance Service

License:        Apache-2.0
URL:            https://github.com/example/myapp
Source0:        %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:      x86_64
Requires:       systemd
Requires:       bash >= 4.0
BuildRequires:  gcc >= 4.8
BuildRequires:  make
BuildRequires:  systemd-rpm-macros

%description
MyApp is a high-performance service application designed for
enterprise environments. It provides advanced features including
load balancing, automatic failover, and real-time monitoring.

%prep
%autosetup -p1

%build
make %{?_smp_mflags} CFLAGS="%{optflags}"

%install
rm -rf %{buildroot}

# 安装二进制文件
make install DESTDIR=%{buildroot}

# 安装配置文件
install -d %{buildroot}%{_sysconfdir}/%{name}
install -m 0644 config.yml %{buildroot}%{_sysconfdir}/%{name}/

# 安装 systemd 服务
install -d %{buildroot}%{_unitdir}
install -m 0644 %{name}.service %{buildroot}%{_unitdir}/

# 创建数据目录
install -d %{buildroot}%{_localstatedir}/lib/%{name}
install -d %{buildroot}%{_localstatedir}/log/%{name}
install -d %{buildroot}%{_localstatedir}/run/%{name}

# 安装配置文件
%config(noreplace) %{_sysconfdir}/%{name}/config.yml

%files
%defattr(-,root,root,-)
%attr(0755,root,root) %{_bindir}/%{name}
%attr(0755,root,root) %{_bindir}/%{name}-ctl
%{_mandir}/man1/%{name}.1.gz
%{_unitdir}/%{name}.service
%dir %attr(0755,root,root) %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/config.yml
%dir %attr(0755,root,root) %{_localstatedir}/lib/%{name}
%dir %attr(0755,root,root) %{_localstatedir}/log/%{name}
%dir %attr(0755,root,root) %{_localstatedir}/run/%{name}

%pre
if ! getent passwd %{name} > /dev/null 2>&1; then
    groupadd -r %{name} 2>/dev/null || true
    useradd -r -g %{name} -d %{_localstatedir}/lib/%{name} \
        -s /sbin/nologin -c "%{summary}" %{name} 2>/dev/null || true
fi

%post
systemctl daemon-reload 2>/dev/null || true
systemctl preset %{name}.service >/dev/null 2>&1 || true

%preun
if [ $1 -eq 0 ]; then
    systemctl stop %{name}.service 2>/dev/null || true
    systemctl disable %{name}.service 2>/dev/null || true
fi

%postun
systemctl daemon-reload 2>/dev/null || true
if [ $1 -eq 0 ]; then
    userdel %{name} 2>/dev/null || true
    groupdel %{name} 2>/dev/null || true
fi

%changelog
* Tue Apr 09 2026 Your Name <your@email.com> - 1.2.3-1
- Initial package release
```

### 5.2 Python 应用 RPM

```specfile
Name:           python3-myapp
Version:        2.0.0
Release:        1%{?dist}
Summary:        MyApp Python Application

License:        MIT
URL:            https://github.com/example/myapp
Source0:        %{url}/archive/v%{version}.tar.gz

BuildArch:      noarch
Requires:       python3 >= 3.6
Requires:       python3-pip
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

%description
MyApp is a Python-based application for data processing and analysis.

%prep
%autosetup -p1

%build
# 无需编译
python3 setup.py build

%install
# 安装 Python 包
%py3_install

# 安装配置文件
install -d %{buildroot}%{_sysconfdir}/%{name}
install -m 0644 config.ini %{buildroot}%{_sysconfdir}/%{name}/

%files
%{python3_sitelib}/%{name}/
%{python3_sitelib}/%{name}-%{version}-py*.egg-info/
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1.gz
%dir %attr(0755,root,root) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.ini

%doc README.md LICENSE
%docdir %{_docdir}/%{name}

%changelog
* Tue Apr 09 2026 Your Name <your@email.com> - 2.0.0-1
- Initial package release
```

## 6. 构建 RPM 包

### 6.1 设置 RPM 构建环境

```bash
# 安装构建工具
# CentOS/RHEL
sudo yum install -y rpm-build rpmdevtools

# Fedora
sudo dnf install -y rpm-build rpmdevtools

# 创建 RPM 构建目录结构
rpmdev-setuptree

# 查看生成的目录
ls -la ~/rpmbuild/
```

### 6.2 构建命令

```bash
# 构建二进制 RPM
rpmbuild -ba SPECS/package.spec

# 只构建二进制 RPM（不构建源码包）
rpmbuild -bb SPECS/package.spec

# 只构建源码包
rpmbuild -bs SPECS/package.spec

# 从源码包构建
rpmbuild --rebuild SRPMS/package-1.0.0-1.el7.src.rpm
```

### 6.3 验证 SPEC 文件

```bash
# 检查 SPEC 文件语法
rpmlint SPECS/package.spec

# 检查生成的 RPM 包
rpmlint RPMS/x86_64/package-1.0.0-1.el7.x86_64.rpm
```

## 7. 常见问题与解决方案

### 7.1 文件未打包

**问题**：某些文件没有包含在 RPM 包中。

**解决方案**：

```specfile
%files
# 使用绝对路径
%{_bindir}/myapp

# 使用通配符
%{_bindir}/*

# 确保目录被声明
%dir %{_sysconfdir}/%{name}
```

### 7.2 脚本执行失败

**问题**：安装/卸载脚本返回非零退出码。

**解决方案**：

```specfile
%pre
set -e
# 脚本内容
set +e
exit 0
```

### 7.3 依赖问题

**问题**：运行时提示缺少依赖。

**解决方案**：

```specfile
Requires:       needed-package >= 1.0
# 或使用虚拟提供
Provides:       webserver = 2.0
```

### 7.4 权限问题

**问题**：文件权限不正确。

**解决方案**：

```specfile
%files
%attr(0755,root,root) %{_bindir}/myapp
%defattr(-,root,root,0755)
```
