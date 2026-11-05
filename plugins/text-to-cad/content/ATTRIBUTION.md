# Attribution

This package is a MiniMax Marketplace distribution of
[`earthtojake/text-to-cad`](https://github.com/earthtojake/text-to-cad) at commit
`0e94cd1d2b5fa2013d89aa9504ecadcf16ce39f6` and upstream Plugin version `0.4.28`.

The complete upstream `skills/` tree is copied verbatim from that commit. It contains twelve
Skills for CAD creation and inspection, CAD Viewer, STEP part discovery, DXF, URDF, SRDF, SDF,
SendCutSend preflight, additive-manufacturing checks, G-code, Bambu Lab handoff, and implicit CAD.
The upstream work is licensed under the MIT License; the original license text is included in
[`LICENSE`](LICENSE).

## MiniMax adaptations

- Added the MiniMax Plugin V1 manifest and regional Marketplace catalog metadata.
- Added an original MiniMax distribution icon; it is not an upstream logo or trademark.
- Limited delivery to Desktop because the workflows operate on local project files and may require
  local Python/CAD dependencies, a browser-based viewer, slicer software, or LAN printer access.
- Disclosed that STEP part discovery accesses the third-party `step.parts` service. Other upstream
  handoff workflows may direct the user to external vendor services when explicitly requested.

No upstream Skill instructions, references, assets, scripts, requirements, or bundled viewer logic
were modified. Trailing whitespace and redundant blank lines at end-of-file were normalized in
vendored text files to satisfy repository diff hygiene.
