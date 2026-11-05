# Python混淆技术详解

## 目录
1. [混淆类型概述](#1-混淆类型概述)
2. [字符串混淆](#2-字符串混淆)
3. [变量名混淆](#3-变量名混淆)
4. [控制流混淆](#4-控制流混淆)
5. [exec/eval加密壳](#5-execeval加密壳)
6. [PyArmor保护](#6-pyarmor保护)
7. [PyInstaller打包](#7-pyinstaller打包)
8. [商业混淆器](#8-商业混淆器)

---

## 1. 混淆类型概述

Python代码混淆主要分为以下几类：

| 类型 | 目的 | 难度 |
|-----|-----|-----|
| 字符串加密 | 隐藏敏感字符串 | 低-中 |
| 标识符混淆 | 破坏代码可读性 | 低 |
| 控制流扁平化 | 阻止理解执行逻辑 | 中-高 |
| 加密壳 | 完全隐藏代码 | 高 |
| 虚拟化 | 最高强度保护 | 极高 |

---

## 2. 字符串混淆

### 2.1 Base64编码
```python
# 原始代码
api_key = "sk-xxxxx"

# 混淆后
import base64
api_key = base64.b64decode("c2steHh4eHg=").decode()
```

### 2.2 多重编码
```python
# 原始代码
print("secret")

# 混淆后
exec(__import__('base64').b64decode(
    __import__('zlib').decompress(
        b'eJwLSS0u0dEBAH/xCQY='
    ).decode()
))
```

### 2.3 反混淆方法
1. 动态执行捕获
2. 静态分析解码链
3. AST重写自动化解密

---

## 3. 变量名混淆

### 3.1 单字符替换
```python
# 原始
def calculate_sum(numbers):
    total = 0
    for n in numbers:
        total += n
    return total

# 混淆后
def oO0(l):
    O = 0
    for l in l:
        O += l
    return O
```

### 3.2 特殊字符混淆
```python
# 使用不可见字符或特殊Unicode
exec("pr\x69nt('hello')")  # \x69 = 'i'
```

### 3.3 反混淆方法
- 上下文语义分析
- 字节码级别追踪
- 类型推断

---

## 4. 控制流混淆

### 4.1 跳转混淆
```python
# 原始
if condition:
    do_a()
else:
    do_b()

# 混淆后 (使用goto-like模式)
while True:
    if condition:
        do_a()
        break
    do_b()
    break
```

### 4.2 控制流扁平化
```python
# 原始
def func():
    step1()
    step2()
    step3()

# 扁平化后 (使用dispatcher模式)
def func():
    state = 0
    while True:
        if state == 0:
            step1()
            state = 1
        elif state == 1:
            step2()
            state = 2
        elif state == 2:
            step3()
            return
```

### 4.3 反混淆方法
1. 构建控制流图(CFG)
2. 识别dispatcher模式
3. 恢复原始跳转关系
4. 基本块重排序

---

## 5. exec/eval加密壳

### 5.1 常见模式
```python
# 模式1: 直接exec加密代码
exec(__import__('base64').b64decode('aW1wb3J0IG9z...'))

# 模式2: 多层嵌套
__builtins__.__dict__['eval'](
    __import__('marshal').loads(
        __import__('zlib').decompress(
            encrypted_data
        )
    )
)

# 模式3: 字符串拼接动态构建
code = "pr" + "int" + "(" + "'hello'" + ")"
exec(code)
```

### 5.2 特征识别
- `exec()` 或 `eval()` 函数调用
- `__import__()` 动态导入
- Base64/Marshal/Zlib 数据
- 大量字符串拼接

### 5.3 反混淆方法
1. **动态执行**: 在受控环境执行并hook输出
2. **静态分析**: 追踪数据流,逐层解码
3. **AST重写**: 自动化识别和解码

---

## 6. PyArmor保护

### 6.1 保护机制
- Python字节码加密
- 运行时解密
- License验证

### 6.2 识别特征
- `.pye` 文件扩展名
- 特殊的pytransform模块
- 加密的code对象

### 6.3 反混淆方法
- 动态内存dump
- Key提取攻击
- 虚拟机模拟执行

---

## 7. PyInstaller打包

### 7.1 打包类型
- **单文件模式**: `pyinstaller -Fw script.py`
- **目录模式**: `pyinstaller -D script.py`

### 7.2 结构分析
```
exe内部结构:
├── Python解释器
├── 依赖库
├── PYZ资源 (加密的Python模块)
│   └── 各个.pyc文件
└── 主脚本.pyz
```

### 7.3 反编译流程
```
1. pyinstxtractor.py 提取exe
      ↓
2. 修复.pyc文件头部
      ↓
3. uncompyle6反编译为.py
```

### 7.4 加密PYZ处理
```
# 识别加密PYZ
- 检查文件头部magic
- 尝试标准marshal解析
- 识别加密标志

# 提取方法
- 动态hook Python解释器
- 内存搜索和解密
- Key提取
```

---

## 8. 商业混淆器

### 8.1 Hyperion
**特点**:
- 多层加密壳
- 字符串编码
- 代码虚拟化

**混淆示例**:
```python
from builtins import *
from math import prod as Power
__obfuscator__ = 'Hyperion'
__authors__ = ('billythegoat356',)

# 多层编码的代码块
```

### 8.2 PyArmor
**特点**:
- 字节码加密
- License绑定
- 代码完整性检查

### 8.3 Cumberland
**特点**:
- 控制流保护
- 字符串加密
- 虚拟机保护

---

## 附录: Python字节码基础

### 常用操作码
| Opcode | 功能 |
|--------|-----|
| LOAD_CONST | 加载常量 |
| LOAD_FAST | 加载局部变量 |
| STORE_FAST | 存储局部变量 |
| LOAD_GLOBAL | 加载全局变量 |
| CALL_FUNCTION | 调用函数 |
| BINARY_ADD | 加法运算 |
| JUMP_ABSOLUTE | 无条件跳转 |
| POP_JUMP_IF_FALSE | 条件跳转 |
| RETURN_VALUE | 返回值 |
| EXEC | 执行代码 |

### dis模块使用
```python
import dis

def example():
    x = 1 + 2
    print(x)

dis.dis(example)
```

输出:
```
  2           0 LOAD_CONST               1 (3)
              2 STORE_FAST               0 (x)

  3           4 LOAD_GLOBAL              0 (print)
              6 LOAD_FAST                0 (x)
              8 CALL_FUNCTION            1
             10 POP_TOP
             12 LOAD_CONST              0 (None)
             14 RETURN_VALUE
```

---

## 参考资源

- [Python dis模块文档](https://docs.python.org/3/library/dis.html)
- [xdis - 跨版本字节码库](https://github.com/rocky/python-xdis)
- [uncompyle6 - Python反编译器](https://github.com/rocky/python-uncompyle6)
- [pyinstxtractor](https://github.com/countercept/python-exe-unpacker)
