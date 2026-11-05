# STDF 数据分析报告 - example.std

## 批次概况

| 指标 | 数值 |
|------|------|
| 测试数量 | 570 DUTs |
| 测试项数 | 395 项 |
| 通过数量 | 486 (85.3%) |
| 失败数量 | 84 (14.7%) |
| **良率** | **85.26%** |

## 整体生产状态评价

⚠️ **警告**: 发现 **63 个高风险测试项** (CPK < 1.0)，**201 个需关注项** (CPK < 1.33)

批次良率 85.26%，但存在严重的过程能力问题：
- **TX_IDD_Current_AVDD18**: CPK 异常 (-1764.01)，实测值单位与规格限不一致
- **Frequency Error 系列**: 多个频点误差严重超规格，CPK 在 -3.86 ~ -0.94 范围

## 关键风险项 - CPK < 1.0 (按 CPK 从低到高排序)

### 1. TX_IDD_Current_AVDD18
- CPK = **-1764.01** (严重)
- 均值 = 0.2337, 标准差 = 0.0094
- 实测范围 = [0.1912, 0.2604]
- 规格限 = [50.0, 350.0]
- **问题**: 测试数据单位可能与规格限单位不一致，需检查

### 2. Frequency Error 系列 (频率误差)
| 测试项 | CPK | 均值 | 标准差 | 分布 |
|--------|-----|------|--------|------|
| Frequency Error_703MHz | -3.86 | -19339.86 | 1667.89 | normal |
| Frequency Error_849MHz | -3.86 | -23335.59 | 2014.25 | normal |
| Frequency Error_915MHz | -3.86 | -25141.82 | 2170.86 | normal |
| Frequency Error_2020MHz | -3.85 | -55432.03 | 4796.62 | normal |
| Frequency Error_2300MHz | -3.85 | -63107.58 | 5461.62 | bimodal |
| Frequency Error_2350MHz | -3.85 | -64473.44 | 5580.16 | normal |
| Frequency Error_2400MHz | -3.85 | -65840.07 | 5699.00 | bimodal |
| Frequency Error_2496MHz | -3.85 | -68477.88 | 5927.35 | normal |
| Frequency Error_3300MHz | -3.84 | -90776.31 | 7873.91 | normal |
| Frequency Error_3500MHz | -3.84 | -96241.02 | 8348.02 | normal |
| Frequency Error_3700MHz | -3.84 | -101709.42 | 8822.79 | normal |

**问题**: 频率误差实测值在 -10000 ~ -100000 范围，但规格限为 [-1.0, 1.0]，表明：
1. 可能是测试程序中 Limits 设置错误，或
2. 数据存储单位问题 (Hz vs kHz/MHz)

### 3. 其他 Cpk < 1.0 项
| 测试项 | CPK | 异常点 | 分布 |
|--------|-----|--------|------|
| Frequency Error_2690MHz | -1.81 | 1 | right_skewed |
| Frequency Error_2590MHz | -1.77 | 1 | right_skewed |
| Frequency Error_1895MHz | -0.94 | 1 | left_skewed |

## 需关注项 - CPK < 1.33 (前15项)

| 测试项 | CPK | 异常点(3σ) |
|--------|-----|------------|
| PSM_Enter_wakeup1_Current | 1.00 | 4 |
| Continuity_VSS - GPIO_8 | 1.00 | 1 |
| ImageLeakage_915MHz | 1.03 | 7 |
| TX_MHB1_N41_MIN_Power_2590MHz | 1.03 | 1 |
| LO_Leak_3700M | 1.09 | 6 |
| LO_Leak_849M | 1.10 | 6 |
| LO_Leak_3500M | 1.13 | 7 |
| LO_Leak_2020M | 1.14 | 7 |
| LO_Leak_2496M | 1.14 | 6 |
| LO_Leak_703M | 1.14 | 4 |
| LO_Leak_2350M | 1.15 | 6 |
| PowerShort - V09_CPU | 1.16 | 2 |
| LO_Leak_2300M | 1.18 | 7 |
| LO_Leak_2400M | 1.21 | 7 |
| LO_Leak_3300M | 1.23 | 8 |

**观察**: LO_Leak (本振泄漏) 系列测试项普遍存在异常点较多的问题

## 可能原因分析

1. **测试程序 Limits 设置问题**
   - Frequency Error 系列规格限 [-1, 1] 可能应为 kHz 单位
   - TX_IDD_Current_AVDD18 数据可能需要乘以 1000

2. **RF 性能问题**
   - LO_Leak 和 ImageLeakage 异常点较多可能与射频模块性能波动有关
   - 部分频点呈双峰分布暗示存在工艺差异

3. **设备稳定性**
   - 多项 Continuity 测试标准差较大
   - 建议检查测试机台通道校准状态

## 改进建议

### 紧急事项 (需立即处理)
1. **复查 Frequency Error 测试项**
   - 确认规格限单位设置
   - 验证测试程序数据处理逻辑

2. **复查 TX_IDD_Current 测试项**
   - 确认 mA 单位的正确解析
   - 验证数据与规格限的匹配性

### 短期改进
3. **对 LO_Leak 异常 DUT 进行 PFA**
   - 选取异常点样本进行物理失效分析
   - 确定失效模式

4. **增加 WAT 关联分析**
   - 将 FT 数据与晶圆测试数据关联
   - 定位问题根因

### 持续改进
5. **建立 CPK 监控机制**
   - 对 CPK < 1.33 项建立趋势监控
   - 设置预警阈值

## ChipID 分布统计

- 唯一 ChipID 组合数: **570** (每个 DUT 唯一)
- 主要 ID 分布: ID0=24 或 88, ID1=221, ID2=88, ID3=95~194

---

*报告生成时间: 2026-03-23*
