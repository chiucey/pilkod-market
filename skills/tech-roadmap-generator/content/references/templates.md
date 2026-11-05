# draw.io XML Template Library

## Basic Template Structure

### Complete XML Document Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>

    <!-- Add nodes and connections here -->

  </root>
</mxGraphModel>
```

## Common Node Styles

### 1. Start/End Nodes (Ellipse)
```xml
<mxCell id="START" value="Start"
        style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=12;"
        vertex="1" parent="1">
  <mxGeometry x="450" y="20" width="100" height="40" as="geometry"/>
</mxCell>
```

### 2. Main Process Nodes (Rectangle)
```xml
<mxCell id="PROCESS1" value="Research Content"
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;"
        vertex="1" parent="1">
  <mxGeometry x="400" y="100" width="200" height="50" as="geometry"/>
</mxCell>
```

### 3. Decision Nodes (Diamond)
```xml
<mxCell id="DECISION1" value="Is it feasible?"
        style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;"
        vertex="1" parent="1">
  <mxGeometry x="425" y="200" width="150" height="80" as="geometry"/>
</mxCell>
```

### 4. Subprocess/Group
```xml
<mxCell id="SUBPROCESS" value="Submodule"
        style="swimlane;horizontal=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=11;resizeParent=1;resizeParentMax=0;collapsible=1;margin=0;"
        vertex="1" parent="1">
  <mxGeometry x="50" y="400" width="1000" height="150" as="geometry"/>
</mxCell>
```

### 5. Connection Lines
```xml
<mxCell id="EDGE1" value=""
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;strokeWidth=1;endArrow=classic;endFill=1;"
        edge="1" parent="1" source="START" target="PROCESS1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### 6. Connection Lines with Labels
```xml
<mxCell id="EDGE2" value="Yes"
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;strokeWidth=1;endArrow=classic;endFill=1;fontColor=#666666;fontSize=10;exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
        edge="1" parent="1" source="DECISION1" target="PROCESS2">
  <mxGeometry relative="1" as="geometry">
    <mxPoint as="offset"/>
  </mxGeometry>
</mxCell>
```

### 7. Parallel Processes
```xml
<mxCell id="PARALLEL1" value="Parallel Task A"
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;"
        vertex="1" parent="1">
  <mxGeometry x="150" y="300" width="180" height="40" as="geometry"/>
</mxCell>
<mxCell id="PARALLEL2" value="Parallel Task B"
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;"
        vertex="1" parent="1">
  <mxGeometry x="670" y="300" width="180" height="40" as="geometry"/>
</mxCell>
```

### 8. Loop/Iteration
```xml
<mxCell id="LOOP_START" value="Iteration Start"
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;"
        vertex="1" parent="1">
  <mxGeometry x="400" y="500" width="200" height="40" as="geometry"/>
</mxCell>
<mxCell id="LOOP_CONDITION" value="Condition satisfied?"
        style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;"
        vertex="1" parent="1">
  <mxGeometry x="425" y="580" width="150" height="70" as="geometry"/>
</mxCell>
<!-- Return Arrow -->
<mxCell id="LOOP_BACK" value=""
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;strokeWidth=1;endArrow=classic;endFill=1;exitX=0;exitY=0.5;exitDx=0;exitDy=0;"
        edge="1" parent="1" source="LOOP_CONDITION" target="LOOP_START">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Complete Example: Basic Research Technical Roadmap

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>

    <!-- Start Node -->
    <mxCell id="start" value="Start"
            style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=12;"
            vertex="1" parent="1">
      <mxGeometry x="475" y="20" width="100" height="40" as="geometry"/>
    </mxCell>

    <!-- Node 1: Problem Identification -->
    <mxCell id="n1" value="Problem Identification&#xa;& Literature Review"
            style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;align=center;"
            vertex="1" parent="1">
      <mxGeometry x="400" y="100" width="200" height="50" as="geometry"/>
    </mxCell>

    <!-- Node 2: Theoretical Hypothesis -->
    <mxCell id="n2" value="Theoretical Hypothesis&#xa;& Model Construction"
            style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;align=center;"
            vertex="1" parent="1">
      <mxGeometry x="400" y="200" width="200" height="50" as="geometry"/>
    </mxCell>

    <!-- Node 3: Experimental Design -->
    <mxCell id="n3" value="Experimental Design&#xa;& Method Selection"
            style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;align=center;"
            vertex="1" parent="1">
      <mxGeometry x="400" y="300" width="200" height="50" as="geometry"/>
    </mxCell>

    <!-- Node 4: Data Collection -->
    <mxCell id="n4" value="Data Collection&#xa;& Processing Analysis"
            style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;align=center;"
            vertex="1" parent="1">
      <mxGeometry x="400" y="400" width="200" height="50" as="geometry"/>
    </mxCell>

    <!-- Decision Node -->
    <mxCell id="d1" value="Result Verification"
            style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;"
            vertex="1" parent="1">
      <mxGeometry x="450" y="500" width="100" height="60" as="geometry"/>
    </mxCell>

    <!-- Node 5: Conclusion -->
    <mxCell id="n5" value="Conclusion Summary&#xa;& Paper Writing"
            style="rounded=0;whiteSpace=wrap;html=1;fillColor=#82b366;strokeColor=#5a8a3c;fontSize=11;align=center;fillColor=#d5e8d4;"
            vertex="1" parent="1">
      <mxGeometry x="400" y="620" width="200" height="50" as="geometry"/>
    </mxCell>

    <!-- End Node -->
    <mxCell id="end" value="Complete"
            style="ellipse;whiteSpace=wrap;html=1;fillColor=#82b366;strokeColor=#5a8a3c;fontStyle=1;fontSize=12;"
            vertex="1" parent="1">
      <mxGeometry x="475" y="720" width="100" height="40" as="geometry"/>
    </mxCell>

    <!-- Connection Lines -->
    <mxCell id="e1" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;endArrow=classic;endFill=1;" edge="1" parent="1" source="start" target="n1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="e2" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;endArrow=classic;endFill=1;" edge="1" parent="1" source="n1" target="n2">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="e3" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;endArrow=classic;endFill=1;" edge="1" parent="1" source="n2" target="n3">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="e4" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;endArrow=classic;endFill=1;" edge="1" parent="1" source="n3" target="n4">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="e5" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;endArrow=classic;endFill=1;" edge="1" parent="1" source="n4" target="d1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="e6" value="Pass" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;endArrow=classic;endFill=1;fontColor=#666666;fontSize=10;" edge="1" parent="1" source="d1" target="n5">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="e7" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;endArrow=classic;endFill=1;" edge="1" parent="1" source="n5" target="end">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Feedback Loop -->
    <mxCell id="e8" value="Return for Revision" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#cc6666;endArrow=classic;endFill=1;strokeWidth=1;dashed=1;fontColor=#cc6666;fontSize=9;exitX=0;exitY=0.5;exitDx=0;exitDy=0;" edge="1" parent="1" source="d1" target="n3">
      <mxGeometry relative="1" as="geometry">
        <Array as="points">
          <mxPoint x="350" y="530"/>
          <mxPoint x="350" y="325"/>
        </Array>
      </mxGeometry>
    </mxCell>

  </root>
</mxGraphModel>
```

## Usage Instructions

1. **Save Format**: Save the XML code as a `.xml` file
2. **Import to draw.io**:
   - Open draw.io (https://app.diagrams.net/)
   - Click "File" → "Open" → Select XML file
   - Or drag and drop the XML file directly onto draw.io interface
3. **Edit**: After import, you can freely modify nodes, text, and connection lines
4. **Export**: Supports export to PNG, SVG, PDF and other formats