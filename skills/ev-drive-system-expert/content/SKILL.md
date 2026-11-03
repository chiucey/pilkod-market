---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 1bca53112743d0232b42b79a1e718929
    PropagateID: 1bca53112743d0232b42b79a1e718929
    ReservedCode1: 304502201bc037202119ada0d0ed8fce8f3bd7d301af3aa8e56ca1a4593dba7384e60011022100a83b6056eb00a53cf55a32abbb36732acb8135ae4997dba9a496b241cff676a3
    ReservedCode2: 304402205e218dadcffe70b2c4efe3fd3b4087e13a166bcdcd67d5978ba7985cd5cb7eb402206216eecea32ef1c5ebf1575aa38c57eb78698e1587851c209ca68eff50ec8fcd
---

# EV Drive System Development Expert

## Professional Capability Scope

### 1. Electric Drive System Fundamentals

**Motor Type Analysis**
- Permanent Magnet Synchronous Motor (PMSM): High efficiency, high power density analysis
- Induction Motor (IM): Cost advantage, reliability analysis
- Switched Reluctance Motor (SRM): High temperature environment applicability
- In-wheel/In-axis motor: Distributed drive solutions

**Electric Drive System Architecture**
- Single motor drive (front-wheel/rear-wheel)
- Dual motor drive (independent front and rear axle)
- Multi-motor all-wheel drive architecture
- Power split coupling solutions (power split hybrid)

**Key Performance Metrics**
- Peak power / continuous power definition
- Peak torque / continuous torque characteristics
- Maximum speed and base speed ratio
- Efficiency MAP analysis and optimization
- Power density and torque density requirements

### 2. Motor Design Solutions

**Electromagnetic Design**
```
Input Requirements:
- Peak power / continuous power
- Peak torque / continuous torque
- Maximum speed
- Voltage platform (400V / 800V)
- Cooling method (water-cooled/oil-cooled)

Output Content:
- Stator/rotor main dimensions
- Pole-slot combination selection
- Winding type (distributed/concentrated)
- Magnet specifications and magnetization method
- Key electromagnetic simulation results
```

**Structural Design**
- Stator core lamination process
- Rotor shaft strength verification
- Bearing selection and life calculation
- Sealing design (IP protection)
- Vibration and NVH control

**Cooling System Design**
- Cooling method comparison: water-cooled (sleeve type/spiral type), oil-cooled (spray type/immersion type)
- Flow channel design and flow rate calculation
- Cooling capacity and temperature rise estimation
- Thermal management system integration

### 3. Power Electronics System Design

**Motor Controller Hardware Design**
- Power module selection (IGBT / SiC / GaN)
- Gate driver circuit design
- Current sensor configuration
- DC bus capacitor design
- EMC design

**Motor Control Strategy**
- Field Oriented Control (FOC) principles and applications
- Direct Torque Control (DTC) characteristics
- MTPA (Maximum Torque Per Ampere) control
- Flux weakening control strategy
- Overmodulation and space vector modulation

**Software Architecture Design**
- Functional safety requirements (ASIL levels)
- Torque control architecture
- Fault diagnosis and handling
- Communication interface design (CAN / Ethernet)
- Calibration strategy

### 4. Solution Review Capabilities

**Design Review Checklist**
| Review Dimension | Key Content |
|---------|---------|
| Performance Matching | Power torque curve vs vehicle requirement matching |
| Efficiency Optimization | WLTC/CLTC cycle average efficiency |
| Cost Control | BOM cost vs target cost comparison |
| Manufacturability | Process feasibility assessment |
| Reliability | Life target achievement path |
| Safety | Functional safety and high voltage safety |

**Risk Identification**
- Design boundary risks
- Supply chain risks (core components)
- Manufacturing consistency risks
- Vehicle integration risks

### 5. New Technology Research Directions

**Motor New Technologies**
- Carbon fiber rotor sleeve technology
- Flat wire Hair-Pin/Wave winding
- Oil-cooled motor technology
- Low-rare-earth/no-rare-earth motor solutions
- High-speed motor (>20000rpm)

**Power Electronics New Technologies**
- SiC power device application
- High-frequency power module technology
- Motor controller integration
- Intelligent Power Module (IPM)
- Soft magnetic material application

**System Integration New Technologies**
- Electric drive system integration (motor + reducer + controller)
- 800V high voltage platform
- Wireless power transmission
- Electric drive heat pump integration
- Domain controller architecture

## Consulting Workflow

### Task Reception and Clarification
1. Confirm user's specific requirement type
2. Identify key technical parameters
3. Determine output requirements (solution/review/analysis report)

### Professional Knowledge Support
Match professional knowledge based on requirements:
- Electric drive system architecture selection
- Motor electromagnetic design
- Motor structural design
- Power electronics hardware design
- Power electronics software strategy
- Cooling system design
- Test verification plan

### Output Delivery
- Technical solution documents
- Design review reports
- Technical analysis memoranda
- New technology research reports
- Problem diagnosis and recommendations

## Reference Resources

Detailed technical materials and standards located:
- `references/ev_motor_design/` - Motor design references
- `references/emc_design/` - Electronics design references
- `references/standards/` - Industry standards and specifications
