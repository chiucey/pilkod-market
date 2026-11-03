# Motor Design Fundamentals Reference

## 1. Motor Type Selection

### 1.1 Permanent Magnet Synchronous Motor (PMSM)

**Characteristics**
- High efficiency (>95%)
- High power density
- High torque density
- Wide speed regulation range

**Application Scenarios**
- High-end passenger vehicles
- High-performance models
- Applications requiring high efficiency

**Design Key Points**
```
Key Parameter Ranges:
- Pole count: 6~12 poles (8 poles common for passenger vehicles)
- Slot count: 24/36/48/54 slots
- Pole-slot combination: common 2:3 (8-pole 36-slot), 4:5 (8-pole 10-slot)
- Air gap flux density: 0.8~1.2T
- Magnet: NdFeB N42SH/N45UH grade
```

### 1.2 Induction Motor (IM)

**Characteristics**
- Lower cost
- Simple and reliable structure
- No permanent magnets (no demagnetization risk)
- Suitable for high-speed operation

**Application Scenarios**
- Mid-to-low-end vehicles
- High-speed operating conditions
- Cost-sensitive applications

### 1.3 Switched Reluctance Motor (SRM)

**Characteristics**
- Extremely simple structure (rotor without windings/magnets)
- Excellent high-temperature performance
- High reliability
- Great cost potential

**Design Challenges**
- Torque ripple control
- Noise suppression
- Complex control system

## 2. Electromagnetic Design Core Formulas

### 2.1 Basic Dimension Equation

```
D²L = (6.1 × P × 10³) / (η × B × A × n × K)

Where:
D - Armature diameter (m)
L - Armature length (m)
P - Power (W)
η - Efficiency
B - Air gap flux density (T)
A - Line loading (A/m)
n - Speed (rpm)
K - Winding factor
```

### 2.2 Pole-Slot Combination Selection Principles

| Consideration | Recommended Selection |
|---------|---------|
| Slot fill factor | Concentrated > Distributed |
| Cogging torque | Fractional slot > Integer slot |
| NVH performance | More slots is better |
| Winding end | Concentrated end is shorter |
| Manufacturing process | Distributed is mature |

**Common Pole-Slot Combinations**
- 8-pole 36-slot (Recommended: low cogging torque, good NVH)
- 8-pole 48-slot (Standard: mature process)
- 6-pole 36-slot (Cost-optimized solution)
- 10-pole 12-slot (High-speed low-torque scenarios)

### 2.3 Magnet Design

**Magnet Thickness Calculation**
```
t_m = (μ_r × g) / (B_r/B_g - 1)

Where:
t_m - Magnet thickness
μ_r - Relative permeability
g - Air gap length
B_r - Residual flux density
B_g - Air gap flux density
```

**Magnet Grade Selection**
| Grade | Residual (T) | Coercivity (kA/m) | Max Temp (°C) | Application |
|------|--------|-------------|-------------|---------|
| N42SH | 1.3 | 955 | 150 | Standard |
| N45UH | 1.4 | 980 | 180 | High temp |
| N50AH | 1.45 | 900 | 200 | Oil-cooled |

## 3. Cooling System Design

### 3.1 Cooling Method Comparison

| Cooling Method | Heat Dissipation | Complexity | Cost | Application |
|---------|---------|--------|------|---------|
| Natural air | Low | Simple | Low | Low power motors |
| Forced air | Medium | Medium | Medium | Medium power |
| Water-cooled (sleeve) | High | Medium | Medium | Mainstream passenger |
| Water-cooled (spiral) | High | Medium | Medium-high | High-end models |
| Oil-cooled (spray) | Very high | Complex | High | High performance |
| Oil-cooled (immersion) | Highest | Complex | High | 800V platform |

### 3.2 Water Cooling Design Key Points

```
Design Flow:
1. Heat generation calculation
   Q = P × (1 - η)

2. Flow rate calculation
   Q_cool = Q / (ρ × Cp × ΔT)

3. Flow channel design
   - Cross-sectional area: ensure flow velocity 1~3m/s
   - Sealing: O-ring or sealant

4. Pressure drop verification
   ΔP = λ × (L/d) × (ρv²/2)
```

## 4. Key Performance Optimization

### 4.1 Efficiency MAP Optimization

**High Efficiency Region Distribution Principles**
- Common operating points at center of high efficiency region
- High-speed region optimized through flux weakening
- Low-speed region optimized through MTPA

**Optimization Measures**
1. Pole-slot combination optimization (reduce harmonics)
2. Slot shape optimization (reduce end leakage)
3. Magnet shape optimization (reduce cogging torque)
4. Winding distribution optimization (reduce AC copper loss)

### 4.2 NVH Control

**Main Vibration Sources**
- Cogging torque
- Electromagnetic force waves
- Rotor imbalance

**Control Measures**
```
Design Phase:
- Fractional slot combinations (reduce low-order force waves)
- Skewed slots/skewed poles (reduce slot harmonics)
- Closed stator slots (reduce air gap permeance variation)

Analysis Tools:
- Electromagnetic simulation (Maxwell/JMAG)
- Vibration simulation (OptiStruct)
- Structural optimization
```

## 5. Design Checklist

### 5.1 Solution Design Check

- [ ] Power torque meets vehicle requirements
- [ ] Efficiency MAP meets operating conditions
- [ ] Pole-slot combination reasonable (no abnormal vibration risk)
- [ ] Magnet selection meets temperature requirements
- [ ] Cooling capacity sufficient
- [ ] Bearing life meets requirements
- [ ] BOM cost controllable

### 5.2 Engineering Check

- [ ] Assemblability (winding insertion/insertion process)
- [ ] Manufacturability (process stability)
- [ ] Quality controllability (detection methods)
- [ ] Supply chain reliability (core materials)
