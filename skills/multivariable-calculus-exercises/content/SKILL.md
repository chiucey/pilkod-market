---
name: multivariable-calculus-exercises
description: 专为多元微积分教学设计的PDF生成器。当用户要求生成微积分习题课讲义、概念辨析课件、考研备考资料，或需要创建多元微积分相关的LaTeX排版PDF时使用。支持Article和Beamer两种输出格式，包含封面自动生成、章节结构智能构建、经典反例分析、考研真题解析等功能。
---

# 多元微积分习题课 PDF 生成器

专为多元微积分教学设计的高质量PDF生成工具，支持LaTeX排版、一键生成标准 Article 或 Beamer 演示文稿。

## 核心功能

### 1. 文档类型
- **Article 格式**：适合习题课讲义、备考资料
- **Beamer 演示文稿**：适合课堂讲授、概念辨析课件

### 2. 自动构建封面
- 教师姓名
- 学院/学校信息
- 日期（自动生成或指定）
- 课程标题与副标题

### 3. 智能章节结构
```
第一章  多元函数基础
├── 1.1 概念判定方法
│   ├── 多元函数极限定义
│   ├── 连续性判定
│   └── 偏导数存在性
├── 1.2 关系图谱
│   ├── 极限→连续→偏导存在→可微
│   └── 各概念间的蕴含关系
└── 1.3 经典反例
    ├── 偏导存在 ≠ 连续
    ├── 可微 ≠ 偏导连续
    └── 其他重要反例

第二章  考研真题解析
├── 典型题型分类
├── 解题方法总结
└── 真题实战演练
```

### 4. 经典反例库
内置以下经典反例及其可视化：
- **反例1**：偏导数存在但函数不连续
- **反例2**：函数可微但偏导数不连续
- **反例3**：方向导数存在但不可微
- **反例4**：偏导数不连续但函数可微

### 5. 视觉模板

#### 玻璃拟态模板 (Glassmorphism)
- 半透明背景层
- 毛玻璃效果
- 渐变色彩

#### 扁平化模板 (Flat Design)
- 简洁几何形状
- 纯色块设计
- 清晰的视觉层次

### 6. 数学公式支持
- TikZ 关系图绘制
- tcolorbox 定理环境
- 自动公式编号
- 多行公式对齐

## 使用方法

### 基本命令
```bash
# 生成Article格式讲义
python3 generate.py --type article --title "多元函数极限与连续"

# 生成Beamer演示文稿
python3 generate.py --type beamer --title "偏导数与可微"

# 指定封面信息
python3 generate.py --type article \
  --title "多元微积分习题课" \
  --subtitle "第二章 偏导数与全微分" \
  --author "张老师" \
  --institution "数学科学学院" \
  --date "2026年春季"

# 指定视觉模板
python3 generate.py --type article \
  --template glassmorphism \
  --title "概念辨析"
```

### 内容配置 (content.json)
```json
{
  "type": "article",
  "title": "多元函数极限与连续",
  "author": "教师姓名",
  "institution": "学院名称",
  "template": "flat",
  "chapters": [
    {
      "title": "概念判定方法",
      "sections": [
        {
          "title": "多元函数极限",
          "content": "定义与判定方法...",
          "examples": ["例1", "例2"]
        }
      ]
    },
    {
      "title": "经典反例",
      "type": "counterexample",
      "cases": [
        {
          "title": "偏导存在≠连续",
          "function": "f(x,y) = xy/(x^2+y^2)",
          "analysis": "详细分析..."
        }
      ]
    }
  ]
}
```

## 技术实现

### 排版引擎
- **LaTeX 编译**：XeLaTeX / LuaLaTeX
- **数学渲染**：TikZ + PGFPlots
- **定理环境**：tcolorbox 增强包

### 图表类型
| 类型 | 用途 | 实现方式 |
|------|------|----------|
| 关系图 | 概念关系可视化 | TikZ flowcharts |
| 函数图 | 3D曲面绘制 | PGFPlots |
| 反例图 | 可视化反例 | TikZ + pgfplots |

### 配色方案

#### 学术蓝 (Academic Blue)
```css
--primary: #1E3A5F;
--accent: #3498DB;
--background: #FAFBFC;
--text: #2C3E50;
```

#### 现代深空 (Modern Dark)
```css
--primary: #2C3E50;
--accent: #E74C3C;
--background: #1A1A2E;
--text: #ECF0F1;
```

## 模板样式

### Article 讲义模板
- 16pt 正文字号
- 1.5 倍行距
- 奇偶页不同的页眉页脚
- 章节编号使用中文数字

### Beamer 演示模板
- 16:9 宽屏比例
- 居中标题页面
- 分栏内容布局
- 进度条指示

## 输出文件
- **Article**: `multivariable_calculus_*.pdf`
- **Beamer**: `multivariable_calculus_slides_*.pdf`

## 示例内容

### 封面信息
```
微积分习题课 · 多元微积分
第二章  偏导数与全微分
张明  教授
数学科学学院 · 2026年春季
```

### 章节示例
```
第一章  多元函数极限与连续

1.1 极限的概念

定义：设函数 f(x,y) 在点 P0(x0,y0) 的某去心邻域内有定义...
（详细定义内容）

判定方法：
• 直接代入法
• 夹逼准则
• 极坐标变换法

1.2 经典反例

【反例1】偏导存在但函数不连续

函数：f(x,y) = { xy/(x²+y²),  (x,y)≠(0,0)
              { 0,            (x,y)=(0,0)

分析：在 (0,0) 点处，fx(0,0)=0, fy(0,0)=0
但沿 y=x 路径趋近时，极限值为 1/2 ≠ f(0,0)
```

## 依赖环境
- Python 3.9+
- LaTeX 发行版 (TeX Live / MiKTeX)
- XeLaTeX 或 LuaLaTeX 编译器
