# PPT Translator - 使用指南

## 功能概述

PPT Translator 是一个智能工具，可以在保持原有幻灯片布局、背景主题和格式的前提下，将 PowerPoint 文件翻译成不同语言。

## 支持的语言

| 代码 | 语言 |
|------|------|
| en | 英语 (English) |
| zh-cn | 简体中文 |
| zh-tw | 繁体中文 |
| ja | 日语 (日本語) |
| ko | 韩语 (한국어) |
| es | 西班牙语 |
| fr | 法语 |
| de | 德语 |
| it | 意大利语 |
| pt | 葡萄牙语 |
| ru | 俄语 |
| ar | 阿拉伯语 |

## 安装依赖

```bash
pip install python-pptx googletrans==4.0.0-rc1
```

## 使用方法

### 命令行使用

```bash
# 基本翻译（英文 → 中文）
python ppt_translator.py input.pptx -t zh-cn

# 指定源语言和目标语言
python ppt_translator.py input.pptx -s en -t ja

# 指定输出文件
python ppt_translator.py input.pptx -o output_translated.pptx -t fr

# 查看PPT信息
python ppt_translator.py input.pptx -i
```

### Python代码使用

```python
from ppt_translator import PptTranslator

# 创建翻译器实例
translator = PptTranslator(
    file_path='input.pptx',
    target_lang='zh-cn',  # 目标语言
    source_lang='en'      # 源语言
)

# 查看PPT信息
info = translator.get_presentation_info()
print(f"幻灯片数量: {info['slide_count']}")

# 执行翻译
translator.translate_presentation('output.pptx')
```

## 智能功能

### 1. 字体大小自动调整

翻译后的文本会自动调整字体大小，确保：
- 长文本不会溢出文本框
- 短文本不会被过分放大
- 最小字体不小于 8pt，最大不超过 72pt

### 2. 样式保持

翻译过程会保留以下元素：
- 字体名称和样式（粗体、斜体）
- 文字颜色
- 对齐方式
- 文本框位置和大小
- 段落格式

### 3. 主题保留

- 幻灯片母版背景
- 配色方案
- 图片和图形
- 图表和表格
- 动画设置（如果有）

## 注意事项

1. **翻译API**: 当前使用 Google Translate API，确保网络连接正常
2. **格式限制**: 对于复杂格式（如多列布局），可能需要手动微调
3. **表格翻译**: 表格内容会单独翻译，表格结构保持不变
4. **图片文字**: 如果文字嵌入在图片中，将无法翻译

## 故障排除

### 问题：翻译API调用失败

解决方案：
1. 检查网络连接
2. 安装/更新 googletrans 库：`pip install --upgrade googletrans==4.0.0-rc1`
3. 或使用其他翻译API（如DeepL、Azure Translator）

### 问题：字体大小不协调

解决方案：
- 手动在 PowerPoint 中微调
- 调整代码中的 `min_size` 和 `max_size` 参数

### 问题：部分文本未被翻译

可能原因：
1. 文本在图片中（需要OCR处理）
2. 文本使用了特殊的艺术字效果
3. 文本在母版中（需要单独处理）

## 技术栈

- **python-pptx**: PowerPoint文件读写
- **googletrans**: Google Translate API接口
- **Python 3.7+**: 运行环境
