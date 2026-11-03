# Official Marketplace release

This package targets the CN official MiniMax Marketplace, category Code, desktop delivery. The catalog entry and package name must remain app-development-workbench. iOS build workflows require macOS even though deliveryTargets does not express an OS filter.

1. Fetch current dev/main and create a feature branch from dev; keep unrelated packages/catalog entries intact.
2. Validate the complete repository using reference_vectors.py, validate_marketplace.py and its JSON projection, plus the repository test suite. Check package references, scripts and the real raster icon.
3. Run publish_marketplace.py --dry-run with deployment cn and an output directory outside the checkout. Inspect the target ZIP, package/icon digests and projection. Never execute --publish locally.
4. Commit and push within user authorization; submit an MR to dev with English title and Chinese description. Passing local checks does not replace the MR pipeline.
5. After authorized dev merge, verify the actual test publication job and package version in the test market. Check list/detail/install/enable, Skill discovery and MCP behavior in the MiniMax client. Standalone tools/list is narrower evidence.
6. Production is a separate task after test acceptance: branch from latest main, transfer only verified target commits, rerun gates, create main MR and require the designated production approval. Never promote all dev contents.

Package changes require a version bump once published. Do not add darkIcon to a production package while the current compatibility gate forbids it. Administrative ordering/listing belongs to the corresponding environment's Plugins Tab, not Git array order.

See the authoritative repository README and .agents/skills/plugin-creator/SKILL.md at https://gitlab.xaminim.com/matrix/minimax-plugin-marketplace . Current CI and marketplace acceptance status belong in the MR/release report, not hard-coded as permanent claims in a reusable skill.
