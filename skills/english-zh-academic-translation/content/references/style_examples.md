# Style Examples — Patterns from the Reference Translation

This file collects concrete patterns from the user's reference translation (WHO PHC Primer, Chapter 9: Health Financing). Use these as templates when translating new chapters in the same series or other WHO/academic publications.

## 1. Chapter title

**Source:**
```
9
Health financing
```

**Target:**
```
第九章  卫生筹资
```

Note: two spaces between "第九章" and the title. Use Chinese chapter numerals (第一章, 第二章, …, 第九章, 第十章, 第十一章 …).

## 2. Author block

**Source:**
```
Kara Hanson, Marcel Venema, Triin Habicht, Ewout van Ginneken,
Xu Jin, Grace Achungura, Faraz Khalid, Beibei Yuan and Melitta Jakab
```

**Target:**
```
卡拉·汉森（Kara Hanson）、马塞尔·韦内马（Marcel Venema）、特林·哈比希特（Triin Habicht）、埃沃特·范希内肯（Ewout van Ginneken）、徐进（Xu Jin）、格蕾丝·阿春古拉（Grace Achungura）、法拉兹·哈利德（Faraz Khalid）、袁贝贝（Beibei Yuan）、梅利塔·雅卡布（Melitta Jakab）
```

Notes:
- Each author gets Chinese transliteration + English in full-width parentheses.
- Authors separated by `、` (Chinese enumeration comma), not `,` or `;`.
- Use `·` (middle dot, U+00B7) between given name and surname for transliterated foreign names: `卡拉·汉森`.
- For Chinese authors writing in pinyin (Xu Jin, Beibei Yuan), use the actual Chinese name if known/inferable: `徐进（Xu Jin）`, `袁贝贝（Beibei Yuan）`. If the actual characters are not knowable, leave the pinyin in parentheses and ask the user.
- "and" before the last author is dropped; just use `、`.

## 3. Key messages section heading and bullets

**Source:**
```
Key messages
■ Political will is the primary factor...
■ Health financing arrangements can be designed to support...
```

**Target:**
```
关键信息

政治意愿（Political will）是确保卫生和初级卫生保健筹资的首要因素。它决定了...

卫生筹资安排可设计为支持（或推动）卫生体系向初级卫生保健方向转变。政策杠杆包括：
```

Notes:
- "Key messages" → "关键信息".
- Each bullet becomes its own paragraph; the `■` marker is dropped.
- A bullet that introduces a sub-list ends with Chinese colon `：`, and sub-bullets become separate paragraphs without bullet markers.

## 4. First-mention parentheticals for terms

**Source:**
```
It is the role of health financing to mobilize sufficient resources to make
primary health care (PHC) effective...
```

**Target:**
```
卫生筹资（Health financing）的职能是调动充足资源，保障初级卫生保健
（Primary Health Care，PHC）有效运转。
```

Pattern: `中文术语（English Term）` on first mention. Note the Chinese full-width parentheses `（）` and the Chinese comma `，` separating the full English name from the acronym inside the parentheses.

## 5. Box title and definitions

**Source:**
```
Box 9.1  Health financing functions

Revenue collection describes how funds for health are mobilized...
```

**Target:**
```
**专栏9.1 卫生筹资功能**

***资金筹集***（Revenue collection）描述卫生资金筹集方式，并根据资金来源进行分类...
```

Notes:
- `Box X.Y` → `专栏X.Y` (no space between 专栏 and the number).
- Box title is bold (rendered as `**...**`).
- The leading term in each box paragraph (Revenue collection, Pooling, Allocation, etc.) becomes a bolded-italic Chinese term + English in parentheses: `***资金筹集***（Revenue collection）`.

## 6. Citations in body text

**Source:**
```
...this share can be increased (Hanson et al., 2022).
```

**Target:**
```
...提高初级保健占比（Hanson et al., 2022）。
```

Pattern: the **outer parentheses are Chinese full-width** `（）`, but the **content inside stays in English** with English commas, semicolons, and ampersands — `（Author et al., Year）`, `（Author1 & Author2, Year）`, `（Author A, Year; Author B, Year）`. The Chinese full stop `。` follows the closing parenthesis. No space before the opening parenthesis.

For citations of Chinese-source authoritative bodies (e.g., the National People's Congress of China), translate the body's name to its standard Chinese form but keep the rest of the citation in English-style format:
`（全国人民代表大会，2019; Ran et al., 2020; Yuan et al., 2020）`

## 7. Cross-references

| English | Chinese |
|---|---|
| (see Chapter 14) | （参见第14章） |
| (see Section 9.3.5) | （参见第9.3.5节） |
| (see Box 9.3) | （参见专栏9.3） |
| (see Fig. 9.1) | （参见图9.1） / （图9.1） |
| (see Table 9.1 in Annex) | （参见附件表9.1） |
| see also Chapter 10 | 另见第10章 |

Cross-references use Chinese full-width parentheses and translated content.

## 8. Country case studies

**Source heading:**
```
9.3.1 United Republic of Tanzania: Direct Facility Funding
allows for more decision-making autonomy
```

**Target heading:**
```
9.3.1 坦桑尼亚联合共和国：直接设施拨款赋予更大的决策自主权
```

Notes:
- Section number preserved.
- Colon `:` becomes Chinese colon `：`.
- Country name uses official Chinese rendering.
- The English term being introduced (Direct Facility Funding) is then given a parenthetical in the body's first mention.

## 9. Acronyms and full-form expansions

**Source:**
```
low- and middle-income countries (LMICs)
the Urban-Rural Residents Medical Insurance (URRMI) funds
```

**Target:**
```
低收入和中等收入国家（Low- and Middle-Income Countries，LMICs）
城乡居民基本医疗保险（Urban-Rural Residents Medical Insurance，URRMI）基金
```

Pattern: full Chinese name + (English full form, Acronym). Subsequent mentions use Chinese full name OR the acronym, whichever flows better.

## 10. References section

**Source heading:** `REFERENCES`
**Target heading:** `参考文献`

Body of references: keep entirely in original English, no translation. Format example:

```
Hanson K et al. (2022). The Lancet Global Health Commission on financing primary
health care: putting people at the centre. Lancet Glob Health, 10(5):e715–72.
Available at: https://linkinghub.elsevier.com/retrieve/pii/S2214109X22000055
(accessed 17 January 2023).
```

These are typeset in 小四号 with English font (Times New Roman is fine), single or 1.5 spacing. URL hyperlinks may be left as plain text.

## 11. Tables

`Table 9.1 Primary health care expenditure averages by country income group`
→ `表9.1 各收入组国家初级卫生保健支出均值`

- Caption: 宋体, 小四, bold
- Cell content: 楷体, 小五
- Source line: 宋体, 小五, e.g., `资料来源：作者基于WHO，2023和OECD，2023计算所得`
- Notes (a, b, c …): 宋体, 小五

If a table has columns with English labels (e.g., variable names from a database), keep the English labels and add a Chinese gloss in parentheses if helpful, or fully translate them — judgment call based on whether the user wants the document to remain navigable to readers comparing it to the English source.

## 12. Figures

`Fig. 9.1 Out-of-pocket spending makes up the largest share of total spending on PHC in LMICs`
→ `图9.1 在中低收入国家，自付费用占初级卫生保健总支出的最大份额`

For figures where the user has not provided an image asset, write the caption and a translator's note placeholder, e.g., `[图9.1 — 原书插图，请插入翻译后的图像]`. Translate any in-figure labels in the caption text or in a dedicated legend below.

Figure note/source line below: 宋体, 小五.

## 13. Common terminology glossary (PHC / health financing domain)

| English | Chinese |
|---|---|
| primary health care (PHC) | 初级卫生保健 |
| universal health coverage (UHC) | 全民健康覆盖 |
| out-of-pocket payment | 自付费用 |
| revenue collection | 资金筹集 |
| pooling | 风险共担 / 资金统筹 |
| purchasing | 服务购买 |
| allocation | 资金分配 |
| coverage policies | 保障覆盖政策 |
| benefit package | 医疗方案 / 服务包 |
| capitation | 按人头付费 |
| fee-for-service (FFS) | 按服务项目付费 |
| pay-for-performance (P4P) | 按绩效付费 |
| pay-for-quality (P4Q) | 按质量付费 |
| line-item budget | 逐项预算 |
| programme-based budgeting | 方案预算 |
| catastrophic health expenditure | 灾难性卫生支出 |
| financial protection | 经济风险保障 |
| stewardship | 管理监督职能 |
| earmarked revenue | 专项税收 |
| community health worker | 社区卫生工作者 |
| social health insurance | 社会医疗保险 |
| general practitioner (GP) | 全科医生 |
| co-payment / co-insurance | 共付 / 共保 |
| Ministry of Health | 卫生部 |
| Ministry of Finance | 财政部 |
| World Health Organization (WHO) | 世界卫生组织 |
| Organisation for Economic Co-operation and Development (OECD) | 经济合作与发展组织 |
| low-income countries (LICs) | 低收入国家 |
| lower-middle-income countries (LMICs) | 中低收入国家 / 低收入和中等收入国家 |
| upper-middle-income countries (UMICs) | 中高收入国家 |
| high-income countries (HICs) | 高收入国家 |

When a new term not in this glossary appears, look it up against authoritative Chinese sources (WHO Chinese publications, MOH terminology, peer-reviewed Chinese journals) before coining a new translation.
