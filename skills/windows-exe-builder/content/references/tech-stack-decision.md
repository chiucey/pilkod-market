# 技术栈决策表(详细版)

主流程只给了快速决策,这里展开完整版。

## 决策流程图

```
用户需求
  │
  ├─ 是 Web 应用/网站/SaaS? → 不在本 skill 范围(转 web 开发 skill)
  │
  ├─ 是 GUI 桌面应用?
  │    │
  │    ├─ 简单交互(几个按钮/输入框) → Python + Tkinter(内置,零依赖)
  │    ├─ 复杂交互(表格/树形/富文本) → Python + PyQt/PySide 或 C# WPF
  │    ├─ Web 风格界面 → Electron(但要警告:80MB+ 体积)
  │    └─ Windows 原生 + 系统集成 → C#/.NET WPF
  │
  └─ 是 CLI 命令行工具?
       │
       ├─ 性能/体积敏感(<20MB,启动<100ms) → Go 或 Rust
       ├─ 标准业务逻辑/数据处理 → Python(开发最快)
       └─ 涉及已有 Python 生态(pandas/requests 等) → Python
```

## 各技术栈的取舍矩阵

| 技术栈 | 体积 | 启动速度 | 开发速度 | GUI 支持 | 跨平台 |
|--------|------|----------|----------|----------|--------|
| Python + PyInstaller | 10-50MB | 慢(单文件解压 1-5s) | ⭐⭐⭐⭐⭐ | Tkinter/PyQt/Electron-like 都有 | 一般(本 skill 仅 Windows) |
| Go | 5-15MB | 极快(<100ms) | ⭐⭐⭐⭐ | Fyne/Wails(可用但不主流) | 好 |
| Rust | 3-10MB | 极快 | ⭐⭐⭐ | egui/Tauri(可用但学习曲线陡) | 好 |
| Electron | 80-200MB | 慢(2-5s) | ⭐⭐⭐⭐ | 原生 web,体验最好 | 好 |
| C#/.NET WPF | 20-50MB | 快 | ⭐⭐⭐⭐ | Windows 原生,体验好 | 仅 Windows |

## 默认选择逻辑

- **没有任何信息时** → Python + Tkinter + PyInstaller
  - 理由:Python 几乎所有环境都有,Tkinter 内置,PyInstaller 一行命令打包
- **用户明确说"要小"/"要快"** → Go
- **用户说"做网站那种界面"** → Electron(同时提醒体积)
- **用户说"Windows 原生"** → C#/.NET

## 不要选错的情况

- ❌ 用 Electron 写一个简单的 5MB CLI 工具 → 浪费(应该用 Go/Python)
- ❌ 用 Go 写一个带 GUI 的桌面应用 → 折腾(应该用 Python/C#)
- ❌ 用 C++/CMake 写一个简单的批量处理工具 → 过度工程(应该用 Python)

## 用户的隐式需求识别

| 用户说 | 推断 | 推荐技术栈 |
|--------|------|------------|
| "做个XX工具" | CLI 工具 | Python 或 Go |
| "做个XX软件/应用" | GUI 应用 | Python + Tkinter 或 C# |
| "网页/网站" | 不在范围 | 转告用户 |
| "快速/体积小" | 性能敏感 | Go 或 Rust |
| "跨平台" | 部分超出范围 | 转告用户本 skill 仅 Windows |
| "Windows 原生" | 系统集成 | C#/.NET |
