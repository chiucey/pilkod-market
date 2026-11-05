# Third-party licenses

The diagram-design skill itself is MIT-licensed (see [`LICENSE`](LICENSE)). It bundles content from the following third-party sources, redistributed under their respective licenses.

## Tabler Icons

- **License:** MIT
- **Upstream:** https://github.com/tabler/tabler-icons
- **Used in:** stroked icons in `skills/diagram-design/references/primitive-icons.md` and `skills/diagram-design/assets/icons.html` (categories: Compute, People, Network, Data, Kubernetes, Action, DevOps, plus the stroked Brand outlines for Docker, Terraform, AWS, Azure, GitHub).

The MIT license is reproduced in full at `third_party/tabler-icons-LICENSE`.

## Simple Icons

- **License:** CC0 1.0 Universal (Public Domain Dedication)
- **Upstream:** https://github.com/simple-icons/simple-icons
- **Used in:** filled brand silhouettes in `skills/diagram-design/references/primitive-icons.md` and `skills/diagram-design/assets/icons.html` (Kubernetes, Google Cloud, PostgreSQL, Nginx, Gitea, Keycloak, MinIO, Apache NiFi, Apache Airflow, Trino, Apache Superset, Jupyter, Python, R).

The CC0 dedication is reproduced in full at `third_party/simple-icons-CC0-1.0`.

## log-z/logos

- **License:** MIT
- **Upstream:** https://github.com/log-z/logos/tree/main/website-logos
- **Used in:** filled brand silhouettes that aren't carried by Simple Icons or Tabler — currently MySQL, Redis, and StarRocks. Source SVGs are 100×100 with embedded `<style>` + class-based fills; the build script strips the style block and rewrites class refs to `currentColor` for monochrome consistency.

The MIT license is reproduced in full at `third_party/log-z-logos-LICENSE`.

## Devicon

- **License:** MIT
- **Upstream:** https://github.com/devicons/devicon
- **Used in:** the RStudio and SPSS icon markup embedded in
  `skills/diagram-design/references/primitive-icons.md` and
  `skills/diagram-design/assets/icons.html`.

The MIT license is reproduced in full at `third_party/devicon-LICENSE`.

## One-off sourced icons

The SAS icon markup embedded in
`skills/diagram-design/references/primitive-icons.md` and
`skills/diagram-design/assets/icons.html` was sourced upstream from
[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:SAS_logo_horiz.svg)
(public domain). Its provenance is recorded here; use of this product mark is
covered by the Trademarks note below. The upstream Stata icon is intentionally
not redistributed because its source did not provide a clear redistribution
license.

## Trademarks

Brand logos remain the trademarks of their respective owners. Their inclusion in this icon set is for documentation and illustrative use only. The presence of a brand mark in this repository does not imply endorsement, sponsorship, or affiliation.
