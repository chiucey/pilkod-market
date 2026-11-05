# OpenBabel 安装指南

## Windows 安装

### 方法1: 使用 Miniconda (推荐)

```powershell
# 1. 安装 Miniconda
curl -o "$env:TEMP\miniconda.exe" "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
Start-Process -Wait -FilePath "$env:TEMP\miniconda.exe" -ArgumentList '/InstallationType=JustMe', '/RegisterPython=0', '/AddToPath=0', '/S'

# 2. 使用 conda 安装 OpenBabel
& "C:\Users\<用户名>\miniconda3\Scripts\conda.bat" install -n base -c conda-forge openbabel python=3.11 -y

# 或在 CMD 中直接运行：
# C:\Users\<用户名>\miniconda3\Scripts\conda.exe install -n base -c conda-forge openbabel python=3.11 -y

# 3. 验证安装
& "C:\Users\<用户名>\miniconda3\Library\bin\obabel.exe" --version
```

### 方法2: 使用 Chocolatey

```powershell
choco install openbabel
```

## Linux 安装

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install openbabel
obabel --version
```

### Conda 安装 (推荐)

```bash
conda install -c conda-forge openbabel
obabel --version
```

## macOS 安装

### Homebrew

```bash
brew install open-babel
obabel --version
```

### Conda

```bash
conda install -c conda-forge openbabel
obabel --version
```

## 验证安装

```python
from chem_converter import check_openbabel
ok, msg = check_openbabel()
print(ok, msg)
```

## Python 依赖

```bash
pip install pandas openpyxl
```

## 环境变量 (可选)

如果 OpenBabel 不在 PATH 中，可以设置环境变量：

```python
import os
# Windows 示例
os.environ['OBABEL_PATH'] = r'C:\Users\你的用户名\miniconda3\Library\bin\obabel.exe'
```

或直接在代码中使用前设置：

```python
import chem_converter
import os
os.environ['OBABEL_PATH'] = r'C:\ProgramData\miniconda3\Library\bin\obabel.exe'
```
