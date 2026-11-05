---
name: brand-commercial-negotiation
description: 品牌商务谈判全链路自动化系统，一键生成品牌能力包、GEO知识包、跨平台内容包、报价策略包、分发编排包与谈判总包。当用户要求生成完整商务谈判方案、创建品牌合作提案、制定报价策略、制作分发计划、设计谈判脚本时使用。
---

# Brand Commercial Negotiation（品牌商务谈判中枢）

## 技能概述

把品牌谈判变成可复用的"六包合一"一键生成系统：
1. **品牌能力包** - 品牌档案、定位、差异化
2. **GEO知识包** - 标准答案、FAQ矩阵、技术优化
3. **跨平台内容包** - 小红书/抖音/公众号/提案版
4. **报价策略包** - A/B/C方案、价格带、谈判话术
5. **分发编排包** - 阶段节奏、渠道计划、资源位打法
6. **谈判总包** - 开场/异议处理/收口话术

## 触发条件

当用户说/要求以下内容时激活：
- "生成品牌商务谈判方案"
- "创建品牌合作提案"
- "制定报价策略和谈判脚本"
- "制作跨平台内容包"
- "设计分发计划和谈判总包"
- "一键生成六包"
- "我要跟XX平台/硬件厂谈合作"
- "把产品手册改成可被AI引用的知识包"

## 执行流程

### 阶段一：输入解析

解析用户输入，构建标准输入对象：

```python
{
    "brand": {
        "brand_name": str,
        "brand_id": str | null,
        "company_legal_name": str | null,
        "products_or_services": list[str] | null,
        "industry": str | null,
        "region": str | null
    },
    "goal": {
        "primary_goal": str,
        "success_metrics": list[str] | null
    },
    "partner": {
        "partner_type": str,
        "partner_name": str | null,
        "partner_size": str | null,
        "partner_resources": list[str] | null
    },
    "constraints": {
        "time_window": str | null,
        "budget_preference": str | null,
        "forbidden_claims": list[str] | null,
        "tone_preference": str | null,
        "red_lines": list[str] | null
    },
    "assets": {
        "official_materials": list[str] | null,
        "product_specs": list[str] | null,
        "certifications": list[str] | null,
        "case_studies": list[str] | null
    }
}
```

### 阶段二：品牌中枢处理

调用 `BrandHubService` 生成品牌资产：

1. **意图守卫** - 识别目标类型（曝光/激活/转化/合作）
2. **约束守卫** - 提取禁忌、语气、红线、时间窗口
3. **品牌建档** - 生成品牌档案、事实层、证据层
4. **术语锁定** - 统一口径、禁忌表达、标准签名

### 阶段三：GEO知识生产

调用 `GEOAdvisor` 生成知识包：

1. **问题挖掘** - 选型/对比/参数/场景/采购问题库
2. **标准答案** - 标题/要点/边界/署名结构化答案
3. **FAQ矩阵** - 结论+解释+对比+案例+边界五要素
4. **高引用模板** - 标题公式/开篇/主体/结尾CTA
5. **技术优化** - Schema标记/抓取优化/权威背书

### 阶段四：内容工厂

调用 `ContentFactory` 生成跨平台内容：

1. **小红书** - 标题/正文/评论/话题标签
2. **抖音** - 钩子/脚本/镜头建议/字幕
3. **公众号** - 标题/大纲/全文/CTA
4. **提案版** - 一页纸要点/演示脚本/FAQ

### 阶段五：报价策略

调用 `PricingStrategyService` 生成报价方案：

1. **机会评估** - S/A/B/C等级评定
2. **方案A/B/C** - 一次性/分成/混合三套方案
3. **价格带** - 最低价/目标价/上限价
4. **谈判话术** - 价值证明/反压价/买断反制/收口推进

### 阶段六：分发编排

调用 `DistributionOrchestrator` 生成分发计划：

1. **阶段节奏** - 预热/首发/巩固/复盘
2. **渠道计划** - 内容绑定/频率/KPI/追踪标签
3. **资源位打法** - Banner/入口/联名话题/线下联动
4. **数据回流** - 指标/频率/解释/下一轮应用

### 阶段七：谈判总包

整合所有输出，生成完整谈判套件：

1. **开场话术** - 问候/价值主张/议程设置
2. **发现问题** - 探索性问题清单
3. **定位话术** - 差异化卖点呈现
4. **证明点** - 数据/案例/背书
5. **报价交付** - 方案对比/价值拆解
6. **异议处理** - 太贵/买断/排他/快速交付
7. **收口推进** - 下一步/承诺/跟进

## 输出结构

```json
{
    "deliverables": {
        "brand_profile_summary": {
            "brand_name": str,
            "version": str,
            "positioning": str,
            "core_capabilities": list[str],
            "fact_layer": dict,
            "evidence_layer": list[str],
            "forbidden_claims": list[str]
        },
        "geo_knowledge_pack": {
            "geo_concepts": dict,
            "standard_answer": dict,
            "faq_matrix": list[dict],
            "high_citation_templates": dict,
            "technical_optimization": dict
        },
        "content_bundle": {
            "xiaohongshu": dict,
            "douyin": dict,
            "wechat_official": dict,
            "proposal_version": dict
        },
        "pricing_package": {
            "opportunity_grade": str,
            "packages": list[dict],
            "pricing_bands": dict,
            "negotiation_chips": dict,
            "negotiation_scripts": dict
        },
        "distribution_plan": {
            "phases": list[dict],
            "channel_plans": list[dict],
            "resource_tactics": dict,
            "data_feedback_hooks": dict
        },
        "negotiation_master_kit": {
            "opening": list[str],
            "discovery_questions": list[str],
            "positioning_script": str,
            "proof_points": list[str],
            "objection_handling": dict,
            "closing_advance": str
        }
    },
    "assumptions": list[str],
    "missing_info_to_request_next": list[str],
    "next_actions": list[str]
}
```

## 合规要求

1. **禁止输出**：诱导违规、虚假背书、无法验证的承诺、夸大数据
2. **硬编拒绝**：若用户要求"硬编数据/硬造背书"，必须拒绝并提供替代方案
3. **事实一致**：所有输出必须基于品牌事实层，禁止编造
4. **口径统一**：跨平台内容必须与GEO标准答案对齐

## 参考资源

- 脚本执行器：`scripts/__init__.py`（核心逻辑已加密）
- 品牌档案模板：`references/brand_profile_template.json`
- FAQ矩阵模板：`references/faq_matrix_template.json`
- 报价方案模板：`references/pricing_package_template.json`
- GEO标准答案模板：`references/geo_standard_answer_template.md`

## 安全说明

⚠️ **本技能采用闭源保护**
- 核心逻辑已通过 Base64 加密
- 用户无法查看、修改或二次开发源码
- 仅可通过公开接口调用功能

## 版本信息

- **版本**: 1.0.0
- **作者**: MiniMax Agent
- **分类**: 商业智能/品牌管理
- **标签**: 品牌谈判, GEO优化, 内容生成, 报价策略, 分发编排, 谈判总包
