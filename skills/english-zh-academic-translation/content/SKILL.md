---
name: english-zh-academic-translation
description: "Translates English academic publications (WHO reports, public health books, policy documents, textbook chapters) into Simplified Chinese and produces a properly formatted Word document. Use this skill whenever the user wants to translate an English document, chapter, report, or paper into Simplified Chinese — even if they don't explicitly mention formatting. Triggers include: '翻译成中文', 'translate to Chinese', 'translate this chapter into 中文', 'Simplified Chinese version of this PDF', 'put this WHO chapter into Chinese', or uploads of English academic content alongside a request to convert it to Chinese. Also use when the user asks to apply specific Chinese typographic conventions (SimSun, SimHei, KaiTi) to a translated document."
---

# English → Simplified Chinese Academic Translation

This skill produces a faithful, well-formatted Simplified Chinese translation of an English academic source (WHO publications, public-health books, policy reports, textbook chapters), output as a `.docx` file with the standard Chinese academic typography conventions.

## When to use

- The user uploads an English document (PDF or .docx) and asks for a Chinese translation.
- The user asks Claude to translate a specific chapter, section, or report into 中文 / 简体中文 / Simplified Chinese.
- The user mentions a translation that needs to follow Chinese academic publishing conventions (宋体, 黑体, 楷体, 小四, 1.5 倍行距, etc.).

## Workflow

1. **Read the source.** If it's a PDF, use `/mnt/skills/public/pdf-reading/SKILL.md` for guidance. If it's a .docx, use `extract-text`. Make sure you capture the entire document — chapter title, authors, key messages, all body sections, all boxes/figures/tables, and references.

2. **Plan the structure.** Before translating, list out the document's structure: chapter number/title, author block, "Key messages" or equivalent intro, numbered sections (e.g., 9.1, 9.2, 9.2.1), boxes (Box 9.1, Box 9.2 …), figures, tables, conclusion, references. Translate this structural map to Chinese first (e.g., Box → 专栏, Chapter → 第X章, References → 参考文献) so the Word document is built consistently.

3. **Translate following the rules** in the next section. Work section by section; do not skip or summarize. Preserve every paragraph, footnote, box, and figure caption. References stay in their original English.

4. **Generate the .docx.** Use `scripts/generate_docx.py` as the helper for applying the correct fonts, sizes, and spacing. Read it first; it exposes a small builder API (`add_h1`, `add_h2`, `add_body`, `add_box`, `add_table_caption`, etc.) that handles the East-Asian font setup correctly. Do NOT try to set Chinese fonts with `run.font.name` alone — `python-docx` requires setting the `w:eastAsia` attribute on `rPr` for SimSun/SimHei/KaiTi to actually render. The helper handles this.

5. **Save to `/mnt/user-data/outputs/`** and present with `present_files`.

## Translation rules (核心翻译规范)

These are derived from the user's `翻译英文著作的基本要求` document. Follow all of them.

### Faithfulness
- Convey the original meaning completely. **No additions, deletions, or distortions.**
- Don't summarize, paraphrase loosely, or skip "obvious" content. Every sentence in the source must appear in the translation.
- If something is genuinely sensitive or inappropriate and must be modified, add a translator's note (译者注) explaining what changed.

### Style — write natural Chinese, not translated English

The translation must read as if originally written by a native Chinese academic, not as translated English. This is the single most important quality criterion. Watch for and correct these patterns of 欧化句式 (Europeanized syntax):

**1. Move time and place to the front.** English puts time/place adverbials at the end ("X happened in 2018"). Chinese prefers them at the front of the clause.
- Bad (欧化): `该机制于2018年在教育部门试点后引入卫生领域。`
- Good: `2018年，该机制在教育部门试点后引入卫生领域。`
- Also good: `该方法于2018年在教育部门成功试点后引入卫生领域。` (time + condition together, before the verb)

**2. Don't bury the verb at the end.** When English uses "subject — long modifier — verb", restructure so the Chinese verb comes earlier or breaks into a separate clause.
- Bad (欧化): `政府为了解决基层医疗机构面临的资金瓶颈、报告负担过重、资源流向不可预测等多重问题，启动了直接设施拨款机制。`
- Good: `为解决基层医疗机构面临的多重问题——资金瓶颈、报告负担过重、资源流向不可预测——政府启动了直接设施拨款机制。`

**3. Avoid `进行 + 动词`, `加以 + 动词`, `作出 + 动词`.** Use the verb directly.
- Bad: `对体系进行了重组` / `对问题加以分析` / `作出了改革`
- Good: `重组了体系` / `分析问题` / `推行了改革`

**4. Avoid the `是...的...` definitional pattern when a direct sentence works.**
- Bad (欧化): `直接设施拨款是一种将医疗机构确立为自主管理实体并使其能够独立接收和管理资金的机制。`
- Good: `直接设施拨款是一种将机构确立为自主管理实体的机制，使其能够独立接收与管理资金。` (split into two clauses)

**5. Don't chain `的` more than twice in a row.** "X 的 Y 的 Z" is a tell-tale sign of Europeanized writing.
- Bad: `一个新的稳定的可持续的筹资模式`
- Good: `一种稳定、可持续的新型筹资模式` (use 顿号 `、` to coordinate, drop redundant `的`)

**6. Avoid `包括...在内` and `…的`-heavy noun phrases when verbs work better.**
- Bad: `通过组建包括全科医生、基层公共卫生人员、乡村医生在内的团队`
- Good: `组建由全科医生、基层公共卫生人员、乡村医生组成的团队`

**7. Avoid passive voice unless natural.** Chinese uses far less 被 than English uses "be V-ed". Use topic-comment structure or active voice.
- Bad: `资金被分配给医院` (when context is neutral)
- Good: `资金分配给医院` / `资金流向医院` / `医院获得资金分配`
- 被 is appropriate when the action is genuinely adverse or unexpected: `捐助方资助被中止` ✓

**8. Drop pronouns when context is clear.** Chinese is more pronoun-light than English.
- Bad: `政府推出了系统。它创建了统一的报告机制。它减少了碎片化。`
- Good: `政府推出了系统，建立了统一的报告机制，减少了碎片化。`

**9. Compress where Chinese permits.** Replace verbose constructions with concise ones.
- `从X下降到了Y` → `由X降至Y`
- `在X方面` (often unnecessary) → drop or use 在X上
- `这一现象的分析显示...` → `分析这一现象可见...`
- `在...的过程中` (often unnecessary) → 在...时 / drop
- `针对...所采取的...` → `为...而采取的...`

**10. Use 4-character structures where natural.** They give Chinese prose its rhythm. e.g., `统筹兼顾`, `行之有效`, `因地制宜`, `共担责任`, `层层推进`. Don't force them, but reach for them when they fit.

**11. Break long English sentences into 2–3 Chinese sentences.** Anything English does with subordinate clauses ("which", "that", "while", "although"), Chinese typically does with parallel short sentences linked by 而 / 但 / 同时 / 此外, or just with a 句号 break.

**12. General rhythm test.** After translating a paragraph, read it aloud (mentally). If you stumble, if a sentence runs more than ~50 characters without a comma break, or if you find yourself parsing the structure to understand it — the sentence is too Europeanized. Rewrite.

### Academic register — scholarly but readable

The anti-欧化 rules above can be over-applied. Choppy short sentences with colloquial idioms ("雪上加霜", "一刀切") read like a magazine column, not a scholarly publication. The translation must sit in the middle: **natural-flowing Chinese with formal academic register**. Concretely:

**Avoid colloquial idioms and journalistic flourishes:**
- ❌ `更为雪上加霜的是` / `火上浇油` / `一刀切` / `众所周知`
- ✅ `此外` / `加之` / `更值得关注的是` / `更进一步` / `尤需指出的是`

**Prefer formal connectives over casual ones:**
| Casual | Academic |
|---|---|
| 但是 | 然而 / 但 |
| 所以 | 故 / 因而 / 由此 |
| 而且 | 而 / 进而 |
| 这样 | 由此 / 因而 |
| 也 (sentence-initial) | 此外 / 与此同时 / 同时 |
| 跟…一起 | 与…共同 / 协同 / 同 |

**Use 此 / 该 / 其 where natural in academic prose.**
- 这种现象 → 此种现象 / 该现象
- 这个机制 → 该机制 / 此机制
- 它的影响 → 其影响

Don't force this — natural variation is best. But when the surrounding context is formal, demonstratives should match.

**Don't atomize sentences.** Academic Chinese readers expect connected reasoning, not bullet-point prose.
- ❌ Over-corrected: `政府推出了系统。它建立了报告机制。它减少了碎片化。`
- ✅ Academic: `政府推出了相应系统，建立起统一的报告机制，从而减少了碎片化。`

The second is still anti-欧化 (no `它` repeats, no buried verb), but reads as a single coherent clause with shared subject — which is how scholarly Chinese flows.

**Choose precise scholarly verbs:**
| Generic | Academic |
|---|---|
| 做了改革 | 推行 / 实施 / 推进了改革 |
| 用了方法 | 采用 / 运用了方法 |
| 增加资金 | 加大投入 / 扩大资金规模 / 提升资金水平 |
| 解决问题 | 应对 / 化解 / 纾解问题 (per context) |
| 让 | 使 / 令 (in formal contexts) |

**Use logical-flow markers explicitly.** Make the argument's structure visible, mirroring how the English source uses "first / second / third", "although", "while", etc.
- 首先…其次…再者…最后
- 一方面…另一方面
- 不仅…而且 / 不仅…更
- 既…又 / 虽…但
- 由于…故而 / 鉴于…因此

**The two-sided test.** Ask, after each paragraph:
- Does any sentence sound like a translation? (subject before long modifier before buried verb; `…的…的…` chains; `进行+动词`) → still 欧化, fix per the rules above.
- Does any sentence sound like a blog post or news article? (idioms, exclamations, choppy 3–5 word sentences, sentence-initial `也`) → too colloquial, raise the register.

The target is a measured, precise, flowing academic voice — like a chapter in a Chinese university textbook or a journal article in 《中华医学杂志》 / 《中国卫生政策研究》.

### Punctuation
- Use Chinese punctuation throughout: `，。；：？！""''（）《》、——……` — never English `,.:;?!"'()`.
- Citations: outer parens are Chinese full-width `（）`, contents stay in English: `（Hanson et al., 2022）`.
- A semicolon-heavy English bullet that ends on a colon-introduced list still uses Chinese punctuation: `：` not `:`.

### Terminology, names, organizations
- **Technical terms:** use the established discipline-standard Chinese translation. On first occurrence, provide the original English in parentheses. Subsequent occurrences use Chinese only.
  - Example: `初级卫生保健（Primary Health Care，PHC）` on first mention; just `初级卫生保健` (or `PHC` where natural) afterwards.
- **Quoted English terms must also be translated.** If the source wraps a name or label in quotes (e.g., `"Planrep"`, `"Contract-based Family Doctor Service"`, `"Sehatmandi"`), still translate to Chinese and put the original in parentheses on first mention. Don't leave raw quoted English just because the source quoted it.
  - Example: source `two complementary systems ("Planrep" and "Facility Accounting and Reporting System")`
  - Translation: `两套互补系统——"规划报告系统"（Planrep）和"设施会计与报告系统"（Facility Accounting and Reporting System）`
  - Keep the Chinese quotation marks `""` to mark it as a proper-name label, just as the source did.
- **Personal names:** use the standard transliteration per 《英语姓名译名手册》 (or established conventional renderings — e.g., Adam Smith → 亚当·斯密). First occurrence: Chinese name + English in parentheses, e.g., `卡拉·汉森（Kara Hanson）`. Use middle dot `·` (not regular period) between given name and surname.
- **Place names:** per 《外国地名译名手册》 or the latest 中国地图出版社 maps. First occurrence: Chinese + English parentheses. e.g., `哈萨克斯坦（Kazakhstan）`.
- **Organizations / acronyms:** common English acronyms (IBM, OECD, WHO) can stay as-is. For less common ones, on first occurrence give the full Chinese translation + original English + acronym in parentheses, e.g., `世界卫生组织（World Health Organization，WHO）`. After that, use the Chinese name or the acronym.
- **Country names:** prefer the formal Chinese rendering used in Chinese government / CCTV style: `坦桑尼亚联合共和国` (United Republic of Tanzania), `刚果民主共和国` (Democratic Republic of the Congo), `吉尔吉斯斯坦` (Kyrgyzstan), `荷兰王国` (Kingdom of the Netherlands).

### Structure & elements
- **Chapter title:** `第X章  <translated title>` (use Chinese number for "第X章", and two spaces between the chapter label and the title — matches the sample's `第九章  卫生筹资`).
- **Author block:** translate each author's name to Chinese with the original English in parentheses, separated by `、` (Chinese enumeration comma).
- **Section headings:** keep the original numbering (9.1, 9.2.1, etc.), translate the heading text.
- **Boxes:** `Box 9.1` → `专栏9.1`. The box title line is bolded.
  - In box bodies, key terms that the source italicizes/bolds at the start of a paragraph should be rendered as bolded italicized Chinese term followed by the English in parentheses. Example: `***资金筹集***（Revenue collection）描述...`
- **Figures:** `Fig. 9.1` → `图9.1`. Figure title translated. Notes/source lines underneath the figure use small font (小五号宋体).
- **Tables:** `Table 9.1` → `表9.1`. Table title translated. Cell content typically 小五号楷体, header/source 小五号宋体. If the table is very complex, you may render it as a plain image embed and translate the caption only — but prefer a real table.
- **Citations in body text:** keep author citations in English, e.g., `(Hanson et al., 2022)`. Place them right after the relevant Chinese sentence with no space before the parenthesis.
- **Cross-references:** translate. `(see Chapter 14)` → `（参见第14章）`. `(see Section 9.3.5)` → `（参见第9.3.5节）`. `(see Box 9.3)` → `（参见专栏9.3）`. `(see Fig. 9.1)` → `（图9.1）` or `（参见图9.1）`.
- **References section:** content stays in the original language (English bibliography stays English — no translation), BUT the **format must be reconverted to Chinese national standard GB/T 7714-2015 (著者-出版年制)**. Translate the section heading to `参考文献`. See the dedicated section below for the full format.
- **Footnotes that contain only a source/citation:** keep in English, also reformat per GB/T 7714 if applicable.

### Numbers and units
- Use Arabic numerals throughout (3美元, not 三美元).
- Use national legal/standard units (e.g., 美元, 千克, 公里).
- Keep statistics and percentages exactly as in the source.

## References — GB/T 7714-2015 reformatting

The source's reference list (typically WHO author-year style) must be **reformatted to Chinese national standard GB/T 7714-2015 (著者-出版年制 / author-year system)**, while keeping the content in original English. This is non-negotiable for Chinese academic publishing.

### Type markers (文献类型标识)

Every entry needs a bracketed type marker after the title:

| Marker | Type | Examples |
|---|---|---|
| `[M]` | Monograph / book | Books, edited volumes |
| `[J]` | Journal article (print) | Peer-reviewed articles in print |
| `[J/OL]` | Journal article (online) | Most modern peer-reviewed articles with a URL |
| `[R]` | Report (print) | Government / institutional reports in print |
| `[R/OL]` | Report (online) | WHO / World Bank / OECD reports with a URL |
| `[M/OL]` | Online book | Open-access books with URL |
| `[D]` | Dissertation | PhD / Master's theses |
| `[C]` | Conference proceedings | Edited proceedings |
| `[N]` | Newspaper | News articles |
| `[S]` | Standard | Technical / national standards |
| `[EB/OL]` | Electronic resource (web) | Databases, web pages, blog posts |
| `[DB/OL]` | Online database | Statistical databases |

When in doubt: if it's online and looks like a journal article → `[J/OL]`; if it's an online report from an institution → `[R/OL]`; if it's a generic web page → `[EB/OL]`.

### Author-year format (著者-出版年制)

The general pattern is:
```
主要责任者. 出版年. 题名[文献类型标识/载体标识]. 出版地: 出版者[引用日期]. 获取和访问途径.
```

For a journal article:
```
主要责任者. 出版年. 题名[J/OL]. 刊名, 卷(期): 起止页码[引用日期]. URL.
```

### Author conventions
- **Western authors:** family name in ALL CAPS, then space, then initials without periods. Use comma + space between authors.
  - `HANSON K`, `BARASA E, MWAUSEGE M, MOLYNEUX S`
- **More than 3 authors:** list first 3, then `, et al.`
  - `HANSON K, GILSON L, BALABANOVA D, et al.`
- **Institutional authors:** use the standard short form. `WHO`, `OECD`, `World Bank`.
- **Chinese institutional authors when source has Chinese-original entity:** use Chinese name (e.g., `全国人民代表大会`).
- **Disambiguation suffix:** preserve `2022a`, `2022b`, etc. when used for citation matching.

### Date / volume / page conventions
- **Year:** placed right after author, ending with period: `HANSON K, et al. 2022.`
- **Volume(Issue):** `10(5)` — no space between volume and parenthesis.
- **Pages:** use full half-width hyphen, both endpoints fully written: `e715-e772` (not `e715–72`); `1227-1242` (not `1227–42`).
- **Access date:** `[YYYY-MM-DD]` half-width brackets, ISO format. Convert "accessed 17 January 2023" → `[2023-01-17]`.
- **URL:** ends with period at the end of the entry.
- **Punctuation throughout reference entries is half-width** (`,` `.` `:` `(` `)`) since the content is English.

### Worked examples (source → GB/T 7714-2015 author-year)

**Journal article (online):**

Source:
> Hanson K et al. (2022). The Lancet Global Health Commission on financing primary health care: putting people at the centre. Lancet Glob Health, 10(5):e715–72. Available at: https://linkinghub.elsevier.com/retrieve/pii/S2214109X22000055 (accessed 17 January 2023).

GB/T 7714-2015:
> HANSON K, et al. 2022. The Lancet Global Health Commission on financing primary health care: putting people at the centre[J/OL]. Lancet Glob Health, 10(5): e715-e772[2023-01-17]. https://linkinghub.elsevier.com/retrieve/pii/S2214109X22000055.

**Institutional report (online):**

Source:
> WHO (2022a). Direct facility financing: concept and role for UHC. Geneva: World Health Organization. Available at: https://www.who.int/publications/i/item/9789240043374 (accessed 10 August 2023).

GB/T 7714-2015:
> WHO. 2022a. Direct facility financing: concept and role for UHC[R/OL]. Geneva: World Health Organization[2023-08-10]. https://www.who.int/publications/i/item/9789240043374.

**Book (print):**

Source:
> Bariş E et al. (2022). Walking the talk: reimagining primary health care after COVID-19. Washington DC: World Bank Publications. Available at: https://openknowledge.worldbank.org/handle/10986/35842 (accessed 10 August 2023).

GB/T 7714-2015:
> BARIŞ E, et al. 2022. Walking the talk: reimagining primary health care after COVID-19[M/OL]. Washington DC: World Bank Publications[2023-08-10]. https://openknowledge.worldbank.org/handle/10986/35842.

**Web page / electronic resource:**

Source:
> OECD (2023). OECD Stat. Health expenditure and financing. Available at: https://stats.oecd.org/index.aspx?DataSetCode=SHA (accessed 13 January 2023).

GB/T 7714-2015:
> OECD. 2023. OECD Stat. Health expenditure and financing[DB/OL]. [2023-01-13]. https://stats.oecd.org/index.aspx?DataSetCode=SHA.

**Chapter in edited book:**

Source:
> Busse R, Mays N (2008). Paying for chronic disease care. In: Nolte E, McKee M (eds), Caring for People with Chronic Conditions. Maidenhead: Open University Press/McGraw Hill, pp. 195–221.

GB/T 7714-2015:
> BUSSE R, MAYS N. 2008. Paying for chronic disease care[M]//NOLTE E, MCKEE M. Caring for People with Chronic Conditions. Maidenhead: Open University Press/McGraw Hill: 195-221.

**Government document:**

Source:
> Government of Ukraine (2016). On approval of the Concept of reform of financing of the healthcare system. No. 1013-r. Available at: https://www.kmu.gov.ua/npas/249626689 (accessed 10 August 2023).

GB/T 7714-2015:
> GOVERNMENT OF UKRAINE. 2016. On approval of the Concept of reform of financing of the healthcare system: No. 1013-r[EB/OL]. [2023-08-10]. https://www.kmu.gov.ua/npas/249626689.

### In-text citations
The format `（Hanson et al., 2022）` (Chinese full-width parens around English citation) used in body text remains unchanged. GB/T 7714 calls this 著者-出版年制 (author-year), which matches the WHO source's in-text citation style — so no conversion is needed for citations within the text, only for the bibliography entries themselves.

## Formatting rules (排版规范)

The output `.docx` must follow:

| Element | Font | Size | Spacing |
|---|---|---|---|
| Body text 正文 | 宋体 SimSun | 小四 (12pt) | 1.5 倍行距 |
| Level 1 heading 一级标题 | 黑体 SimHei | 小四 (12pt) | 1.5 倍行距 |
| Level 2 heading 二级标题 | 宋体 SimSun (bold) | 小四 (12pt) | 1.5 倍行距 |
| Level 3 heading 三级标题 | 宋体 SimSun (bold) | 小四 (12pt) | 1.5 倍行距 |
| Box title 专栏标题 | 宋体 SimSun (bold) | 小四 (12pt) | 1.5 倍行距 |
| Table cell content | 楷体 KaiTi | 小五 (9pt) | single |
| Table caption / source / notes | 宋体 SimSun | 小五 (9pt) | single |
| Figure caption | 宋体 SimSun (bold) | 小四 (12pt) | 1.5 倍行距 |
| Figure note / source | 宋体 SimSun | 小五 (9pt) | single |
| References (English) | Times New Roman | 小四 (12pt) | 1.5 倍行距 |

Bold and italic emphasis from the source must be preserved.

## The helper script

`scripts/generate_docx.py` provides a small builder class that handles all the East-Asian font configuration correctly. **Always read it before writing the document-generation code** so you use the right method names and don't reinvent the font-setting logic. The typical pattern is:

```python
from generate_docx import ChineseDoc

doc = ChineseDoc()
doc.add_chapter_title("第九章  卫生筹资")
doc.add_authors("卡拉·汉森（Kara Hanson）、马塞尔·韦内马（Marcel Venema）、...")
doc.add_h1("9.1 引言")
doc.add_body("卫生筹资安排是卫生部门政策制定者...")
doc.add_box_title("专栏9.1 卫生筹资功能")
doc.add_box_body("***资金筹集***（Revenue collection）描述...")
doc.add_h1("参考文献")
doc.add_reference("Hanson K et al. (2022). The Lancet Global Health Commission...")
doc.save("/mnt/user-data/outputs/translated.docx")
```

## Style examples

For paragraph-level style examples (how the user's prior translation rendered specific patterns: author blocks, key-message bullets, box definitions, country case studies, citation handling), read `references/style_examples.md`.

## Quality checks before saving

Before calling `doc.save(...)`, mentally verify:

1. **No content is missing.** Compare your section list against the source's table of contents/structure.
2. **First-mention parentheticals exist** for major terms, key acronyms, and named people/places/organizations.
3. **All punctuation is Chinese** in Chinese sentences (check for stray English `,` `.` `:` `;` `(` `)` `"`).
4. **Citations are preserved verbatim** — same author names, same year, same parenthesis style.
5. **References section is fully in English** and has every entry from the source.
6. **Cross-references are translated** (no stray "see Chapter X", "see Box X", "see Fig X" in English).
7. **Numbers and statistics match** the source exactly.
