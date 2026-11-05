# Chrome DevTools MCP Plugin attribution

This package is a MiniMax Marketplace distribution of the official
[`ChromeDevTools/chrome-devtools-mcp`](https://github.com/ChromeDevTools/chrome-devtools-mcp)
plugin at commit `d1e73ffd7e7329386c7606c947b0f88047bbe765` and npm version `1.8.0`.

The five MCP-oriented Skills in this package are copied verbatim from that commit and are
distributed under the Apache License 2.0 in [`LICENSE`](LICENSE). The upstream CLI-only Skill is
not included because it requires a separate global npm installation that is outside the Plugin
runtime. The MCP launch configuration is adapted for MiniMax Plugin V1: it pins version `1.8.0`,
uses non-interactive `npx`, disables anonymous usage statistics, and disables redundant upstream
update checks. The MCP executable itself is fetched from npm on first use and is not redistributed
inside this archive.

The icon is the unmodified 512 x 512 WebP Chrome DevTools logo from
[`ChromeDevTools/devtools-logo`](https://github.com/ChromeDevTools/devtools-logo) at commit
`6dd4391f4855e11c4b959fac0b5bed71cbef6f30`, path
`logos/webp/devtools-square-512.webp`, with SHA-256
`9576ba861375d6464d67db58db5f4c1efe8de2c4a0d394d73001d29b457d3401`. The logo is licensed
under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

Chrome DevTools MCP requires a supported Node.js LTS release, npm, and Google Chrome or Chrome for
Testing. It can inspect and modify data in the browser instance. Performance tools may query the
Google CrUX API for field data; the package disables Chrome DevTools MCP usage statistics but does
not disable CrUX-backed performance insights.
