---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 185ee55ca79d4f91d5212ac6989220f7
    PropagateID: 185ee55ca79d4f91d5212ac6989220f7
    ReservedCode1: 3044022068baeaf1f1223b59706a6bcea7e39cb25981012b07f1c1efc9f30cb66b459ed502202e246690df15b32338093dd451c7bbbd43ce9ba4893407653b54e556c38c746c
    ReservedCode2: 3046022100a248f29a0feffa71168b453300d2dd673456bf2aed41d40725c0242cf59487fd02210087006f97f10c7546f457a5c3727ec86219a3b5b853e9f774c2e71602401685e1
---

# amazon-image-requirements

亚马逊主图套图和A+套图设计需求文档生成器。专门为RC遥控车/攀爬车产品（基于FMS品牌5款产品模板）设计，
根据用户提供的产品信息（基础信息、车型/外观、核心卖点、技术参数、素材情况）自动生成符合公司标准格式的Excel设计需求文档。

## 📦 包含内容

- `SKILL.md` - Skill 主说明文件
- `scripts/generate_requirements.py` - Excel 生成核心脚本
- `scripts/validate.py` - Skill 验证脚本
- `scripts/package.py` - 打包脚本（本文件）
- `examples/118L01_Ford_F-100_示例.json` - 使用示例
- `assets/template_structure.md` - 文档结构说明
- `manifest.json` - 发布清单

## 🚀 安装方法

### 方式 1：本地自动加载（推荐）

将本文件夹解压后，移动到：

```
~/.minimaxagent/skills/amazon-image-requirements/
```

下次开启 minimax Agent 会话时自动加载。

### 方式 2：技能广场安装

在 minimax 技能广场搜索 `amazon-image-requirements` 或 `FMS 设计需求`，点击安装。

## 📋 使用方法

### 快速使用

提供以下 5 类信息：

1. **基础信息**：产品名称/型号、比例、电机类型
2. **车型/外观**：车型、官方授权、颜色、外观风格
3. **核心卖点**：5-7 个核心卖点（按优先级）
4. **技术参数**：尺寸、轴距、离地间隙、电池/电机
5. **素材情况**：是否已有素材、是否需要场景图

### 编程方式

```python
from generate_requirements import generate_amazon_image_requirements

product_info = {
    "model": "118L01",
    "product_name": "Ford F-100",
    "full_name": "FMS 1:18 FCXII 118L01 Ford F-100",
    "scale": "1/18",
    "motor_type": "有刷",
    "vehicle_model": "福特F100",
    "license": "Ford",
    "colors": ["黑白", "蒂芙尼蓝", "红白"],
    "features": [
        "全新FCX18二代低重心(LCG)底盘",
        "多品牌授权，福特官方授权仿真车壳",
        "磁吸快拆结构",
        "全球首推1/18福特F-100攀爬车"
    ],
    "dimensions": "330*145*147mm",
    "wheelbase": "199mm",
    "ground_clearance": "31mm",
    "battery_motor": "180有刷",
    "has_source_assets": True,
    "need_scene_images": True,
    "need_shooting": False,
    "output_dir": "./"
}

generate_amazon_image_requirements(product_info)
```

## 🛠️ 工具脚本

### 验证

```bash
python scripts/validate.py
```

### 打包

```bash
python scripts/package.py
```

## 📊 生成的文档结构

- **主图**（3 张，1600×1600，黄色标识）
- **副图**（7 张，1600×1600，绿色标识）
- **A+ 产品长图**（2 个尺寸，橙色标识）
- **A+ Banner**（3 个尺寸）
- **A+ 导航栏**（3 张 × 3 尺寸）
- **配件清单**（3 个尺寸）
- **场景图**（3 个尺寸）
- **细节图**（4-5 张，2600×1400）

## 📄 许可证

MIT License

## 👤 作者

Matrix Agent

## 🔖 版本

v1.0.0 (2026-06-25)
