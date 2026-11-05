# Python字节码分析与逆向工程

## 目录
1. [Python编译过程](#1-python编译过程)
2. [字节码结构](#2-字节码结构)
3. [dis模块详解](#3-dis模块详解)
4. [反编译技术](#4-反编译技术)
5. [控制流分析](#5-控制流分析)
6. [实战案例](#6-实战案例)

---

## 1. Python编译过程

```
源代码 (.py)
     ↓
   解析器 (Parser)
     ↓
 AST (抽象语法树)
     ↓
 编译器 (Compiler)
     ↓
 PyCodeObject (代码对象)
     ↓
 解释器 (Interpreter)
     ↓
 字节码 (.pyc)
```

### Python版本与字节码
| 版本 | Magic Number | 头部大小 |
|-----|-------------|---------|
| 3.11+ | 33 0D 0D 0A | 16 |
| 3.10 | 42 0D 0D 0A | 16 |
| 3.9 | 55 0D 0D 0A | 16 |
| 3.8 | 61 0D 0D 0A | 16 |
| 3.7 | 42 13 0D 0A | 16 |
| 3.6 | 6F 0D 0D 0A | 16 |
| 3.5 | 33 0D 0D 0A | 16 |
| 3.4 | EE 0C 0D 0A | 16 |

---

## 2. 字节码结构

### 2.1 .pyc文件结构
```
+------------------+
| Magic Number (4) | Python版本标识
+------------------+
| Bit Field (4)    | 编译标志
+------------------+
| Timestamp (4)    | 编译时间
+------------------+
| Size (4)        | 源文件大小 (3.7+)
+------------------+
| Marshal Data     | 序列化的PyCodeObject
+------------------+
```

### 2.2 PyCodeObject结构
```python
class PyCodeObject:
    co_argcount: int        # 位置参数个数
    co_posonlyargcount: int # 仅位置参数个数
    co_kwonlyargcount: int  # 关键字参数个数
    co_nlocals: int         # 局部变量个数
    co_stacksize: int       # 栈大小
    co_flags: int           # 编译标志
    co_code: bytes          # 字节码指令
    co_consts: tuple        # 常量元组
    co_names: tuple         # 名称元组
    co_varnames: tuple      # 局部变量名元组
    co_filename: str        # 源代码文件名
    co_name: str            # 函数/类名
    co_firstlineno: int     # 源代码首行号
    co_lnotab: bytes        # 行号表
    co_freevars: tuple      # 自由变量名
    co_cellvars: tuple      # cell变量名
```

---

## 3. dis模块详解

### 3.1 常用函数
```python
import dis

# 反汇编整个函数
dis.dis(func)

# 反汇编代码对象
dis.dis(code_object)

# 反汇编字节码对象
dis.dis(bytes_code)

# 反汇编文件
with open('example.pyc', 'rb') as f:
    # 跳过pyc头部
    f.read(16)
    marshal_data = f.read()
    code = marshal.loads(marshal_data)
    dis.dis(code)

# 获取指令列表
instructions = list(dis.get_instructions(func))
```

### 3.2 指令对象
```python
for instr in dis.get_instructions(func):
    print(f"Offset: {instr.offset}")
    print(f"Opcode: {instr.opcode}")
    print(f"Name: {instr.opname}")
    print(f"Arg: {instr.arg}")
    print(f"ArgVal: {instr.argval}")
    print(f"ArgRepr: {instr.argrepr}")
    print("---")
```

### 3.3 Bytecode类
```python
from dis import Bytecode

bc = Bytecode(func)
for instr in bc:
    print(instr.opname, instr.argval)
```

---

## 4. 反编译技术

### 4.1 反编译工具

#### uncompyle6
```bash
pip install uncompyle6
uncompyle6 script.pyc > script_decoded.py
```

#### decompyle3
```bash
pip install decompyle3
decompyle3 script.pyc
```

#### pycdc (C++实现的更快反编译器)
```bash
# 从源码编译
git clone https://github.com/zrax/pycdc
cd pycdc && cmake . && make
./pycdc script.pyc
```

### 4.2 marshal模块
```python
import marshal

# 读取pyc
with open('script.pyc', 'rb') as f:
    f.read(16)  # 跳过头部
    code = marshal.load(f)

# code现在是一个PyCodeObject
print(code.co_name)
print(code.co_code)

# 保存为新的pyc
with open('output.pyc', 'wb') as f:
    f.write(pycache_header)  # 16字节头部
    marshal.dump(code, f)
```

### 4.3 反编译流程
```
1. 提取.pyc文件
      ↓
2. 读取marshal数据
      ↓
3. 解析PyCodeObject
      ↓
4. 生成AST
      ↓
5. 生成Python源码
```

---

## 5. 控制流分析

### 5.1 构建控制流图(CFG)
```python
import dis
from collections import defaultdict

def build_cfg(code):
    cfg = defaultdict(set)
    instructions = list(dis.get_instructions(code))
    
    # 识别跳转目标
    jump_targets = set()
    for instr in instructions:
        if 'JUMP' in instr.opname:
            jump_targets.add(instr.argval)
    
    # 构建边
    for i, instr in enumerate(instructions):
        if i + 1 < len(instructions):
            next_instr = instructions[i + 1]
            # Fall-through edge
            if instr.opname not in ('JUMP_FORWARD', 'RETURN_VALUE', 'RAISE_VARARGS'):
                cfg[instr.offset].add(next_instr.offset)
        
        # Jump edges
        if 'JUMP' in instr.opname:
            cfg[instr.offset].add(instr.argval)
    
    return cfg

# 可视化 (生成DOT格式)
def cfg_to_dot(cfg, name='CFG'):
    lines = [f'digraph {name} {{']
    for src, targets in cfg.items():
        for tgt in targets:
            lines.append(f'    {src} -> {tgt};')
    lines.append('}')
    return '\n'.join(lines)
```

### 5.2 基本块识别
```python
def identify_basic_blocks(instructions):
    blocks = []
    jump_targets = set()
    
    # 收集所有跳转目标
    for instr in instructions:
        if 'JUMP' in instr.opname:
            jump_targets.add(instr.argval)
    
    # 识别块
    current_block = []
    for instr in instructions:
        current_block.append(instr)
        
        if instr.offset in jump_targets:
            blocks.append(current_block)
            current_block = []
        
        if instr.opname in ('RETURN_VALUE', 'RAISE_VARARGS'):
            blocks.append(current_block)
            current_block = []
    
    if current_block:
        blocks.append(current_block)
    
    return blocks
```

---

## 6. 实战案例

### 案例1: 解码exec加密壳
```python
# 混淆代码
obfuscated = """
exec(__import__('base64').b64decode(
    __import__('zlib').decompress(
        b'eJwLSS0u0dEBAH/xCQY='
    ).decode()
).decode())
"""

# 静态解码
import base64, zlib
encoded = b'eJwLSS0u0dEBAH/xCQY='
decoded = zlib.decompress(base64.b64decode(encoded))
print(decoded.decode())  # print("Hello")
```

### 案例2: 提取PyInstaller exe中的代码
```python
# 使用pyinstxtractor
import pyinstxtractor
pyinstxtractor.extract('target.exe', 'output_dir')

# 修复pyc头部
import struct
with open('extracted.pyc', 'rb') as f:
    magic = f.read(4)
    if magic == b'\x55\x0d\x0d\x0a':  # Python 3.9
        # 添加缺失的4字节
        data = f.read()
        with open('fixed.pyc', 'wb') as out:
            out.write(magic)
            out.write(b'\x00\x00\x00\x00')  # flags
            out.write(b'\x00\x00\x00\x00')  # timestamp
            out.write(struct.pack('<I', len(data)))  # size
            out.write(data)
```

### 案例3: 分析控制流扁平化
```python
# 检测扁平化模式
def detect_flattening(instructions):
    states = []
    for instr in instructions:
        if instr.opname == 'LOAD_CONST':
            states.append(('load_const', instr.argval))
        elif instr.opname == 'STORE_FAST' and states and states[-1][0] == 'load_const':
            var = instr.argval
            states[-1] = ('state_var', var)
        elif instr.opname == 'LOAD_FAST' and states and states[-1][0] == 'state_var':
            # 检测状态机模式
            return True
    return False
```

---

## 参考工具

| 工具 | 用途 | 链接 |
|-----|-----|-----|
| dis | 标准库字节码分析 | 内置 |
| xdis | 跨版本字节码支持 | github.com/rocky/python-xdis |
| uncompyle6 | Python反编译 | github.com/rocky/python-uncompyle6 |
| decompyle3 | Python 3反编译 | github.com/rocky/decompyle3 |
| pycdc | C++反编译器 | github.com/zrax/pycdc |
| pyinstxtractor | PyInstaller提取 | github.com/countercept/python-exe-unpacker |
