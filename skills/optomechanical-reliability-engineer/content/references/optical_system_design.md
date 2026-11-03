# 光学系统设计指南

## 1. 光学系统设计基础

### 1.1 基本参数定义

```python
class OpticalSystemParameters:
    """光学系统核心参数"""

    def __init__(self):
        # 波长参数
        self.wavelength = 193.4e-9  # ArF准分子激光器 [m]
        self.bandwidth = 1.0e-9      # 光谱带宽 [m]

        # 数值孔径
        self.NA = 1.35               # 浸没式光刻数值孔径
        self.object_NA = 0.25        # 照明系统数值孔径

        # 视场参数
        self.field_size = 26e-3      # 像面视场直径 [m]
        self.object_height = 104e-3  # 物高 [m]

        # 放大率
        self.magnification = 0.25     # 投影物镜放大率

        # 分辨率 (瑞利判据)
        # R = k1 × λ / NA
        self.resolution = 0.61 * self.wavelength / self.NA

        # 焦深 (DOF)
        # DOF = k2 × λ / NA²
        self.depth_of_focus = self.wavelength / (2 * self.NA**2)
```

### 1.2 像差分类与校正

| 像差类型 | 描述 | 对系统的影响 | 校正方法 |
|---------|------|-------------|---------|
| 球差 | 边缘光线与近轴光线焦点不一致 | 分辨率下降 | 非球面透镜、透镜组合 |
| 彗差 | 轴外点成像呈彗星状 | 视场边缘模糊 | 孔径光阑位置优化 |
| 像散 | 子午/弧矢方向焦距不同 | 椭圆光斑 | 透镜间隔调整 |
| 场曲 | 平面物体成曲面像 | 周边聚焦不良 | 弯月透镜组合 |
| 畸变 | 放大率随视场变化 | 图形失真 | 对称光学结构 |
| 色差 | 不同波长焦点位置不同 | 彩虹边缘 | 消色差透镜组合 |

### 1.3 光学传递函数(MTF)

```python
import numpy as np

class MTFAnalyzer:
    """
    光学传递函数分析
    MTF = |OTF| 是评价光学系统成像质量的核心指标
    """

    def __init__(self, wavelength, NA, field_height):
        self.wavelength = wavelength
        self.NA = NA
        self.field_height = field_height
        self.f_number = 1 / (2 * NA)

    def diffraction_limited_mtf(self, spatial_frequency):
        """
        理想光学系统的衍射极限MTF

        参数：
        - spatial_frequency: 空间频率 [cycles/mm]

        返回：
        - MTF值 [0-1]
        """
        # 截止频率 (光学系统的分辨率极限)
        fc = 1 / (self.wavelength * self.f_number)  # cycles/m

        # 归一化频率
        f_norm = spatial_frequency / fc

        if f_norm > 1:
            return 0.0

        # 切趾(Apodized)圆孔径MTF
        if f_norm <= 1:
            mtf = (2/np.pi) * (
                np.arccos(f_norm) - f_norm * np.sqrt(1 - f_norm**2)
            )
            return mtf

        return 0.0

    def system_mtf(self, field_mtf, detector_mtf=None, motion_mtf=None):
        """
        系统总MTF (各环节MTF乘积)

        MTF_system = MTF_optics × MTF_detector × MTF_motion × ...
        """
        total = field_mtf

        if detector_mtf is not None:
            total *= detector_mtf

        if motion_mtf is not None:
            total *= motion_mtf

        return total

    def strehl_ratio(self, wavefront_rms):
        """
        斯特列尔比计算
        Strehl Ratio = exp(-(2π×RMS/λ)²)
        用于评价实际光学系统与理想系统的差异
        """
        wavefront_rms_nm = wavefront_rms / 1e-9  # 转换为nm
        wavelength_nm = self.wavelength / 1e-9

        strehl = np.exp(-(2 * np.pi * wavefront_rms_nm / wavelength_nm)**2)

        return strehl
```

---

## 2. 光刻机投影物镜设计

### 2.1 投影物镜架构

```
投影物镜结构示意：
┌─────────────────────────────────────────┐
│                                         │
│  掩模(Mask) ←── 照明光束 ──→ 透镜组     │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ 第1组: 口径200mm, 用于光束成形  │    │
│  ├─────────────────────────────────┤    │
│  │ 第2组: 口径150mm, 像差校正主镜  │    │
│  ├─────────────────────────────────┤    │
│  │ 第3组: 口径100mm, 场镜          │    │
│  ├─────────────────────────────────┤    │
│  │ 第4组: 口径80mm, 中继镜组       │    │
│  ├─────────────────────────────────┤    │
│  │ 第5组: 口径60mm, 最终成像组     │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ↓                                      │
│  晶圆(Wafer)                            │
│                                         │
└─────────────────────────────────────────┘
```

### 2.2 设计要求

| 参数 | 规格 | 公差 |
|-----|------|-----|
| 波长 | 193.374nm (ArF) | ±0.001nm |
| 数值孔径(NA) | 1.35 (浸没式) | ±0.001 |
| 视场大小 | 26mm × 8mm (环形) | ±0.1mm |
| 分辨率 | 38nm (k1=0.31) | - |
| 放大率 | 4:1 (4倍) | ±0.1% |
| 波前误差 | <0.1λ RMS | @RMS |
| 畸变 | <5nm | 3σ |
| 工作距离 | 2-5mm | - |
| 透镜数量 | 25-30片 | - |
| 总重量 | 500-800kg | - |

### 2.3 材料选择

```python
class LensMaterial:
    """光刻机透镜材料选型"""

    MATERIALS = {
        'CaF2': {
            'name': '氟化钙(萤石)',
            'transmittance': 0.999,  # @193nm
            ' CTE': 18.9e-6,  # /K
            'Young_modulus': 75e9,  # Pa
            'Knoop_hardness': 158,
            'applications': ['深紫外透镜', '准分子激光光学']
        },

        'SiO2': {
            'name': '熔融石英',
            'transmittance': 0.999,  # @193nm
            'CTE': 0.5e-6,  # /K
            'Young_modulus': 73e9,  # Pa
            'Knoop_hardness': 500,
            'applications': ['主透镜', '场镜', '照明系统']
        },

        'BaF2': {
            'name': '氟化钡',
            'transmittance': 0.98,  # @193nm
            'CTE': 18.1e-6,  # /K
            'Young_modulus': 53e9,  '''# Pa
            'Knoop_hardness': 82,
            'applications': ['红外光学', '紫外窗口']
        }
    }

    @staticmethod
    def select_material(wavelength, thermal_stability, mechanical_requirement):
        """
        材料选择决策树

        参数：
        - wavelength: 工作波长 [nm]
        - thermal_stability: 热稳定性要求等级 [1-5]
        - mechanical_requirement: 机械强度要求等级 [1-5]

        返回：
        - 推荐材料列表
        """
        candidates = []

        if wavelength < 200:  # DUV/EUV波段
            # 优先选择紫外透过率高的材料
            for mat_id, props in LensMaterial.MATERIALS.items():
                score = 0
                if props['transmittance'] > 0.99:
                    score += 3
                if props['CTE'] < 1e-6:
                    score += 2
                if thermal_stability >= 4:
                    score += 2
                if props['Knoop_hardness'] > 100:
                    score += 1

                candidates.append((mat_id, score))

        # 按评分排序
        candidates.sort(key=lambda x: x[1], reverse=True)

        return candidates
```

---

## 3. 光机结构设计原则

### 3.1 稳定性设计

```
热稳定性分析流程：

┌─────────────┐
│ 热源识别     │
│ (激光器、   │
│ 驱动电机)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 热传导分析  │
│ (有限元)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 温升计算    │
│ ΔT = Q/(k·A)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 热变形估算  │
│ δ = α·L·ΔT │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 补偿设计    │
│ (主动/被动) │
└─────────────┘
```

### 3.2 低膨胀材料对比

| 材料 | CTE (×10⁻⁶/K) | 密度 (g/cm³) | 特点 |
|-----|---------------|-------------|------|
| 殷钢(Invar) | 1.2 | 8.1 | 低膨胀、磁性 |
| 超殷钢(SuperInvar) | 0.0 | 8.1 | 超低膨胀 |
| Zerodur | 0.0±0.1 | 2.53 | 玻璃陶瓷 |
| ULE | 0.0±0.03 | 2.21 | 超低膨胀玻璃 |
| 碳化硅(SiC) | 2.2 | 3.2 | 高刚度、高导热 |
| 铝 | 23 | 2.7 | 轻量化 |
| 钛合金 | 8.6 | 4.5 | 高强度 |

### 3.3 结构刚度设计

```python
class StructuralStiffness:
    """光机结构刚度设计工具"""

    # 光刻机典型刚度要求
    REQUIREMENTS = {
        'wafer_stage_x': 100e6,  # N/m
        'wafer_stage_y': 100e6,  # N/m
        'wafer_stage_z': 200e6,  # N/m
        'lens_mount_radial': 50e6,  # N/m
        'lens_mount_axial': 100e6,  # N/m
    }

    @staticmethod
    def calculate_beam_deflection(P, L, E, I):
        """
        悬臂梁最大挠度计算

        参数：
        - P: 载荷 [N]
        - L: 梁长度 [m]
        - E: 弹性模量 [Pa]
        - I: 截面惯性矩 [m⁴]

        返回：
        - δ_max: 最大挠度 [m]
        """
        return P * L**3 / (3 * E * I)

    @staticmethod
    def calculate_plate_deflection(q, a, b, D):
        """
        矩形板中心挠度计算

        参数：
        - q: 均布载荷 [Pa]
        - a, b: 板尺寸 [m]
        - D: 弯曲刚度 D = Eh³/[12(1-ν²)]

        返回：
        - δ_center: 中心挠度 [m]
        """
        # 长宽比
        aspect = a / b

        # 系数表(根据边支撑条件)
        alpha = {
            1.0: 0.0443,
            1.2: 0.0538,
            1.5: 0.0641,
            2.0: 0.0753
        }

        k = alpha.get(round(aspect, 1), 0.0753)

        return k * q * a**4 / D

    @staticmethod
    def modal_analysis(mass, stiffness, damping_ratio=0.02):
        """
        模态分析基本参数计算

        参数：
        - mass: 等效质量 [kg]
        - stiffness: 刚度 [N/m]
        - damping_ratio: 阻尼比

        返回：
        - fn: 固有频率 [Hz]
        - Q: 品质因子
        """
        import numpy as np

        fn = 1 / (2 * np.pi) * np.sqrt(stiffness / mass)
        Q = 1 / (2 * damping_ratio)

        return fn, Q
```

---

## 4. 公差分析

### 4.1 公差分配流程

```python
class ToleranceAllocation:
    """公差分配分析"""

    def __init__(self, target_performance, cost_weight=1.0):
        self.target = target_performance
        self.cost_weight = cost_weight
        self.tolerances = []

    def rss_allocation(self, component_errors):
        """
        RSS(Root Sum Square)公差分配法
        综合误差 = √(Σδi²)

        适用于误差独立且服从正态分布的情况
        """
        rss_error = np.sqrt(sum(e**2 for e in component_errors))
        return rss_error

    def equal_tolerance_allocation(self, n_components, total_tolerance):
        """
        等公差分配法
        每个部件分配相同的公差
        """
        individual = total_tolerance / np.sqrt(n_components)
        return [individual] * n_components

    def sensitivity_based_allocation(self, sensitivities, cost_coefficients):
        """
        灵敏度加权公差分配

        基于各部件对总误差的灵敏度和制造成本来分配公差

        公式：δi ∝ |∂P/∂xi| / Ci

        参数：
        - sensitivities: 各部件灵敏度列表
        - cost_coefficients: 各部件成本系数
        """
        weights = [abs(s) / c for s, c in zip(sensitivities, cost_coefficients)]
        total_weight = sum(weights)

        tolerances = [self.target * w / total_weight for w in weights]

        return tolerances

    def worst_case_allocation(self, component_tolerances):
        """
        最坏情况分析法(WCA)
        总误差 = Σ|δi|

        用于安全关键系统
        """
        return sum(abs(t) for t in component_tolerances)
```

### 4.2 光刻机典型公差要求

| 参数 | 规格 | 公差类型 | 备注 |
|-----|------|---------|-----|
| 透镜间隔 | 50mm | ±0.01mm | 空气隙透镜 |
| 透镜偏心 | 0 | ±0.5μm | 同轴度控制 |
| 透镜倾斜 | 0 | ±1arcsec | 角度控制 |
| 镜座直径 | 200mm | ±0.005mm | 配合公差 |
| 安装力矩 | 10N·m | ±0.5N·m | 螺栓预紧 |
| 温控精度 | 20℃ | ±0.01℃ | 温度梯度 |

---

## 5. 环境控制要求

### 5.1 温度控制规范

```python
class EnvironmentalControl:
    """光刻机环境控制系统"""

    # 光刻机环境控制规格
    SPECIFICATIONS = {
        'temperature': {
            'nominal': 20.0,  # ℃
            'tolerance': 0.01,  # ℃ (短期)
            'gradient': 0.001,  # ℃/m (空间梯度)
            'stability': 0.05,  # ℃ (24h变化)
            'control_zone': 'iso_zone_1'  # 温控分区
        },

        'humidity': {
            'nominal': 40.0,  # %RH
            'tolerance': 1.0,  # %RH
            'gradient': 0.2,  # %RH/m
            'control_method': 'dew_point_control'  # 露点控制
        },

        'vibration': {
            'micro_vibration': 5e-6,  # m/s² RMS @1-100Hz
            'floor_vibration': 50e-6,  # m/s²
            'isolation_frequency': 5,  # Hz (隔振频率)
            'transmissibility': 0.05,  # 传递率 @10Hz以上
        },

        'cleanliness': {
            'class': 1,  # ISO 14644-1
            'airflow': 0.45,  # m/s
            'particles': '<10 @0.1μm',  # 粒径<0.1μm, <10个
            'recirculation': 20,  # 次/小时
        }
    }

    @staticmethod
    def calculate_thermal_deformation(alpha, L, delta_T):
        """
        热变形计算

        参数：
        - alpha: 热膨胀系数 [/K]
        - L: 特征长度 [m]
        - delta_T: 温升 [K]

        返回：
        - deformation: 热变形量 [m]
        """
        return alpha * L * delta_T

    @staticmethod
    def vibration_isolation(transmissibility, frequency_ratio):
        """
        隔振系统传递率计算

        参数：
        - frequency_ratio: f/fn (激励频率/固有频率)
        - transmissibility: T = 1/√[(1-(f/fn)²)² + (2ζf/fn)²]

        返回：
        - T: 传递率
        """
        import numpy as np

        if frequency_ratio < 0.7:
            return 1.0  # 未隔振

        zeta = 0.05  # 阻尼比

        T = 1 / np.sqrt(
            (1 - frequency_ratio**2)**2 +
            (2 * zeta * frequency_ratio)**2
        )

        return T
```

---

## 6. 设计检查清单

### 光学设计检查
- [ ] 波前误差满足<0.1λ RMS要求
- [ ] MTF在截止频率60%以上
- [ ] 像差校正覆盖全视场
- [ ] 杂散光分析完成
- [ ] 材料透过率验证(193nm)
- [ ] 抗激光损伤阈值满足要求

### 光机设计检查
- [ ] 热变形分析覆盖所有工况
- [ ] 结构刚度满足动力学要求
- [ ] 一阶固有频率>100Hz
- [ ] 材料CTE匹配性验证
- [ ] 公差分配满足性能指标
- [ ] 制造工艺可行性确认

### 环境系统检查
- [ ] 温控系统响应时间满足要求
- [ ] 振动隔离传递率<5%
- [ ] 洁净度维持能力验证
- [ ] 温湿度传感器布点优化
