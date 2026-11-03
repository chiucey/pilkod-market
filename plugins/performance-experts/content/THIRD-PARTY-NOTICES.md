# Third-Party Notices

Popularity and repository statistics were checked on 2026-08-11. Install counts come from
[skills.sh](https://skills.sh/), whose leaderboard is based on anonymous `skills` CLI install
telemetry. Source code is pinned to the commits below so the packaged guidance is reproducible.
All bundled text has trailing whitespace removed to satisfy the Marketplace repository gate; this
format-only normalization does not change the guidance.

## Vercel React and React Native

- Source: [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- Commit: `7c180d9044c9ae2b442b567aad4e42a28dd5ed62`
- Included skills: `vercel-react-best-practices`, `vercel-react-native-skills`
- Popularity evidence: [React](https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices),
  [React Native](https://skills.sh/vercel-labs/agent-skills/vercel-react-native-skills)
- Popularity: 620.6K and 184.2K installs; 29.9K repository stars
- Security: Gen Agent Trust Hub, Socket, and Snyk audits passed on skills.sh
- License: each included upstream `SKILL.md` declares MIT
- Packaging change: generated `AGENTS.md`, README, and metadata files are omitted; the original
  rule files are included and the compiled-document pointer is replaced with a local routing note.

## Addy Osmani General Performance

- Source: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- Commit: `7676817c12a1317454ae3898a0c5c1eacf5dd3d5`
- Included skill: `performance-optimization`
- Popularity evidence: [skills.sh](https://skills.sh/addyosmani/agent-skills/performance-optimization)
- Popularity: 20.3K installs; 85.1K repository stars
- Security: Gen Agent Trust Hub, Socket, and Snyk audits passed on skills.sh
- License: MIT; see `licenses/MIT-ADDY-2025.txt`
- Packaging change: the referenced performance checklist is moved inside the skill so it remains
  self-contained.

## Addy Osmani Web Quality

- Source: [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills)
- Commit: `95d6e255afe1596b557d7a8498517884438f5b3a`
- Included skills: `performance`, `core-web-vitals`
- Popularity evidence: [Web performance](https://skills.sh/addyosmani/web-quality-skills/performance),
  [Core Web Vitals](https://skills.sh/addyosmani/web-quality-skills/core-web-vitals)
- Popularity: 26.3K and 19.2K installs; 2.6K repository stars
- Security: Gen Agent Trust Hub, Socket, and Snyk audits passed on skills.sh
- License: MIT; see `licenses/MIT-ADDY-2026.txt`
- Packaging change: none to skill content.

## Seth Hobson Python Performance

- Source: [wshobson/agents](https://github.com/wshobson/agents)
- Commit: `c4b82b0ad771190355eb8e204b1329732a18449a`
- Included skill: `python-performance-optimization`
- Popularity evidence: [skills.sh](https://skills.sh/wshobson/agents/python-performance-optimization)
- Popularity: 29.8K installs; 38.3K repository stars
- Security: Gen Agent Trust Hub, Socket, and Snyk audits passed on skills.sh
- License: MIT; see `licenses/MIT-SETH-HOBSON.txt`
- Packaging change: none to skill content.

## Paul Hudson SwiftUI

- Source: [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill)
- Commit: `be297ff80dddec529af1f9b1f1f114aab6c9d11c`
- Included skill: `swiftui-pro`, including its performance review guidance
- Popularity evidence: [skills.sh](https://skills.sh/twostraws/swiftui-agent-skill/swiftui-pro)
- Popularity: 25.4K installs; 4.4K repository stars
- License: MIT; see `licenses/MIT-PAUL-HUDSON.txt`
- Packaging change: agent-specific UI metadata and upstream artwork are omitted; the skill and all
  referenced guidance files are included unchanged.
