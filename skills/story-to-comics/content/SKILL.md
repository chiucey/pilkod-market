---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fe1ea558ab9fe445fb54db8ab9c4672e
    PropagateID: fe1ea558ab9fe445fb54db8ab9c4672e
    ReservedCode1: 30460221009e7bb02e13ea00a48486effe8b4298bcaaf5973256ad0b09dc58c3d4e83a030b0221008ab516064473293871b990bb9296c38c6b98228650dd82493391124a86a084b1
    ReservedCode2: 3045022100e5f9de393ec01146eea25f9972da86eea959f8744adaef029652c2a6afae48b4022016c7fd97abbba6a24ab20bb598fc560e06eb4c4c5de1e72d5fc8e9211c7fd7bd
description: 将规范格式的故事剧本转换为系列漫画。当用户上传符合格式要求的剧本（包含故事设定、主角特征、剧情脉络、最终结局等）并要求生成漫画时使用。不使用大模型，纯Python图像处理实现。
name: story-to-comics
---

# 故事剧本转漫画技能

## 功能概述

本技能将规范格式的故事剧本自动转换为系列漫画图像，使用纯Python技术实现，无需大模型支持。通过解析剧本结构，提取场景、人物、对话等元素，生成可视化漫画页面。

## 剧本格式规范

### 必须包含的章节

1. **剧名信息**
   - 剧名：《标题》
   - 时长：约X分钟
   - 场景：场景描述

2. **主角特征**
   - 角色名（性别，身份）
   - 人设：角色性格特点
   - 可选：特殊能力、外貌描述、隐藏身份等

3. **剧情脉络**
   - 序号+场景名称
   - 镜头描述（括号内的场景描写）
   - 角色名称（动作/对话描述）
   - 角色对话内容

4. **最终结局**（可选）
   - 结尾场景描述
   - 字幕/总结语

### 示例剧本结构

```
一、剧名：《标题》
时长：约3-4分钟
场景：某高校图书馆

二、主角特征
小科（男，大一新生）
- 人设：信奉"搜索引擎解决一切"。
小图（女，资深学科馆员）
- 人设：25岁左右，戴金属框智能眼镜...
- 特殊能力：能将抽象的概念转化为具象场景...

三、剧情脉络
1. 开场：闯入者
（镜头：小科一边看手机地图一边走进图书馆...）
小科（对着手机吐槽）："这破图书馆APP..."
小图（无声出现在他身后）："同学，你拿错了..."

2. 发展：不服与较量
...

四、结局：新生的开始
...
```

## 使用方法

### 方式一：上传剧本文件

用户上传符合格式的 `.txt` 或 `.docx` 文件，系统自动解析并生成漫画。

### 方式二：直接输入剧本

将剧本内容粘贴到输入框中，系统解析并生成漫画。

## 生成结果

### 输出内容

1. **系列漫画图像**
   - 每场景生成一个或多个漫画面板
   - 包含场景背景、人物形象、对话气泡
   - 高清PNG格式，可自定义分辨率

2. **漫画配置选项**
   - 画风选择：简约、传统、卡通
   - 面板布局：1格、2格、3格
   - 图像尺寸：800x600、1200x900、1920x1080

3. **输出格式**
   - 单张漫画面板（PNG）
   - 漫画页面（多面板组合）
   - 完整漫画册（PDF）

## 技术实现

### 核心依赖

- `Pillow`：图像绘制和合成
- `Pillow-PillowFight`：图像滤镜效果
- `reportlab`：PDF生成
- `python-docx`：Word文档解析

### 模块架构

```
story-to-comics/
├── scripts/
│   ├── __init__.py
│   ├── parser.py          # 剧本解析器
│   ├── character.py      # 角色管理
│   ├── scene.py          # 场景生成
│   ├── dialogue.py       # 对话气泡
│   ├── panel.py          # 面板生成
│   └── generator.py      # 主生成器
├── assets/
│   └── templates/        # 模板资源
└── examples/
    └── sample_script.py   # 示例脚本
```

### 生成流程

1. **解析阶段**
   - 读取剧本文本
   - 提取剧名、角色、场景
   - 解析对话和动作描述

2. **角色阶段**
   - 根据角色描述生成基础形象
   - 支持表情变化
   - 支持位置控制

3. **场景阶段**
   - 匹配场景关键词
   - 应用背景模板
   - 添加氛围效果

4. **合成阶段**
   - 绘制面板框架
   - 放置角色和背景
   - 生成对话气泡
   - 合成最终图像

## 配置参数

### 漫画参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| style | str | "simple" | 画风：simple/traditional/cartoon |
| layout | str | "2x2" | 布局：1x1/2x1/2x2/3x2 |
| width | int | 1200 | 输出宽度（像素） |
| height | int | 900 | 输出高度（像素） |
| dpi | int | 150 | 图像DPI |

### 颜色主题

| 主题 | 适用场景 | 主色调 |
|------|----------|--------|
| day | 日间场景 | #FFE4B5, #87CEEB |
| night | 夜间场景 | #191970, #4169E1 |
| indoor | 室内场景 | #F5DEB3, #DEB887 |
| fantasy | 奇幻场景 | #9370DB, #BA55D3 |

## 注意事项

1. **剧本格式**：必须严格按照上述格式提供剧本
2. **角色描述**：越详细的角色描述生成的形象越准确
3. **场景切换**：每个场景用数字序号标识
4. **对话格式**：角色名后跟冒号和对话内容
5. **镜头描述**：使用全角括号「（）」包裹

## 错误处理

- 格式错误：提示用户修正剧本格式
- 解析失败：返回具体错误位置
- 生成失败：提供备选默认方案

## 使用示例

```python
from story_to_comics import ComicGenerator

# 初始化生成器
generator = ComicGenerator(style="simple")

# 加载剧本
with open("script.txt", "r", encoding="utf-8") as f:
    script_content = f.read()

# 解析剧本
parsed = generator.parse_script(script_content)

# 生成漫画
result = generator.generate(
    parsed,
    output_dir="output",
    format="png"
)

print(f"生成 {len(result['panels'])} 张漫画面板")
```
