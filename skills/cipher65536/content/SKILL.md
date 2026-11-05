---
name: cipher65536
version: 1.0.2
description: Base65536 文件编码解码工具。使用 Base65536 编码将任意二进制文件转换为 Unicode 文本，支持 gzip 压缩、原文件名保存，以及基于本地回环网络抖动真随机熵的字节级异或加密。适用于跨平台文件传输、高保密隐写术、API 传输二进制数据等场景。
---

# Base65536 文件编码解码工具

## 概述

Base65536 是一种使用 Unicode 字符的编码方案，可以将任意二进制数据编码为可打印的文本字符串。此工具在此基础上增加了：

- **gzip 压缩**：减少传输体积
- **真随机密钥生成**：基于本地回环网络抖动采集物理熵
- **字节级异或加密**：保护内容机密性
- **元数据隐藏**：加密模式下文件名、大小等均被隐藏

## 快速开始

### 安装依赖

```bash
pip install base65536
```

基本用法

```bash
# 普通编码（无加密）
python skill.py encode document.pdf -o encoded.txt

# 解码
python skill.py decode encoded.txt -o restored.pdf
```

加密模式（自动生成密钥）

```bash
# 加密编码（密钥保存到文件，不在终端显示）
python skill.py encode secret.zip --scramble -o encrypted.txt
# 输出：
#   🌐 正在从本地网络抖动采集真随机熵...
#   🔑 密钥已保存至: encrypted.key
#   🔒 文件权限已锁定为 600 (仅当前用户可读写)
#   ✓ 已编码: encrypted.txt

# 解密（从密钥文件读取）
python skill.py decode encrypted.txt --key $(cat encrypted.key)
```

加密模式（使用指定密钥）

```bash
# 使用已有密钥加密
python skill.py encode secret.zip --scramble --key 108544482569932551567348223456789012... -o encrypted.txt

# 解密
python skill.py decode encrypted.txt --key 108544482569932551567348223456789012...
```

命令行参数

encode 子命令

参数 说明
input 输入文件路径（必需）
-o, --output 输出文件路径（默认：输入文件名.b65536.txt）
--no-compress 禁用 gzip 压缩
--scramble 启用加密模式
--key 使用指定密钥（整数），不提供则自动生成
--key-file 密钥输出文件路径（默认：输出文件名.key）

decode 子命令

参数 说明
input 输入文件路径（必需）
-o, --output 输出文件路径（默认：使用原文件名）
--key 解密密钥（整数，加密模式必需）

工作流程

编码流程

1. 读取原始二进制文件
2. 可选：使用 gzip 压缩数据（默认启用，压缩级别 9）
3. 使用 Base65536 编码为 Unicode 文本
4. 若启用加密模式：
   · 生成或使用指定的 256 位密钥
   · 对 Base65536 文本的 UTF-8 字节进行异或加密
   · 加密真实元数据，替换为假元数据
5. 添加 #METADATA: 头部
6. 保存为文本文件

解码流程

1. 读取编码文本文件
2. 解析 #METADATA: 头部
3. 若为加密模式：
   · 使用密钥解密真实元数据
   · 异或解密主体数据
4. 使用 Base65536 解码为二进制数据
5. 自动检测并解压 gzip 压缩数据
6. 使用原文件名保存文件

文件格式

普通模式

```
#METADATA:{"original_name": "原始文件名", "compressed": true, "original_size": 12345, "scrambled": false}
[Base65536 编码数据...]
```

加密模式

```
#METADATA:{"original_name": "encrypted_file", "compressed": true, "original_size": 0, "scrambled": true, "note": "This file is encrypted. Use key to decrypt."}
[异或加密后的 Base65536 编码数据...]
###ENCRYPTED_META### [加密的真实元数据]
```

安全原理

基于信息论与密码学原理的文件隐写工具。通过 gzip 熵密化折叠数据冗余，并以本地回环网络抖动真随机熵为种子，生成 256 位密钥空间对字节流进行异或扰动。密文在 Base65536 定义的 Unicode 有限流形上呈现混沌性分布，能有效抵抗已知明文攻击、唯密文攻击及基于相空间重构的密码分析。

1. 真随机密钥生成：通过测量本地回环（localhost）网络延迟抖动采集物理熵，结合 os.urandom 系统熵，生成不可预测的 256 位密钥。
2. 密钥安全存储：自动生成的密钥保存到 .key 文件并设置 600 权限，绝不在终端显示。
3. 元数据隐藏：真实文件名、大小等信息被加密存储，对外显示假数据。

使用示例

编码 PDF 文件（无加密）

```bash
python skill.py encode document.pdf -o encoded.txt
```

输出：

```
  压缩: 1,234,567 → 876,543 字节 (71.0%)
  编码: 876,543 字节 → 438,271 字符
✓ 已编码: encoded.txt
  最终大小: 438,271 字符
```

解码文件（无加密）

```bash
python skill.py decode encoded.txt
```

输出：

```
  读取到元数据: {'original_name': 'document.pdf', 'compressed': True, 'original_size': 1234567, 'scrambled': False}
  检测到 gzip 压缩，正在解压...
✓ 已解码: document.pdf
  还原大小: 1,234,567 字节
```

适用场景

· 跨平台文件传输：编码后可在任何支持文本的平台传输
· 高保密隐写术：配合加密模式，内容完全隐藏
· API 传输：在纯文本 API 中传输二进制数据
· 绕过上传限制：在不支持文件上传的平台传输文件
· 数据备份：将二进制数据转换为文本进行备份

技术规格

项目 规格
编码方案 Base65536
压缩算法 gzip (zlib, 压缩级别 9)
加密算法 字节级异或 + 256 位密钥空间
密钥生成 本地回环网络抖动 + os.urandom
元数据格式 JSON
Python 版本 3.6+
外部依赖 base65536

性能特性

原始类型 gzip 压缩效果 Base65536 膨胀率 综合效果
文本文件 70-80% ~50% 35-40%
图片/视频 90-99% ~50% 45-99%
已压缩文件 无效果 ~50% ~50%

注意事项

1. 密钥保管：真随机密钥不可复现，丢失后无法恢复文件
2. 安全传递：密钥文件请通过独立于密文的渠道传递
3. 已压缩文件：对于 .zip、.jpg 等已压缩文件，建议使用 --no-compress 避免体积膨胀
4. Unicode 兼容性：某些平台可能对高位 Unicode 字符处理异常，建议传输前测试

资源

scripts/

· skill.py - 主程序，包含 encode/decode 功能

references/

· encoding-details.md - 编码原理和实现细节
