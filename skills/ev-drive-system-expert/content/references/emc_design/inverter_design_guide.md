# Power Electronics System Design Reference

## 1. Motor Controller Architecture

### 1.1 System Architecture Overview

```
Power Electronics System Components:
├── Power Conversion Unit
│   ├── DC Bus Capacitor
│   ├── IGBT/SiC Power Module
│   └── Gate Driver Circuit
├── Control Unit
│   ├── Main Control Chip (DSP/MCU)
│   ├── Position Sensor Interface
│   └── Communication Interface
├── Sensor Unit
│   ├── Current Sensor
│   ├── Voltage Sensor
│   └── Temperature Sensor
└── Protection Unit
    ├── Overcurrent Protection
    ├── Overvoltage Protection
    └── Short Circuit Protection
```

### 1.2 Power Module Selection

#### IGBT vs SiC Comparison

| Parameter | IGBT | SiC MOSFET |
|------|------|------------|
| Voltage rating | 650V/1200V | 650V/1200V/1700V |
| Switching loss | High | Low (reduced 60-80%) |
| Conduction loss | Medium | Low |
| Operating frequency | 2-10kHz | 10-50kHz |
| High temp performance | Average | Excellent |
| Cost | Low | High (2-3x) |
| Thermal resistance | Medium | Low |

#### Selection Calculation

```
Power Module Selection Steps:
1. Determine voltage level
   V_max = V_bus × 1.2 + switching overvoltage

2. Determine current rating
   I_cont = P_out / (√3 × V_bus × η × PF)
   I_peak = I_cont × 2~3 (overload factor)

3. Thermal loss estimation
   P_loss = P_cond + P_switch
   - Conduction loss: related to Rdson and duty cycle
   - Switching loss: related to Eon/Eoff and switching frequency

4. Heat dissipation design
   R_th(jc) = (T_j - T_case) / P_loss
```

### 1.3 DC Bus Capacitor Design

**Capacitance Calculation**
```
C_min = (I_load × t_sw) / ΔV_bus

Where:
I_load - Load current
t_sw - Switching period
ΔV_bus - Allowable voltage ripple (typically 5%)

Empirical formula:
C (μF) = (P_out × 1000) / (2 × V_bus² × f_sw)
```

**Capacitor Selection Key Points**
- Low ESR (Equivalent Series Resistance)
- Low ESL (Equivalent Series Inductance)
- High ripple current capability
- Stable temperature characteristics
- Life meets requirements (automotive: 5000h@125°C)

## 2. Motor Control Strategy

### 2.1 Coordinate Transformation

**Clarke Transformation**
```
[ia]   [1    -1/2      -1/2    ] [iα]
[ib] = [0   √3/2      -√3/2   ] [iβ]
[ic]   [1/2   1/2       1/2    ] [i0]
```

**Park Transformation**
```
[id]   [cosθ   sinθ] [iα]
[iq] = [-sinθ  cosθ] [iβ]
```

### 2.2 FOC Vector Control

**Control Block Diagram**
```
Setpoint          Measured
  │                  │
  ▼                  ▼
┌──────┐        ┌────────┐
│MTPA  │        │Coordinate│
│      ─┼──────│Transform │
└──────┘        └────────┘
                     │
                     ▼
                ┌────────┐
                │Current │
                │Loop PI │
                │Id*, Iq*│
                └────────┘
                     │
                     ▼
                ┌────────┐
                │SVPWM   │
                │Space   │
                │Vector  │
                └────────┘
                     │
                     ▼
                ┌────────┐
                │Inverter│
                │Power  │
                │Device │
                └────────┘
```

**Key Parameter Tuning**
| Loop | Bandwidth | Typical Time Constant |
|------|---------|-------------|
| Current loop | 500-1000Hz | 0.5-1ms |
| Speed loop | 50-100Hz | 5-10ms |
| Torque loop | Following current loop | - |

### 2.3 Flux Weakening Control

**Flux Weakening Principle**
When motor speed exceeds base speed, adjust Id (demagnetizing current) to weaken air gap flux, achieving flux weakening speed increase.

```
Flux weakening condition:
ω > ω_base = V_dc / (√3 × ψ_f)

Voltage limit circle:
V_sd² + V_sq² ≤ (V_dc/√3)²
```

**Flux Weakening Control Strategies**
1. **Current feedback flux weakening**: Id = (V_dc/√3 - V_s) / ωL
2. **Advance angle flux weakening**: Calculate flux weakening current through lookup table or formula
3. **MTPA + flux weakening**: Comprehensive efficiency and output capability optimization

### 2.4 Overmodulation Technology

**Modulation Method Comparison**
| Modulation | Modulation Ratio | Voltage Utilization | Harmonic Content |
|---------|--------|-----------|---------|
| Linear (SVPWM) | 0-0.907 | 100% | Low |
| Overmodulation | 0.907-1.0 | Increased | Medium |
| Square wave | 1.0 | Maximum | High |

**Transition Strategy**
```
Modulation strategy selection:
┌─────────────────┐
│  Normal region   │  SVPWM modulation
│    (M ≤ 0.9)     │
├─────────────────┤
│  Overmodulation1 │  Overmodulation SVPWM
│  (0.9 < M < 0.95)│
├─────────────────┤
│  Overmodulation2 │  Square wave transition
│  (0.95 < M < 1.0)│
├─────────────────┤
│  Max speed region│  Square wave control
│    (M = 1.0)     │
└─────────────────┘
```

## 3. Functional Safety Design

### 3.1 ASIL Level Requirements

| Safety Goal | ASIL | Diagnostic Coverage | Hardware Metrics |
|---------|------|-----------|---------|
| Motor torque loss of control | ASIL D | ≥90% | SPFM≥97%, LFM≥90% |
| Motor unexpected stop | ASIL B | ≥60% | - |
| Communication failure | ASIL B | ≥60% | - |

### 3.2 Safety Mechanisms

**Hardware Protection**
- Hardware overcurrent protection (two levels: fast + slow)
- DC bus overvoltage/undervoltage protection
- Power module overtemperature protection
- Position sensor failure detection

**Software Protection**
- Torque correlation check
- Current limiting protection
- Fault state machine management
- Watchdog monitoring

### 3.3 Fault Diagnosis Matrix

| Fault Type | Detection Method | Handling Strategy | Fault Tolerance |
|---------|---------|---------|---------|
| Current sensor fault | Hardware redundancy/estimation | Limp home | Yes |
| Position sensor fault | Estimation/model observer | Degraded operation | Yes |
| Power module fault | Temperature/current detection | Shutdown protection | Partial |
| DC bus fault | Voltage detection | Fast discharge | No |

## 4. EMC Design

### 4.1 EMC Requirements

| Test Item | Standard | Limit Requirement |
|---------|------|---------|
| Conducted emission | CISPR 25 | Class 5 |
| Radiated emission | CISPR 25 | Class 5 |
| Conducted immunity | ISO 11452-4 | 100mA |
| Radiated immunity | ISO 11452-2 | 100V/m |

### 4.2 EMC Design Measures

**Switching Device Design**
```
Key measures:
1. Gate drive optimization
   - Add gate resistance (RG_on/RG_off separated)
   - Soft turn-off technology
   - Active clamping

2. Snubber circuit
   - DC bus RC snubber
   - IGBT RCD snubber
   - SiC dedicated snubber

3. Layout and wiring
   - Minimize power loop
   - Separate drive signals from power loop
   - Ground plane integrity
```

**EMI Filter Design**
```
EMI filter topology:
┌─────────────────────────────────┐
│                                 │
│    L1         L2                │
│ ──┤ ├────┤ ├───┤                │
│         C1       C2    ── GND   │
│ ──┴───────┴─────┴──             │
│                                 │
└─────────────────────────────────┘

Selection principles:
- Common mode inductor: high frequency MnZn ferrite
- Differential mode inductor: small inductance, low DCR
- X capacitor: film capacitor, 1.5kV rating
- Y capacitor: safety capacitor, low leakage current
```

## 5. Thermal Design

### 5.1 Loss Calculation

```
Total loss = Conduction loss + Switching loss + Drive loss

1. Conduction loss
   P_cond = I² × Rds_on × D

2. Switching loss (IGBT)
   P_sw = (E_on + E_off) × f_sw × I_avg/I_ref

3. Switching loss (SiC)
   P_sw = (E_on + E_off + E_rr) × f_sw
```

### 5.2 Heat Dissipation Design

```
Thermal resistance network:
junction → case → TIM → heatsink → ambient

Design flow:
1. Determine maximum allowable junction temperature (Tj_max, typically 150°C)
2. Estimate ambient temperature (Tamb, typically 85°C)
3. Calculate allowable thermal resistance
   R_th(ja) = (Tj_max - Tamb) / P_loss
4. Distribute thermal resistance
   R_th(jc) + R_th(ct) + R_th(cs) + R_th(sa) ≤ R_th(ja)
```

## 6. Design Checklist

### 6.1 Hardware Design Check

- [ ] Power module selection meets current/voltage requirements
- [ ] DC bus capacitor capacity sufficient
- [ ] Gate driver circuit design reasonable
- [ ] Current sensor accuracy meets requirements
- [ ] PCB layout meets EMC requirements
- [ ] Thermal design meets heat dissipation requirements
- [ ] Protection circuit complete and effective

### 6.2 Software Design Check

- [ ] FOC control algorithm implementation correct
- [ ] MTPA/flux weakening logic complete
- [ ] Torque response meets requirements
- [ ] Fault diagnosis coverage comprehensive
- [ ] Functional safety requirements achieved
- [ ] Calibration interface complete
