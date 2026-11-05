# 通用问题排查

跨技术栈的常见问题汇总。

## 1. .exe 启动闪退

**症状**:双击 exe,屏幕闪一下就没了。

**诊断步骤**:
1. 打开 cmd,cd 到 exe 所在目录,直接 `MyApp.exe` 跑,看真实报错
2. 如果是 PyInstaller 打包的 GUI,临时去掉 `--noconsole` 重新打包,再跑
3. 看 exe 同目录是否生成了日志文件

**常见原因**:
- 资源文件路径错(用绝对路径,打包后找不到)
- 缺 DLL(用 `--hidden-import` 或 `dotnet publish --self-contained`)
- 依赖的系统库用户机器没有(用 self-contained 或换打包方式)

## 2. 体积过大

**症状**:`dist/MyApp.exe` 100MB+。

**优化方向**:
- **Python**:用 venv 隔离依赖,只装真正用到的包(全局 site-packages 是头号元凶)
- **Go**:`-ldflags="-s -w"` 去掉符号表
- **Rust**:`release` 模式 + `lto=true`
- **Electron**:没办法,这就是 Electron 的代价,提醒用户
- **.NET**:`PublishTrimmed=true` + ReadyToRun 编译

## 3. 杀毒软件报毒

**症状**:Windows Defender / 360 / 火绒 把 .exe 标为病毒。

**原因**:PyInstaller / Nuitka 等打包的 exe 没有数字签名,触发启发式扫描。**这是打包机制固有问题,不是 bug。**

**不在本 skill 范围**。建议:
- 用户加白名单
- 买代码签名证书(自费)
- 换 Go/Rust(报毒率低很多,因为编译型语言的产物更"正常")
- 用 [PyInstaller bootloader 自定义](https://pyinstaller.org/en/stable/bootloader-building.html) 一定程度缓解

明确告诉用户:**"打包方案本身的固有限制,不算 skill 出错"**。

## 4. 首次启动很慢

**症状**:双击 exe 后 3-10 秒才出现界面。

**原因**:单文件模式(--onefile)启动时需要把内部文件解压到临时目录。

**优化**:
- 改用 `--onedir`(目录模式),启动几乎秒开,但分多个文件
- 引导用户预期:"首次启动慢 3-5s 是正常的"

## 5. 资源文件找不到

**症状**:运行时 `FileNotFoundError: assets/icon.png`。

**修复**:
1. 打包时加 `--add-data "assets;assets"`(PyInstaller)
2. 代码用 `sys._MEIPASS` 定位资源(参考 python-pyinstaller.md)

## 6. 中文/Unicode 乱码

**症状**:界面或控制台输出中文乱码。

**修复**:
- Python:文件开头加 `# -*- coding: utf-8 -*-`,GUI 用 UTF-8 字体
- Go:用 `utf8` 包,exe 编译时无乱码
- C#:默认 UTF-16,文件读取指定 Encoding
- Windows 控制台(老 cmd):`chcp 65001` 切到 UTF-8,或用 `Write-Output` PowerShell

## 7. 跨技术栈依赖装不上

**症状**:Go/Rust/Electron 装环境卡半天失败。

**兜底**:直接退回 Python+PyInstaller。
- Python 几乎所有机器都有
- `pip install pyinstaller` 通常秒装
- 用一个简单但能用的方案交付,比折腾完美方案强

## 8. 用户要 Mac / Linux

**直接说**:"本 skill 只做 Windows exe。Mac 用 .app,Linux 用 ELF,需要不同工具链。"

**可选引导**:
- Mac:`pyinstaller` 在 Mac 上能产 .app;或用 `dotnet publish -r osx-x64`
- Linux:`pyinstaller` 能产 ELF;Go 交叉编译最方便(`GOOS=linux go build`)

但**不在本 skill 范围内**,告诉用户另找资源。

## 9. 用户要安装包(MSI / NSIS)

**直接说**:"本 skill 只做免安装单 exe。需要安装包另找 electron-builder / WiX / NSIS 教程。"

如果你判断用户其实不需要安装包(他只是想让用户"能跑起来"),就一个 .exe 加个使用说明就够,主动引导他理解。

## 10. Windows SmartScreen 拦截

**症状**:用户看到 "Windows protected your PC" 蓝色警告。

**原因**:未签名的 exe 会被 SmartScreen 拦。

**不在 skill 范围**。告知用户:
- 点 "More info" → "Run anyway" 就能用
- 长期解决:买代码签名证书
- 也可以:让用户把 exe 加 Defender 排除项

## 错误信息查阅

- PyInstaller 报错 → 看 `build/MyApp/warn-MyApp.txt`
- Go 报错 → 直接看 stdout
- Rust 报错 → Rust 编译器信息很详细,直接看
- .NET → `dotnet publish` 输出 + 运行时日志
