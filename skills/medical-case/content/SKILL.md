---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d935a4ad2c41a380ab552b9eba6d1e42
    PropagateID: d935a4ad2c41a380ab552b9eba6d1e42
    ReservedCode1: 3044022012271d91d82981e16594ada2b2d0cd119afe536200bf61cbd03fd8c926f8809402203300df7da4bc7b5baca9280135c308c697edb8297b3f7cadf227641e26cf78d2
    ReservedCode2: 3044022055cd31bacf026752bd79cacba05d0509ba595df02dbb40388fe7ad3e7594e6cc02207b491b5d799ccfc428230dfe513eb38ab68b0adb61d8088fc4561bf63d5f7895
---

# 医疗病例文档生成技能（专业版）
> T/CHSA 002-2020 口腔AI初诊大病例系统
> 基于 SOAP 格式 + BPE 牙周检查标准

---

## 文档类型

| 类型 | 触发词 | 内容 |
|------|--------|------|
| 初诊大病例 | 「初诊」「大病例」「SOAP」 | S+O+A+P 完整结构 |
| 病程记录 | 「病程」「复诊」 | 日期+主诉+检查+处理+医嘱 |
| 病例回顾 | 「终止」「结束」「回顾」 | 全程时间线+总结+Word输出 |

---

## SOAP 标准结构

### 【S - Subjective 主观资料】
- **主诉**：症状+部位+时间（<20字）
- **现病史**：发病时间、疼痛性质、加重/缓解因素、既往治疗史
- **既往史/家族史**：继承自全身病史评估表

### 【O - Objective 客观检查】
- **影像AI分析**：曲面断层片判读（骨吸收/龋坏/阻生齿定位）
- **牙周检查**：BPE筛查（6区段）或6位点全口探诊
- **牙体牙髓**：视诊+探诊+叩诊+松动度+活力测试
- **咬合与关节**：颌骨关系+张口度+张口型+关节弹响

### 【A - Assessment 评估/诊断】
- 牙体牙髓诊断（急性/慢性牙髓炎/根尖周炎）
- 牙周诊断（2018新分类：Stage I-IV, Grade A-C）
- 风险评估（CAMBRA / 牙周风险计算器）

### 【P - Plan 治疗计划】
- 第一阶段（紧急处理）
- 第二阶段（基础治疗 Phase I）
- 第三阶段（专科治疗 Phase II）
- 第四阶段（维护期 SPT）

---

## BPE 牙周检查标准

**6区段记录：**
| 区段 | 牙位 |
|------|------|
| 右上 | 17-14 |
| 上前 | 13-23 |
| 左上 | 24-27 |
| 左下 | 34-37 |
| 下前 | 43-33 |
| 右下 | 44-47 |

**BPE编码：** 0→无出血 | 1→有出血 | 2→有结石 | 3→3.5-5.5mm | 4→>5.5mm或根分叉

---

## 工作流

### Step 1：接收素材
- 🎤 语音 → `listen_audio` 转写
- 🖼️ X光片/照片 → `images_understand` 分析
- 📋 文字/表单 → 直接使用

### Step 2：结构化提取
按 SOAP 四段式填入：
```
S：主诉 + 现病史 + 既往史
O：影像所见 + 牙周检查 + 牙体检查 + 关节检查
A：诊断 + 风险评级
P：分阶段治疗计划
```

### Step 3：生成文档
- 调用 `/workspace/scripts/medical_case_generator.py`
- 文档类型自动识别（主诉→初诊 / 有"终止"→病例回顾）
- 输出 `.docx`，A4专业格式（含页眉/页脚/三线表）

---

## 合规与安全

- 过敏史、既往史：强制人工复核标识 ⚠️
- AI生成内容标注「AI辅助」字样
- 符合《医疗纠纷预防和处理条例》

---

## 快速启动

| 用户发送 | 系统动作 |
|---------|---------|
| 语音 + 「写初诊病历」 | 转写→分析X光→生成SOAP初诊大病例→发.docx |
| 语音/图片 + 「病程」 | 生成复诊病程记录 |
| 所有素材 + 「终止」 | 生成完整病例回顾Word文档 |

---

## 配置文件格式（JSON）

```json
{
  "DocType": "初诊大病例",
  "ClinicName": "诊所名称",
  "CaseNumber": "病历号",
  "PatientName": "姓名",
  "Gender": "男/女",
  "Age": "年龄",
  "Phone": "电话",
  "VisitDate": "yyyy-MM-dd",
  "SOAP": {
    "S": {
      "ChiefComplaint": "主诉<20字",
      "HistoryOfPresentIllness": "现病史",
      "PastMedicalHistory": "既往史",
      "AllergyHistory": "过敏史"
    },
    "O": {
      "XrayAnalysis": "影像AI判读",
      "BPEResults": {"UR": "", "UL": "", "LL": "", "LR": ""},
      "DentalExam": "牙体牙髓检查",
      "TMDExam": "颞下颌关节检查"
    },
    "A": {
      "Diagnosis": "诊断",
      "RiskLevel": "风险评级"
    },
    "P": {
      "Phase1": "紧急处理",
      "Phase2": "基础治疗",
      "Phase3": "专科治疗",
      "Phase4": "维护期"
    }
  },
  "ImageAnalyses": [
    {"ImageType": "曲面断层片", "Description": "AI判读描述"}
  ]
}
```
