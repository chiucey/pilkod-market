# Environment doctor

Load this file when the user asks to run diagnostics, health checks, or first-run troubleshooting.

The goal is a one-shot report that checks local readiness for Diagram Design import/export, without mutating user files or installing dependencies.

Resolve the Diagram Design installation from this loaded reference, not from the
user's current working directory. A normal project directory is the expected
place to invoke the doctor and must not be treated as a repository-path error.

## Inputs

Optional flags:

- `--strict` — treat warnings as failures in the final summary.
- `--json` — print a machine-readable JSON report in addition to human summary.

If no flags are provided, run in standard mode.

## Required checks

Run all checks in this order and report each as `pass`, `warn`, or `fail`.

1. Python runtime
- Resolve `python3` first, then `python`.
- Require version >= 3.10.
- `fail` if no Python interpreter is found.
- `fail` if version is below 3.10.

2. Playwright availability for PNG export
- Check whether Playwright import works in the active Python interpreter (`import playwright`).
- Check whether Chromium is installed for Playwright (`playwright install --help` availability is sufficient for command presence; prefer also checking browser cache when practical).
- If missing, mark `warn` and print exact setup hint:
  - `pip install playwright && playwright install chromium`
- Never auto-install dependencies.

3. Skill installation integrity
- Verify `SKILL.md`, `assets/example-architecture.html`, and the referenced
  import/export guides exist beneath the resolved installation root.
- Missing installed files are `fail` and should suggest reinstalling or updating
  Diagram Design.

4. Common path mistakes
- Verify `SKILL.md` beneath the resolved installation root. Do not search for it
  relative to the user's current project and do not instruct users to enter the
  maintainer repository.
- Detect Windows path quoting risk when paths contain spaces and the provided command examples omit quotes.
- Detect references to local installed skill paths that do not exist (if command output includes one).
- Mark these as `warn` with a precise fix suggestion.
- A missing resolved `SKILL.md` should suggest reinstalling or updating Diagram
  Design, not changing into a repository checkout.

## Output contract

Always print:

1. A compact summary line:
- `Doctor summary: <PASS|WARN|FAIL> (<pass_count> pass, <warn_count> warn, <fail_count> fail)`

2. A checklist with one line per check:
- `[PASS] Python 3.11.9 found at ...`
- `[WARN] Playwright not installed ...`
- `[FAIL] Missing scripts/verify-docs-sync.py`

3. A `Next actions` section only when warn/fail exists.

4. If `--json` is present, append JSON object with:
- `status`, `counts`, `checks[]` (`name`, `status`, `message`, `fix` optional), `timestamp`.

## Safety and behavior rules

- Read-only diagnostics only: do not modify files, do not install packages, do not run destructive git commands.
- If any command fails unexpectedly, capture stderr and continue remaining checks.
- Never claim a check passed unless verified directly in this run.
- Prefer explicit, copy-pastable remediation commands.

## Example result

```text
Doctor summary: WARN (3 pass, 1 warn, 0 fail)
[PASS] Python 3.11.9 found at /usr/bin/python3
[WARN] Playwright package not found in active interpreter
[PASS] Installed skill files present
...

Next actions
- Install PNG export dependencies: pip install playwright && playwright install chromium
- Re-run the Diagram Design doctor in strict mode.
```
