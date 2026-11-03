# Codex adapter

Read this file only in Codex. Preserve the platform-neutral workflow and map it
to currently available tools.

## Capability detection

At setup, inspect callable tools and Skills rather than assuming them:

- `browser`: controllable Chrome or in-app Browser;
- `fetch`: non-rendered web access;
- `image_generation`: callable generation for approved Logo/page-media batches
  and optional visual concept mockups/cards;
- `subagent`: independent collaboration capability;
- `git`: usable Git in the target project.

Record `available`, `unavailable`, or `failed`, plus the chosen route and
failure when applicable.

Read the relevant Browser-control Skill before using Chrome or the in-app
Browser. Read the image-generation Skill before generation. Content-stage
generation still requires explicit approval of a named batch; visual concept
mockups require enough approved project context and the user's choice of the
generated-still or combined preview route. Do not call Image Generation when
the user selects HTML-only comparison.

For HTML visual comparison, update files under the project's review area and
inspect them in a real Browser. Prefer HTML when testing color Tokens,
typography, Chinese wrapping, component states, contrast, or responsive
behavior. Generated stills remain optional and never replace actual homepage
implementation.

## Browser routing

Prefer:

1. the user's Chrome session when login, cookies, or user state matter;
2. the Codex in-app Browser for a clean rendered session;
3. another real Browser-control capability.

For external references, open live rendered pages, change Desktop/Mobile
viewports, scroll, capture useful evidence, and exercise navigation and
interactions. Do not choose Fetch because it is faster.

When login is required, keep the session open, ask the user to log in there,
never request/type/store their password, and set
`waiting-for-user-login`.

Use Codex web access or another Fetch route only after no real Browser exists or
an actual rendered attempt fails. Record the failure and label evidence
`Fetched`. If Browser and Fetch both fail, stop in `reference`.

Use current internet search only when the user asks the Agent to recommend
references, when current asset licensing must be verified, or for another
current fact. Prefer primary/authoritative sources.

## Local review and website preview

Browser-visible HTML is the approval surface from `requirements` through
`review`.

1. Reuse an existing safe local development command.
2. Otherwise start a minimal static server rooted at the approved website
   directory when `file://` is unreliable.
3. Record its URL and process status.
4. Open both:
   - `/review/` for the conversation-language project review;
   - `/` and changed routes for the actual website.
5. Inspect changed routes at Desktop and Mobile.
6. Capture screenshots or equivalent evidence when supported.
7. Give the user both links, the changed pages, and what they need to decide.
8. Do not deploy the preview.

Do not install a framework merely to preview static HTML.

Expected actual-site state:

| Stage | Rendered state |
|---|---|
| requirements | neutral page/Section skeleton |
| reference | neutral evidence-backed navigation and broad structural rhythm |
| sitemap | all approved routes/templates exist |
| content | approved copy, links, and media states |
| layout | responsive composition for all templates |
| visual | approved tokens/components across all templates |
| animation | approved Hero/menu/scroll/media behavior or reviewed no-motion state |
| review | fully checked static delivery candidate |

If Codex cannot control a Browser but local files run, provide exact
instructions and ask the user to inspect. Mark automated rendered QA
`unable-to-verify`; never claim a Browser pass from source.

## Document assembly

Use the Skill's standard-library script:

```bash
python3 /absolute/path/to/hey-web-design/scripts/assemble_docs.py \
  /absolute/path/to/project all
```

Run `spec` or `design` when only one master changed. Do not edit compiled
masters manually. After compilation, update the matching `source_hash` in
project state from the generated header.

## Subagent review

Use Codex collaboration tools only for bounded, independent, read-only review
tasks. Provide role, stage, raw paths, Browser URL/screenshots, approved and
locked decisions, applicable rules, and report format. Do not provide the
expected answer or another Reviewer's conclusion before their first pass.

Use one or two Reviewers for Standard Review. Use three by default, at most
four, only for requested Deep Review, complex homepage finalization, or
full-site final delivery. Limit each checkpoint to one first pass and one
targeted re-review. Replace one failed Reviewer, then use a labeled
self-second-pass.

The main Agent alone edits files, merges reports, updates state, and asks the
user to change an approved decision.

## Filesystem and Git

Inspect `git status --short` before editing an existing repository.

- edit only the approved target;
- preserve unrelated files and dirty changes;
- stage explicit managed paths, never broad-add;
- if target lines overlap uncommitted user work, enter
  `waiting-for-user-git-decision`;
- never automatically Stash, Reset, Clean, Rebase, Checkout, or change global
  Git configuration;
- initialize Git only for a new standalone project, never as a nested repo.

Create a scoped checkpoint after a valid stage command. If Git is unavailable,
record it and continue without fabricating backups.

## Communication

Read [user-language.md](user-language.md) before every user-facing message.
Keep tool names, stage IDs, schema keys, Reviewer roles, and technical
vocabulary internal unless they materially affect a decision.

At each boundary, provide the review-page URL, actual website URL/routes,
visible change, remaining decision, browser-check status, and exact command in
plain language. Write the accepted command and time to project state; do not
let chat praise, a tool result, or a review pass advance the stage.
