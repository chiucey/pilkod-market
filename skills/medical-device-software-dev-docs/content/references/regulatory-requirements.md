# 医疗器械软件法规要求参考

## 一、国际标准

### 1. IEC 62304:2006+AMD1:2015
**医疗器械软件 - 软件生命周期过程**

核心要求:
- 软件开发过程（策划、需求、设计、实现、验证、发布）
- 软件维护过程
- 软件风险管理过程
- 软件配置管理

### 2. ISO 14971:2019
**医疗器械 - 风险管理在医疗器械中的应用**

核心要求:
- 风险管理体系建立
- 危害识别
- 风险估计
- 风险评价
- 风险控制
- 剩余风险评价
- 风险/受益分析
- 风险管理报告

### 3. IEC 62304 AMD1:2024（新增）
**医疗器械软件 - 网络安全补充**

新增要求:
- 网络安全策划
- 网络安全风险分析
- 网络安全设计
- 网络安全验证与确认
- 网络安全维护

## 二、中国法规要求

### 1. NMPA法规体系

| 法规/指导原则 | 适用范围 |
|---------------|----------|
| 《医疗器械监督管理条例》(国务院令第739号) | 医疗器械监督管理 |
| 《医疗器械生产监督管理办法》 | 生产许可管理 |
| 《医疗器械注册与备案管理办法》 | 注册申报要求 |
| YY/T 0664-2020 | 等同采用IEC 62304 |
| GB/T 25000系列 | 软件质量要求 |
| 《医疗器械软件注册审查指导原则》(2022年修订) | 软件注册技术审评 |
| 《医疗器械网络安全注册审查指导原则》 | 网络安全审查 |

### 2. 注册申报资料要求

根据《医疗器械软件注册审查指导原则》:

**软件描述文档**:
1. 企业名称、地址、联系方式
2. 软件产品概述
3. 软件规范
   - 功能列表
   - 性能指标
   - 使用限制
4. 危害和风险分析
5. 软件设计文档
   - 软件架构
   - 软件功能
   - 软件接口
6. 软件开发和维护计划
7. 软件需求规范
8. 软件测试计划
9. 软件测试结果
10. 软件变更记录
11. 配置管理文档
12. 其他资料

## 三、美国FDA要求

### 1. 法规基础
- 21 CFR Part 820 - 质量体系法规
- 21 CFR Part 11 - 电子记录与签名
- FDA软件安全分类指南

### 2. 510(k)/PMA申报

**Software Documentation**:
- Software Description
- Device Hazard Analysis
- Software Requirements Specification
- Software Architecture Design Chart
- Software Design Specification
- Software Verification and Validation Documentation
- Unresolved Anomalies (Bugs/Defects)
- Software History Record (SHR)

### 3. FDAGuidance
- "Off-The-Shelf Software Use in Medical Devices" (FDA)
- "Cybersecurity for Networked Medical Devices Containing Off-The-Shelf Software"
- "Premarket Submissions for Management of Cybersecurity in Medical Devices"

## 四、欧盟MDR要求

### 1. 法规基础
- Regulation (EU) 2017/745 (MDR)
- EN 62304:2006+A1:2015 (等同采用IEC 62304)
- EN ISO 14971:2019

### 2. 技术文档要求

MDR Annex II, III要求:
- 产品描述与规格
- 设计与制造信息
- 通用安全与性能要求
- 风险管理文档
- 临床评价
- 软件文档（按MDR Article 11）

### 3. 软件分类
依据MDR Rule 11:
- Class I: 非诊断功能
- Class IIa: 诊断/监测功能
- Class IIb/III: 治疗决策功能

## 五、文档编制检查清单

### 立项阶段
- [ ] 确定软件安全分类
- [ ] 制定风险管理计划
- [ ] 制定软件开发计划
- [ ] 确定项目团队与职责

### 需求阶段
- [ ] 收集用户需求
- [ ] 编写软件需求规格
- [ ] 建立需求追溯矩阵
- [ ] 需求评审与批准

### 设计阶段
- [ ] 架构设计评审
- [ ] 详细设计评审
- [ ] 更新追溯矩阵
- [ ] 安全设计评审

### 实现阶段
- [ ] 编码规范执行
- [ ] 代码评审
- [ ] 单元测试
- [ ] 配置管理

### 验证阶段
- [ ] 测试计划编制
- [ ] 测试用例设计
- [ ] 测试执行
- [ ] 缺陷管理
- [ ] 覆盖率分析

### 确认阶段
- [ ] 确认计划编制
- [ ] 临床评价
- [ ] 实际使用环境验证
- [ ] 确认报告编制

### 维护阶段
- [ ] 维护计划
- [ ] 问题跟踪
- [ ] 变更控制
- [ ] 上市后监测
