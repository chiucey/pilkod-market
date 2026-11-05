# DEB包构建命令参考

## 构建基础

### 打包命令
```bash
dpkg-deb --build <目录> [输出.deb]
```

### 示例
```bash
# 基本打包
dpkg-deb --build my-package

# 指定输出文件
dpkg-deb --build my-package my-package_1.0.0_amd64.deb

# 详细输出
dpkg-deb --build --verbose my-package
```

## 查看包内容

### 列出文件
```bash
dpkg-deb --contents <.deb>
```

### 显示信息
```bash
dpkg-deb --info <.deb>
```

### 提取包内容
```bash
# 解压到目录
dpkg-deb --extract <.deb> <目录>

# 列出内容到文件
dpkg-deb --ctrl-tarfile <.deb> | tar -tf -
```

## 安装与卸载

### 安装
```bash
# 使用dpkg（不自动处理依赖）
sudo dpkg -i <.deb>

# 使用apt（自动处理依赖）
sudo apt install <.deb>
```

### 卸载
```bash
# 移除包（保留配置）
sudo dpkg -r <package-name>

# 完全清除（包含配置）
sudo dpkg --purge <package-name>
```

## 包信息查询

### 列出已安装文件
```bash
dpkg -L <package-name>
```

### 包状态
```bash
dpkg -s <package-name>
```

### 检查文件属于哪个包
```bash
dpkg -S <file-path>
```

### 查找包
```bash
# 搜索包名
dpkg -l | grep <pattern>

# 查找文件位置
dpkg-query -S <file>
```

## 包验证

### 检查构建依赖
```bash
dpkg-checkbuilddeps
```

### 验证包
```bash
# 验证包签名
debsigs --verify <.deb>

# 检查包策略合规性
lintian <.deb>
```

### MD5校验
```bash
# 提取md5sums
dpkg-deb --fsys-tarfile <.deb> | tar -xf - ./DEBIAN/md5sums

# 手动验证
dpkg-deb --contents <.deb> | md5sum -c
```

## 权限设置

### DEBIAN目录
```bash
sudo chmod 755 DEBIAN
sudo chmod 755 DEBIAN/*
```

### 用户文件
```bash
sudo chown -R root:root DEBIAN
sudo chown -R root:root usr etc var
```

## lintian检查

lintian是Debian包的静态分析工具：

```bash
# 安装lintian
sudo apt install lintian

# 检查包
lintian <.deb>

# 详细输出
lintian -i <.deb>

# 警告视为错误
lintian -W error <.deb>
```

## debuild构建

debuild是高级构建工具：

```bash
# 安装
sudo apt install devscripts

# 在包目录中执行
debuild -us -uc  # 不签名构建
```

## 签名包

### 生成GPG密钥
```bash
gpg --full-generate-key
```

### 签名包
```bash
debsign <.changes文件>
dpkg-sig --sign builder <.deb>
```

## 常见工作流

### 完整构建流程
```bash
# 1. 创建包结构
mkdir -p my-package/DEBIAN
mkdir -p my-package/usr/bin
mkdir -p my-package/etc/myapp

# 2. 添加文件
cp myapp my-package/usr/bin/
cp config.conf my-package/etc/myapp/

# 3. 创建control文件
cat > my-package/DEBIAN/control << EOF
Package: myapp
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Maintainer: Name <email@example.com>
Description: My application
EOF

# 4. 设置权限
sudo chmod 755 my-package/DEBIAN

# 5. 生成md5sums
find my-package -type f ! -path '*/DEBIAN/*' -exec md5sum {} \; > my-package/DEBIAN/md5sums

# 6. 构建
dpkg-deb --build my-package

# 7. 验证
dpkg-deb --info my-package.deb
dpkg-deb --contents my-package.deb
```

## 输出文件

### .deb文件
最终的Debian包文件，可分发和安装。

### .changes文件
构建变更日志，用于上传到仓库。

### .dsc文件
源码包描述文件。
