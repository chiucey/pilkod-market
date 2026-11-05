---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7194c30e81de7b877793836a42d42aa8
    PropagateID: 7194c30e81de7b877793836a42d42aa8
    ReservedCode1: 3046022100c6cc8c0233ea399299e222eae0b81b5ec38ce2e33c0010713a1e088ca5216f41022100f1e46597ad5175062823dd92990369117dfea2974df361a9506a869b827d6302
    ReservedCode2: 3045022041797a69bca1298dbc953b2567ddcd50f5cd1194d2d13a67a61f79b7d7391f8e022100bee094194df5b5315c01d12b487950e89f04c709d8281175b44bd3ee49788ded
---

# STDF 文件格式参考

## 记录结构

每个 STDF 记录由 4 字节头部和数据组成：
- **REC_LEN** (2 bytes): 数据长度
- **REC_TYP** (1 byte): 记录类型
- **REC_SUB** (1 byte): 记录子类型

## 关键记录类型

| REC_TYP | REC_SUB | 记录名称 | 功能 |
|---------|---------|----------|------|
| 0 | 10 | FAR | 文件属性（确定字节序） |
| 1 | 10 | MIR | 主信息记录 |
| 1 | 30 | PCR | Part Count Record |
| 5 | 10 | PIR | Part Information Record (芯片开始) |
| 5 | 20 | PRR | Part Results Record (芯片结束) |
| 15 | 10 | PTR | Parametric Test Record (测试结果) |
| 15 | 20 | FTR | Functional Test Record |

## PIR 记录结构 (Type 5, Subtype 10)

```
HEAD_NUM (U*1): 测试头编号
SITE_NUM (U*1): 测试站点编号
```

## PRR 记录结构 (Type 5, Subtype 20)

```
HEAD_NUM (U*1): 测试头编号
SITE_NUM (U*1): 测试站点编号
PART_FLG (B*1): 芯片信息标志
NUM_TEST (U*2): 执行测试数量
HARD_BIN (U*2): 硬件分 Bin
SOFT_BIN (U*2): 软件分 Bin
```

## PTR 记录结构 (Type 15, Subtype 10)

```
TEST_NUM (U*4): 测试编号
HEAD_NUM (U*1): 测试头编号
SITE_NUM (U*1): 测试站点编号
TEST_FLG (B*1): 测试标志
PARM_FLG (B*1): 参数测试标志
RESULT (R*4): 测试结果值
TEST_TXT (C*n): 测试名称
LO_LIMIT (R*4): 下限
HI_LIMIT (R*4): 上限
UNITS (C*n): 单位
```

## 字节序判断

- FAR 记录的 REC_LEN:
  - 值为 2 → 小端序 (little-endian, '<')
  - 值为 512 → 大端序 (big-endian, '>')

## 数据类型

| 代码 | 类型 | 描述 |
|------|------|------|
| U*1 | unsigned char | 1字节无符号整数 |
| U*2 | unsigned short | 2字节无符号整数 |
| U*4 | unsigned long | 4字节无符号整数 |
| I*1 | char | 1字节有符号整数 |
| R*4 | float | 4字节浮点数 |
| R*8 | double | 8字节浮点数 |
| C*n | char[] | 可变长度字符串 (首字节=长度) |
| B*1 | char | 1字节位字段 |

## ChipID 字段

ChipID 通常作为测试项名称包含在 PTR 记录中：
- `read_chipid_0`
- `read_chipid_1`
- `read_chipid_2`
- `read_chipid_3`

这些值是 0-255 的整数，用于唯一标识芯片。
