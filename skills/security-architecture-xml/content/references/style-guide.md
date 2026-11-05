# 样式规范

以下规范用于生成与本会话一致的 draw.io / diagrams.net XML 风格。

## 1. 画布与外层背景

优先使用：
- 外层背景框：`fillColor=#e6e6e6`
- 外层边框：`strokeColor=#000000`
- 外层边框宽度：`strokeWidth=1.5`

示例：
```xml
style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e6e6e6;strokeColor=#000000;strokeWidth=1.5;"
```

## 2. 主标题

主标题使用文本节点，不加底色：
- 居中
- 加粗
- 字号 24

示例：
```xml
style="text;html=1;align=center;verticalAlign=middle;fontSize=24;fontStyle=1;strokeColor=none;fillColor=none;"
```

## 3. 层容器

每一层都是圆角大容器：
- `rounded=1`
- `arcSize=18`
- `fillColor=#f2f2f2`
- `strokeColor=#000000`
- `strokeWidth=1.5`
- 左上角标题，左对齐

示例：
```xml
style="rounded=1;whiteSpace=wrap;html=1;arcSize=18;align=left;verticalAlign=top;spacingLeft=16;spacingTop=10;fontStyle=1;fontSize=16;fillColor=#f2f2f2;strokeColor=#000000;strokeWidth=1.5;"
```

## 4. 层内分组框

当一层中需要表达一个较大的能力域时，使用分组框：
- `fillColor=#f7f7f7`
- `strokeColor=#000000`
- `strokeWidth=1.2`
- 标题左上角显示

## 5. 小模块框

具体模块或功能点使用白底矩形：
- `fillColor=#ffffff`
- `strokeColor=#000000`
- 字号 11–12
- 居中

示例：
```xml
style="rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=11;fillColor=#ffffff;strokeColor=#000000;"
```

## 6. 布局规则

- 采用横向分层布局，自上而下排列。
- 层与层之间保持稳定间距。
- 同层模块尽量等宽分布。
- 一张图中尽量保持统一的模块尺寸。
- 文字过长时，使用 `&lt;br/&gt;` 分行。
- 一张图不要混用过多样式。

## 7. 连线规则

默认不强制加连线。

只有在以下场景使用连线：
- 需要明确表示数据流转顺序
- 需要明确表示平台联动方向
- 用户明确要求展示箭头关系

若使用连线：
- 用黑色或深灰色
- 不使用花哨箭头
- 优先正交线

## 8. 尺寸建议

适用于常规一页 PPT / Word 插图：
- 外层总宽度约 800 左右
- 每层高度 80–180 不等
- 标题高度约 40
- 小模块高度 24–44

## 9. 禁止事项

不要：
- 使用彩色科技风渐变
- 使用蓝紫多色面板
- 使用密集箭头网络图风格
- 把整段说明文字直接塞进模块
- 用营销词代替架构层名称
