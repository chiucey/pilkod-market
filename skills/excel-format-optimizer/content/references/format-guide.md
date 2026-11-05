# Excel 排版优化参考指南

本文档提供详细的排版规范、配色方案和最佳实践，作为 SKILL.md 的补充参考。

## 1. 字体规范

### 字体选择

| 用途 | 推荐字体 | 备选字体 |
|------|---------|---------|
| 中文正文 | 微软雅黑、思源黑体 | 宋体（打印） |
| 英文正文 | Calibri、Arial | Times New Roman |
| 代码/数字 | Consolas、Source Code Pro | Courier New |

### 字号层级

```
标题 H1: 18-20pt，加粗
标题 H2: 14-16pt，加粗
正文: 11-12pt，常规
注释: 9-10pt，常规
脚注: 8pt，常规
```

## 2. 对齐规范

### 水平对齐

| 数据类型 | 对齐方式 | 示例 |
|---------|---------|------|
| 数值/金额 | 右对齐 | ¥ 1,234.56 |
| 文本/名称 | 左对齐 | 张三 |
| 标题/表头 | 居中 | 部门名称 |
| 百分比 | 右对齐 | 85.5% |
| 日期 | 右对齐 | 2024-01-15 |

### 垂直对齐

- 默认使用**垂直居中**
- 超长文本可使用顶部对齐
- 多行文本使用两端对齐

## 3. 边框系统

### 边框样式

```
外边框 (outer):
  - 粗细: 1.5pt
  - 颜色: #000000 或 #2F5496

内边框 (inner):
  - 粗细: 0.5pt
  - 颜色: #BFBFBF

仅底边 (header separator):
  - 粗细: 1pt
  - 颜色: #2F5496
```

### 边框类型

| 类型 | 样式 | 适用场景 |
|------|------|---------|
| 实线 | continuous | 一般数据表 |
| 双线 | double | 表头与数据分隔 |
| 虚线 | dashed | 次要分隔 |
| 无边框 | none | 视觉分隔/空行 |

## 4. 配色方案

### 商务标准色

```yaml
主色:
  名称: 深海蓝
  HEX: #1F4E79
  RGB: 31, 78, 121

辅色:
  名称: 商务蓝
  HEX: #4472C4
  RGB: 68, 114, 196

强调:
  名称: 金色
  HEX: #FFC000
  RGB: 255, 192, 0

背景:
  表头: #4472C4 (白字)
  交替行: #F2F2F2 / #FFFFFF
  强调行: #FFF2CC
```

### 色阶使用

```python
# 数值热力图色阶示例
colors = [
    '#63BE7B',  # 高值
    '#91CF60',  #
    '#C5E0B4',  #
    '#F8F8F8',  # 中值
    '#F4B084',  #
    '#E59866',  #
    '#E74C3C',  # 低值
]
```

## 5. 打印设置

### 页边距标准

| 标准 | 上/下 | 左/右 |
|------|-------|-------|
| 窄边距 | 1.91cm | 1.27cm |
| 普通 | 2.54cm | 2.54cm |
| 宽边距 | 2.54cm | 3.18cm |

### 打印方向

- 横向：列数 > 8 的表格
- 纵向：列数 ≤ 8 的表格

### 缩放规则

```
避免最后一列被截断：
  - 计算内容总宽度 vs 纸张宽度
  - 缩放比例 = 纸张宽度 / 内容总宽度
  - 最小缩放: 50%
  - 最佳缩放: 80-100%
```

## 6. 条件格式规则

### 数据验证类

```python
# 负数红色
rule_negative = {
    'type': 'cellIs',
    'operator': 'lessThan',
    'formula': 0,
    'format': {'fontColor': '#C00000'}
}

# 零值处理
rule_zero = {
    'type': 'cellIs',
    'operator': 'equal',
    'formula': 0,
    'format': {'fontColor': '#7F7F7F'}
}
```

### 阈值提醒类

```python
# 超过阈值高亮
rule_threshold = {
    'type': 'greaterThan',
    'formula': 100,
    'format': {'background': '#FFEB9C'}
}
```

## 7. 列宽计算

### 自动列宽算法

```python
def calculate_column_width(data, font_name="微软雅黑", font_size=11):
    """
    计算最优列宽
    原理：中文按字符宽度计算
    """
    # 中文字符宽度系数
    chinese_ratio = 2.0
    # 英文字符宽度系数
    english_ratio = 0.5
    # 数字字符宽度系数
    digit_ratio = 0.6

    max_width = 0
    for cell in data:
        width = 0
        for char in str(cell):
            if '\u4e00' <= char <= '\u9fff':  # 中文
                width += chinese_ratio
            elif char.isdigit():
                width += digit_ratio
            else:
                width += english_ratio

        # 加上边距
        width += 2
        max_width = max(max_width, width)

    return min(max_width, 50)  # 最大50
```

## 8. 常见问题处理

### Q: 如何处理合并单元格？

A: 合并策略建议
- 仅在表头横向合并
- 避免在数据区使用合并
- 如必须合并，确保对齐方式正确

### Q: 超长文本如何处理？

A: 多策略组合
1. 设置自动换行 (`wrap_text: true`)
2. 增大行高
3. 截断 + tooltip
4. 拆分到多列

### Q: 如何保持打印一致性？

A: 关键设置
- 打印区域设置 (print_area)
- 重复标题行 (print_title_rows)
- 页面布局锁定 (page_setup)
