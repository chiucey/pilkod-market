# 可靠性工程方法论

## 1. 可靠性工程基础

### 1.1 可靠性指标体系

```python
class ReliabilityMetrics:
    """可靠性核心指标计算"""

    import numpy as np

    @staticmethod
    def exponential_mttf(lambda_rate):
        """
        指数分布平均无故障时间(MTTF)

        MTTF = 1/λ

        参数：
        - lambda_rate: 故障率 [1/h] 或 [1/ cycles]

        返回：
        - MTTF: 平均无故障时间
        """
        return 1 / lambda_rate

    @staticmethod
    def weibull_reliability(t, beta, eta):
        """
        威布尔分布可靠性函数

        R(t) = exp(-(t/η)^β)

        参数：
        - t: 运行时间
        - beta: 形状参数 (β<1早期失效, β=1随机失效, β>1磨损失效)
        - eta: 尺度参数 (特征寿命)
        """
        return np.exp(-(t / eta) ** beta)

    @staticmethod
    def series_system_reliability(component_reliabilities):
        """
        串联系统可靠性

        R_system = R1 × R2 × ... × Rn

        串联系统可靠性低于任一部件
        """
        R = 1.0
        for r in component_reliabilities:
            R *= r
        return R

    @staticmethod
    def parallel_system_reliability(component_reliabilities):
        """
        并联系统可靠性

        R_system = 1 - Π(1-Ri)

        并联系统可靠性高于任一部件
        """
        failure_prob = 1.0
        for r in component_reliabilities:
            failure_prob *= (1 - r)
        return 1 - failure_prob

    @staticmethod
    def redundancy_effectiveness(n, r, R_component):
        """
        冗余系统可靠性 (n中取r冗余)

        n: 总部件数
        r: 最少工作部件数
        R: 单部件可靠性
        """
        from math import comb

        reliability = 0
        for k in range(r, n + 1):
            reliability += comb(n, k) * (R_component ** k) * ((1 - R_component) ** (n - k))

        return reliability
```

### 1.2 浴盆曲线与失效物理

```
浴盆曲线模型：

失效率
λ(t)
  ▲
  │    ╱╲
  │   ╱  ╲
  │  ╱    ╲
  │ ╱      ╲
  │╱        ╲___________
  └──────────────────→ 时间
  ↑      ↑        ↑
 早期   偶然     磨损
 失效   失效     失效
```

| 失效阶段 | 失效机理 | 典型措施 |
|---------|---------|---------|
| 早期失效 | 制造缺陷、安装错误 | 老化筛选、ESS |
| 偶然失效 | 应力过载、环境突变 | 降额设计、保护电路 |
| 磨损失效 | 磨损、疲劳、腐蚀 | 定期维护、寿命管理 |

---

## 2. DFMEA设计失效模式与影响分析

### 2.1 DFMEA标准流程

```python
class DFMEAAnalyzer:
    """设计失效模式与影响分析工具"""

    # 严重度(S)评分标准 (1-10)
    SEVERITY_SCALE = {
        10: '无预警的严重危害 - 安全法规违反',
        9: '有预警的严重危害 - 危及人员安全',
        8: '严重功能丧失 - 产品无法使用',
        7: '主要功能丧失 - 产品主要功能失效',
        6: '次要功能丧失 - 产品可用但性能下降',
        5: '功能退化 - 客户感到不满意',
        4: '功能退化可察觉 - 客户轻微不满',
        3: '干扰性问题 - 客户抱怨但可接受',
        2: '轻微问题 - 客户未注意到',
        1: '无影响'
    }

    # 频度(O)评分标准 (1-10)
    OCCURRENCE_SCALE = {
        10: '非常高 - 失效几乎不可避免 (>100/1000)',
        9: '高 - 经常失效 (50/1000)',
        8: '较高 - 频繁失效 (20/1000)',
        7: '中等 - 偶尔失效 (10/1000)',
        6: '较低 - 少见失效 (2/1000)',
        5: '低 - 相对少见失效 (0.5/1000)',
        4: '很低 - 极少失效 (0.1/1000)',
        3: '极低 - 失效罕见 (0.01/1000)',
        2: '几乎不可能 (>0.001/1000)',
        1: '不可能 - 使用类似设计无失效记录'
    }

    # 探测度(D)评分标准 (1-10)
    DETECTION_SCALE = {
        10: '绝对不可能探测 - 无设计控制',
        9: '很不可能 - 设计控制效果差',
        8: '很不可能 - 设计控制可能性低',
        7: '低 - 设计控制可能性较低',
        6: '中等 - 设计控制可能性中等',
        5: '中上 - 设计控制可能性中上',
        4: '高 - 设计控制可能性较高',
        3: '很高 - 设计控制可能性很高',
        2: '几乎肯定 - 探测有效性高',
        1: '肯定探测 - 有确认的设计控制'
    }

    def __init__(self, project_name, analyst, date):
        self.project = project_name
        self.analyst = analyst
        self.date = date
        self.items = []

    def add_item(self, item_id, item_name, function, potential_failure_mode,
                 potential_effect, severity, potential_cause,
                 occurrence, current_detection, detection):
        """
        添加DFMEA项目

        参数：
        - item_id: 项目编号
        - item_name: 项目名称
        - function: 功能描述
        - potential_failure_mode: 潜在失效模式
        - potential_effect: 潜在失效影响
        - severity: 严重度 S (1-10)
        - potential_cause: 潜在失效原因
        - occurrence: 频度 O (1-10)
        - current_detection: 现行探测控制
        - detection: 探测度 D (1-10)
        """
        rpn = severity * occurrence * detection

        item = {
            'item_id': item_id,
            'item_name': item_name,
            'function': function,
            'potential_failure_mode': potential_failure_mode,
            'potential_effect': potential_effect,
            'severity': severity,
            'potential_cause': potential_cause,
            'occurrence': occurrence,
            'current_detection': current_detection,
            'detection': detection,
            'rpn': rpn,
            'severity_desc': self.SEVERITY_SCALE.get(severity, '未知'),
            'occurrence_desc': self.OCCURRENCE_SCALE.get(occurrence, '未知'),
            'detection_desc': self.DETECTION_SCALE.get(detection, '未知')
        }

        self.items.append(item)
        return rpn

    def prioritize_risks(self, rpn_threshold=100):
        """
        风险优先级排序

        RPN > 100: 需要立即采取行动
        RPN 50-100: 需要关注
        RPN < 50: 可接受
        """
        high_risk = [item for item in self.items if item['rpn'] >= rpn_threshold]
        high_risk.sort(key=lambda x: x['rpn'], reverse=True)

        return high_risk

    def generate_report(self):
        """生成DFMEA分析报告"""
        report = {
            'project': self.project,
            'analyst': self.analyst,
            'date': self.date,
            'total_items': len(self.items),
            'average_rpn': sum(i['rpn'] for i in self.items) / len(self.items) if self.items else 0,
            'high_risk_count': len([i for i in self.items if i['rpn'] >= 100]),
            'items_by_severity': {},
            'items_by_rpn': sorted(self.items, key=lambda x: x['rpn'], reverse=True)
        }

        # 按严重度分类
        for item in self.items:
            s = item['severity']
            if s not in report['items_by_severity']:
                report['items_by_severity'][s] = []
            report['items_by_severity'][s].append(item)

        return report
```

### 2.2 DFMEA表格模板

```markdown
# DFMEA分析表格模板

| 项番 | 项目编号 | 项目名称 | 功能 | 潜在失效模式 | 潜在失效影响 | S | 潜在失效原因/机理 | O | 现行探测控制 | D | RPN | 建议措施 | 责任人 | 目标完成日期 | 措施状态 |
|-----|---------|---------|-----|------------|------------|---|-----------------|---|------------|---|-----|---------|--------|-------------|---------|
| 1 | SYS-001 | 镜片支撑座 | 定位并固定光学镜片 | 支撑座变形 | 镜片位置偏移>1μm | 7 | 热膨胀变形 | 3 | 热变形仿真 | 4 | 84 | 增加加强筋 | 张工 | 2024-03-15 | 进行中 |
| 2 | SYS-002 | 气浮轴承 | 支撑运动平台 | 气体泄漏 | 支撑刚度下降 | 8 | 密封圈磨损 | 4 | 气压监测 | 3 | 96 | 优化密封结构 | 李工 | 2024-03-20 | 计划中 |
```

### 2.3 DFMEA实施指南

```
DFMEA实施流程：

┌─────────────────────────────────────────┐
│ 1. 项目定义                              │
│    - 确定分析边界                         │
│    - 建立功能分解结构                      │
│    - 识别接口关系                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 2. 团队组建                               │
│    - 多学科团队参与                        │
│    - 设计工程师主导                        │
│    - 工艺/质量/客服参与                   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 3. 失效模式识别                           │
│    - 功能失效定义                         │
│    - 失效模式枚举                         │
│    - 失效链构建                           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 4. 风险评估                              │
│    - S/O/D评分                           │
│    - RPN计算                             │
│    - 风险矩阵绘制                         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 5. 优化行动                               │
│    - 高风险优先处理                        │
│    - 措施有效性验证                        │
│    - 重新评估RPN                          │
└─────────────────────────────────────────┘
```

---

## 3. 加速寿命试验(ALT)

### 3.1 加速模型

```python
class AcceleratedLifeTesting:
    """加速寿命试验设计与分析"""

    import numpy as np

    # 物理常数
    BOLTZMANN_CONSTANT = 8.617e-5  # eV/K
    ROOM_TEMPERATURE = 298.15  # K (25°C)

    @staticmethod
    def arrhenius_acceleration(T_use, T_acc, Ea):
        """
        阿伦尼乌斯模型 - 温度加速因子

        AF = exp(Ea/k × (1/T_use - 1/T_acc))

        参数：
        - T_use: 使用温度 [K]
        - T_acc: 加速温度 [K]
        - Ea: 激活能 [eV] (典型值: 0.3-1.5eV)

        返回：
        - AF: 加速因子
        """
        k = AcceleratedLifeTesting.BOLTZMANN_CONSTANT
        return np.exp(Ea / k * (1/T_use - 1/T_acc))

    @staticmethod
    def power_law_acceleration(stress_use, stress_acc, n):
        """
        幂律模型 - 应力加速因子

        AF = (σ_acc/σ_use)^n

        参数：
        - stress_use: 使用应力水平
        - stress_acc: 加速应力水平
        - n: 应力指数 (温度相关，通常2-4)
        """
        return (stress_acc / stress_use) ** n

    @staticmethod
    def combined_acceleration(T_use, T_acc, stress_use, stress_acc, Ea, n):
        """
        复合加速模型

        AF_total = AF_temp × AF_stress

        用于温度+功率/振动等复合应力
        """
        AF_temp = AcceleratedLifeTesting.arrhenius_acceleration(T_use, T_acc, Ea)
        AF_stress = AcceleratedLifeTesting.power_law_acceleration(stress_use, stress_acc, n)

        return AF_temp * AF_stress

    @staticmethod
    def sample_size_design(beta, B10_life_target, AF, confidence=0.90):
        """
        加速试验样本量设计

        参数：
        - beta: 威布尔形状参数
        - B10_life_target: B10目标寿命 [h]
        - AF: 加速因子
        - confidence: 置信度
        """
        # 简化计算，假设指数分布
        import scipy.stats as stats

        z = stats.norm.ppf(confidence)

        # 在加速条件下需要的运行时间
        test_time = B10_life_target / AF * 0.1  # 取B10的10%作为试验时间

        # 所需样本数(基于检测到失效的要求)
        n = int(np.ceil(z**2 / (0.1**2)))

        return {
            'test_time_hours': test_time,
            'sample_size': n,
            'equivalent_field_hours': test_time * AF
        }

    @staticmethod
    def data_analysis(failure_times, censoring_type='right'):
        """
        加速试验数据分析

        参数：
        - failure_times: 失效时间列表
        - censoring_type: 截尾类型 ('right', 'interval')
        """
        failure_times = np.array(failure_times)

        # 基本统计量
        n = len(failure_times)
        mean = np.mean(failure_times)
        median = np.median(failure_times)

        # 参数估计 (极大似然法简化)
        # 威布尔分布参数估计需要迭代计算

        return {
            'sample_size': n,
            'mean_time_to_failure': mean,
            'median_time_to_failure': median,
            'min_time_to_failure': np.min(failure_times),
            'max_time_to_failure': np.max(failure_times)
        }
```

### 3.2 加速试验方案模板

| 试验项目 | 应力类型 | 使用水平 | 加速水平 | 加速倍数 | 试验时间 | 样本量 | 失效判据 |
|---------|---------|---------|---------|---------|---------|-------|---------|
| 高温工作 | 温度 | 50°C | 85°C | AF=32 | 1000h | 6 | 功能丧失 |
| 温度循环 | ΔT | 20°C | 60°C | AF=8 | 500cycles | 6 | 性能退化>10% |
| 功率循环 | ΔP | 50W | 150W | AF=15 | 2000cycles | 6 | 热阻增加>20% |
| 振动耐久 | 加速度 | 5g | 20g | AF=4 | 100h | 6 | 结构损坏 |

---

## 4. 失效物理分析(PoF)

### 4.1 常见失效机理

```python
class PhysicsOfFailure:
    """失效物理模型库"""

    @staticmethod
    def thermal_mismatch_strain(delta_T, delta_alpha, E, thickness):
        """
        热失配应变计算

        ε = Δα × ΔT × f(h1/h2, E1/E2)

        用于焊点、芯片粘接等界面失效分析
        """
        # 简化模型 (薄芯片/厚基板)
        strain = delta_alpha * delta_T

        return strain

    @staticmethod
    def coffin_manson_cycles_to_failure(delta_T, exponent, C):
        """
        Coffin-Manson公式 - 热循环疲劳寿命

        Nf = C × (ΔT)^(-m)

        参数：
        - ΔT: 温度循环幅值
        - m: Manson-Coffin指数 (通常1.5-3.0)
        - C: 材料常数
        """
        return C * (delta_T) ** (-exponent)

    @staticmethod
    def electromigration_mtbf(T, j, cross_section):
        """
        电迁移MTBF预测 (用于互连引线)

        MTBF ∝ 1/(j² × exp(-Ea/kT))

        参数：
        - T: 温度 [K]
        - j: 电流密度 [A/m²]
        - cross_section: 引线截面积 [m²]
        """
        k = 8.617e-5  # eV/K
        Ea = 0.5  # 激活能 eV

        # 简化模型
        j_normalized = j / 1e6  # A/mm² → A/μm²
        mtbf_factor = 1 / (j_normalized ** 2 * np.exp(-Ea / (k * T)))

        return mtbf_factor

    @staticmethod
    def wear_volumes_lubrication(velocity, pressure, time, wear_coefficient):
        """
        磨损体积计算

        V = K × P × V × t

        参数：
        - K: 磨损系数
        - P: 接触压力
        - V: 滑动速度
        - t: 运行时间
        """
        return wear_coefficient * pressure * velocity * time

    @staticmethod
    def corrosion_rate(temp, humidity, salt_concentration):
        """
        腐蚀速率估算

        基于经验模型

        参数：
        - temp: 温度 [°C]
        - humidity: 相对湿度 [%RH]
        - salt_concentration: 盐浓度 [g/m³]
        """
        # 简化经验公式
        rate = salt_concentration * (humidity / 50) * np.exp(0.1 * temp)

        return rate  # μm/year
```

### 4.2 失效机理分类

| 类别 | 失效机理 | 激活能(eV) | 加速因子 | 影响部件 |
|-----|---------|-----------|---------|---------|
| 温度相关 | 热疲劳 | 0.3-1.2 | Arrhenius | 焊点、粘接剂 |
| 温度相关 | 氧化生长 | 0.6-1.4 | Arrhenius | 金属膜 |
| 温度相关 | 蠕变 | 1.0-2.0 | Arrhenius | 引线、弹簧 |
| 机械 | 磨损 | - | Power law | 导轨、轴承 |
| 机械 | 疲劳 | - | Miner's rule | 结构件 |
| 电气 | 电迁移 | 0.5-0.9 | Current² | 互连引线 |
| 电气 | 介质击穿 | 1.0-2.0 | Voltage | 电容器 |
| 化学 | 腐蚀 | 0.3-0.8 | Humidity | 金属表面 |

---

## 5. 可靠性增长管理

### 5.1 可靠性增长模型

```python
class ReliabilityGrowth:
    """可靠性增长模型"""

    import numpy as np

    @staticmethod
    def duane_model(time, alpha, beta):
        """
        Duane模型 - 连续性可靠性增长

        MTBF(t) = MTBF_initial × (t/T)^β

        参数：
        - t: 运行时间
        - alpha: 尺度参数
        - beta: 增长指数 (0<β<1)
        """
        mtbf = alpha * (time ** beta)
        return mtbf

    @staticmethod
    def army_leo_model(failures, test_time):
        """
        Army LEO模型 - 离散失效数据分析

        基于CMSR (连续均值比)方法
        """
        failures = np.array(failures)

        # 计算CMSR
        cumulative_failures = np.cumsum(failures)
        cumulative_time = test_time

        cmsr = cumulative_failures / cumulative_time

        # 可靠性增长趋势检验
        n = len(failures)
        Mann_statistic = np.sum(np.sign(failures[1:] - failures[:-1]))

        return {
            'cmsr': cmsr,
            'trend': 'improving' if Mann_statistic > 0 else 'degrading',
            'Mann_statistic': Mann_statistic
        }

    @staticmethod
    def goel_okumoto_model(t, a, b):
        """
        Goel-Okumoto模型 - 非齐次泊松过程

        适用于软件/复杂系统早期失效分析

        μ(t) = a × (1 - exp(-b×t))  # 期望失效数
        λ(t) = a × b × exp(-b×t)     # 失效率函数
        """
        mu = a * (1 - np.exp(-b * t))  # 累积失效数
        lambda_t = a * b * np.exp(-b * t)  # 失效率

        return {
            'cumulative_failures': mu,
            'failure_intensity': lambda_t,
            'reliability': np.exp(-mu)
        }
```

### 5.2 可靠性增长计划模板

```markdown
# 可靠性增长计划

## 1. 当前可靠性水平评估
| 指标 | 当前值 | 目标值 | 差距 |
|-----|-------|-------|-----|
| MTBF | 5000h | 20000h | 4倍 |
| 可用度 | 95% | 99.5% | 4.5% |
| 维修时间 | 4h | 1h | 3h |

## 2. 增长策略
| 阶段 | 时间 | 主要措施 | 预期MTBF |
|-----|------|---------|---------|
| G1 | 0-3月 | 问题整改、老化筛选 | 8000h |
| G2 | 3-6月 | 设计改进、工艺优化 | 12000h |
| G3 | 6-12月 | 可靠性验证、增长试验 | 20000h |

## 3. 里程碑与验证
| 里程碑 | 完成日期 | 验证方法 | 接收准则 |
|-------|---------|---------|---------|
| M1: 首批样机 | 2024-04 | 环境应力筛选 | 无致命失效 |
| M2: 设计改进 | 2024-07 | 可靠性摸底试验 | MTBF>10000h |
| M3: 型式试验 | 2024-10 | 加速寿命试验 | MTBF>15000h |
| M4: 鉴定试验 | 2024-12 | 综合可靠性试验 | MTBF>20000h |
```

---

## 6. 可靠性设计检查清单

### 设计阶段检查
- [ ] FMEA已完成并评审
- [ ] 关键部件清单(CTQ)已识别
- [ ] 降额设计满足要求
- [ ] 热设计余量充足
- [ ] 冗余设计已评估
- [ ] 设计更改已更新FMEA

### 验证阶段检查
- [ ] 加速寿命试验方案已批准
- [ ] 应力筛选计划已制定
- [ ] 可靠性增长跟踪机制建立
- [ ] 现场失效数据收集系统运行

### 管理阶段检查
- [ ] 可靠性指标定期评审
- [ ] 供应商可靠性管理
- [ ] 设计手册更新机制
- [ ] 知识库维护更新
