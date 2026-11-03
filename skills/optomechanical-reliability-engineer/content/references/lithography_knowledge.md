# 光刻机专业知识库

## 1. 光刻技术概述

### 1.1 光刻工艺流程

```
晶圆光刻工艺流程：

┌──────────────────────────────────────────────────────────┐
│                                                           │
│  晶圆预处理 ──→ 涂胶 ──→ 前烘 ──→ 对准曝光 ──→ 显影 ──→ 后烘 ──→ 刻蚀 ──→ 去胶 │
│                                                           │
└──────────────────────────────────────────────────────────┘

各步骤详解：
├── 预处理: 去除表面杂质、水汽，确保光刻胶良好附着
├── 涂胶: 匀胶机Spin Coater将光刻胶均匀涂覆(厚度100nm-1μm)
├── 前烘(Soft Bake): 去除溶剂，稳定光刻胶膜(90-100°C, 60-120s)
├── 对准曝光: 掩模版与晶圆精密对准，紫外光照射
├── 显影(Development): 化学溶液溶解曝光/未曝光区域
├── 后烘(Hard Bake): 固化图案，提高抗刻蚀性(110-130°C)
├── 刻蚀: 图案转移到下层材料(干法/湿法刻蚀)
└── 去胶(Strip): 去除残余光刻胶
```

### 1.2 光刻分辨率公式

```python
class LithographyFundamentals:
    """光刻基础知识"""

    # Rayleigh分辨率公式
    # R = k1 × λ / NA

    # 工艺因子k1 (与工艺能力相关)
    # 传统光刻: k1 ≈ 0.61
    # 先进工艺: k1 ≈ 0.25-0.40
    # 理论极限: k1 ≈ 0.25

    @staticmethod
    def resolution(lambda_nm, NA, k1=0.4):
        """
        光刻分辨率计算

        参数：
        - lambda_nm: 光源波长 [nm]
        - NA: 数值孔径
        - k1: 工艺因子 (典型值0.25-0.61)

        返回：
        - 最小可分辨线宽 [nm]
        """
        return k1 * lambda_nm / NA

    @staticmethod
    def depth_of_focus(lambda_nm, NA, k2=0.5):
        """
        焦深(DOF)计算

        DOF = k2 × λ / NA²

        参数：
        - k2: 焦深因子 (典型值0.25-1.0)
        """
        return k2 * lambda_nm / (NA ** 2)

    @staticmethod
    def numerical_aperture(object_side, image_side=None):
        """
        数值孔径计算

        NA = n × sin(θ)

        参数：
        - n: 介质折射率
        - θ: 最大入射角的一半
        - object_side: 物方NA
        - image_side: 像方NA (对系统放大率)
        """
        # 物方NA与像方NA的关系
        if image_side is not None:
            magnification = object_side / image_side
            return image_side * (1 + magnification)
        return object_side
```

### 1.3 光刻机代际演进

| 代际 | 节点(nm) | 光源 | 波长 | NA | 套刻精度 | 产出(WPH) |
|-----|---------|------|------|-----|---------|----------|
| i-line | 500+ | Hg lamp | 365nm | 0.28-0.45 | 50-100nm | 50-100 |
| KrF | 350-180 | KrF激光 | 248nm | 0.50-0.73 | 20-50nm | 100-150 |
| ArF Dry | 130-65 | ArF激光 | 193nm | 0.75-0.93 | 5-15nm | 100-200 |
| ArF Immersion | 45-7 | ArF激光 | 193nm | 1.0-1.35 | 2-5nm | 200-300 |
| EUV | 7-3 | EUV光源 | 13.5nm | 0.25-0.33 | 1-2nm | 100-200 |

---

## 2. 光刻机系统架构

### 2.1 整机布局

```
典型浸没式光刻机系统布局：

┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   ┌─────────┐                                                 │
│   │ 照明系统 │                                                 │
│   │ (Illum) │                                                 │
│   └────┬────┘                                                 │
│        │                                                      │
│   ┌────▼────┐        ┌─────────┐        ┌─────────┐          │
│   │ 掩模台   │◄───────│ 掩模    │───────►│ 工件台   │          │
│   │(Mask    │        │ 传输    │        │ (Wafer  │          │
│   │ Stage)  │        │ (LMC)   │        │  Stage) │          │
│   └────┬────┘        └─────────┘        └────┬────┘          │
│        │                                      │               │
│        │         ┌─────────┐                  │               │
│        └────────►│ 投影物镜 │◄────────────────┘               │
│                  │ (Projection│                               │
│                  │   Lens)   │                               │
│                  └─────────┘                                 │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    环境控制系统                          │  │
│  │  • 温控精度: ±0.01°C                                    │  │
│  │  • 振动隔离: 5μm/s² @1-100Hz                           │  │
│  │  • 洁净度: ISO Class 1                                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 照明系统

```python
class IlluminationSystem:
    """照明系统设计参数"""

    # 光源类型对比
    LIGHT_SOURCES = {
        'ArF': {
            'wavelength': 193.368,  # nm
            'bandwidth': 0.003,  # nm (深紫外)
            'power': 90,  # W (典型值)
            'lifetime': 5000,  # hours
            'type': 'Excimer Laser'
        },
        'KrF': {
            'wavelength': 248.4,  # nm
            'bandwidth': 0.003,  # nm
            'power': 60,  # W
            'lifetime': 10000,  # hours
            'type': 'Excimer Laser'
        },
        'EUV': {
            'wavelength': 13.5,  # nm
            'bandwidth': 0.27,  # nm
            'power': 250,  # W (锡液滴靶)
            'lifetime': 'TBD',  # 待定
            'type': 'LPP Source'
        }
    }

    # 照明模式
    ILLUMINATION_MODES = [
        {'name': 'Conventional', 'sigma_in': 0.7, 'sigma_out': 0.9},
        {'name': 'Annular', 'sigma_in': 0.4, 'sigma_out': 0.8},
        {'name': 'Dipole', 'sigma_in': 0.15, 'sigma_out': 0.3},
        {'name': 'Quadrupole', 'sigma_in': 0.2, 'sigma_out': 0.5},
        {'name': 'Custom', 'sigma_in': 'variable', 'sigma_out': 'variable'}
    ]

    @staticmethod
    def uniformity_requirement(power_stability, intensity_uniformity):
        """
        照明均匀性要求

        参数：
        - power_stability: 功率稳定性 [%]
        - intensity_uniformity: 照度均匀性 [% 3σ]

        返回：
        - 评估结果
        """
        requirements = {
            'power_stability_max': 1.0,  # %
            'uniformity_3sigma_max': 0.3,  # %
            'dose_control_accuracy': 0.5  # %
        }

        return {
            'power_stability_pass': power_stability <= requirements['power_stability_max'],
            'uniformity_pass': intensity_uniformity <= requirements['uniformity_3sigma_max'],
            'dose_accuracy_pass': True  # 根据具体要求
        }
```

### 2.3 投影物镜

```
投影物镜结构特点：

┌─────────────────────────────────────────────────────┐
│                                                      │
│  镜片数量: 25-30片 (高端机型)                         │
│  总长度: 约1米                                       │
│  镜片口径: 200mm(大) → 50mm(小)                      │
│  镜片材料: CaF₂ (萤石) + 熔融石英                     │
│  镜片镀膜: 抗反射膜 @193nm                            │
│  装配精度: 纳米级                                     │
│  温度控制: ±0.01°C                                   │
│                                                      │
│  镜片分组:                                            │
│  ├── 前组 (Field Lens): 口径大，场曲校正             │
│  ├── 中组 (Relay): 中继成像                          │
│  └── 后组 (Projection): 投影缩小                      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 3. 工件台与掩模台

### 3.1 运动系统架构

```python
class StageSystem:
    """工件台与掩模台运动系统"""

    # 运动平台架构
    STAGE_ARCHITECTURE = {
        'wafer_stage': {
            'type': 'Dual Stage',
            'platform': 'Wafer + Measurement',
            'stages': 2,  # 交替工作
            'resolution': 0.1,  # nm
            'position_accuracy': 1.0,  # nm 3σ
            'repeatability': 0.3,  # nm 3σ
            'max_velocity': 1.0,  # m/s
            'max_acceleration': 20,  # m/s²
            'stroke_x': 310,  # mm
            'stroke_y': 310,  # mm
            'stroke_z': 0.1,  # mm (调焦)
            'mass': 200,  # kg
            'drive_technology': 'Linear Motor + Air Bearing'
        },

        'mask_stage': {
            'type': 'Reticle Stage',
            'platform': 'Single/Multi Reticle',
            'stages': 1,
            'resolution': 0.05,  # nm
            'position_accuracy': 0.5,  # nm 3σ
            'repeatability': 0.15,  # nm 3σ
            'max_velocity': 0.5,  # m/s
            'max_acceleration': 10,  # m/s²
            'stroke_x': 156,  # mm
            'stroke_y': 26,  # mm (扫描方向)
            'mass': 50,  # kg
            'drive_technology': 'Linear Motor + Voice Coil'
        }
    }

    @staticmethod
    def position_error_budget(total_budget_nm):
        """
        位置误差预算分配

        典型分配:
        - 传感器: 30%
        - 运动平台: 35%
        - 环境: 20%
        - 其他: 15%
        """
        budget = {
            'interferometer': total_budget_nm * 0.30,
            'stage_mechanics': total_budget_nm * 0.35,
            'environment': total_budget_nm * 0.20,
            'aberration': total_budget_nm * 0.10,
            'other': total_budget_nm * 0.05
        }

        return budget

    @staticmethod
    def settling_time(velocity, acceleration, deceleration):
        """
        行程计算与稳定时间

        快速往复运动时序:
        1. 加速阶段: t1 = v/a
        2. 匀速阶段: t2 = (L - 0.5*a*t1²)/v
        3. 减速阶段: t3 = v/d
        """
        return {
            'accel_time': velocity / acceleration,
            'decel_time': velocity / deceleration,
            'settling_time': velocity / acceleration + velocity / deceleration,
            'notes': '不包括定位调整时间'
        }
```

### 3.2 气浮轴承系统

```
气浮轴承工作原理：

         ┌─────────────────┐
         │                 │
         │    气体入口      │
         │    (供气压力P)   │
         │         ↓       │
         │   ┌─────────┐   │
    ─────┴──►│  节流孔  │──┴─────
             └────┬────┘
                  │
                  ▼
    ════════════════════════════
         气膜间隙 h (约5-10μm)
    ════════════════════════════
                  │
    ────────────────────────────── 导向面

    承载能力: W = (P₀ - Pa) × A_effective
    刚度: K = dW/dh (典型值: 100-1000 N/μm)
```

| 参数 | 典型值 | 单位 |
|-----|-------|------|
| 气膜间隙 | 5-10 | μm |
| 供气压力 | 4-6 | bar |
| 承载刚度 | 100-1000 | N/μm |
| 气体流量 | 10-50 | NL/min |
| 温度升高 | <2 | °C |
| 平面度 | 0.1 | μm |

---

## 4. 调焦调平系统

### 4.1 对焦原理

```python
class FocusLevelingSystem:
    """调焦调平系统设计"""

    # 调焦检测方法对比
    FOCUS_SENSORS = {
        'confocal': {
            'principle': '光学共聚焦',
            'resolution': 1,  # nm
            'sampling_rate': 10,  # kHz
            'spot_size': 20,  # μm
            'advantage': '高分辨率、非接触'
        },
        'interferometric': {
            'principle': '干涉检测',
            'resolution': 0.1,  # nm
            'sampling_rate': 100,  # kHz
            'spot_size': 50,  # μm
            'advantage': '超高分辨率'
        },
        'capacitive': {
            'principle': '电容传感',
            'resolution': 0.5,  # nm
            'sampling_rate': 100,  # kHz
            'spot_size': 'N/A',
            'advantage': '高速、高精度'
        },
        'air_gauge': {
            'principle': '气动测距',
            'resolution': 10,  # nm
            'sampling_rate': 1,  # kHz
            'spot_size': 500,  # μm
            'advantage': '不受污染影响'
        }
    }

    # 调平方法
    LEVELING_METHODS = [
        'Three-Point Focus',  # 三点调焦法
        'AFM (Auto Focus Mapping)',  # 全场调焦映射
        'Direct Z-tilt Control',  # 直接Z-倾斜控制
        'Multi-Channel Synchronous'  # 多通道同步
    ]

    @staticmethod
    def z_position_error_sources():
        """
        Z方向位置误差源分析

        误差预算分解:
        """
        return {
            'sensor_noise': {
                'value': 1.0,  # nm RMS
                'contribution': 0.3,
                'mitigation': '信号平均、滤波'
            },
            'stage_motion': {
                'value': 5.0,  # nm RMS
                'contribution': 0.5,
                'mitigation': '振动隔离、主动控制'
            },
            'thermal_drift': {
                'value': 2.0,  # nm/°C
                'contribution': 0.2,
                'mitigation': '温控、热对称设计'
            },
            'wafer_topography': {
                'value': 10.0,  # nm
                'contribution': 0.6,
                'mitigation': '预扫描补偿'
            }
        }
```

---

## 5. EUV光刻技术

### 5.1 EUV系统特点

```
EUV光刻 vs DUV光刻对比:

┌────────────────┬──────────────────┬──────────────────┐
│     参数        │     DUV (ArF)     │     EUV (13.5nm) │
├────────────────┼──────────────────┼──────────────────┤
│ 光源波长        │     193nm         │     13.5nm       │
├────────────────┼──────────────────┼──────────────────┤
│ 数值孔径NA     │     1.35          │     0.33         │
├────────────────┼──────────────────┼──────────────────┤
│ 分辨率(k1=0.3) │     43nm          │     12nm         │
├────────────────┼──────────────────┼──────────────────┤
│ 光学材料       │ 熔融石英、CaF₂     │  Mo/Si多层膜     │
├────────────────┼──────────────────┼──────────────────┤
│ 光学系统       │ 透射式折射系统      │ 反射式光学系统   │
├────────────────┼──────────────────┼──────────────────┤
│ 投影物镜镜片数 │     25-30片        │     6-8片        │
├────────────────┼──────────────────┼──────────────────┤
│ 工作环境       │     大气           │     真空(10⁻⁵Pa) │
├────────────────┼──────────────────┼──────────────────┤
│ 光源功率       │     90W           │     250W         │
├────────────────┼──────────────────┼──────────────────┤
│ 产出           │     200+ WPH      │     150 WPH      │
└────────────────┴──────────────────┴──────────────────┘
```

### 5.2 EUV光学元件

```python
class EUVOptics:
    """EUV光学元件设计"""

    # EUV反射镜涂层结构
    REFLECTOR_COATING = {
        'Mo/Si_multilayer': {
            'layers': 40-80,  # 双层对数
            'd_spacing': 7.0,  # nm (周期厚度)
            'reflectance': 0.7,  # @13.5nm
            'incident_angle': 'Normal or Grazing',
            'bandwidth': 0.5,  # nm FWHM
            'temperature_limit': 200,  # °C
            'contamination': 'C, O, H partial pressure < 10⁻⁶ Pa'
        },

        'Bragg_reflector': {
            'layers': 20-40,
            'd_spacing': 6.5,  # nm
            'reflectance': 0.6,
            'angle_range': 'narrow',
            'application': 'Spectral purity filter'
        }
    }

    # EUV光源类型
    EUV_SOURCES = {
        'LPP': {
            'name': '激光等离子体光源',
            'target': 'Sn (锡液滴)',
            'conversion_efficiency': 0.03,  # 3-5%
            'power': 250,  # W @IF
            'debris': 'High, need collector'
        },
        'DPP': {
            'name': '放电等离子体光源',
            'target': 'Xe (氙气)',
            'conversion_efficiency': 0.02,  # 2%
            'power': 100,  # W @IF
            'debris': 'Medium'
        },
        'Synchrotron': {
            'name': '同步辐射光源',
            'source_size': 'Large',
            'power': 'Very high',
            'application': 'Research only'
        }
    }

    # EUV光罩
    EUV_RETICLE = {
        'substrate': 'Low thermal expansion glass (LTEM)',
        'absorber': 'TaN or Cr',
        'pellicle': 'No (in vacuum)',
        'defect_size': '< 2nm (target)',
        'reflectivity': 0.6,
        'flatness': '< 30nm'
    }
```

---

## 6. 行业标准与规范

### 6.1 主要标准体系

| 标准组织 | 标准编号 | 内容 |
|---------|---------|------|
| SEMI | E84 | 晶圆传送标准 |
| SEMI | E90 | 晶圆承载器标准 |
| SEMI | E95 | 设备性能标准 |
| SEMI | E133 | 光刻设备规范 |
| ISO | 14644 | 洁净室分级 |
| ISO | 10110 | 光学绘图规范 |
| IEC | 60068 | 环境试验 |
| VDI | 3445 | 精密机床验收 |

### 6.2 关键性能指标(KPI)

```python
class LithographyKPI:
    """光刻机关键性能指标"""

    # 典型指标要求 (ArF Immersion)
    SPECIFICATIONS = {
        # 分辨率
        'resolution_min': {
            'value': 38,
            'unit': 'nm',
            'condition': 'k1=0.31'
        },

        # 套刻精度
        'overlay': {
            'value': 2.0,  # nm 3σ
            'between_layers': 'Same tool',
            'across_chips': '3σ requirement'
        },

        # 产能
        'throughput': {
            'value': 260,
            'unit': 'wafers/hour',
            'conditions': '300mm, full field'
        },

        # 焦深
        'DOF': {
            'value': 100,  # nm
            'condition': 'k2=0.5'
        },

        # 缺陷率
        'defect_addition': {
            'value': 0.1,  # /cm²
            'condition': 'killer defects'
        },

        # 可用度
        'availability': {
            'value': 0.95,  # 95%
            'uptime_target': 0.98
        }
    }

    # 设备综合效率(OEE)计算
    OEE_COMPONENTS = {
        'availability': {
            'description': '时间利用率',
            'target': 0.95
        },
        'performance': {
            'description': '性能利用率',
            'target': 0.90
        },
        'quality': {
            'description': '质量合格率',
            'target': 0.99
        }
    }

    @staticmethod
    def calculate_oee(availability, performance, quality):
        """
        OEE = A × P × Q

        典型OEE目标: 0.85-0.95
        世界级OEE: > 0.85
        """
        return availability * performance * quality
```

---

## 7. 供应商与产业链

### 7.1 光刻机主要厂商

| 厂商 | 市场份额 | 主要产品 | 技术优势 |
|-----|---------|---------|---------|
| ASML | ~80% | Twinscan系列 | EUV领先 |
| Canon | ~15% | KrF/ArF | i-line优势 |
| Nikon | ~5% | ArF Dry/Imm | 浸没式 |
| 上海微电子(SMEE) | <1% | KrF | 国产化 |

### 7.2 关键子系统供应商

```
光刻机供应链：

主机集成商
├── ASML (荷兰)
├── Canon (日本)
└── Nikon (日本)

关键子系统供应商:
├── 光源
│   ├── Cymer (ASML子公司) - EUV/DUV激光器
│   ├── Gigaphoton (Gigaphoton Inc.) - ArF/KrF激光器
│   └── Ushio (日本) - 汞灯光源
│
├── 投影物镜
│   ├── Carl Zeiss (德国) - ArF投影物镜
│   ├── Nikon (日本) - 自供+外销
│   └── Veeco (美国) - EUV光学
│
├── 工件台
│   ├── S Nik (日本) - 气浮平台
│   ├── ETEL (瑞士) - 直线电机
│   └── Renishaw (英国) - 干涉仪
│
├── 运动控制
│   ├── ACS (美国) - 运动控制器
│   ├── Delta Tau (美国) - 实时控制器
│   └── Aerotech (美国) - 运动平台
│
└── 调焦调平
    ├── MKS Instruments (美国) - 真空/流量
    └── Zygo (美国) - 干涉测量
```
