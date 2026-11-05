# RedSkill distribution — 5.1.1

This distribution uses the public PPT Smith v5.1.1 source and preserves its authoring routes.

- ES-module runtime scripts use `.js` instead of `.mjs`; `runtime/pptxgenjs/package.json` retains `type: module` and all callers use the new filenames.
- Version and license text are retained in `VERSION.txt` and `LICENSE.txt`. Version-checking tools use `VERSION.txt`.
- Sample PNG/PPTX downloads are linked to the fixed upstream v5.1.1 release tag in the README instead of bundled, because RedSkill does not accept these file types. These samples are documentation resources, not runtime dependencies.
- Original upstream distribution: https://github.com/SkillMelody/PPT-Smith/tree/v5.1.1
