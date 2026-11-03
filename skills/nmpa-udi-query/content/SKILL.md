---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8e5fc9dfa3e860493d2e0dad97bef5e5
    PropagateID: 8e5fc9dfa3e860493d2e0dad97bef5e5
    ReservedCode1: 3046022100c0be1098ed6d4cfee1556db33c3da3d543da4e9165cfe5dfe331a0f4bc324b3a022100e914f73c0d63bb697f9632b6426efac9e09552b07bd5b83452496b238db9c6f8
    ReservedCode2: 30440220032cad19edb9dd6ff5f9612684f2f6de1b4b0a0caf692451d70e6cc4074ce1cd02203c5b91a1a5d783718c4db9cf059b9dd07b9f3c2deeb6d9695e25952c1fcd4655
author: MiniMax Agent
description: NMPA医疗器械UDI查询工具 - 从国家药品监督管理局数据库查询企业产品注册证信息，支持自动生成Excel/CSV表格。
name: nmpa-udi-query
tags:
    - 医疗器械
    - UDI
    - NMPA
    - 注册证
    - 数据查询
trigger_keywords:
    - NMPA查询
    - 医疗器械查询
    - UDI查询
    - 医疗器械注册证
    - 查询医疗器械数据
    - 企业产品信息
    - NMPA
    - 医疗器械
version: 1.0.0
---

# NMPA医疗器械UDI查询技能

## 技能简介

这是一个用于从国家药品监督管理局（NMPA）医疗器械唯一标识（UDI）数据库查询指定企业产品注册证信息的智能工具。

**数据来源**: https://udi.nmpa.gov.cn

## 触发方式

当用户提到以下关键词时，自动触发此技能：
- "查询" + 企业名称 + "医疗器械"
- "NMPA查询"
- "UDI查询"
- "医疗器械注册证"
- "查询医疗器械数据"

## 执行流程

### 1. 接收用户请求
用户只需提供**企业名称**即可，例如：
- "查询迈瑞医疗的医疗器械数据"
- "帮我查一下广州瑞派医疗的产品注册证信息"
- "搜索珠海普生医疗的所有医疗器械"

### 2. 执行查询
使用Python爬虫连接NMPA UDI数据库：
```python
# API端点
POST https://udi.nmpa.gov.cn/getDeviceList.html

# 参数
{
    "query": "企业名称",
    "searchType": "1",
    "rows": "15",
    "page": "1"
}
```

### 3. 获取产品详情
对于每个产品，获取注册证编号：
```python
# 详情页URL
GET https://udi.nmpa.gov.cn/showDetailCX.html?deviceRecordKey={deviceRecordKey}
```

### 4. 生成结果表格
输出包含以下三列的数据：
| 产品名称 | 最小销售单元产品标识 | 注册证编号 |

### 5. 保存文件
- **Excel文件**: `nmpa_udi_results_{企业名称}.xlsx`
- **CSV文件**: `nmpa_udi_results_{企业名称}.csv`

## 输出格式

### 命令行输出
```
============================================================
NMPA医疗器械唯一标识(UDI)数据库爬虫
============================================================
搜索企业: {企业名称}
------------------------------------------------------------
[步骤1/2] 获取产品列表...
共获取 {数量} 条产品记录
[步骤2/2] 获取注册证编号...
总计: {数量} 条记录
CSV文件已保存: nmpa_udi_results_{企业名称}.csv
Excel文件已保存: nmpa_udi_results_{企业名称}.xlsx
```

### 示例结果
| 产品名称 | 最小销售单元产品标识 | 注册证编号 |
|---------|-------------------|-----------|
| 一次性使用输尿管内窥镜导管 | 06972498490264 | 皖械注准20242060229 |
| 灌注吸引系统 | 06972498491001 | 皖械注准20252060025 |
| 电子内窥镜图像处理器 | 06972498490318 | 皖械注准20222060241 |

## 技术实现

### 依赖环境
```bash
pip install requests beautifulsoup4 openpyxl pandas
```

### 核心代码结构
```python
class NMPAUDIScraper:
    def get_product_list(company_name, max_pages):
        """获取产品列表"""

    def get_registration_number(device_record_key):
        """获取注册证编号"""
```

### API配置
- **基础URL**: https://udi.nmpa.gov.cn
- **列表API**: POST /getDeviceList.html
- **详情API**: GET /showDetailCX.html
- **请求头**: X-Requested-With: XMLHttpRequest

## 注意事项

1. **频率限制**: 建议每次请求间隔0.3-0.5秒
2. **数据用途**: 仅供学习研究使用
3. **商业使用**: 请遵守相关法律法规
4. **注册证格式**: 部分产品可能有多个注册证编号（用逗号分隔）

## 示例查询记录

| 企业名称 | 查询结果数量 | 主要产品类型 |
|---------|------------|------------|
| 迈瑞 | 45条 | 化学发光免疫分析试剂盒 |
| 广州瑞派医疗 | 54条 | 一次性使用电子内窥镜导管 |
| 珠海普生医疗 | 58条 | 电子内窥镜、支气管成像导管 |
| 安徽省幸福工场医疗设备有限公司 | 63条 | 输尿管内窥镜、取石套件 |

## 使用建议

1. 用户只需提供**企业名称关键词**即可
2. 可以指定**查询页数**（默认5页，每页约15条）
3. 查询结果自动生成**Excel和CSV**两种格式
4. 支持查看**实时进度**和**预览前5条数据**
