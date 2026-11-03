---
name: perler-crossstitch-generator
description: 拼豆十字绣图纸生成器。当用户要求生成拼豆图纸、十字绣图案、像素画设计、串珠图纸、十字绣导出、拼豆导出、图片转像素画、像素化处理、设计像素图案、导出PDF图纸时使用。
---

# 拼豆十字绣图纸生成器

一款专业的拼豆与十字绣图纸生成工具，将图片智能转化为精美的像素化图纸，支持高清 PDF 导出。

## 功能概览

### 核心功能

1. **智能图片处理**
   - 支持 JPG、PNG、GIF、WebP 格式图片上传
   - 拖拽上传或点击上传两种方式
   - 自动像素化处理，保留图像细节

2. **专业编辑工具**
   | 工具 | 快捷键 | 功能 |
   |------|--------|------|
   | 画笔 | B | 绘制像素点 |
   | 橡皮 | E | 擦除像素 |
   | 填充 | G | 填充连续区域 |
   | 吸管 | I | 吸取颜色 |
   | 颜色替换 | R | 替换所有相同颜色 |
   | 撤销 | Ctrl+Z | 撤销操作 |
   | 重做 | Ctrl+Y | 重做操作 |

3. **智能调色**
   - 颜色数量：8-256 色可调
   - 缩放模式：最近邻（像素风）/ 双线性（平滑）/ 双三次（高清）
   - 抖动处理：Floyd-Steinberg 算法

4. **丰富色库**
   - 内置 Perler 标准 62 色
   - DMC 十字绣 450+ 色
   - 支持 CSV 自定义导入

5. **一键导出**
   - PDF 矢量图纸（A4/Letter）
   - CSV 数据表格
   - 颜色图例和用豆统计

## 使用流程

```
上传图片 → 自动像素化 → 微调编辑 → 选择色库 → 导出 PDF
```

## 文件结构

```
perler-crossstitch-generator/
├── SKILL.md              # 技能定义文件
├── _meta.json            # 元数据
├── scripts/
│   ├── pixel-processor.js # 核心像素处理
│   ├── pdf-export.js     # PDF 导出模块
│   ├── quick_validate.py # 验证脚本
│   └── package_skill.py # 打包脚本
├── assets/
│   ├── pixel-art-app.html # 完整应用
│   ├── perler-colors.json # Perler 色库
│   └── dmc-colors.json    # DMC 色库
└── references/           # 参考文档
```

## 技术实现

- **前端**：原生 JavaScript + Canvas API
- **PDF 生成**：jsPDF
- **颜色量化**：Floyd-Steinberg 抖动算法
- **文件格式**：HTML 单文件应用

## 输出说明

### PDF 图纸
- 包含完整像素网格
- 显示颜色代码
- 附带颜色图例
- 用豆数量统计

### CSV 数据
- X/Y 坐标
- HEX 颜色值
- 色库代码
