# 射频硬件参考指南

## 射频链路预算

### 链路计算公式

```
Friis传输方程:
Pr = Pt + Gt + Gr - Lp - Lm

其中:
- Pr: 接收功率 (dBm)
- Pt: 发射功率 (dBm)
- Gt: 发射天线增益 (dBi)
- Gr: 接收天线增益 (dBi)
- Lp: 自由空间路径损耗 (dB)
- Lm: 其他损耗总和 (dB)

自由空间路径损耗:
Lp = 32.45 + 20*log10(f_GHz) + 20*log10(d_km)
```

### 预算表格模板

| 参数 | 符号 | 典型值 | 单位 | 备注 |
|------|------|--------|------|------|
| 发射功率 | Pt | 20 | dBm | 100mW |
| 天线增益 | Gt | 3 | dBi | 全向天线 |
| 发射端线损 | Ltx | 1 | dB | 馈线+接头 |
| 路径损耗 | Lp | -100 | dB | 2.4GHz, 10m |
| 接收端线损 | Lrx | 1 | dB | 馈线+接头 |
| 接收天线增益 | Gr | 2 | dBi | 全向天线 |
| 接收功率 | Pr | -76 | dBm | |
| 接收灵敏度 | Pmin | -85 | dBm | BER<1% |
| **链路余量** | **M** | **+9** | **dB** | |

## 匹配网络设计

### L型匹配

```python
#!/usr/bin/env python3
"""
L型匹配网络计算器
"""
import math

def l_match(z1, z2, freq_ghz):
    """
    计算L型匹配网络元件值

    参数:
        z1: 源阻抗 (ohm)
        z2: 负载阻抗 (ohm)
        freq_ghz: 频率 (GHz)

    返回:
        元件类型和值
    """
    w = 2 * math.pi * freq_ghz * 1e9  # 角频率

    # 计算Q值
    if z1 > z2:
        # 并联-串联电感
        q = math.sqrt(z1 / z2 - 1)
        # 元件值
        l = q * z2 / w  # Henry
        c = 1 / (q * z1 * w)  # Farad
        return {
            'type': 'series_ind',
            'L_nH': l * 1e9,
            'C_pF': c * 1e12,
            'Q': q
        }
    else:
        # 串联-并联电容
        q = math.sqrt(z2 / z1 - 1)
        c = 1 / (q * z2 * w)
        l = q * z1 / w
        return {
            'type': 'series_cap',
            'L_nH': l * 1e9,
            'C_pF': c * 1e12,
            'Q': q
        }

def pi_match(z1, z2, q, freq_ghz):
    """
    Pi型匹配网络
    """
    w = 2 * math.pi * freq_ghz * 1e9

    # Q = w * R * C => C = Q / (w * R)
    # Z_series = j * w * L
    if z1 < z2:  # 高Q
        c1 = q / (w * z1) * 1e12  # pF
        c2 = q / (w * (z2 - z1)) * 1e12  # pF
        l = (z2 - z1) / (w * q) * 1e9  # nH
    else:
        c1 = q / (w * z2) * 1e12
        c2 = q / (w * (z1 - z2)) * 1e12
        l = (z1 - z2) / (w * q) * 1e9

    return {'C1_pF': c1, 'C2_pF': c2, 'L_nH': l, 'Q': q}

if __name__ == '__main__':
    # 50ohm to 200ohm @ 2.4GHz
    result = l_match(50, 200, 2.4)
    print(f"匹配类型: {result['type']}")
    print(f"L = {result['L_nH']:.2f} nH")
    print(f"C = {result['C_pF']:.2f} pF")
    print(f"Q = {result['Q']:.2f}")
```

### 传输线计算

```python
#!/usr/bin/env python3
"""
射频传输线计算器
"""
import math

class MicrostripLine:
    """微带线特性计算"""

    def __init__(self, h_mm, w_mm, eps_r, freq_ghz):
        self.h = h_mm * 1e-3      # 介质厚度(m)
        self.w = w_mm * 1e-3      # 线宽(m)
        self.eps_r = eps_r        # 相对介电常数
        self.f = freq_ghz * 1e9  # 频率(Hz)

    def z0(self):
        """计算特性阻抗"""
        h = self.h
        w = self.w
        eps = self.eps_r

        if w/h < 1:
            # 窄微带
            z0 = 60 / math.sqrt(eps) * math.log(8*h/w + w/(4*h))
        else:
            # 宽微带
            z0 = 120 * math.pi / (
                math.sqrt(eps) * (w/h + 1.393 + 0.667*math.log(w/h + 1.444))
            )
        return z0

    def velocity(self):
        """计算相速度"""
        eff_eps = (self.eps_r + 1) / 2  # 近似有效介电常数
        return 3e8 / math.sqrt(eff_eps)

    def wavelength(self):
        """计算波长(mm)"""
        v = self.velocity()
        return v / self.f * 1000

    def loss_dB_per_mm(self, rho=1.68e-8, t_um=35):
        """
        计算导体损耗
        rho: 铜电阻率
        t_um: 铜厚(um)
        """
        skin_depth = math.sqrt(2 * rho / (2 * math.pi * self.f * 4*math.pi*1e-7))
        t = t_um * 1e-6

        if t > 3 * skin_depth:
            effective_t = skin_depth
        else:
            effective_t = t

        R_s = math.sqrt(math.pi * self.f * 4*math.pi*1e-7 * rho)
        R = R_s / (w * effective_t) if self.w * effective_t > 0 else float('inf')

        alpha = R / (2 * self.z0()) * 8.686  # dB
        return alpha

if __name__ == '__main__':
    # FR4板, 1.6mm厚度, 50ohm阻抗 @ 2.4GHz
    line = MicrostripLine(h_mm=1.6, w_mm=3.0, eps_r=4.4, freq_ghz=2.4)
    print(f"特性阻抗: {line.z0():.1f} ohm")
    print(f"波长: {line.wavelength():.1f} mm")
    print(f"损耗: {line.loss_dB_per_mm():.4f} dB/mm")
```

## 射频测试方法

### S参数测量流程

```python
#!/usr/bin/env python3
"""
VNA S参数测量辅助工具
"""
import visa
import numpy as np

class VNA_Controller:
    def __init__(self, addr='TCPIP0::192.168.1.100::INSTR'):
        self.rm = visa.ResourceManager()
        self.inst = self.rm.open_resource(addr)

    def setup_sweep(self, start_ghz, stop_ghz, points=201):
        """配置扫描"""
        self.inst.write('SENS:FREQ:STAR {:f}GHz'.format(start_ghz))
        self.inst.write('SENS:FREQ:STOP {:f}GHz'.format(stop_ghz))
        self.inst.write('SENS:SWE:POIN {:d}'.format(points))
        self.inst.write('CALC:PAR:DEF S11, S11')
        self.inst.write('CALC:PAR:DEF S21, S21')
        self.inst.write('CALC:PAR:DEF S12, S12')
        self.inst.write('CALC:PAR:DEF S22, S22')

    def measure(self):
        """执行测量"""
        self.inst.write('INIT:IMM')
        self.inst.write('CALC:PAR:SEL S11')
        s11 = self.inst.query_binary_values('CALC:DATA:SDAT?')
        # ... 其他S参数
        return {
            'S11': s11,
            'S21': s21,
            'S12': s12,
            'S22': s22
        }

    def save_touchstone(self, filename):
        """保存为Touchstone格式"""
        data = self.measure()
        freq = self.inst.query_binary_values('SENS:FREQ:DATA?')
        with open(filename, 'w') as f:
            f.write('# Hz S RI R 50\n')
            for i, f_hz in enumerate(freq):
                f.write('{:e} {:.6f} {:.6f} {:.6f} {:.6f} '
                        '{:.6f} {:.6f} {:.6f} {:.6f}\n'.format(
                            f_hz,
                            data['S11'][i].real, data['S11'][i].imag,
                            data['S21'][i].real, data['S21'][i].imag,
                            data['S12'][i].real, data['S12'][i].imag,
                            data['S22'][i].real, data['S22'][i].imag
                        ))

    def close(self):
        self.inst.close()
        self.rm.close()
```

### EMC预兼容测试

```python
#!/usr/bin/env python3
"""
EMC预兼容测试脚本
"""
import numpy as np
from scipy import signal

class EMC_Test:
    """EMC辐射预兼容测试"""

    def __init__(self, freq_range_mhz=(30, 1000)):
        self.freq_min = freq_range_mhz[0] * 1e6
        self.freq_max = freq_range_mhz[1] * 1e6
        self.limit_lines = {
            'class_a': self._class_a_limit,
            'class_b': self._class_b_limit
        }

    @staticmethod
    def _class_a_limit(f_mhz):
        """Class A限值 (dBuV/m @ 10m)"""
        if f_mhz < 230:
            return 40  # 40-230MHz: 40 dBuV/m
        elif f_mhz < 1000:
            return 47  # 230-1000MHz: 47 dBuV/m
        return 0

    @staticmethod
    def _class_b_limit(f_mhz):
        """Class B限值 (dBuV/m @ 10m)"""
        if f_mhz < 230:
            return 30 + 20/200 * f_mhz  # 30-230MHz: 渐变
        elif f_mhz < 1000:
            return 37  # 230-1000MHz: 37 dBuV/m
        return 0

    def apply_antenna_factor(self, v_emf_dbuv, f_mhz):
        """天线因子转换为场强"""
        # AF (dB/m) 近似
        af = 20 + 0.03 * f_mhz if f_mhz < 300 else 40 + 1.2 * np.log10(f_mhz)
        e = v_emf_dbuv + 20 - af  # dBuV/m
        return e

    def check_compliance(self, measured_dbuv, freq_mhz, limit_class='class_b'):
        """检查符合性"""
        limit_fn = self.limit_lines[limit_class]
        margin = []

        for f, v in zip(freq_mhz, measured_dbuv):
            limit = limit_fn(f)
            m = limit - v
            margin.append(m)

        return {
            'pass': all(m > 0 for m in margin),
            'margin_dB': margin,
            'worst_case': min(margin),
            'fails': [(f, m) for f, m in zip(freq_mhz, margin) if m < 0]
        }
```
