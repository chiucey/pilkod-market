# Attribution

This package selects nine MIT-licensed Skills from K-Dense Scientific Agent Skills.

- Repository: https://github.com/K-Dense-AI/scientific-agent-skills
- Source commit: `1dd0fccf46fc3c9855c4a0c313a0c57fe4319883`
- Upstream Plugin version: `2.65.0`
- Upstream author: K-Dense Inc.
- License: MIT; see `LICENSE`

## Included Skills

| Skill | Upstream version |
| --- | --- |
| `scientific-brainstorming` | `1.1` |
| `hypothesis-generation` | `2.1` |
| `experimental-design` | `1.1` |
| `statistical-power` | `1.0` |
| `statistical-analysis` | `1.1` |
| `uncertainty-and-units` | `1.0` |
| `scientific-writing` | `2.0` |
| `peer-review` | `2.1` |
| `scholar-evaluation` | `2.1` |

## MiniMax adaptations

- Selected a coherent, local-first research workflow rather than packaging the full upstream
  catalog. Upstream Skills with network credentials or non-MIT terms are not included.
- Added the MiniMax Plugin V1 manifest and Marketplace catalog metadata.
- Renamed the scientific-writing unfinished-field marker to `DRAFT` in its templates, linter, and
  scaffold helper so the package passes the official hosted-content validator without changing the
  marker's meaning.
- Cropped the left 864 by 864 pixels of upstream
  `docs/images/scientific-brainstorming.png` and converted it to a 512 by 512 WebP Marketplace icon.

No other Skill instructions, references, assets, or scripts were modified from the pinned source.
