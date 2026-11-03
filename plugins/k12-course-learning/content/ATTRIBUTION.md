# Attribution and provenance

This Plugin combines original MiniMax packaging and learning workflows with a verified subset of
the Marble Skill Taxonomy. It does not relicense third-party material.

## Plugin integration and original files

- Author: MiniMax
- Original components: `recall-k12-taxonomy`, the stateless implementation packaged as
  `study-tutor`, `visualize-k12-concepts`, the Python retrieval and HTML-generation scripts, the
  Chinese query aliases, and the generated marketplace icon.
- The generated icon was created for this package with the built-in image-generation tool on
  2026-08-04. It uses an open book, a learning path, and connected knowledge nodes; it contains no
  text, upstream logo, institutional mark, or watermark.

## Marble Skill Taxonomy

- Authors: Guillaume Boniface-Chang and Generative Spark, Inc. (Marble)
- Source: https://github.com/withmarbleapp/os-taxonomy
- Source revision: `96a7933754af672e1bfdbf7ecb05c325860c6e0d`
- Database license: ODbL 1.0; see `data/os-taxonomy/LICENSE`.
- Authored content license: CC BY-SA 4.0; see `data/os-taxonomy/LICENSE-CONTENT`.
- Upstream provenance and citation: `data/os-taxonomy/PROVENANCE.md` and
  `data/os-taxonomy/CITATION.cff`.
- Included unmodified data subset:
  - `data/os-taxonomy/data/topics.json`, SHA-256
    `2d99fc3b5e57d9ddb86b6c179b58a1b0390f048d9798585fe03b13cbc183719b`
  - `data/os-taxonomy/data/dependencies.json`, SHA-256
    `86a24efb44b480e5be23082b4bdea653f69f6d6fd54c5409a2f33c185be1d87f`
- The full upstream curriculum-standards, clusters, media, build scripts, and development metadata
  are not included because the Plugin's offline retrieval path does not consume them. Topic records
  may retain factual standard identifiers; the package does not redistribute the omitted standards
  database or its full text.

Required attribution when reusing taxonomy text:

> Marble Skill Taxonomy (v1) · © Generative Spark, Inc. (Marble) · https://withmarble.com

## User-supplied `study-tutor` input

- Original author metadata: `jiangkaiqi2005`
- Recorded upstream commit:
  https://github.com/openclaw/skills/commit/f57c069631244daa94b9de7358c585a0946d8778
- The supplied Skill identified its license as `Proprietary` and contained persistent learning
  profiles, memory lookup, file updates, and scheduled reminders.
- To meet the requested cloud-stateless contract and avoid redistributing proprietary prose, this
  package does not include that upstream README, Chinese duplicate, metadata, examples, or original
  long-form instructions. The packaged `study-tutor/SKILL.md` is a new, compact stateless workflow
  written for this Plugin. The original author remains credited for provenance.

## Packaging changes

- Converted the local Codex Plugin structure to MiniMax Plugin V1.
- Removed Codex marketplace metadata and all unreferenced Skill UI metadata.
- Limited all runtime content to supplied files, bundled local data, and current-request outputs.
- Added explicit routing, privacy, attribution, offline, and statelessness boundaries.
- Kept HTML output as a user-requested deliverable; it is never read back as hidden learner state.
