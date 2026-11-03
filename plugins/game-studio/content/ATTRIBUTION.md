# Attribution

This package adapts the `game-studio` plugin from the OpenAI Plugins repository.

- Repository: https://github.com/openai/plugins
- Source path: `plugins/game-studio`
- Source commit: `1e285826e604f66f7208f7ac4dba0fe8341d1f57`
- Upstream version: `0.1.2`
- Upstream author: OpenAI
- Upstream license declaration: MIT

## MiniMax adaptations

- Removed Codex-specific manifest and agent presentation metadata from the packaged runtime surface.
- Replaced the optional OpenAI `imagegen` Skill dependency in `sprite-pipeline` with MCode's host-native `image_synthesize` capability.
- Made helper-script examples resolve from the installed plugin root and keep outputs inside the active workspace.
- Converted the upstream 400×400 PNG app icon into a 512×512 WebP marketplace icon.

The upstream package did not contain a standalone license file at the pinned commit. Its `.codex-plugin/plugin.json` manifest declares `"license": "MIT"`; this package preserves that declaration and includes the MIT terms in `LICENSE`.
