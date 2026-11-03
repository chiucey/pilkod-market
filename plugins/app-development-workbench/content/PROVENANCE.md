# Sources and independent rewrite

Author: AppCraft Lab. Version: 0.1.0.

This package contains newly authored Chinese skill instructions, references, templates and Python helpers. It does not copy the original plugin's code, reference corpus, icon assets, or project-specific HTML. No numerical similarity claim is made.

## Method sources

- OpenAI Build iOS Apps 0.1.2: studied the task sequence for SwiftUI, Simulator debugging, App Intents, Liquid Glass, CPU profiles and memory graphs. Source manifest declares MIT. Its branded assets and scripts are not redistributed here. Public project reference: https://github.com/openai/plugins .
- User-supplied app-design skill: used the exploration/refinement distinction, per-page direction comparison, explicit design decisions and browser evidence as requirements. Instructions were rewritten for the target host; old product templates and personal data are excluded.
- User-supplied project rules and development records: generalized the rule-discovery, shared DesignSystem, contract handoff, persistence and layered verification practices. Specific product colors, user data, private endpoints and local paths are excluded.
- Apple primary documentation is linked in each technical reference; version availability must be checked against the actual project SDK.
- XcodeBuildMCP 2.7.0 is an external MIT-licensed dependency executed through npx, not a vendored binary. https://github.com/getsentry/XcodeBuildMCP . Upstream licensing and third-party notices remain with that package.

## Coverage mapping

| Original responsibility | New location | Preservation/change |
|---|---|---|
| App Intents | ios-system-integration + system-integration.md | actions, entities, routing, discoverability and actual invocation |
| Simulator debugger | ios-simulator-debug + tool-runtime.md | discover, configure, build, launch, inspect, interact, capture logs; host-neutral tool discovery |
| ETTrace | ios-performance-investigate + performance.md | exact target, temporary linkage, matching symbols, focused capture, fresh processed outputs, restore |
| Memgraph | ios-memory-investigate + memory.md | correct process, capture, ownership chain, targeted repair and recapture |
| Liquid Glass | ios-system-integration + system-integration.md | SDK availability, shared components, fallback and accessibility |
| Performance review | ios-performance-investigate | code suspicion separated from trace evidence |
| SwiftUI UI patterns | ios-feature-build + swiftui-implementation.md | state ownership, navigation, async states, build and runtime checks |
| View refactor | ios-component-refactor + design-system.md | narrow inputs, named actions, stable identity, shared-style verification |
| Browser mirror / preview | ios-simulator-debug | capability-dependent path retained; no claim of arbitrary browser hot reload |

New responsibilities: project-rule discovery, prototype exploration/refinement/handoff, backend implementation and cross-layer acceptance. Templates preserve pending states rather than manufacturing requirements or completed evidence.

## Artwork

The default PNG is newly generated for this package using the built-in image generation tool. It is not the source plugin's logo and does not use Apple, Xcode or OpenAI marks. Prompt and generation record: references/icon-generation.md.
