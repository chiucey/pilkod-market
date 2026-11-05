# PaddleOCR 3.x 升级说明

## 概览

PaddleOCR 3.x 进行了重大更新，整合了多个独立包的功能，简化了依赖管理和使用方式。

## 主要变化

### 1. 依赖整合

**PaddleOCR 2.x（旧版）**：
```bash
pip install paddleocr
pip install paddlestructure  # 需要单独安装
pip install paddleclas      # 需要单独安装
```

**PaddleOCR 3.x（新版）**：
```bash
pip install paddleocr>=3.0.0  # 包含所有功能
```

### 2. 功能整合

| 功能 | PaddleOCR 2.x | PaddleOCR 3.x |
|------|--------------|--------------|
| 基础 OCR | `paddleocr` | `paddleocr` |
| 版面分析 | `paddlestructure` | `paddleocr` (PP-StructureV3) |
| 表格识别 | `paddlestructure` | `paddleocr` (PP-StructureV3) |
| 文档问答 | `ppchatocr` | `paddleocr` (PP-ChatOCRv4) |
| 视觉语言 | `paddleocr-vl` | `paddleocr` (PaddleOCR-VL) |
| 印章识别 | `paddleclas` | `paddleocr` (PaddleOCR-VL-1.5) |

### 3. 导入方式变化

**PaddleOCR 2.x**：
```python
from paddleocr import PaddleOCR
from paddlestructure import PaddleStructure  # 需要单独导入
```

**PaddleOCR 3.x**：
```python
from paddleocr import PaddleOCR
# PP-StructureV3 已整合到 PaddleOCR 中，通过配置启用
```

### 4. 配置方式变化

**PaddleOCR 2.x**：
```python
# 使用 PaddleStructure
table_engine = PaddleStructure(
    show_log=False,
    table=True,
    ocr=True,
    layout=True,
    structure_version='PP-StructureV3'
)
```

**PaddleOCR 3.x**：
```python
# 使用 PaddleOCR 的 PP-StructureV3 模块
ocr_engine = PaddleOCR(
    show_log=False,
    det=True,
    rec=True,
    table=True,      # 启用表格识别
    layout=True,     # 启用版面分析
    ocr=True,
    structure_version='PP-StructureV3'
)
```

## 依赖要求

### 核心依赖
```txt
paddleocr>=3.0.0  # 包含所有功能
paddlepaddle>=2.6.0  # 深度学习框架
```

### 可选依赖（根据需要安装）
```txt
transformers>=4.30.0  # VL 能力支持
torch>=2.0.0  # VL 能力支持
```

## 迁移指南

### 从 PaddleOCR 2.x 迁移到 3.x

**步骤 1：更新依赖**
```bash
# 卸载旧版本
pip uninstall paddleocr paddlestructure paddleclas

# 安装新版本
pip install paddleocr>=3.0.0 paddlepaddle>=2.6.0
```

**步骤 2：更新导入语句**
```python
# 旧代码
from paddlestructure import PaddleStructure

# 新代码
from paddleocr import PaddleOCR
# 通过配置启用 PP-StructureV3 功能
```

**步骤 3：更新初始化代码**
```python
# 旧代码
table_engine = PaddleStructure(
    show_log=False,
    table=True,
    layout=True
)

# 新代码
ocr_engine = PaddleOCR(
    show_log=False,
    det=True,
    rec=True,
    table=True,
    layout=True
)
```

**步骤 4：更新调用方式**
```python
# 旧代码
result = table_engine(image_path)

# 新代码
result = ocr_engine(image_path, table=True, layout=True)
```

## 功能对比

### OCR 识别

**2.x 和 3.x**：基本一致
```python
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr(image_path)
```

### 表格识别

**PaddleOCR 2.x**：
```python
from paddlestructure import PaddleStructure
table_engine = PaddleStructure(table=True)
result = table_engine(image_path)
```

**PaddleOCR 3.x**：
```python
from paddleocr import PaddleOCR
table_engine = PaddleOCR(table=True)
result = table_engine(image_path)
```

### 版面分析

**PaddleOCR 2.x**：
```python
from paddlestructure import PaddleStructure
layout_engine = PaddleStructure(layout=True)
result = layout_engine(image_path)
```

**PaddleOCR 3.x**：
```python
from paddleocr import PaddleOCR
layout_engine = PaddleOCR(layout=True)
result = layout_engine(image_path)
```

## 注意事项

### 1. API 变化
PaddleOCR 3.x 引入了多项重要的接口变动，基于 2.x 编写的旧代码很可能无法在 3.x 上运行。

### 2. 模型下载
PaddleOCR 3.x 使用新的模型下载机制，首次使用时会自动下载所需模型。

### 3. GPU 支持
GPU 支持需要安装对应版本的 PaddlePaddle-GPU：
```bash
pip install paddlepaddle-gpu>=2.6.0
```

### 4. Python 版本
PaddleOCR 3.x 支持 Python 3.8 - 3.12。

## 常见问题

### Q: 迁移后代码报错怎么办？

A: 检查以下几点：
1. 确认已安装 PaddleOCR 3.x 版本：`pip show paddleocr`
2. 检查导入语句是否正确
3. 查看错误信息，参考官方文档

### Q: PP-StructureV3 功能如何启用？

A: 在初始化 PaddleOCR 时设置相应参数：
```python
ocr = PaddleOCR(
    table=True,   # 启用表格识别
    layout=True   # 启用版面分析
)
```

### Q: VL 能力如何使用？

A: 安装额外依赖并使用 VL 模型：
```bash
pip install transformers>=4.30.0 torch>=2.0.0
```

```python
ocr = PaddleOCR(use_vl=True)
result = ocr.ocr(image_path, vl=True)
```

### Q: 印章识别功能在哪里？

A: PaddleOCR 3.x 的印章识别功能已整合到 PaddleOCR-VL-1.5 中：
```python
ocr = PaddleOCR(use_vl=True)
result = ocr.ocr(image_path, stamp_recognition=True)
```

## 参考资料

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR 3.0 技术报告](https://arxiv.org/abs/2507.05595)
- [PaddleOCR-VL 技术报告](https://arxiv.org/abs/2510.14528)
- [PaddleOCR 官网](https://www.paddleocr.com)

## Skill 中的更新

### requirements.txt
已移除 `paddlestructure` 和 `paddleclas`，只保留：
```txt
paddleocr>=3.0.0
paddlepaddle>=2.6.0
```

### SKILL.md
已更新 dependency 说明，明确说明 PaddleOCR 3.x 包含所有功能。

### 脚本更新
所有使用 `paddlestructure` 的脚本已更新为使用 PaddleOCR 3.x 的新 API。
