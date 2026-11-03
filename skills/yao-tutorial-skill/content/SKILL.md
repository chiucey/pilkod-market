---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 86e834513160886df08bb8b42ca56b0c
    PropagateID: 86e834513160886df08bb8b42ca56b0c
    ReservedCode1: 3045022007eedbb89d32e1a5be296aa0de52e56d2daa894efdfd7e81c81637cdb005954e022100a72262c265dcfac8a50a9594a930c334ac835b2599701d2762a5a1c09b812c9f
    ReservedCode2: 3045022100b3010d6470d5f32549cad68289cc65c12c17de3153050ceb46bcd5882a9bd8f60220154f48f420a207170780952064ec69ad254bbed56232aff43cbc73d228eb92c1
description: Create standalone beginner tutorial packages from a topic or supplied references, with adaptive research, course-style outline design, chapter visuals, and Markdown/DOCX/PDF/HTML exports. Use for textbook-like tutorials, course guides, teaching documents, or long beginner guides; not for quick answers, link summaries, pure diagrams, or file conversion.
name: yao-tutorial-skill
---

# Yao Tutorial Skill

## Workflow

1. Normalize topic, audience, outcome, language, formats, user material, style references, and exclusions into `brief.json`.
2. Read `references/input-adaptation.md`; use user material as the spine when sufficient, then add only needed external research.
3. Read `references/research-sourcing.md`; create `research/user-materials-register.md` when needed, `research/source-register.md`, and `research/evidence-map.md`.
4. Read `references/tutorial-outline-and-writing.md` plus `references/course-design-principles.md`; write `outline.md`, then standalone public `tutorial.md` using `第1章` and `1.1`.
5. Read the editorial and visual references; create `visuals/visual-spec.json`, then run `build_visual_pack.py` and `capture_visuals.py`.
6. Read `references/export-workflow.md`; run `export_tutorial.py` and then `validate_package.py`.
7. Report exact failures and fallbacks. Never fabricate X posts, papers, repo details, dates, or citations.

## Quality Gates

- User material controls intent when strong enough; external evidence fills verification and gaps.
- Public exports never show internal source IDs or reference-packet provenance.
- Copy reads as a standalone formal teaching product.
- Every numbered chapter has a matching visual spec and embedded visual.
- Default full tutorial length is `5000-10000` Chinese characters or `3500-7000` English words unless requested otherwise.
- HTML uses centered `report-shell`; DOCX/PDF have no visible headers, footers, local paths, or print chrome.
- Delivery passes `scripts/validate_package.py` or names the remaining warnings/failures.

## References

- `references/input-adaptation.md`
- `references/research-sourcing.md`
- `references/tutorial-outline-and-writing.md`
- `references/course-design-principles.md`
- `references/editorial-production.md`
- `references/visual-html-workflow.md`
- `references/visual-board-benchmarks.md`
- `references/export-workflow.md`
- `scripts/build_visual_pack.py`, `scripts/capture_visuals.py`, `scripts/export_tutorial.py`, `scripts/validate_package.py`
- `templates/topic-brief-template.json`, `templates/visual-spec-template.json`, `templates/tutorial-style.css`
