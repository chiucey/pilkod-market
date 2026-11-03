# DEB包control文件规范

## 必须字段

### Package
- **格式**: 纯小写字母、数字和连字符
- **示例**: `myapp`, `python3-flask`
- **限制**: 最小2字符，最大255字符

### Version
- **格式**: `upstream_version[-debian_revision]`
- **示例**: `1.0.0`, `2.3.1-1`, `1.0~beta`
- **Debian修订版**: 可选，用于Debian/Ubuntu打包

### Architecture
- **选项**: `all`, `any`, 或特定架构
- **常用值**: `amd64`, `i386`, `arm64`, `armhf`
- **`all`**: 跨架构兼容，无需编译
- **`any`**: 需要针对每个架构编译

### Maintainer
- **格式**: `Name <email@example.com>`
- **示例**: `John Doe <john@example.com>`

### Description
- **格式**: 第一行简短描述，后续行缩进描述
- **首行限制**: 简短，通常不超过60字符
- **示例**:
  ```
  Description: A powerful CLI tool
   This tool provides advanced features for
   system administration and automation.
  ```

## 常用可选字段

### Depends
- **格式**: 包名及版本约束列表
- **版本约束符**: `<<`, `<=`, `=`, `>=`, `>>`
- **示例**: `bash (>= 4.0)`, `python3, curl`
- **替代符**: `|` (或), `{}` (版本可选)

### Pre-Depends
- 必须在主包之前完全安装的包
- 用于关键系统包

### Recommends
- 建议安装但非必需的包

### Suggests
- 建议但不自动安装的包

### Conflicts
- 与本包不能同时安装的包

### Provides
- 本包提供的虚拟包名

### Replaces
- 本包替换的文件

### Section
- **常用值**: `utils`, `net`, `admin`, `text`, `graphics`, `web`, `mail`, `devel`
- 用于软件包分类

### Priority
- **选项**: `required`, `important`, `standard`, `optional`
- 大多数用户包使用 `optional`

### Homepage
- 项目主页URL

### Built-Using
- 编译时使用的源码包

## 版本约束语法

```
Package                  # 任意版本
Package (>= 1.0)        # 大于等于
Package (= 1.0)          # 精确版本
Package (>> 1.0)        # 严格大于
Package (>= 1.0 < 2.0)  # 版本范围
Package1 | Package2      # 任一包
```

## 完整示例

```
Package: myapp
Version: 1.2.3-1
Section: utils
Priority: optional
Architecture: all
Depends: bash (>= 4.0), python3 (>= 3.6)
Recommends: curl, wget
Suggests: vim, emacs
Maintainer: John Doe <john@example.com>
Description: A versatile CLI tool
 A powerful command-line utility that helps with
 daily development tasks. Features include:
  - File management
  - System monitoring
  - Quick deployment
Homepage: https://github.com/user/myapp
```
