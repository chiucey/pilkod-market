# Attribution and provenance

This Plugin combines four user-supplied Skill archives. Their original authors remain credited in
the Plugin manifest and in each Skill. Packaging changes are limited to restoring omitted companion
files, clarifying routing and evidence/privacy boundaries, and removing runtime-specific assumptions.

## Included Skills

### `academic-paper-polish`

- Author: yzy (`yzy1996` on GitHub)
- Source: https://github.com/yzy1996/English-Writing
- Upstream revision used for missing references: `b84f1bccae0c07b14cca843640278214af75b354`
- Supplied archive SHA-256: `cc2ffa2b19a033b0157f5fe0ae1d50ffd27ae145386dfce2ec3c0dac4261b33f`
- License: the upstream repository did not contain a license file when checked on 2026-08-04.
  This package does not relicense the work. It is included on the user's confirmation that they have
  permission and the necessary rights to publish it.
- Packaging changes: restored the three referenced Markdown files; clarified model-agnostic routing,
  meaning preservation, and the prohibition on invented evidence.

### `academic-abstract-refiner`

- Author: AIPOCH
- Source: https://github.com/aipoch/medical-research-skills
- Upstream revision used for the omitted script: `f5ef65b9bea79b6dd9553f52f95b0d08f7d64d26`
- Supplied archive SHA-256: `2fa6ac4a9360804e3d27ba3355aa4aa56b32761d03da7514a8e20f2122f59761`
- License: MIT; see `licenses/AIPOCH-MIT.txt`.
- Packaging changes: restored `scripts/refine_abstract.py`; clarified the script working directory,
  privacy handling, and the boundary between agent refinement and deterministic report rendering.

### `academic-paper-review`

- Author: ByteDance DeerFlow Authors
- Source: https://github.com/bytedance/deer-flow/tree/main/skills/public/academic-paper-review
- Upstream revision checked: `bec6277930d6ee73c58156689f1556780724e35d`
- Supplied archive SHA-256: `3d901748e0b84cfc373dcc85ce4fa871dbbf931b8eff9821a91edd579f8b9cc4`
- License: MIT; see `licenses/BYTEDANCE-DEERFLOW-MIT.txt`.
- Packaging changes: replaced DeerFlow-specific tool and output-path assumptions with portable capability
  checks; made external literature search conditional for confidential manuscripts.

### `academic-writing-latex`

- Author: Wentor AI
- Source: https://github.com/wentorai/research-plugins/tree/main/skills/writing/latex/academic-writing-latex
- Upstream revision checked: `bf44b3cd617fa94c8a1b254c5d1987142ca3d631`
- Supplied archive SHA-256: `2c7ceb06890de37a30cad4474dd1d1ccc06df3242aab3ce76828ddff9a5a52d3`
- License: MIT; see `licenses/WENTOR-AI-MIT.txt`.
- Packaging changes: fixed the thesis document-class example, removed runtime-specific assumptions,
  and added compilation and citation-integrity boundaries.

## Plugin icon

The marketplace icon is an original generated asset created for this package. It does not reuse any
upstream project logo or institutional mark.
