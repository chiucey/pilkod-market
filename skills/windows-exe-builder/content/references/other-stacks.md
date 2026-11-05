# 其他技术栈快速参考(Go / Rust / Electron / .NET)

Python 之外的备选。各给一段最小可工作流程。

---

## Go

**适合**:CLI 工具、系统工具、性能敏感场景。

**环境**:装 Go 1.21+,`go version` 验证。

**最小项目结构**:
```
myapp/
├── go.mod
├── go.sum
└── main.go
```

**main.go 最小骨架**:
```go
package main
import "fmt"
func main() {
    fmt.Println("hello from go")
}
```

**打包**:
```bash
# CLI 程序
go build -ldflags="-s -w" -o MyApp.exe .

# GUI 程序(无控制台窗口)
go build -ldflags="-H windowsgui -s -w" -o MyApp.exe .
```

- `-s -w` 去掉符号表,体积更小(从 ~10MB → ~6MB)
- `-H windowsgui` 隐藏控制台(GUI 必备)

**GUI 选项**:
- [Fyne](https://fyne.io/) — Material Design 风格,简单
- [Wails](https://wails.io/) — Web 前端 + Go 后端,比 Electron 小很多
- [gioui](https://gioui.org/) — 原生体验,API 较底层

**坑**:
- 跨平台编译需要装交叉编译工具链,本 skill 范围只做 Windows
- CGO 依赖会让打包复杂,尽量用纯 Go 库

---

## Rust

**适合**:性能极敏感场景(图像处理、算法、系统工具)。

**环境**:装 Rust toolchain,`rustup target add x86_64-pc-windows-msvc`(Windows 上)或 `x86_64-pc-windows-gnu`(跨平台编译到 Windows)。

**最小项目**:
```bash
cargo new myapp --bin
cd myapp
cargo build --release
# 产物:target/release/myapp.exe
```

**GUI 选项**:
- [egui](https://www.egui.rs/) — 即时模式 GUI,简单
- [Tauri](https://tauri.app/) — Web 前端 + Rust 后端,比 Electron 小 10 倍
- [Slint](https://slint-ui.com/) — 原生 UI,声明式

**坑**:
- 学习曲线陡,只建议在性能真的重要时用
- 编译时间长(首次几分钟)
- 跨编译到 Windows 需要装额外的 target 和 linker

---

## Electron

**适合**:Web 风格复杂 GUI(只在前端代码已经存在时推荐)。

**环境**:Node.js 18+,`npm install -g electron-builder`。

**最小项目**:
```
myapp/
├── package.json
├── main.js          # Node 主进程
├── preload.js       # 预加载脚本
├── index.html       # 前端入口
├── renderer.js
└── build/
    └── icon.ico
```

**package.json 关键字段**:
```json
{
  "name": "myapp",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "build": "electron-builder --win --x64"
  },
  "build": {
    "appId": "com.example.myapp",
    "productName": "MyApp",
    "win": {
      "icon": "build/icon.ico",
      "target": "nsis"
    }
  }
}
```

**打包**:
```bash
npm install
npm run build
# 产物:dist/MyApp Setup 1.0.0.exe(NSIS 安装包)或 dist/win-unpacked/MyApp.exe(免安装版)
```

**注意**:Electron 的产物通常是 NSIS 安装包,不是单文件 exe。本 skill 范围内用 `--dir` 模式可以输出免安装版:
```bash
electron-builder --win --x64 --dir
# 产物:dist/win-unpacked/MyApp.exe(免安装)
```

**坑**:
- 体积大(80-200MB,几乎不可避免)
- 启动慢(2-5s)
- 默认会产生 NSIS 安装包,提醒用户需要免安装版
- Chromium 安全更新频繁,需要定期升级

**只在用户明确要 Web 风格界面或已有前端代码时选**。

---

## C# / .NET

**适合**:Windows 原生 GUI、强 Windows 系统集成。

**环境**:.NET SDK 6/7/8,`dotnet --version` 验证。

**最小项目**:
```bash
dotnet new winforms -n MyApp     # WinForms(简单)
dotnet new wpf -n MyApp          # WPF(现代,推荐)
cd MyApp
```

**打包(单文件自包含)**:
```bash
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o publish
# 产物:publish/MyApp.exe(单文件,自带 .NET 运行时,~70MB)
```

**体积优化**(用 trimmed self-contained,~30MB):
```bash
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:PublishTrimmed=true -o publish
```

**注意**:trimmed 模式会裁剪未用到的库,某些反射/动态特性可能挂掉,需要测试。

**坑**:
- 只支持 Windows(GUI 部分,console 部分 .NET 跨平台)
- WinForms 学习曲线低但界面老;WPF 现代化但 XAML 学习成本
- 默认依赖 .NET runtime(用户机器要装);`--self-contained` 自带但体积大

---

## 选哪个?——快速决策

| 场景 | 推荐 |
|------|------|
| 默认 / 不确定 | **Python** |
| CLI 工具,体积小 | **Go** |
| 性能敏感(算法/图像) | **Rust** |
| Web 风格 GUI | **Electron**(但警告体积) |
| Windows 原生体验 | **C# WPF** |
| 已有 Python 库依赖 | **Python** |
| 已有前端代码想打包 | **Electron** |
