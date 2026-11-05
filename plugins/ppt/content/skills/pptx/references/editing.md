# Editing Existing Presentations

## Template-Based Workflow

When using an existing presentation as a template:

1. **Copy and analyze**:
   ```bash
   cp /path/to/user-provided.pptx template.pptx
   python -m markitdown template.pptx > template.md
   ```
   Review `template.md` to see placeholder text and slide structure.

2. **Plan slide mapping**: For each content section, choose a template slide.

   **USE VARIED LAYOUTS** — monotonous presentations are a common failure mode. Don't default to basic title + bullet slides. Actively seek out:
   - Multi-column layouts (2-column, 3-column)
   - Image + text combinations
   - Full-bleed images with text overlay
   - Quote or callout slides
   - Section dividers
   - Stat/number callouts
   - Icon grids or icon + text rows

   **Avoid:** Repeating the same text-heavy layout for every slide.

   Match content type to layout style (e.g., key points -> bullet slide, team info -> multi-column, testimonials -> quote slide).

3. **Unpack**: Extract the PPTX into an editable XML tree using Python's `zipfile` module. Pretty-print the XML for readability.

4. **Build presentation** (do this yourself, not in worker sessions):
   - Delete unwanted slides (remove from `<p:sldIdLst>`)
   - Duplicate slides you want to reuse (copy slide XML, relationships, and update `Content_Types.xml` and `presentation.xml`)
   - Reorder slides in `<p:sldIdLst>`
   - **Complete all structural changes before step 5**

5. **Edit content**: Update text in each `slide{N}.xml`.
   **Parallelize here if a delegation mechanism is available** — slides are separate XML files, so background sub-agent tasks can edit them in parallel. Do NOT spawn new user-visible sessions for this — sessions are reserved for users and external apps.

6. **Clean**: Remove orphaned files — slides not in `<p:sldIdLst>`, unreferenced media, orphaned rels.

7. **Pack**: Repack the XML tree into a PPTX file. Validate, repair, condense XML, re-encode smart quotes.

   Always write to `/tmp/` first, then copy to the final path. Python's `zipfile` module uses `seek` internally, which fails on some volume mounts (e.g. Docker bind mounts). Writing to a local temp path avoids this.

## Output Structure

Copy the user-provided file to `template.pptx` in cwd. This preserves the original and gives a predictable name for all downstream operations.

```bash
cp /path/to/user-provided.pptx template.pptx
```

```text
./
├── template.pptx               # Copy of user-provided file (never modified)
├── template.md                 # markitdown extraction
├── unpacked/                   # Editable XML tree
└── edited.pptx                 # Final repacked deck
```

Minimum expected deliverable: `edited.pptx`.

## Slide Operations

Slide order is in `ppt/presentation.xml` -> `<p:sldIdLst>`.

**Reorder**: Rearrange `<p:sldId>` elements.

**Delete**: Remove `<p:sldId>`, then clean orphaned files.

**Add**: Copy the source slide's XML file, its `.rels` file, and update `Content_Types.xml` and `presentation.xml`. Never manually copy slide files without updating all references — this causes broken notes references and missing relationship IDs.

### Notes Preservation

- Never point two slides at the same `notesSlideN.xml`. Notes parts are slide-owned, not reusable
  style resources.
- A cloned structural slide must receive its own notes part with the source plain text.
- Imported content notes relationships are dropped during cross-deck merge. Write final content
  notes after assembly through `mavis.ppt_notes.v1`.
- Rich notes formatting is not preserved by this flow.

## Editing Content

**Worker parallelism:** If available, delegate here (after completing step 4). Each slide is a separate XML file, so background sub-agent tasks can edit them in parallel; do NOT spawn new user-visible sessions for this (sessions are reserved for users and external apps). In your prompt to each worker, include:
- The slide file path(s) to edit
- **"Use the Edit tool for all changes"**
- The formatting rules and common pitfalls below

For each slide:
1. Read the slide's XML
2. Identify ALL placeholder content — text, images, charts, icons, captions
3. Replace each placeholder with final content

**Use the Edit tool, not sed or Python scripts.** The Edit tool forces specificity about what to replace and where, yielding better reliability.

## Formatting Rules

- **Bold all headers, subheadings, and inline labels**: Use `b="1"` on `<a:rPr>`. This includes:
  - Slide titles
  - Section headers within a slide
  - Inline labels like (e.g.: "Status:", "Description:") at the start of a line
- **Never use unicode bullets**: Use proper list formatting with `<a:buChar>` or `<a:buAutoNum>`
- **Bullet consistency**: Let bullets inherit from the layout. Only specify `<a:buChar>` or `<a:buNone>`.

## Common Pitfalls — Template Editing

### Template Adaptation

When source content has fewer items than the template:
- **Remove excess elements entirely** (images, shapes, text boxes), don't just clear text
- Check for orphaned visuals after clearing text content
- Run content QA with `markitdown` to catch mismatched counts

When replacing text with different length content:
- **Shorter replacements**: Usually safe
- **Longer replacements**: May overflow or wrap unexpectedly
- Verify with `markitdown` after text changes
- Consider truncating or splitting content to fit the template's design constraints

**Template slots != Source items**: If template has 4 team members but source has 3 users, delete the 4th member's entire group (image + text boxes), not just the text.

### Multi-Item Content

If source has multiple items (numbered lists, multiple sections), create separate `<a:p>` elements for each — **never concatenate into one string**.

**WRONG** — all items in one paragraph:
```xml
<a:p>
  <a:r><a:rPr .../><a:t>Step 1: Do the first thing. Step 2: Do the second thing.</a:t></a:r>
</a:p>
```

**CORRECT** — separate paragraphs with bold headers:
```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" .../><a:t>Do the first thing.</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 2</a:t></a:r>
</a:p>
<!-- continue pattern -->
```

Copy `<a:pPr>` from the original paragraph to preserve line spacing. Use `b="1"` on headers.

### Smart Quotes

The Edit tool converts smart quotes to ASCII. **When adding new text with quotes, use XML entities:**

```xml
<a:t>the &#x201C;Agreement&#x201D;</a:t>
```

| Character | Name | Unicode | XML Entity |
|-----------|------|---------|------------|
| \u201c | Left double quote | U+201C | `&#x201C;` |
| \u201d | Right double quote | U+201D | `&#x201D;` |
| \u2018 | Left single quote | U+2018 | `&#x2018;` |
| \u2019 | Right single quote | U+2019 | `&#x2019;` |

### Other

- **Whitespace**: Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces
- **XML parsing**: Use `defusedxml.minidom`, not `xml.etree.ElementTree` (corrupts namespaces)

## Merging Two Decks

When combining a structural-base PPTX (template-derived structure pages) with a content-only PPTX (PptxGenJS-generated content pages):

### Principles

1. The structural deck is the **base** — its theme, masters, and layouts are authoritative.
2. Content slides are imported as **standalone slides** without linking to the structural deck's layouts (they carry their own inline styling from PptxGenJS).
3. Media and chart files may have naming collisions between the two decks — always remap on conflict.
4. Imported content notes are dropped by default and regenerated after final assembly. Never retain
   a relationship such as `../notesSlides/notesSlide1.xml` without copying/remapping its complete
   owned part graph.
5. Every final page has a unique stable `slideId`; write a merge manifest for page identity.

### XML-Level Steps

```text
1. Unpack both PPTX files to temp directories
2. Identify slide files in each: ppt/slides/slideN.xml
3. For each content slide to import:
   a. Copy slideN.xml → structural/ppt/slides/slideM.xml (M = next available number)
   b. Copy slideN.xml.rels → structural/ppt/slides/_rels/slideM.xml.rels
   c. Parse the rels to find referenced media/charts
   d. Copy media files to structural/ppt/media/ (rename on collision)
   e. Copy chart files to structural/ppt/charts/ (rename on collision)
   f. Update rels targets if files were renamed
   g. Repoint the content slideLayout relationship to the structural deck's blank layout
   h. Remove imported notesSlide relationships under the default post-assembly notes policy
4. Update structural/ppt/_rels/presentation.xml.rels — add rId entries for new slides
5. Rewrite structural/ppt/presentation.xml <p:sldIdLst> in final order
6. Update structural/[Content_Types].xml — add Override entries for new slide files
7. Write `mavis.ppt_merge_manifest.v1` with final page identity
8. Repack into a static intermediate PPTX
9. Sanitize the assembled PPTX, apply the final notes sidecar when requested, and verify readback
```

### rId Remapping

Each slide relationship file has rId values (rId1, rId2, ...). These are scoped per-file and do NOT conflict across slides. However, `presentation.xml.rels` has a global rId space — when adding new slide relationships, always find the current max rId and increment from there.

### Content_Types

Each new slide needs an Override entry:

```xml
<Override PartName="/ppt/slides/slideM.xml"
         ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
```

Charts also need entries:

```xml
<Override PartName="/ppt/charts/chartN.xml"
         ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>
```

### Size Consistency

Both decks must use the same slide dimensions. The content deck (PptxGenJS) should detect and match the template's `<p:sldSz>` values. Common sizes:

| Name | Width | Height | PptxGenJS layout |
| --- | --- | --- | --- |
| Standard 4:3 | 9144000 EMU (10") | 6858000 EMU (7.5") | `LAYOUT_4x3` |
| Widescreen 16:9 | 9144000 EMU (10") | 5143500 EMU (5.625") | `LAYOUT_16x9` |
| Wide | 12192000 EMU (13.33") | 6858000 EMU (7.5") | `LAYOUT_WIDE` |
