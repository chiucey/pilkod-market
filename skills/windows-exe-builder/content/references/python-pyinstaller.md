# Python + PyInstaller 详细指南

最常用的打包方式,默认兜底方案。

## 基础命令

### 打包前环境检查(GUI 必做)

```bash
# 确认 PyInstaller 可用
pyinstaller --version

# GUI 程序确认 tkinter 可用
python -c "import tkinter; print('tk ok')" 2>&1
# 失败:Linux 上 `sudo apt install python3-tk`,Windows 上重装 Python 时勾选 tcl/tk
```

### CLI 程序(带控制台窗口)

```bash
pip install pyinstaller
pyinstaller --onefile --name=MyApp main.py
# 产物:dist/MyApp.exe
```

### GUI 程序(隐藏控制台)

```bash
pyinstaller --onefile --noconsole --name=MyApp --icon=app.ico main.py
```

### 单目录模式(启动更快,适合大项目)

```bash
pyinstaller --onedir --noconsole --name=MyApp main.py
# 产物:dist/MyApp/ 整个目录,exe 启动快但分多个文件
```

## 常用参数

| 参数 | 作用 |
|------|------|
| `--onefile` | 打包成单个 exe(默认) |
| `--onedir` | 打包成目录(启动快,适合大型 GUI) |
| `--noconsole` / `--windowed` | 隐藏控制台(GUI 必备) |
| `--console` | 显示控制台(默认,CLI 必备) |
| `--icon=app.ico` | 设置 exe 图标 |
| `--name=MyApp` | 指定输出名字 |
| `--add-data "src;dst"` | 添加额外文件(Windows 用 `;` 分隔) |
| `--hidden-import=module` | 强制包含某个模块 |
| `--collect-all pkg` | 收集整个包(包括数据/二进制) |
| `--clean` | 清理缓存后打包(解决莫名其妙的问题) |
| `--upx-dir=path` | 用 UPX 压缩(可选) |

## 资源文件处理

### 方案 A:代码中动态定位(推荐)

```python
import sys, os

def resource_path(rel):
    """PyInstaller 单文件模式:资源会解压到 _MEIPASS"""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

# 使用
icon = resource_path('assets/icon.png')
```

打包时也要加 `--add-data "assets;assets"` 把资源带进去。

### 方案 B:外部资源(用户运行时能看到)

不放进 exe,exe 旁边建 `data/` 目录,代码读相对路径。优点:用户能修改数据;缺点:不是真正单文件。

## 常见报错和修复

### `ModuleNotFoundError: No module named 'xxx'`

PyInstaller 没自动检测到某些动态导入的模块。

修复:
```bash
pyinstaller --hidden-import=xxx --hidden-import=yyy main.py
# 或者
pyinstaller --collect-all xxx main.py  # 整个包都收
```

### 打包后 exe 闪退 / 没反应

去掉 `--noconsole` 再打包,看真实报错:
```bash
pyinstaller --onefile main.py  # 不加 --noconsole
```

### 体积太大(>100MB)

原因:全局 site-packages 太大,把不必要的库也打包了。

修复:
```bash
# 1. 用虚拟环境只装需要的包
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install pyinstaller <实际依赖>

# 2. 然后再 pyinstaller
pyinstaller --onefile --noconsole main.py
```

### `RecursionError: maximum recursion depth exceeded`

某些库(numpy/pandas 偶尔)在打包时递归太深。

修复:用 spec 文件加 `import numpy; numpy.set_printoptions(...)` 或在 spec 文件中调 `__ recursion_limit__`。

## .spec 文件(高级)

`pyinstaller main.spec` 用 spec 文件打包,适合复杂配置。

最小 spec 文件示例:
```python
# main.spec
a = Analysis(['main.py'],
             hiddenimports=['requests', 'bs4'],
             datas=[('assets', 'assets')])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas,
          name='MyApp', icon='app.ico', console=False)
```

第一次 `pyinstaller main.py` 会自动生成 `main.spec`,之后改 spec 然后 `pyinstaller main.spec`。

## GUI 库选择速查

| 库 | 风格 | 依赖 | 学习曲线 |
|----|------|------|----------|
| **Tkinter** | 朴素 | 内置,零依赖 | 低 |
| **PySimpleGUI** | 友好 | 需 pip install | 低 |
| **PyQt5/6 / PySide** | 专业 | 需 pip install | 中 |
| **Dear PyGui** | 现代 | 需 pip install | 中 |
| **wxPython** | 原生 | 需 pip install | 中 |

**默认推荐**:能用 Tkinter 就 Tkinter,体验不行再换 PySimpleGUI 或 PyQt。

## 验证清单

打包后逐项检查:
- [ ] `dist/MyApp.exe` 存在且 size > 1MB
- [ ] 双击能启动(秒退就是失败,见上面的"闪退"修复)
- [ ] 功能正常(手动测一遍用户需求的所有路径)
- [ ] 图标正确(任务栏/标题栏看 .ico 是否生效)
- [ ] 资源文件能加载(图片/数据/字体)
