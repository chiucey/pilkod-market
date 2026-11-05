# 沙箱环境限制(Linux/macOS 跑本 skill 的注意事项)

主流程默认假设运行环境有 Windows 或能装 Wine。如果你跑在 Linux/macOS 沙箱里,部分技术栈无法直接产 Windows .exe。

## 各技术栈在 Linux 沙箱的可行性矩阵

| 技术栈 | Linux 沙箱能否产 Windows .exe? | 备注 |
|--------|--------------------------------|------|
| **Go** | ✅ **能,首选** | 原生支持 `GOOS=windows GOARCH=amd64`,无需任何额外工具。1-3 秒产出。 |
| **Rust** | ✅ **能** | 需装 `mingw-w64` 交叉编译工具链;`rustup target add x86_64-pc-windows-gnu`;首次编译 1-5 分钟。 |
| **PyInstaller** | ❌ 不能 | 跨平台打包需要 Wine + Windows Python 解释器,沙箱通常装不上。 |
| **Electron** | ❌ 不能 | electron-builder 在 Linux 上能产 .exe,但内部仍需 Wine,沙箱跑不了。 |
| **C# / .NET** | ⚠️ 部分能 | .NET 8+ 跨发布较成熟:`dotnet publish -c Release -r win-x64 --self-contained`,但需要装 dotnet SDK。 |

## 沙箱环境的实操建议

**如果你跑在 Linux 沙箱(没 Windows、没 Wine):**

1. **默认选 Go**——它是在沙箱里**唯一可靠能产真 Windows .exe** 的主流技术栈
2. CLI 工具直接用 Go
3. 简单 GUI 工具可以考虑 Go + Fyne(纯 Go 库,无 CGO)
4. 复杂 GUI 在沙箱里基本别想,告诉用户"在 Windows 上跑这个 skill 才能做复杂 GUI"

**如果你跑在 macOS 沙箱(可能有 Wine):**

- Go 仍然首选
- PyInstaller 装 macOS Python 解释器,产 macOS .app,跟 Windows 不通用
- 提醒用户:macOS 沙箱产 Windows .exe 仍需 Wine

## 真测试结论(2026-07-19,在 Linux sandbox)

实际跑过两个技术栈:

**Go 路径**:
- ✅ 真产出了 1.7MB 的 `loc.exe`(LOC 计数器)
- ✅ PE 头完全合法(MZ/PE/AMD64/Subsystem=3 Console)
- ✅ 只依赖 kernel32.dll,跨 Windows 版本都能跑
- 命令: `GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o loc.exe .`

**PyInstaller 路径**:
- ❌ 产物是 Linux ELF,不是 Windows .exe
- ❌ Linux 沙箱无 Wine,无法补齐跨平台打包所需的 Windows Python 解释器
- 在 Windows 上跑应该完全 work

## 兜底话术

当用户明确要复杂 GUI,但你在沙箱里,直接说:

> "你描述的 GUI(比如有动画/拖拽/富文本)用 PyInstaller/Electron 在 Windows 上做最合适。但当前环境是 Linux 沙箱,装不了 Wine,没法直接产 Windows .exe。
>
> 两条路:
> 1. 你在 Windows 上跑这个 skill,我可以出 PyInstaller/Electron 的完整方案
> 2. 我现在在沙箱里用 Go + Fyne 给你做个简化版(纯 Go 库,能产真 .exe,但 UI 简陋)
>
> 你选哪个?"
