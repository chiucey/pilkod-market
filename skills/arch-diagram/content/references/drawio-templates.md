# draw.io XML 模板与 Schema 说明

## draw.io XML 基本结构

draw.io 的 XML 格式遵循以下基本结构：

```xml
<mxGraphModel dx="1420" dy="874" grid="1" gridSize="10" guides="1" tools="9" 
              export="" xmlns="http://draw.mx.cn.cn/graph">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    
    <!-- ========== 层级标题行 ========== -->
    <mxCell id="layer1_header" value="层级名称" 
            style="shape=rect;rounded=0;whiteSpace=wrap;fillColor=#3182CE;strokeColor=none;fontColor=#FFFFFF;fontStyle=1;fontSize=14;align=center;verticalAlign=middle;"
            vertex="1" parent="1">
      <mxGeometry x="40" y="40" width="920" height="36" as="geometry"/>
    </mxCell>
    
    <!-- ========== 模块卡片 ========== -->
    <mxCell id="module1" value="模块标题&#xa;子内容1&#xa;子内容2" 
            style="shape=rect;rounded=0;whiteSpace=wrap;fillColor=#F7FAFC;strokeColor=#CBD5E0;strokeWidth=1;fontColor=#1A202C;fontSize=11;align=center;verticalAlign=middle;"
            vertex="1" parent="1">
      <mxGeometry x="40" y="90" width="200" height="80" as="geometry"/>
    </mxCell>
    
    <!-- ========== 分隔线（可选） ========== -->
    <mxCell id="divider1" value="" 
            style="shape=line;strokeColor=#E2E8F0;strokeWidth=1;movable=0;resizable=0;"
            vertex="1" parent="1">
      <mxGeometry x="40" y="85" width="920" height="1" as="geometry"/>
    </mxCell>
    
  </root>
</mxGraphModel>
```

---

## 常用 Style 属性速查

| 属性 | 说明 | 示例值 |
|------|------|--------|
| `shape` | 形状 | `rect`, `roundedRect`, `ellipse` |
| `fillColor` | 填充色 | `#3182CE`, `#F7FAFC` |
| `strokeColor` | 边框色 | `#CBD5E0`, `none` |
| `strokeWidth` | 边框宽度 | `1`, `2` |
| `fontColor` | 字体颜色 | `#FFFFFF`, `#1A202C` |
| `fontStyle` | 字体样式 | `0=常规`, `1=粗体`, `2=斜体`, `3=粗斜` |
| `fontSize` | 字号 | `10`, `12`, `14`, `16` |
| `align` | 水平对齐 | `left`, `center`, `right` |
| `verticalAlign` | 垂直对齐 | `top`, `middle`, `bottom` |
| `whiteSpace` | 文字换行 | `wrap` |
| `rounded` | 圆角 | `0`=无, `1`=有 |
| `movable` | 可移动 | `0`=否, `1`=是 |
| `resizable` | 可缩放 | `0`=否, `1`=是 |

---

## 标准层级颜色对照表

| 层级类型 | fillColor | fontColor | 适用层级 |
|---------|-----------|-----------|---------|
| 基础设施/底座 | `#2D3748` | `#FFFFFF` | 底层 |
| 数据平台层 | `#4A5568` | `#FFFFFF` | 中下层 |
| 模型/算法层 | `#3182CE` | `#FFFFFF` | 中层 |
| 知识/RAG层 | `#805AD5` | `#FFFFFF` | 中层 |
| 平台工具层 | `#4299E1` | `#FFFFFF` | 中上层 |
| 应用场景层 | `#319795` | `#FFFFFF` | 顶层 |
| 治理/合规层 | `#718096` | `#FFFFFF` | 底座 |
| 模块卡片(默认) | `#F7FAFC` | `#1A202C` | 任何层内 |
| 模块卡片(强调) | `#EBF8FF` | `#2C5282` | 重点模块 |
| 模块卡片(警示) | `#FFF5F5` | `#C53030` | 重要提示 |

---

## 双栏并列模板（适用于复杂层）

当某一层需要并排展示两个子系统时（如：大模型体系 | 知识体系）：

```xml
<!-- 父层容器（占满一行） -->
<mxCell id="layer3_bg" value="" 
        style="shape=rect;rounded=0;whiteSpace=wrap;fillColor=#EBF8FF;strokeColor=#BEE3F8;strokeWidth=1;movable=0;resizable=0;portrait=false;"
        vertex="1" parent="1">
  <mxGeometry x="40" y="200" width="920" height="120" as="geometry"/>
</mxCell>

<!-- 左栏：LLM体系 -->
<mxCell id="llm_header" value="大模型体系" 
        style="shape=rect;rounded=0;fillColor=#3182CE;fontColor=#FFFFFF;fontStyle=1;fontSize=12;align=left;verticalAlign=middle;spacingLeft=8;movable=0;"
        vertex="1" parent="1">
  <mxGeometry x="50" y="210" width="420" height="24" as="geometry"/>
</mxCell>
<mxCell id="llm_module1" value="GLM-5 | GLM-4.7 | GLM-4.6" 
        style="shape=rect;rounded=0;fillColor=#F7FAFC;strokeColor=#CBD5E0;fontColor=#1A202C;fontSize=10;align=center;"
        vertex="1" parent="1">
  <mxGeometry x="50" y="242" width="420" height="70" as="geometry"/>
</mxCell>

<!-- 右栏：知识体系 -->
<mxCell id="knowledge_header" value="知识体系" 
        style="shape=rect;rounded=0;fillColor=#805AD5;fontColor=#FFFFFF;fontStyle=1;fontSize=12;align=left;verticalAlign=middle;spacingLeft=8;movable=0;"
        vertex="1" parent="1">
  <mxGeometry x="530" y="210" width="420" height="24" as="geometry"/>
</mxCell>
<mxCell id="knowledge_module1" value="知识库 | 知识图谱 | RAG" 
        style="shape=rect;rounded=0;fillColor=#F7FAFC;strokeColor=#CBD5E0;fontColor=#1A202C;fontSize=10;align=center;"
        vertex="1" parent="1">
  <mxGeometry x="530" y="242" width="420" height="70" as="geometry"/>
</mxCell>
```

---

## 画布尺寸建议

| 用途 | 宽度 | 高度 | gridSize |
|------|------|------|----------|
| 16:9 演示 | 960 | 540 | 10 |
| 4:3 文档 | 800 | 600 | 10 |
| A4 纵向 | 620 | 877 | 10 |
| 高清图生图 | 1920 | 1080 | 10 |

---

## 导出方法

1. 在 draw.io 打开 XML 文件
2. `File → Export as → PNG`（选择 2x 分辨率）
3. 或直接另存为 `.drawio` 文件供后续编辑
