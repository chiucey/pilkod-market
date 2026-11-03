## Method 2: KOL-Centered Search

**Trigger**: User names key research groups, or asks to identify them, or asks to survey a specific group.

### Step 1: KOL Identification

Ask Researcher: *"在这个领域，哪些课题组的工作你最关注？或者有没有你特别想了解的 PI？"*

- If Researcher names groups → proceed to Step 2 with those groups
- If Researcher doesn't know → identify top-cited authors from citation databases, present 5-8 candidate groups for Researcher's selection

### Step 2: Three-Dimension Survey of Named Groups

For each named KOL group, apply the **same three-dimension filter** as Method 1:

```
Dimension A - Citation Leaders:
  → Select 2-3 most cited papers from this group in the relevant domain
  → These anchor the group's intellectual contribution

Dimension B - Top-Tier Journal Papers:
  → Prioritize: Nature/Science/Cell > Nature Methods/Chem/Biotech > JACS > Anal. Chem.
  → Select 1-2 papers from this group in top-tier venues

Dimension C - Recent Papers (≤3 years):
  → Select 2-3 latest publications from this group
  → Shows current research direction and hot topics

MAX per group: 5 papers total
```

**KOL Selection criteria**:
```
Prioritize:
  ✓ First-author or corresponding-author papers from named groups
  ✓ Papers with high citation count (established impact)
  ✓ Papers in Researcher's priority journals (Nature > JACS > Anal. Chem.)
  ✓ Recent papers showing current research direction

Exclude:
  ✗ Incremental follow-up papers from same group (note but don't deeply report)
  ✗ Papers where the group's core claim was later retracted/disputed
  ✗ Papers outside the scope of Researcher's research question
```

### Step 3: Present KOL List to Researcher for Curation

**Present a structured KOL list for Researcher's feedback:**

```
## KOL Survey: [Research Topic]
**Groups surveyed**: [N]
**Survey date**: YYYY-MM-DD

---

### Group: [PI Name], [Institution]
**Papers surveyed**: [N]

| # | Paper Title | Journal | Year | Citations | Dimension |
|---|-------------|---------|------|-----------|-----------|
| 1 | [Title] | [Journal] | [Year] | [N] | [A/B/C] |
| 2 | ... | ... | ... | ... | ... |

**Researcher's curation needed**:
Which papers from [PI Name]'s group are most important for your research?
Please flag: ⭐ = core must-read, ✓ = relevant, ? = uncertain

---

### Group: [PI Name 2], [Institution]
...

---

*Please review the lists above and tell me:*
1. *Which ⭐ papers should be marked as "essential reading"?*
2. *Did I miss any important papers from these groups?*
3. *Should I add any new groups to the survey?*
```

### Step 4: Deep-Dive Based on Researcher's Curation (Interactive)

After Researcher provides feedback:

**For papers marked ⭐ (core must-read):**
→ Full summary: 1-page synthesis per paper (what was done, key finding, significance)
→ Trace forward: what papers cited this work (citation "descendants")
→ Trace backward: what foundational work this built on

**For papers marked ✓ (relevant):**
→ Standard summary: 2-3 sentence synthesis

**Combining Method 2 + Method 3:**
→ If Researcher identifies a specific ⭐ paper as a "classic anchor": activate Method 3 to trace its intellectual lineage and connect it to other KOL groups working in the same lineage
→ Identify: which other KOL groups were cited by / cite this paper → map the intellectual network

### KOL List Template (Maintained Per Research Area)

```
## KOL Registry: [Research Topic]

| Group | PI / Institution | Core Domain | Essential Papers | Recent Focus | Last Updated |
|-------|-----------------|-------------|-----------------|--------------|--------------|
| Group 1 | Prof. X, Institution | [Domain] | [N] ⭐ + [N] ✓ | [Topic] | YYYY-MM-DD |
| Group 2 | Prof. Y, Institution | [Domain] | [N] ⭐ + [N] ✓ | [Topic] | YYYY-MM-DD |

*This registry is updated with Researcher's curation feedback after each survey.*
```

### Output for Method 2 (Final)

After Researcher's curation + deep-dive:

```
## KOL Survey Complete: [Research Topic]
**Groups surveyed**: [N]
**Researcher-curated essential papers (⭐)**: [N]
**Deep-dive completed**: [Y/N]

### Intellectual Network Map
[Which groups cite each other - constructed from citation analysis]

### Key Research Fronts (from KOL analysis)
1. [Front 1] - [Which groups are working on this]
2. [Front 2] - [Which groups are working on this]

### Gap from KOL Analysis
[What the KOL network reveals is missing - different from Method 1 gap]
```

## Method 3: Researcher's Knowledge Source Network + Classic Literature Anchoring

**Status**: ✅ Partially Active — IMA cloud KB is live. RAGFlow, Zotero, Obsidian are reserved interfaces.

**Trigger**: User wants to build on papers already in their knowledge base, or wants to trace the intellectual lineage of a technique or concept.

### Unified Knowledge Source Interface (UnifiedInformationSource)

LR maintains a **virtual unified search layer** across all knowledge sources. Sources are registered here as they come online. Each source has a standard adapter interface.

#### Registered Sources

| # | Source | Type | Status | Priority | Connection |
|---|--------|------|--------|---------|-----------|
| 1 | **IMA** | Cloud lightweight KB | ✅ Live | Highest | IMA OpenAPI |
| 2 | **RAGFlow** | Local enterprise KB | 🔜 Reserved | High | REST API (TBD) |
| 3 | **Zotero** | Reference manager | 🔜 Reserved | Medium | Zotero API (TBD) |
| 4 | **Obsidian** | Knowledge vault | 🔜 Reserved | Medium | Local vault (TBD) |

#### Source Characteristics

```
IMA（已接入）:
  优势：云端随时访问，轻量，已 curation 的内容信号最高
  局限：仅限用户已手动添加的条目，无向量检索
  接口：IMA OpenAPI（/openapi/wiki/v1/）

RAGFlow（待接入）:
  优势：企业级 RAG，向量语义检索，PDF/网页深度解析
  局限：本地部署，需配置 IP + port + API key
  接口：REST API at /v1/
  接入触发：用户 提供 RAGFlow URL + API key

Zotero（待接入）:
  优势：文献元数据完整（DOI/PMID/引用数），PDF 全文
  局限：需配置 Zotero API key，仅限个人文库
  接口：Zotero REST API v3
  接入触发：用户 提供 Zotero API key

Obsidian（待接入）:
  优势：个人知识网络，图谱连接，Markdown 原生化
  局限：本地 vault，需 vault 地址或 Obsidian Sync
  接口：Obsidian Shell Commands / Templater / Dataview (TBD)
  接入触发：用户 提供 vault 路径或同步方式
```

#### How LR Uses the Source Network

```
触发规则（精确匹配，用户 指定哪个就只搜哪个）：

1. 用户 说"知识库"（未指定具体来源）：
   → 搜索所有已接入知识源（IMA + RAGFlow + Zotero + Obsidian）
   → 各自返回结果后合并去重

2. 用户 指定具体知识库，例如"IMA 个人知识库"：
   → 仅搜索 IMA 个人知识库
   → 不去其他源，不去 IMA 共享知识库

3. 用户 指定到文件夹，例如"代谢组学文件夹"：
   → 仅搜索该文件夹内的条目
   → 不搜索同级其他文件夹

4. 用户 指定多个知识库，例如"IMA 和 Zotero"：
   → 仅搜索这两个源，其他跳过
```

#### Source-Level Trigger Keywords

| 用户 的说法 | LR 行为 |
|------------|---------|
| "知识库"、"搜我的知识库"、"knowledge base" | 搜索所有已接入源 |
| "IMA"、"IMA 知识库"、"个人知识库"、"IMA KB" | 仅 IMA 个人知识库 |
| "IMA 共享知识库"、"shared knowledge base" | 仅 IMA 共享知识库（如已接入）|
| "RAGFlow"、"RAG Flow" | 仅 RAGFlow |
| "Zotero" | 仅 Zotero |
| "Obsidian"、"Obsidian vault" | 仅 Obsidian |
| "代谢组学文件夹"（在 IMA 里）| 仅 IMA → 个人知识库 → 代谢组学文件夹 |
| "IMA + Zotero"、"Zotero 和 IMA" | 仅这两个源 |
| "搜一下 Zotero 里关于 X" / "search Zotero for X" | 仅 Zotero |
| "搜一下 Obsidian 里关于 X" / "search Obsidian for X" | 仅 Obsidian |
| "搜一下 RAGFlow 里关于 X" / "search RAGFlow for X" | 仅 RAGFlow |

**用户 不说"知识库"时，LR 不会主动跨源搜索。**
**用户 说了具体源名，LR 严格只在该源内搜索。**
```

#### Source Adapter Template (For Future Integration)

When a new source comes online, add an adapter section:

```markdown
## [Source Name] Adapter

**Source**: [Full name]
**Type**: [Cloud KB / Local KB / Reference manager / Knowledge vault]
**Connection**:
  - Base URL: [URL or path]
  - Auth: [API key / token / none]
  - Endpoint: [key search/read endpoint]

**Adapter functions**:
  - search(query) → returns list of documents/notes
  - read(doc_id) → returns full content
  - get_metadata(doc_id) → returns author/year/venue/citations

**Priority in source network**: [1-4]
**Deduplication**: Compare with IMA results by [title/DOI/keyword overlap]
```

#### Source Registry（LR维护，接入时更新）

```
已接入：
  ✅ IMA — KB ID: 见 ~/.config/ima/kb_id（运行时读取，不硬编码）

待接入：
  🔜 RAGFlow — URL: [用户 提供]
  🔜 Zotero — API key: [用户 提供]
  🔜 Obsidian — vault path: [用户 提供]
```

#### When Multiple Sources Return the Same Paper

```
LR deduplicates across sources by:
  1. DOI exact match（最可靠）
  2. Title exact match（忽略大小写）
  3. Title keyword overlap > 80%（宽松匹配）

优先级规则：
  IMA KB 结果 = 最高信号（Researcher 已 curation）
  RAGFlow 结果 = 高信号（语义相关）
  Zotero 结果 = 元数据最完整（引用数/PMID）
  Obsidian 结果 = 笔记上下文最丰富

当同一篇论文出现在多个源时：
→ 合并元数据（用 Zotero 的引用数 + IMA 的研究者备注）
→ 标注来源："[Paper] — 来自：IMA KB + Zotero"
```

### Step 1: Query IMA Knowledge Base

LR searches Researcher's IMA knowledge base **before** broader web searches — the KB is already curated and relevant to Researcher's interests, making it the highest-signal starting point.

**Knowledge base structure** (visible folders):
```
个人知识库/
  📁 化生技术         📁 生物医药行业动态    📁 书影剧展
  📁 认知进化         📁 AI                📁 代谢生物学
  📁 时空组学         📁 旅游              📁 美食
  📁 代谢组学         📁 色谱分析
  📄 [文件/笔记] ×4
```

**Search approach**:
```
IMA KB search is useful when:
- Researcher has already bookmarked papers on the topic
- Researcher stored relevant notes/summaries on a technique
- Researcher wants to find "what do I already have on X"
- The survey involves cross-referencing Researcher's curated papers

IMA KB has limitations:
- Only returns items Researcher has already added
- No cross-folder deep search across all folders at once (search is within one KB)
- File types: PDF/Word/notes + bookmarks
```

### Step 2: IMA KB Search Execution

**When to use IMA KB search:**
```
LR should query the IMA KB when:
□ Researcher mentions papers they have ("I have some relevant papers in my KB")
□ Topic overlaps with known KB folders (代谢组学, 时空组学, AI, etc.)
□ Researcher says "search my knowledge base for X"
□ Stage 1 preliminary material mentions specific papers that might be in KB

LR may skip IMA KB when:
□ Researcher explicitly says "search PubMed only"
□ Topic is clearly outside any KB folder domain
□ Researcher provides a fresh topic with no prior curation
□ IMA KB search already returned nothing on prior similar topic
```

**Search execution**:
```
LR calls IMA KB search via the knowledge-base module (see SKILL.md):
  → search_knowledge_base(query="[topic]", knowledge_base_id="用户的 KB ID")
  → browse specific folders if topic clearly belongs to one

LR also reads KB file contents when:
  → File title is directly relevant to the search query
  → Researcher has explicitly referenced that file
```

### Step 3: Integration with Web Search

```
IMA KB results inform, not replace, web search:

LR workflow:
1. Search IMA KB first → get relevant papers Researcher already curated
2. Tell Researcher: "In your IMA KB, I found: [list]"
3. Then proceed with Method 1 (web search) to fill gaps
4. Compare KB results + web results → identify papers in KB not in web search

This is the key value of IMA KB:
  → Papers Researcher bookmarked = highest relevance signal
  → Web search fills the rest
  → Combined = most complete + most relevant survey
```

### Step 4: Classic Literature Anchoring (via IMA KB + Web)

**Trigger**: User wants to trace intellectual lineage of a technique/concept.

**Process**:
```
1. Researcher provides a starting point (paper, technique, or concept)
2. LR searches IMA KB for related entries
3. LR traces forward (what cited this) + backward (what did this cite) via web
4. Researcher applies academic taste to decide which lineage to follow
```

**Classic anchoring output**:
```
## Classic Literature Anchoring: [Starting Point]
**Researcher's KB contributions**: [N papers found]
**Intellectual lineage**: [brief description]

### Papers from Researcher's IMA KB
| Paper | Folder | Relevance |
|-------|--------|-----------|
| [Title] | [Folder] | ★★★★★ |

### Lineage Trace (Web)
[What this built on → what it enabled → current frontier]
```

### IMA KB Integration Summary

```
Three ways IMA KB fits into LR workflow:

WAY A — KB as starting point:
  Researcher mentions KB topic → LR searches KB first → fills gaps with web
  Use when: Researcher's interests overlap with KB folders

WAY B — KB + Web combined:
  LR searches both simultaneously
  → Combine, deduplicate, prioritize KB results
  → Use when: Researcher wants comprehensive survey

WAY C — KB after web search:
  LR does web search first → checks if results are in KB
  → Marks which results are "in Researcher's KB" vs "new findings"
  → Use when: Researcher wants to know what's already curated

LR chooses the approach that gives Researcher the highest signal survey.
Always note: "This paper is in your IMA KB" when relevant.
```
