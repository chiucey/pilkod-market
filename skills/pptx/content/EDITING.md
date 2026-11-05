---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 95c10b8904c542dfcfbbe8273db1dbb5
    PropagateID: 95c10b8904c542dfcfbbe8273db1dbb5
    ReservedCode1: 30440220499861aa8cad2dd4315249c1014094c5bbc4dffa5ad52779e6a55c962b148be702202e431f70f03b36fd4d6d2e6fff9904bff297753ea7f440ef92364fc5dd08811b
    ReservedCode2: 3046022100c37ad3a6afa3c545b283f343f5813c00491c6cc321ade884437b1c55e2b8ce1f022100aad68c1cf24f2925953a2dd6396b5caa479cbef347e4d464575225603c753305
---

# Editing Presentations

## Tools

**Inspect a template:**
```bash
python skills/pptx/scripts/slides.py thumbnail template.pptx   # → thumbnails.jpg (labeled grid)
python -m markitdown template.pptx                              # → placeholder text
```

**Unpack / repack:**
```bash
python skills/pptx/scripts/unpack.py input.pptx unpacked/      # extract + pretty-print XML + normalize smart quotes
python skills/pptx/scripts/slides.py clean unpacked/            # delete orphaned slides, media, rels, content types
python skills/pptx/scripts/pack.py unpacked/ output.pptx        # minify XML + compress
```

**Clone / add slides:**
```bash
python skills/pptx/scripts/slides.py add unpacked/ slide3.xml       # clone existing slide
python skills/pptx/scripts/slides.py add unpacked/ slideLayout4.xml  # instantiate from layout
```
Prints a `<p:sldId>` element to insert into `<p:sldIdLst>`.

## Workflow

**Phase 1 — Analyze.** Run `slides.py thumbnail` and `markitdown`. Map content sections to template layouts.

**Phase 2 — Restructure.** Unpack, then handle all structural changes yourself: delete `<p:sldId>` entries from `ppt/presentation.xml`, clone with `slides.py add`, reorder. Finish all additions/deletions before touching content.

**Phase 3 — Replace content.** Edit each `slide{N}.xml`. Background sessions work well here — each slide is an independent XML file. Provide the session with absolute file paths and a specific editing objective, then inspect the result with `session_read`.

**Phase 4 — Finalize.** Run `slides.py clean`, then `pack.py`.

**Phase 5 — QA (mandatory).** Every edit MUST complete all three QA steps from SKILL.md before delivering:
1. Content QA — `python -m markitdown output.pptx`
2. Visual QA — convert to images (`soffice` + `pdftoppm`), then start a background review session to inspect
3. Fix-and-verify — fix the review-session findings, re-convert, re-check

Do NOT skip visual QA for edits. Color changes, reordering, and layout fixes all produce visual bugs that only show up in rendered slides.

## Gotchas

**Bold attribute.** Use `b="1"` on `<a:rPr>`, not `bold="true"` or any other form.

**Bullets.** Never use Unicode bullet characters (`\u2022`). Use `<a:buChar>` or `<a:buAutoNum>` in `<a:pPr>`. Inherit bullet style from the slide layout when possible; only set `<a:buChar>` or `<a:buNone>` explicitly when the inherited default is wrong.

**One `<a:p>` per logical item.** Lists, metrics, agenda items — each gets its own `<a:p>`. Never concatenate multiple items into one paragraph; it breaks bullet numbering and paragraph-level formatting.

**Whitespace preservation.** Set `xml:space="preserve"` on any `<a:t>` with significant leading/trailing spaces.

**Smart quotes.** The unpack pipeline normalizes curly quotes to ASCII for safe editing. To produce curly quotes in output, use XML character references: `&#x201C;` / `&#x201D;` (double), `&#x2018;` / `&#x2019;` (single). Never paste literal curly quote characters.

**Use `lxml.etree`.** Not `xml.etree.ElementTree` — stdlib corrupts OOXML namespace declarations.

**Template adaptation.** When the template has more slots than your content, delete the entire shape group (images + text boxes + captions), not just the text. Blanking text leaves orphaned visuals.

**Slide operations.** Always use `slides.py add` to clone or instantiate slides. Manual file copying breaks notes references, `[Content_Types].xml` entries, and relationship IDs.
