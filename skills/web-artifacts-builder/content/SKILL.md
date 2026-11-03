---
name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
---

# Web Artifacts Builder

To build powerful frontend claude.ai artifacts, follow these steps:

1. Initialize the frontend repo using `scripts/init-artifact.sh`
2. Develop your artifact by editing the generated code
3. Bundle all code into a single HTML file using `scripts/bundle-artifact.sh`
4. Display artifact to user
5. (Optional) Test the artifact

**Stack**: React 18 + TypeScript + Vite + Parcel + Tailwind CSS + shadcn/ui

## Design & Style Guidelines

**VERY IMPORTANT**: To avoid "AI slop", avoid:
- Excessive centered layouts
- Purple gradients
- Uniform rounded corners
- Inter font

## Quick Start

### Step 1: Initialize Project

```bash
bash scripts/init-artifact.sh
cd <project-name>
```

This creates a fully configured project with:
- React + TypeScript (via Vite)
- Tailwind CSS 3.4.1 with shadcn/ui theming
- Path aliases (`@/`) configured
- 40+ shadcn/ui components pre-installed
- All Radix UI dependencies
- Parcel configured for bundling

### Step 2: Develop Your Artifact

Edit the generated files. See Common Development Tasks for guidance.

### Step 3: Bundle to Single HTML

```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined.

### Step 4: Share Artifact

Share the bundled HTML file in conversation with the user.

### Step 5: Testing (Optional)

Only test if necessary or requested. Avoid testing upfront as it adds latency.

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components
