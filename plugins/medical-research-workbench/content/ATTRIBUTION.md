# Attribution and packaging notes

## Original work

- Original author: **AIPOCH**
- Upstream repository: <https://github.com/aipoch/medical-research-skills>
- Upstream collection: `awesome-med-research-skills`
- Source revision recorded in the supplied archive: `f5ef65b9bea79b6dd9553f52f95b0d08f7d64d26`
- Supplied archive: `medical-research-skills-main.zip`
- Supplied archive SHA-256: `0854aa48f3a92fa7987e1475873748a28461989e9c1a264ecb932e4ea6c77c44`
- License: MIT. The complete upstream license notice is included at `licenses/AIPOCH-MIT.txt`.

The Marketplace manifest preserves `AIPOCH` as the Plugin author. Packaging does not transfer or
replace upstream authorship.

## Included Skills

This package selects 18 Skills from the upstream collection:

- Evidence work: clinical question clarification, search strategy design, paper screening, evidence
  mapping, research-gap finding, literature deep reading, study-design identification, methods
  reconstruction, result-reliability checking, claim verification, and contradiction resolution.
- Protocol work: objective refinement, primary-plan selection, feasibility-aware planning, endpoint
  definition, confounder and bias control, sample-size and power planning, and validation strategy.

## Marketplace adaptations

The original instructional substance is retained. The following packaging changes were made for a
portable, cloud-compatible MiniMax Plugin:

1. Selected only the 18 cohesive Skills listed in the manifest and retained every reference file
   they cite.
2. Omitted upstream `eval_report_*` self-evaluation artifacts because they are development reports,
   not runtime dependencies.
3. Omitted the unreferenced
   `medical-research-gap-finder/references/workflow-step-template.md`; the included Skill does not
   cite it, and its active workflow remains fully defined in `SKILL.md` and referenced modules.
4. Omitted the optional `biomedical-search-strategy-builder/scripts/main.py` helper and its
   `requirements.txt`. The Skill does not invoke them; omitting them removes an unnecessary network
   helper and Python dependency without removing the query-design capability.
5. Normalized Skill frontmatter to the Marketplace-required `name` and `description`; original
   author, source, and MIT license attribution remain in each Skill body and this file.
6. Added explicit routing boundaries between bundled Skills, availability-aware literature
   retrieval language, and guardrails against fabricated evidence or claims of tool success.
7. Added privacy, patient-safety, research-ethics, regulatory, and cloud-statelessness boundaries.
8. Renamed the literature reader's optional output “plugins” to “optional deliverables” so it is not
   confused with Marketplace Plugins, and tightened verification requirements for generated
   experiment, bioinformatics, paper-discovery, and project-idea outputs.
9. Added navigation tables to long reference modules for progressive disclosure; this does not
   change their scientific content.

## Icon

`icon.png` is original AI-generated artwork created for this Marketplace package at the user's
direction. It is not an AIPOCH logo, institutional mark, or asset from the upstream repository.

## Runtime and state boundary

The package contains instructions and Markdown references only; it includes no App, MCP server,
executable code, credential, database, cache, session store, background service, or persistent
writer. Any external literature lookup is conditional on tools and access supplied by the host at
request time. Outputs are inline or host-managed request artifacts and must not be treated as
durable cross-request state.
