---
name: windows-exe-builder
description: |
  End-to-end "需求 → Windows 可运行 .exe" workflow. When the user describes a software need and wants a runnable .exe they can double-click to launch, this skill picks the best tech stack, writes the code, packages it, verifies the .exe, and delivers the binary. Trigger on phrases like: 打包exe, 生成exe, 做个XX工具, 写个XX应用, build exe, package to exe, create executable, pyinstaller, exe 文件, 双击运行, 直接可用的exe. Supports Python, Go, Rust, Electron, C#/.NET — picks the right one based on the need. Do NOT use for: web apps / SaaS, server deployments, Mac/Linux binaries, installers / MSI, code signing, UAC elevation, antivirus false-positive workarounds — all out of scope.
---

# Windows EXE Builder

## Inputs to collect

- **软件需求描述**(必填)——用户说"做个XX"时,先复述一遍你打算做的,确认理解一致
- **目标形态**:CLI 还是 GUI(没说就按需求推断:有"窗口/界面/按钮"→ GUI;有"命令/参数/批处理"→ CLI)
- **必需资源**:图标(`.ico`)、数据文件、配置——**可选**;用户没提就跳过 `--icon` 参数,产物用默认图标
- **运行环境**:目标机器是 Windows(本 skill 范围默认就是;若用户要 Mac/Linux,直接说不在范围)

> 用户说"做个XX"时不要反复追问细节。按合理默认值实现,完成度比完美度重要。

**环境注意**:如果你在 Linux/macOS 沙箱里跑(没有 Windows),只有 **Go** 和 **Rust(mingw target)** 能原生跨编译出真 Windows .exe。PyInstaller/Electron/C# 需要 Wine 或真 Windows 环境。详见 `references/sandbox-limitations.md`。

## Procedure

1. **分析需求,选择技术栈**
   原因:不同技术栈打包难度、体积、启动速度差 10-100 倍,选错会让用户等 10 分钟拿到一个 200MB 的 exe
   - 决策表:
     - Python 逻辑 / 脚本 / 小工具 / 数据处理 → **Python + PyInstaller**(最稳,默认兜底)
     - CLI 工具,要求体积小(<20MB)启动快(<100ms) → **Go**
     - 性能敏感(图像处理 / 算法 / 系统工具) → **Rust**
     - 现代 GUI,跨设备长得一样,Web 风格 → **Electron**(体积大,慎用,默认不用)
     - 简单 GUI 桌面应用 → **Python + Tkinter**(内置,零额外依赖)
     - Windows 原生 GUI + 强 Windows 集成 → **C# / .NET**(self-contained publish)
   - 不确定时,无脑选 Python+PyInstaller
   - 详见 `references/tech-stack-decision.md`

2. **写代码到工作目录**
   - 入口文件要能独立跑(`if __name__ == "__main__"` / `func main()` / `void Main()`)
   - 路径用相对路径或 `__file__` / `os.path.dirname(os.path.abspath(__file__))`,不要硬编码绝对路径
   - 资源(数据/图标)放 `assets/` 子目录,运行时用 `sys._MEIPASS`(PyInstaller)或 `__file__` 定位

3. **准备打包环境**
   - 检查对应工具链是否就绪(详见各技术栈 reference)
   - Python: `pyinstaller --version` → 没有就 `pip install pyinstaller`
   - Go: `go version`
   - Rust: `cargo --version`
   - Electron: `node --version && npm list -g electron-builder`

4. **执行打包生成 .exe**
   - 常用命令骨架(具体参数和坑见 `references/<tech>.md`):
     - Python GUI:`pyinstaller --onefile --noconsole --icon=app.ico --name=AppName main.py`
     - Python CLI:`pyinstaller --onefile --icon=app.ico --name=AppName main.py`
     - Go:`go build -ldflags="-H windowsgui -s -w" -o AppName.exe .`(GUI 加 `-H windowsgui`,CLI 不要)
     - Rust:`cargo build --release` → 产物 `target/release/AppName.exe`
     - C#/.NET:`dotnet publish -c Release -r win-x64 --self-contained -p:PublishSingleFile=true`
     - Electron:`electron-builder --win --x64`

5. **验证 .exe**
   - 文件存在且 size > 100KB(避免空文件/失败产物)
   - 能启动:在 Windows 容器/Wine/本机跑一次,看是否秒退
   - 失败时:去掉 `--noconsole` 重新打包拿真实报错

6. **交付**
   - `.exe` 放工作目录 `dist/` 或项目根
   - 告诉用户:启动方式、首次启动为何慢(单文件 PyInstaller 需解压)、已知限制
   - 用 `<deliver-assets>` 块把 exe 文件交付用户
   - 如果用户没指定代码去向,把源码也一起给(打包成 zip)

## Output contract

- 一个可运行的 `.exe` 文件(主要交付物)
- 打包日志(成功/失败/警告信息摘要)
- 简短交付说明:怎么启动 + 已知限制(如"首次启动需 3-5 秒解压")

## Failure handling

- **打包命令找不到** → 引导装工具链:`pip install pyinstaller` / 装 Go / 装 Rust / `npm i -g electron-builder`
- **PyInstaller ModuleNotFoundError** → 提示加 `--hidden-import=<module>` 或 `--collect-all <pkg>`
- **.exe 启动闪退** → 去掉 `--noconsole` 重新打包,让控制台报错显示出来
- **体积过大(>100MB)** → 用 venv 装依赖、或换技术栈(Go/Rust 通常 <20MB)
- **跨技术栈依赖装不上** → 兜底到 Python+PyInstaller
- **杀毒报毒** → 不在 skill 范围,提示用户加白名单或换打包方式(说明:这是打包机制固有问题,不是 bug)
- **target 是 Mac/Linux** → 直接说不在范围,引导用户装对应平台工具或找 cross-compile 教程

## Examples

**Input**: "帮我做个批量重命名小工具,把当前文件夹下所有 .txt 改成 .md 后缀,GUI 的,带个图标"
**Output**:
- 写 `main.py`(Tkinter GUI:按钮触发 + pathlib 遍历)
- 准备 `app.ico`
- `pyinstaller --onefile --noconsole --icon=app.ico --name=RenameTool main.py`
- 交付 `dist/RenameTool.exe`,提示"双击运行,会处理 exe 所在目录的所有 .txt 文件"

**Input**: "build me a fast CLI that counts lines of code in a folder"
**Output**:
- 选 Go(CLI 工具 + 体积小 + 启动快)
- 写 `main.go`
- `go build -ldflags="-s -w" -o loc.exe .`
- 交付 `loc.exe`,提示"`loc.exe <folder_path>` 调用"
