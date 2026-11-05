# P&ID Symbol Reference Guide

Standard P&ID symbols and conventions for process instrumentation diagrams.

## Equipment Symbols

### Tanks & Vessels

| Equipment | Symbol | Description |
|-----------|--------|-------------|
| Storage Tank | Cylindrical vessel, flat or dished ends | Vertical or horizontal |
| Reactor | Cylindrical vessel with agitator symbol | May include heating/cooling jacket |
| Weighing Tank | Cylindrical vessel with load cell base | Weight measurement underneath |
| Surge Tank | Cylindrical vessel | Level control common |
| Mixers | Tank with mixer symbol | Top-mounted agitator |

### Pumps

| Equipment | Symbol | Description |
|-----------|--------|-------------|
| Centrifugal Pump | Circle with triangle | Single stage, most common |
| Positive Displacement | Circle with rectangle | Lobe, gear, screw pumps |
| Diaphragm Pump | Circle with membrane symbol | Batch transfer applications |
| Peristaltic Pump | Circle with rollers | hygienic applications |
| Vacuum Pump | VP in circle | Negative pressure systems |

### Heat Exchangers

| Equipment | Symbol | Description |
|-----------|--------|-------------|
| Shell & Tube | Two parallel lines with cross marks | Counter/current flow |
| Plate Heat Exchanger | Stacked plate symbol | Compact design |
| Kettle Reboiler | Vessel with draft tube | Level indication needed |
| Air Cooler | Rectangle with fins | Fan symbol optional |
| Fired Heater | Box with flame symbol | Direct fired |

### Valves

| Equipment | Symbol | Description |
|-----------|--------|-------------|
| Gate Valve | Two triangles pointing outward | On/off service |
| Ball Valve | Circle with line through | Quick acting |
| Globe Valve | Two triangles pointing inward | Throttling |
| Check Valve | Triangle pointing one direction | Backflow prevention |
| Control Valve | Circle with hourglass shape | Modulating control |
| Safety Valve | Half circle with spring | Overpressure protection |
| Butterfly Valve | Circle with diagonal line | Large diameter |

## Instrumentation Symbols

### Instrument Shapes

| Shape | Meaning | Example |
|-------|---------|---------|
| Circle | Display only (local) | TI, PI |
| Square | Control function | TIC, PIC |
| Diamond | Switch or alarm | TSHH, PSH |
| Hexagon | Computer function | DCS |
| Double circle | Primary element | FT, PT |

### Common Instruments

| Tag | Name | Description |
|-----|------|-------------|
| TT | Temperature Transmitter | Measures temperature, outputs 4-20mA |
| PT | Pressure Transmitter | Measures pressure |
| FT | Flow Transmitter | Measures flow rate |
| LT | Level Transmitter | Measures level |
| WT | Weight Transmitter | Measures weight/load |
| TI | Temperature Indicator | Local temperature display |
| PI | Pressure Indicator | Local pressure gauge |
| FI | Flow Indicator | Local flow display |
| LI | Level Indicator | Local level gauge |
| WI | Weight Indicator | Local weight display |

### Control Functions

| Tag | Name | Description |
|-----|------|-------------|
| TIC | Temperature Indicator Controller | Display + control temperature |
| PIC | Pressure Indicator Controller | Display + control pressure |
| FIC | Flow Indicator Controller | Display + control flow |
| LIC | Level Indicator Controller | Display + control level |
| WIC | Weight Indicator Controller | Display + control weight |

### Alarms & Interlocks

| Tag | Meaning | Action |
|-----|---------|--------|
| TSHH | Temperature Switch High-High | Shutdown on very high temp |
| THH | Temperature High-High | Trip at high temperature |
| PSHH | Pressure Switch High-High | Shutdown on very high pressure |
| PHH | Pressure High-High | Trip at high pressure |
| PAL | Pressure Alarm Low | Alert on low pressure |
| LSHH | Level Switch High-High | Shutdown on high level |
| LALL | Level Alarm Low-Low | Alert on very low level |
| WSHH | Weight Switch High-High | Shutdown on high weight |

## Line Types

| Line Type | Meaning | Usage |
|-----------|---------|-------|
| Solid thick | Process piping | Primary process streams |
| Solid thin | Instrument impulse lines | Pressure, level connections |
| Dashed thin | Pneumatic signal | Air supply to valves |
| Dotted thin | Electrical signal | cables |
| Long dash short dash | Hydraulic signal | High pressure hydraulic |
| Zigzag | Capacitor signal | Radio/telemetry |

## Line Connections

| Connection | Symbol | Usage |
|-----------|--------|-------|
| Flanged | Filled circle at junction | Permanent, high pressure |
| Screwed | Small filled circle | Low pressure, temporary |
| Welded | Filled square at junction | Permanent, no maintenance |
| Mechanical joint | Filled semicircle | Flexible connection |

## Actuator Types

| Type | Symbol | Description |
|------|--------|-------------|
| Electric | Motor symbol attached | Most common |
| Pneumatic | Diaphragm spring symbol | Instrument air |
| Solenoid | Coil symbol | On/off operation |
| Manual | Hand wheel symbol | No automation |
| Solenoid + Pneumatic | Combined symbols | Fail-safe control |
| electrohydraulic | Combined electric/pneumatic | Precision control |

## Control Logic Symbols

| Symbol | Meaning | Usage |
|--------|---------|-------|
| AND | Logic gate | All conditions must be met |
| OR | Logic gate | Any condition triggers |
| NOT | Inversion | Opposite logic |
| TD | Time Delay | Delayed action |
| LAS | Logic Auto Select | Redundant system control |

## Common P&ID Abbreviations

| Abbreviation | Full Term | Meaning |
|-------------|-----------|---------|
| P&ID | Piping and Instrumentation Diagram | Process design drawing |
| UOM | Unit of Measure | Engineering units |
| HH | High High | Highest alarm/shutdown |
| LL | Low Low | Lowest alarm/shutdown |
| H | High | High alarm |
| L | Low | Low alarm |
| S | Switch | Binary on/off signal |
| A | Alarm | Audible/visible alert |
| T | Transmitter | Continuous measurement |
| I | Indicator | Local display |
| C | Controller | Control function |

## Example Tag Numbers

| Tag | Full Tag | Meaning |
|-----|----------|---------|
| TT-101 | Temperature Transmitter 101 | First temperature measurement |
| TIC-101 | Temperature Indicating Controller 101 | First temp control loop |
| TT-101A/B | Temperature Transmitter 101 A/B | Redundant measurements |
| PV-101 | Process Variable 101 | Controlled variable |
| SP-101 | Set Point 101 | Desired value |
| OP-101 | Output 101 | Controller output signal |
| FIC-101 | Flow Indicating Controller 101 | First flow control loop |
| WSHH-101 | Weight Switch High High 101 | Weight shutdown |

## Best Practices

1. **Tag Numbering**: Use sequential numbering for similar instruments
2. **Line Sizing**: Show relative sizes but maintain readability
3. **Flow Direction**: Always show flow direction arrows
4. **Instrument Placement**: Primary instruments on left/top, controls on right/bottom
5. **Interlock Labels**: Always label shutdown conditions clearly
6. **Coordinate with PFD**: P&ID should match process flow diagram
7. **Include Utilities**: Show instrument air, power, seal water
8. **Version Control**: Keep drawings updated with process changes
