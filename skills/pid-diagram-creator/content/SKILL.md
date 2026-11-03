---
name: pid-diagram-creator
description: 专业P&ID（工艺仪表流程图）生成技能。当用户要求生成P&ID图、创建工艺流程图、绘制P&ID、生成工艺仪表流程图时使用。支持铅笔素描、钢笔、圆珠笔三种手绘风格输出。触发短语：P&ID diagram, 工艺流程图, P&ID图, 仪表流程图, 管道仪表流程图, process flow diagram, 简笔P&ID, 手绘P&ID
---

# P&ID Diagram Creator

Professional P&ID (Piping and Instrumentation Diagram) generator with multiple hand-drawn style outputs.

## Overview

This skill generates professional P&ID diagrams using text-to-image AI generation. Users can create detailed process and instrumentation diagrams in three distinct hand-drawn styles: pencil sketch, ink pen, and ballpoint pen.

## Supported Drawing Styles

| Style | Description | Use Case |
|-------|-------------|----------|
| Pencil Sketch | Light gray strokes, soft shading, erase marks visible | Drafting, conceptual design |
| Ink Pen | Bold black lines, clean strokes, technical drawing | Final drawings, blueprints |
| Ballpoint Pen | Blue/black ink, varying line weights, casual sketch | Quick notes, informal documentation |

## Core P&ID Elements

### Process Equipment
- **Tanks & Vessels**: Cylindrical tanks, reactors, receivers (flat top/bottom options)
- **Pumps**: Centrifugal, diaphragm, lobe, gear pumps
- **Valves**: Ball, gate, globe, check, control, safety valves
- **Heat Exchangers**: Shell & tube, plate, kettle reboilers
- **Columns**: Distillation, absorption, stripping columns
- **Filters**: Strainers, bag filters, filter presses

### Instrumentation Symbols
- **Transmitters**: TT (temperature), PT (pressure), FT (flow), LT (level)
- **Indicators**: TI, PI, FI, LI with circle display
- **Controllers**: TIC, PIC, FIC with square display
- **Switches**: TSHH, PSHH, FSHH with diamond display
- **Actuators**: Electric, pneumatic, hydraulic symbols

### Control Logic Elements
- **Interlocks**: High/high (HH), high (H), low (L), low/low (LL)
- **Delays**: Time delay relays (e.g., 10s delay on startup)
- **Logic Gates**: AND, OR, NOT symbols
- **Weight Control**: Load cells, weight transmitters (WT/WI)

## Workflow

### Step 1: Collect User Requirements

Gather the following information:
1. **Process Equipment**: What equipment needs to be included (tanks, pumps, reactors, etc.)
2. **Connections**: How equipment is connected (pipes, streams)
3. **Instrumentation**: What instruments are needed (TT, PT, FT, etc.)
4. **Control Logic**: Interlocks, shutdown conditions, delays
5. **Drawing Style**: Pencil sketch, ink pen, or ballpoint pen (default: pencil sketch)
6. **Layout Preference**: Top-to-bottom, left-to-right flow direction

### Step 2: Construct P&ID Prompt

Build a structured prompt following this template:

```
[STYLE] P&ID diagram, hand-drawn [STYLE_DESCRIPTION]:
- [Equipment 1]: [Description] with [key features]
- [Equipment 2]: [Description] with [key features]
- Pipeline connections with flow arrows
- Instrumentation: [List instruments with locations]
- Control logic: [Interlocks, delays, shutdown conditions]
- Instrument signal lines (dashed for pneumatic, dotted for electrical)
- Minimalist technical line drawing, clean [STYLE] strokes
```

### Step 3: Generate Image

Use `image_synthesize` tool with:
- `aspect_ratio`: "16:9" for landscape, "9:16" for portrait
- Output file: `pid_[style]_[timestamp].png`

### Step 4: Present Results

Deliver the generated P&ID with:
- Summary description
- Key elements included
- Style information
- File path for download

## Example Prompts

### Example 1: Basic Tank to Reactor System

**User Request**: "称重罐通过隔膜泵输送到反应釜，管线上有温压变送器"

**Generated Prompt (Pencil Style)**:
```
Pencil sketch P&ID diagram, hand-drawn with light gray strokes:
- Weighing tank: Cylindrical vessel with flat top and bottom, load cells underneath measuring weight, bottom outlet at lowest point
- Electric diaphragm pump: Connected to tank bottom outlet, motor driven
- Reactor vessel: Receiving material via pipeline from pump, top inlet entry
- Pipeline: From pump discharge to reactor top inlet, with flow direction arrow
- Instrumentation on pipeline: TT (temperature transmitter) with THH interlock, PT (pressure transmitter) with PHH and PAL interlocks
- Low pressure interlock enabled 10 seconds after pump startup (标注: 10s delay)
- Load cells as weight control loop (WT) controlling pump start/stop
- Dashed instrument signal lines
- Simple minimalist pencil sketch, clean technical line drawing, light gray strokes on white background
```

### Example 2: Heat Exchanger System

**User Request**: "换热器系统，带控制阀和温度联锁"

**Generated Prompt (Ink Pen Style)**:
```
Ink pen P&ID diagram, bold black line technical drawing:
- Shell and tube heat exchanger: Horizontal configuration, inlet/outlet nozzles
- Hot fluid pipeline: From source to exchanger inlet with flow arrow
- Cold fluid pipeline: From exchanger outlet to destination
- Control valve: Pneumatic diaphragm control valve on hot fluid inlet
- Temperature transmitter TT: On cold fluid outlet with THH interlock to close control valve
- Temperature indicator TI: On hot fluid inlet
- Safety relief valve: On exchanger shell
- Instrument air line: Dashed line to control valve
- Clean ink pen strokes, technical blueprint style, black lines on white background
```

### Example 3: Pump Station with Multiple Units

**User Request**: "泵站，三台离心泵，两用一备"

**Generated Prompt (Ballpoint Pen Style)**:
```
Ballpoint pen P&ID diagram, blue ink casual sketch style:
- Three centrifugal pumps: Pump A (duty), Pump B (duty), Pump C (standby)
- Pump suction header: Connected to tank outlet
- Pump discharge header: Combined from all pumps
- Check valves: On each pump discharge to prevent backflow
- Isolation valves: Gate valves on suction and discharge of each pump
- Flow transmitter FT: On common discharge header
- Pressure transmitter PT: On discharge header with PAL interlock
- Control logic: Auto start second pump on low flow, auto start standby on first pump failure
- Ballpoint pen strokes, varying line weights, informal technical sketch
```

## Style-Specific Prompt Modifiers

### Pencil Sketch
- "light gray strokes"
- "soft shading effects"
- "erase marks visible"
- "hatching for texture"
- "graphite pencil on white paper"

### Ink Pen
- "bold black lines"
- "clean precise strokes"
- "technical drawing style"
- "blueprint aesthetic"
- "India ink on drafting film"

### Ballpoint Pen
- "blue ink strokes"
- "varying line weights"
- "casual sketch style"
- "hand-drawn feel"
- "ballpoint pen on notebook paper"

## Quality Guidelines

1. **Completeness**: Include all major equipment, pipelines, and instrumentation
2. **Clarity**: Use clear symbols and labels
3. **Consistency**: Maintain uniform style throughout
4. **Proportions**: Keep equipment sizes realistic
5. **Annotations**: Add key parameters where needed (e.g., "10s delay", "HH interlock")

## Output Format

Final deliverable includes:
- Generated P&ID image file (PNG)
- Summary description of included elements
- Style information
- File path for user access

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Equipment not clear | Add more descriptive text in prompt |
| Lines too dense | Specify "minimalist" or "simplified" |
| Style too dark | Use "light" or "faint" modifier |
| Missing instruments | Explicitly list each instrument needed |
| Interlocks unclear | Add annotation text in prompt |

## References

See `references/pid-symbols.md` for standard P&ID symbols and conventions.
