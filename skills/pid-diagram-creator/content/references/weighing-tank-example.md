# P&ID Example: Weighing Tank System

Complete P&ID specification for a weighing tank with diaphragm pump transfer to reactor.

## Process Description

A weighing tank (weighing vessel) with load cells is used to batch transfer liquid to a reactor. The tank has flat top and flat bottom cylindrical design. Material exits from the bottom of the tank and is transferred via an electric diaphragm pump to a reactor vessel through a top entry nozzle.

## Equipment List

| Equipment ID | Description | Key Features |
|--------------|-------------|---------------|
| TK-101 | Weighing Tank | Flat top/bottom cylindrical vessel |
| LC-101 | Load Cells | Weight measurement, 3-point support |
| P-101 | Diaphragm Pump | Electric motor driven |
| R-101 | Reactor | Vertical cylindrical vessel |

## Instrumentation List

| Tag | Description | Location | Function |
|-----|-------------|----------|----------|
| WT-101 | Weight Transmitter | Tank LC-101 | Measure tank weight |
| WI-101 | Weight Indicator | Control Room | Display weight |
| LALL-101 | Level Alarm Low-Low | Tank | Low level shutdown |
| LAHH-101 | Level Alarm High-High | Tank | High level shutdown |
| TT-101 | Temperature Transmitter | Pump discharge line | Measure temperature |
| THH-101 | Temperature High-High | TT-101 output | Temperature shutdown |
| PT-101 | Pressure Transmitter | Pump discharge line | Measure pressure |
| PHH-101 | Pressure High-High | PT-101 output | High pressure shutdown |
| PAL-101 | Pressure Alarm Low | PT-101 output | Low pressure alarm |
| PSL-101 | Pressure Switch Low | PT-101 output | Low pressure shutdown |

## Control Logic

### Weight Control Loop

```
WT-101 → WIC-101 → Pump P-101 Start/Stop
         ↓
    Weight Setpoints:
    - High Stop (LAHH): Stop pump when tank empty
    - Low Start (LALL): Start pump when tank filled
```

### Interlock Logic

#### Temperature High (THH-101)
- **Condition**: Temperature > SHUTDOWN_SETPOINT
- **Action**: Stop pump P-101 immediately
- **Reset**: Manual reset required

#### Pressure High (PHH-101)
- **Condition**: Pressure > SHUTDOWN_SETPOINT
- **Action**: Stop pump P-101 immediately
- **Reset**: Manual reset required

#### Pressure Low (PSL-101) with 10s Delay
- **Condition**: Pressure < LOW_SETPOINT for > 10 seconds
- **Action**: Stop pump P-101
- **Logic**: Timer starts on pump startup, interlock enabled after 10s
- **Purpose**: Prevent nuisance trip on initial pump startup

### Pump Control Philosophy

1. **Auto Mode**: WIC-101 controls pump based on weight
2. **Manual Mode**: Operator can start/stop pump from control room
3. **Interlock Override**: All interlocks can stop pump regardless of mode

## P&ID Generation Prompts

### Style 1: Pencil Sketch

```
Pencil sketch P&ID diagram, hand-drawn with light gray strokes:
- Weighing tank TK-101: Cylindrical vessel with flat top and flat bottom, load cells LC-101 underneath measuring weight, bottom outlet at lowest point, simple line art
- Electric diaphragm pump P-101: Connected to tank bottom outlet via pipe, pump shown with diaphragm symbol and electric motor
- Process pipeline: From pump discharge to reactor R-101, with flow direction arrow
- Reactor vessel R-101: Receiving material via pipeline, top inlet nozzle for receiving material
- Temperature transmitter TT-101: On pipeline between pump and reactor, with THH interlock to stop pump on high temperature
- Pressure transmitter PT-101: On pipeline between pump and reactor, with PHH interlock to stop pump on high pressure and PAL interlock on low pressure
- Low pressure interlock PSL-101: Enabled 10 seconds after pump startup (标注: 10s delay)
- Weight transmitter WT-101: Connected to load cells LC-101, weight control loop (WIC-101) controlling pump start/stop based on tank level
- Dashed lines showing instrument signal connections
- Simple minimalist pencil sketch, clean technical line drawing, light gray strokes on white background
```

### Style 2: Ink Pen

```
Ink pen P&ID diagram, bold black line technical drawing style:
- Weighing tank TK-101: Cylindrical vessel with flat top and flat bottom, load cells LC-101 underneath measuring weight, bottom outlet at lowest point
- Electric diaphragm pump P-101: Connected to tank bottom outlet via pipe, pump shown with diaphragm symbol and electric motor, bold ink strokes
- Process pipeline: From pump discharge to reactor R-101, with bold flow direction arrow
- Reactor vessel R-101: Receiving material via pipeline, top inlet nozzle for receiving material
- Temperature transmitter TT-101: On pipeline between pump and reactor, with THH interlock to stop pump on high temperature, circle symbol with TT label
- Pressure transmitter PT-101: On pipeline between pump and reactor, with PHH interlock and PAL interlock, circle symbol with PT label
- 10 second time delay relay: On PSL-101 low pressure interlock, labeled "10s delay after pump start"
- Weight transmitter WT-101: Connected to load cells LC-101, weight control loop WIC-101 controlling pump start/stop
- Dashed lines for instrument signals
- Bold black ink pen strokes, clean technical drawing, professional blueprint aesthetic, black lines on white background
```

### Style 3: Ballpoint Pen

```
Ballpoint pen P&ID diagram, blue ink casual sketch style:
- Weighing tank TK-101: Cylindrical vessel with flat top and flat bottom, load cells LC-101 underneath, bottom outlet, casual ballpoint sketch strokes
- Electric diaphragm pump P-101: Connected to tank bottom outlet, pump with diaphragm symbol and motor, ballpoint pen style
- Process pipeline: From pump to reactor R-101, flow arrow in blue ink
- Reactor vessel R-101: Top inlet nozzle receiving material from pump
- Temperature transmitter TT-101: With THH interlock to stop pump, blue ballpoint circle symbol
- Pressure transmitter PT-101: With PHH and PAL interlocks, blue ballpoint circle symbol
- 10s time delay: On low pressure interlock, casual hand annotation "10s delay"
- Weight transmitter WT-101: Weight control loop WIC-101, blue ballpoint lines
- Varying line weights typical of ballpoint pen, informal technical sketch, blue ink on white paper
```

## Drawing Layout

```
         +---------------+
         |  TK-101      |
    LT   | Weighing     | LT
   [ ]---|  Tank        |---[ ]
         |   |          |
         |   V (outlet) |
         +---|----------+
             |
             | Pipe
             V
         +-------+
         | P-101 |---(M)--- PUMP
         |Diaph. |
         +---+---+
             |
    TT---[ ] | PT---[ ]
             |
             | Pipeline
             V
         +---|----------------+
         |   V                |
         |  +---+              |
         |  |R-101|            |
    TI---[ ]|Reactor|<--------+
         |  +---+  (top inlet)|
         |             |
         +-------------+

         LC-101 (load cells)
         [===] [===] [===]
         Three-point weighing

LEGEND:
[ ] = Transmitter
(M) = Motor
V   = Flow direction
--- = Pipeline
--- = Instrument signal (dashed)
```

## Instrument Details

### Weight Measurement (WT-101)
- **Type**: Load cell based weight transmitter
- **Range**: 0-100% of tank capacity
- **Output**: 4-20mA to WIC-101
- **Accuracy**: ±0.1% of full scale

### Temperature Measurement (TT-101)
- **Type**: RTD or thermocouple
- **Range**: 0-150°C (typical)
- **THH Setpoint**: Process dependent (e.g., 80°C)
- **Location**: Pump discharge line, 1m from pump

### Pressure Measurement (PT-101)
- **Type**: Pressure transmitter
- **Range**: 0-10 bar (typical)
- **PHH Setpoint**: Design pressure - 10%
- **PAL Setpoint**: Minimum operating pressure
- **PSL Delay**: 10 seconds after pump start
- **Location**: Pump discharge line

## Operator Interface

### Control Room Displays
- Current tank weight (WI-101)
- Pump status (running/stopped)
- Line temperature (TI-101)
- Line pressure (PI-101)
- Active alarms
- Interlock status

### Alarm Panel
- High temperature alarm
- High pressure alarm
- Low pressure alarm
- Low level alarm
- Pump fault

## Safety Considerations

1. **Overpressure Protection**: Relief valve on pump discharge
2. **Temperature High**: THH interlock stops pump
3. **Pressure High**: PHH interlock stops pump
4. **Pressure Low**: PSL interlock (delayed) prevents dry running
5. **Weight Low**: LALL prevents pump running dry
6. **Emergency Stop**: Local and remote ESD buttons
