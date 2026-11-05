---
name: medical-literature-ppt
description: create chinese medical literature interpretation slide decks from an original journal article pdf, with optional chinese translation docx and optional style-reference slides or pdfs. use when the user asks to turn a paper into a chinese ppt or wants literature解读/文献解读/医学文献解读 slides. the output should be a polished pptx, usually within 20 slides, faithful to the source paper, covering every original figure and table, using only visuals extracted from the original paper or charts redrawn from original paper data, and placing a fixed literature citation at the lower left of every slide. also use this skill when figure/table coverage must be audited explicitly before delivery.
---

Create the deck in Chinese and stay strictly faithful to the source paper.

## Required outcome

Deliver a `.pptx` slide deck that:
- stays within 20 slides unless the user explicitly allows more
- uses Chinese titles and Chinese explanatory text
- includes a title on every slide
- includes text plus at least one source-derived visual on every content slide
- covers **all original figures and tables** from the source paper somewhere in the final deck
- uses **only** visuals from the original paper, or charts/tables redrawn from original paper data
- places the literature citation string at the **lower left of every slide**
- does **not** introduce non-source decorative photos, icons, or illustrations

## Input rules

1. The original paper PDF is mandatory.
2. The original paper may be in English or Chinese.
3. A Chinese translation `.docx` is optional but preferred; use it to improve wording consistency, but defer to the source PDF if there is any mismatch.
4. A style-reference PDF or PPT is optional; if present, imitate its tone, palette, and layout logic without copying unrelated content.

## Tools and skills to use

- Use the `pdfs` skill to inspect and extract source figures, tables, captions, and page-level structure from the article PDF.
- Use the `docx` skill when a translation Word file is provided.
- Use the `slides` skill to build the final `.pptx`; follow its QA rules and use PptxGenJS.
- Use the `spreadsheets` skill only if you need a reliable intermediate extraction or verification of tabular data before charting.

## Workflow

1. **Validate inputs**
   - Confirm that an original article PDF is present.
   - Check whether a Chinese translation docx and/or style-reference file is present.

2. **Read the paper structurally**
   - Identify the article title, citation line, abstract, background, methods, results, discussion, and conclusion.
   - Build a complete inventory of every original figure and table: number, caption, source page, and core message.
   - Note which figures are multipanel and which tables are dense enough to require partial enlargement or split placement.
   - Explicitly distinguish true article figures/tables from decorative publisher items, logos, footers, license panels, graphical abstracts, and reference-only screenshots.

3. **Define the citation footer**
   - Use the uploaded article citation exactly when available.
   - Default format example: `Chittka L, et al. Philos Trans R Soc Lond B Biol Sci. 2025 Nov 13;380(1939):rstb20240302.`
   - Place the same citation at the lower left of every slide in a small, legible font.

4. **Run mandatory figure/table coverage audit before building**
   - Create a private source inventory table with these columns:
     - item id (`Figure 1`, `Table 2`, etc.)
     - source page
     - caption short form
     - content type (`figure`, `table`, `multi-panel figure`)
     - must-preserve details (axis labels, legends, footnotes, p values, panel labels)
     - planned destination slide number(s)
     - implementation method (`crop original`, `recreate chinese table`, `redraw source-data chart`)
   - Treat a figure as covered only if the final slide shows the actual figure, one or more essential panels from that figure, or a source-faithful redraw that preserves the original comparison logic.
   - Treat a table as covered only if the final slide shows the original table or a source-faithful recreated Chinese table containing the clinically relevant structure and values.
   - Do **not** mark an item covered merely because its results are mentioned in text.
   - For multipanel figures, record whether all panels are needed or whether only the clinically material panels are required; if any panel is omitted, mention this in the slide text only when omission would otherwise distort interpretation.
   - If the article contains only mechanistic diagrams and summary tables, all of them still count as required source visuals.

5. **Plan slide allocation before building**
   - Keep the deck within 20 slides.
   - Merge related content instead of creating one slide per paragraph.
   - A sensible default structure is:
     - title slide
     - study background / clinical question
     - study objective and design
     - population / methods
     - results slides covering every original figure/table
     - interpretation / takeaways
     - final summary
   - If the paper has many figures/tables, combine logically related items on the same slide while preserving readability.
   - Do not start slide production until every source figure/table has an assigned destination slide.

6. **Slide writing rules**
   - Write concise Chinese interpretation text that is faithful to the paper.
   - Prefer 3 to 6 short bullets or 1 short paragraph plus 2 to 4 bullets per slide.
   - Keep wording close to the original paper and translation; do not add claims not supported by the source.
   - Titles should state the slide’s clinical or scientific point, not generic labels like “Results 1”.
   - When discussing a figure/table, mention the endpoint, comparison, and direction of effect clearly.

7. **Visual rules**
   - Prefer directly cropping the original paper’s figures and tables.
   - Preserve axis labels, legends, footnotes, and significance marks whenever they are needed for interpretation.
   - For dense tables, you may recreate the table in Chinese if that improves readability, but keep all values faithful to the original and keep nearby text aligned with the original table’s meaning.
   - For result visuals, you may redraw bar charts, line charts, pie charts, waterfall charts, or similar only when the values come directly from the original paper.
   - If you redraw, clearly preserve the original comparison logic, numbers, units, and statistical annotations where possible.
   - Never add non-source stock images, unrelated molecular art, generic patient photos, or decorative icons.

8. **Layout and style rules**
   - Default to 16:9 widescreen.
   - Follow the uploaded style-reference deck if present; otherwise use a clean medical presentation style with restrained color, clear hierarchy, and generous whitespace.
   - Every content slide must contain:
     - slide title
     - Chinese interpretation text
     - at least one original-source figure/table or a redrawn source-data chart
     - lower-left literature citation footer
   - Keep visual balance similar to the provided examples: headline-driven slides, clinically oriented summaries, and large readable charts/tables.

9. **Mandatory final coverage QA before delivery**
   - Re-open the private inventory and verify every listed figure/table has a real destination slide.
   - Perform a slide-by-slide reverse check: for each final slide, note which source item(s) it covers.
   - Then perform a source-to-deck forward check: `Figure 1 -> slide x`, `Figure 2 -> slide y`, `Table 1 -> slide z`, etc.
   - If any source item has no verified destination slide, revise the deck before delivery.
   - If an item is too dense to read after cropping, it is **not** yet covered; enlarge it, split it, or recreate it.
   - If a recreated chart/table omits values, units, labels, or footnotes needed to understand the result, it is **not** yet covered.
   - Never deliver the deck with “partial coverage” unless the user explicitly authorizes omission.

## Hard failure conditions

Do not finalize the deck if any of these are true:
- one or more original figures/tables are missing from the coverage audit
- one or more audited items are not mapped to a slide
- a slide uses a non-source visual
- any slide lacks the lower-left citation
- a result claim in Chinese cannot be traced to the source PDF

## Decision rules for common cases

- **If the paper has more figures/tables than fit comfortably**: combine related visuals on one slide, use multi-panel layouts, and shorten text before increasing slide count.
- **If the translation docx is incomplete or stylistically weak**: rewrite the Chinese cleanly, but remain strictly faithful to the source PDF.
- **If a figure is unreadable when cropped directly**: enlarge the needed panel or redraw the chart from source data.
- **If a table is too dense**: recreate it in Chinese or split it across two coordinated slides, but keep within the page budget when possible.
- **If the article contains supplementary figures/tables**: include them only if the user explicitly asks, or if they are embedded in the uploaded “original paper” PDF and necessary for fidelity.
- **If the article is a review or narrative paper**: treat mechanistic diagrams, evidence-summary tables, and therapy-comparison tables as required source visuals just like result figures/tables.

## Default slide blueprint

Use this default slide logic unless the paper clearly demands another structure. See `references/slide-blueprint.md`.

## Coverage audit details

Use the stricter audit rules in `references/coverage-audit.md` before delivery.

## Style cues from the provided examples

Mirror these cues when the user asks for the same style:
- strong title-led storytelling
- Chinese medical-commercial literature interpretation tone
- large central visuals
- clinically oriented takeaway statements
- restrained palette and clean whitespace
- footer-style citation on each slide

## Deliverable discipline

Return only the final `.pptx` unless the user explicitly requests intermediate files.
