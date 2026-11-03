# Scoring And Action Rules

Use these rules when processing an Amazon keyword library into listing and advertising actions.

## Decision Columns

Add these columns to the keyword sheet:

| Column | Purpose | Recommended values |
| --- | --- | --- |
| Level-1 English root | Concrete English root extracted from the keyword | `pop up canopy`, `popup canopy`, `coleman`, `10x10 canopy`, `waterproof`, etc. |
| Product intent | Buyer intent fit | precise, near-precise, testable, off-intent |
| Attribute match | Whether keyword constraints match the product title and selling points | match, no keyword attribute, needs product evidence, mismatch |
| Brand risk | Whether keyword contains competitor/proprietary brand | yes, no |
| Opportunity score | Sum of six scoring dimensions | 6-30 |
| Priority | Execution priority | S, A, B, C |
| Risk note | Human-readable reason for caution/exclusion | free text |
| Final action | Execution bucket | main push, test, backend, negative |
| Placement/ad suggestion | Listing or ad placement | title, bullet, Search Terms, SP exact, SP phrase/broad, negative |

## Level-1 English Root

This column must contain the actual English root, not a Chinese translation or a broad category label.

Use the most decision-relevant English root from the keyword itself:

| Keyword example | Correct level-1 English root | Why |
| --- | --- | --- |
| `10x10 pop up canopy` | `10x10 canopy` | exact size/product-form root |
| `popup canopy tent` | `popup canopy` | exact product form root |
| `canopy tent 10x20` | `10x20 canopy` | hard size attribute is the key root |
| `coleman pop up canopy` | `coleman` | brand root overrides product form for risk review |
| `eurmax canopy tent` | `eurmax` | target/self brand root for separate review |
| `waterproof pop up canopy` | `waterproof` | hard performance attribute is the key root |
| `heavy duty canopy tent` | `heavy duty` | hard durability attribute is the key root |
| `canopy weights` | `canopy weights` | adjacent accessory root |
| `outdoor shade canopy` | `outdoor canopy` | scenario/root broader than the core product |

Do not use vague operational categories such as `core canopy keyword`, `brand/product-line`, `shade adjacent`, `canopy accessory`, or `main keyword`. Those are analysis categories, not level-1 English roots.

Recommended priority when multiple roots appear:

1. Explicit brand or product line: `coleman`, `eurmax`, `e-z up`, `abccanopy`, `crown shades`.
2. Hard attribute that can affect conversion: `10x10 canopy`, `10x20 canopy`, `waterproof`, `heavy duty`, sidewalls, frame type.
3. Exact product form: `pop up canopy`, `popup canopy`, `canopy tent`.
4. Broader or adjacent product form: `outdoor canopy`, `instant canopy`, `shade canopy`.
5. Scenario/accessory root: `canopy weights`, `canopy sidewalls`, `vendor booth canopy`, `beach canopy`.

## Intent Labels

- `precise`: buyer is probably looking for this exact product form.
- `near-precise`: buyer intent is close but broader than the product's exact identity.
- `testable`: related scenario or adjacent product need; useful for controlled exploration.
- `off-intent`: buyer likely wants another product form, incompatible use case, or unrelated solution.

## Attribute Matching

Attribute matching must compare keyword attributes against the user's product title and selling points/bullets. Do not finalize attribute matching from the keyword table alone.

Before finalizing this column, extract product evidence from the title and bullets:

- Product form: e.g. pop up canopy, canopy tent, instant shelter, canopy weights.
- Size/specs: 10x10, 10x20, dimensions, pack count, sidewall count, frame type, leg style.
- Material/performance: steel frame, aluminum frame, waterproof, UV protection, fire retardant, CPAI-84, etc.
- Usage constraints: outdoor event, vendor booth, patio, beach, camping, commercial use, carport/gazebo substitute.

Use these labels:

| Label | Use when |
| --- | --- |
| `match` | The keyword specifies an attribute and the product title/selling points support it. |
| `no keyword attribute` | The keyword does not specify a comparable size/material/model/spec attribute. |
| `needs product evidence` | The keyword specifies an attribute, but the provided title/selling points do not prove whether the product matches it. Ask for missing specs before final delivery. |
| `mismatch` | The keyword specifies an attribute that conflicts with the title/selling points. |

Examples:

| Keyword | Product evidence | Attribute match |
| --- | --- | --- |
| `10x10 pop up canopy` | Title says 10x10 instant canopy | `match` |
| `10x20 pop up canopy` | Title says 10x10 canopy only | `mismatch` |
| `waterproof pop up canopy` | Bullets say water-resistant only, not waterproof | `mismatch` |
| `heavy duty canopy tent` | Title/bullets do not mention frame strength, weight, or commercial-duty claims | `needs product evidence` |
| `popup canopy tent` | No size/material/model attribute in keyword | `no keyword attribute` |

If `needs product evidence` remains in a final workbook, clearly flag it as unresolved and do not treat the term as main push until the user confirms the missing attribute.

## Score Dimensions

Calibrate thresholds to the category. The example formulas assume these columns:

- `D`: relevance score
- `E`: weekly search volume
- `G`: conversion rate
- `I`: suggested mid bid/CPC
- `K`: Top3 click concentration
- `L`: Top3 conversion concentration
- `S`: product intent

Use this source-column mapping when naming or explaining helper scores:

| Helper score | Source column |
| --- | --- |
| Relevance score | `相关性得分` |
| Product intent score | Added `产品意图` / `Product intent` column |
| Search volume score | `周搜索量` |
| Conversion score | `24小时归因的点击转化率` |
| CPC score | `建议竞价(中)` |
| Competition environment score | Average of `Top3点击集中度` and `Top3转化集中度` |
| Opportunity score | Sum of the six helper scores above |
| Priority | Opportunity score after hard exclusions for brand risk, attribute mismatch, unresolved product evidence, or off-intent |

### Relevance Score

```excel
=IF(D2>=80,5,IF(D2>=60,4,IF(D2>=40,3,IF(D2>=20,2,1))))
```

### Product Intent Score

If using Chinese labels:

```excel
=IF(S2="精准",5,IF(S2="较精准",4,IF(S2="可测试",2,0)))
```

If using English labels:

```excel
=IF(S2="precise",5,IF(S2="near-precise",4,IF(S2="testable",2,0)))
```

### Search Volume Score

```excel
=IF(E2>=3000,5,IF(E2>=1500,4,IF(E2>=800,3,IF(E2>=300,2,1))))
```

### Conversion Score

```excel
=IF(OR(G2="",ISBLANK(G2)),1,IF(G2>=0.22,5,IF(G2>=0.18,4,IF(G2>=0.14,3,IF(G2>=0.1,2,1)))))
```

### CPC Score

Lower CPC is better:

```excel
=IF(OR(I2="",ISBLANK(I2)),3,IF(I2<=0.8,5,IF(I2<=0.95,4,IF(I2<=1.1,3,IF(I2<=1.25,2,1)))))
```

### Competition Environment Score

Use the average of Top3 click concentration and Top3 conversion concentration. Lower concentration is better:

```excel
=IF(OR(K2="",ISBLANK(K2),L2="",ISBLANK(L2)),3,
   IF(((K2+L2)/2)<=0.2,5,
   IF(((K2+L2)/2)<=0.275,4,
   IF(((K2+L2)/2)<=0.35,3,
   IF(((K2+L2)/2)<=0.45,2,1)))))
```

## Opportunity Score

```text
Opportunity score = relevance score + intent score + search volume score + conversion score + CPC score + competition environment score
```

Score range is usually 6-30.

## Priority

Use this conceptual mapping:

- `S`: 22+ or top calibrated tier
- `A`: 18-21
- `B`: 14-17
- `C`: 13 or below, or any hard exclusion

If the workbook uses a stricter calibrated version, this formula is acceptable:

```excel
=IF(OR(U2="是",T2="不匹配",T2="需要产品信息",S2="跑偏"),"C",
   IF(AB2>=25,"S",
   IF(AB2>=20,"A",
   IF(AB2>=15,"B","C"))))
```

For English labels:

```excel
=IF(OR(U2="yes",T2="mismatch",T2="needs product evidence",S2="off-intent"),"C",
   IF(AB2>=25,"S",
   IF(AB2>=20,"A",
   IF(AB2>=15,"B","C"))))
```

## Final Action Mapping

Apply hard exclusions first:

- brand risk = yes -> not main push; usually negative during launch or cautious test later.
- attribute match = mismatch -> negative unless user intentionally sells a close substitute.
- attribute match = needs product evidence -> not main push until the user confirms title/bullet/spec evidence.
- product intent = off-intent -> negative or exclude.

Then assign:

| Conditions | Final action | Placement/ad suggestion |
| --- | --- | --- |
| Precise/near-precise, no hard risk, high priority | main push | Title plus SP exact for S tier; bullets plus SP exact for A tier |
| Testable intent or medium priority, no hard mismatch | test | SP phrase/broad with budget cap |
| Relevant but awkward/broad/low ad value | backend | Search Terms |
| Off-intent, hard mismatch, launch-stage brand risk, unresolved product evidence, or wasteful traffic | negative or hold | Negative exact/phrase, or hold for user confirmation |

Example placement formula after `AD` contains final action and `AC` contains priority:

```excel
=IF(AD2="主推",
    IF(AC2="S","标题+SP精准","五点+SP精准"),
    IF(AD2="测试","SP词组/广泛",
    IF(AD2="埋后台","Search Terms","否词")))
```

English version:

```excel
=IF(AD2="main push",
    IF(AC2="S","Title + SP exact","Bullets + SP exact"),
    IF(AD2="test","SP phrase/broad",
    IF(AD2="backend","Search Terms","negative")))
```

## Risk Notes

Use short, explicit notes:

- `brand term`: competitor/proprietary brand demand.
- `size mismatch`: keyword specifies unsupported size.
- `material mismatch`: keyword specifies unsupported material.
- `product-form mismatch`: buyer likely wants a different product form.
- `too broad`: relevant scene but weak product intent.
- `high concentration`: Top3 click/conversion concentration is high.
- `needs product evidence`: keyword attribute cannot be compared until title/selling points/specs are provided.
- `missing conversion/CPC`: scoring confidence is lower.

## Reporting Checks

Before finalizing, verify:

- Every keyword has exactly one final action.
- No brand-risk, mismatch, needs-product-evidence, or off-intent term appears in main push.
- Main push terms are reflected in listing and SP exact recommendations.
- Test terms have controlled match types and a negative-keyword plan.
- Backend terms are relevant and not misleading.
