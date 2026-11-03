---
name: heluo-interference-meta-model
description: Implements the HeLuo Coaxial Double Helix Interference Meta-Model. Use when users mention "HeLuo model", "interference meta", "64 hexagram phase", "double helix", "kernel-shell", "HeluoKernel", "HeluoShell", "HeluoInterferometer".
---

# HeLuo Coaxial Double Helix Interference Meta-Model

Engineering implementation based on I Ching 64 Hexagrams and financial physical phase detection.

## Architecture Overview

```
+-------------------------------------------------------------+
|                    Number 5 - Axis (Interference)            |
|                  HeluoInterferometer                        |
|              [ Kernel Tensor ⊗ Shell Tensor = Phase Diff ]   |
+-------------------------------------------------------------+
|        ↑ Attention Inner Product Coupling                   |
|  +-----+-----+                                             |
|  |  Kernel   |  Shell                                     |
|  | HeluoKernel| HeluoShell                                 |
|  | (River Map - Static) | (Luo Shu - Dynamic Spiral)       |
|  +-------------+                                           |
+-------------------------------------------------------------+
```

## Core Modules

### 1. HeluoKernel (Static Kernel Pool)

Stores immutable constants: fundamentals, macro anchors, alpha factors

### 2. HeluoShell (Dynamic Shell Pool)

Time-series spiral evolution, designed based on the irrationality of π

### 3. HeluoInterferometer (Interference Axis)

Core algorithm: inner product coupling for phase difference calculation

### 4. HeluoObserver (90-Degree Dimensionality Reduction)

Six-dimensional state output → 64 Hexagram mapping

### 5. HeluoAutoCalibrator (Adaptive Calibration)

Spiral slope fine-tuning to adapt to chaotic drift

## Usage

When user describes requirements, output complete Python implementation including:
- Complete class structure
- Interference calculation logic
- Hexagram mapping algorithm
- Running examples

## References

See `references/` directory
