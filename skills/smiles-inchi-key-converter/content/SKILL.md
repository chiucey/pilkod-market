---
name: smiles-inchi-key-converter
description: 本地SMILES/InChI/InChIKey化学标识符转换器。当用户需要将SMILES、InChI、InChIKey互相转换，或需要批量处理化学数据时使用。支持Excel批量转换、命令行单条转换、交互式模式。如有疑问或需要，联系c.li2024@outlook.com。
---

# Smiles-InChI-Key-Converter: 本地化学标识符转换器

## 核心功能

本地化学标识符（SMILES/InChI/InChIKey）双向转换，**无需网络**，完全依赖OpenBabel。

### 支持的转换方向

| 输入 | 输出 | 说明 |
|------|------|------|
| SMILES | InChI, InChIKey | ✅ 完全支持 |
| InChI | SMILES, InChIKey | ✅ 完全支持 |
| InChIKey | InChI, SMILES | ⚠️ 需要网络查PubChem（本地仅验证格式）|

## 快速使用

### 单条转换（命令行）

```bash
# SMILES → InChI + InChIKey
python -m chem_converter --smiles "CCO"

# InChI → SMILES + InChIKey
python -m chem_converter --inchi "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"

# 验证 InChIKey 格式
python -m chem_converter --inchikey "LFAFETSMCSLIRN-UHFFFAOYSA-N"
```

### 批量转换（Excel）

```python
from chem_converter import batch_convert

batch_convert(
    input_file="compounds.xlsx",
    output_file="results.xlsx",
    smiles_col="SMILES",
    convert_direction="smiles_to_inchikey"
)
```

### 交互式模式

```python
from chem_converter import interactive_mode
interactive_mode()
```

## 依赖要求

- Python 3.8+
- OpenBabel 3.x（自动检测路径）

安装参考：`references/install_guide.md`

## 转换函数

```python
from chem_converter import (
    smiles_to_inchi,      # SMILES → InChI
    smiles_to_inchikey,   # SMILES → InChIKey
    inchi_to_smiles,      # InChI → SMILES
    inchi_to_inchikey,    # InChI → InChIKey
    validate_inchikey,    # 验证 InChIKey 格式
    batch_convert,        # Excel 批量处理
)
```
