# Windows Tool Bootstrap

Use this guide when `platform` is `win32`. Detect required tools before running a workflow. Do not
install or modify system software without user authorization.

## Required tools

Run these checks in PowerShell:

```powershell
bash --version
python --version
node --version
npm --version
uv --version
soffice --version
python -m markitdown --help
```

The core PPTX workflows require:

- Git Bash for `.sh` commands and pipelines
- Python plus `uv` for `python-pptx` and Pillow workflows
- Node.js plus PptxGenJS for deck generation
- MarkItDown for content QA
- LibreOffice for rendering or format conversion when that route is used

If a check fails, report the missing dependency and obtain approval before installing it. Use the
organization-approved installer or package manager. After installation, open a new PowerShell
session or refresh `PATH`, then rerun the check.

Python and Node package checks:

```powershell
uv run --with python-pptx python -c "from pptx import Presentation; print('python-pptx ok')"
uv run --with pillow python -c "from PIL import Image; print('Pillow ok')"
node -e "require('pptxgenjs'); console.log('PptxGenJS ok')"
```

## Running Bash commands

Invoke Bash scripts explicitly from PowerShell:

```powershell
bash -c "python -m markitdown output.pptx | grep -iE 'xxxx|lorem|ipsum|placeholder'"
```

Git Bash usually maps `/tmp/` automatically. Prefer forward-slash paths when passing Windows
paths to Bash:

```powershell
bash -c "python -m markitdown 'C:/path/to/input.pptx'"
```

The bundled `scripts/pptx-screenshot.sh` remains macOS-only because it requires Swift. On Windows,
render with LibreOffice or another approved PowerPoint-compatible renderer, then inspect the
resulting PDF or slide images.
