---
name: android-apk-builder
description: Build a complete, signed Android APK from a one-line product spec — "make me a calculator app" or "build an APK for a habit tracker with daily reminders". Handles JDK + Android SDK + Gradle install, project scaffolding (Kotlin + Jetpack Compose + Material 3, minSdk 24, targetSdk 34), `assembleDebug`, debug-keystore signing, and source/APK delivery. Use when the user wants to develop an Android app, generate an APK, build a mobile app from requirements, or run Android builds inside this cloud sandbox. Do NOT use for iOS apps, web apps, or existing Android projects the user wants to *open* in Android Studio locally.
---

# Android APK Builder

Build a signed, installable Android APK from a one-line product spec. The skill owns
the full pipeline: environment bootstrap → project scaffold → Gradle build → keystore
signing → source zip → delivery.

## Triggers

Activate when the user says any of:
- "做一个 Android app / 写个 APK / 帮我开发一个 App"
- "Build me an Android app that…"
- "Generate an APK for a [type] app"
- "From requirements to APK, one shot"

Do **not** activate for:
- iOS / iPadOS apps (no Xcode in this sandbox)
- React Native / Flutter / Capacitor (different build chain)
- Pure web apps or websites
- "Open my existing project in Android Studio" (user is on a local machine, not us)

## Required Inputs

Ask the user for any of these that are missing (keep it to one round of questions):

| Input | Default if unspecified |
|---|---|
| App display name | derive from requirement (TitleCase) |
| Package name (`com.x.y`) | `com.example.<slug>` |
| minSdk | 24 (Android 7.0, ~98% device coverage) |
| targetSdk | 34 (Android 14) |
| Version name / code | 1.0 / 1 |

Reject package names that don't match `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$`.

## Pipeline

Run these scripts in order. The first one is expensive on a fresh sandbox;
the rest are fast and idempotent.

```bash
# 1. Bootstrap JDK 17 + Android SDK + Gradle 8.9 under /opt (idempotent).
#    Cold start: ~5-10 min (downloads ~1.2 GB). Warm start: <5 s.
bash scripts/env-setup.sh

# 2. Scaffold the project from the base template.
#    Runs a preflight scan for the Kotlin nested-comment gotcha — see below.
bash scripts/new-project.sh \
  --out /workspace/<project-slug> \
  --name "My App" \
  --package com.example.myapp \
  --min 24 --target 34
# Add --force to overwrite an existing output directory.

# 3. Build & sign (debug keystore auto-generated on first run).
#    First build: ~5-10 min (downloads Gradle + Maven deps).
#    Cached rebuild: 30-90 s.
#    Output streams live to a log file under /workspace/.android-build-logs/.
bash scripts/build.sh --project /workspace/<project-slug>

# 4. Zip the source for delivery.
bash scripts/package-source.sh \
  --project /workspace/<project-slug> \
  --output /workspace/<project-slug>-source.zip

# 5. Stage the deliverables. ALWAYS run this before wrapping in <deliver-assets>.
#    It produces:
#      <slug>-app-debug.apk       — original APK (for adb install)
#      <slug>-app-debug.apk.zip   — byte-identical, .apk.zip rename
#      <slug>-source.zip          — Android Studio project source
bash scripts/deliver.sh --project /workspace/<project-slug>
```

The base template already wires up:
- Kotlin 2.0.20 + AGP 8.5.2 + Compose BOM 2024.09
- Material 3 with dynamic color (Android 12+)
- Bottom navigation with `Home` and `Settings` tabs
- `DataStore`-backed user preferences (proves persistence works)
- Adaptive icon (vector, no PNGs needed)

The user's stated features go in as `TODO` comments inside the relevant screen's
ViewModel — the app builds and runs, and the user (or you, in a follow-up turn) fills
in the feature logic without touching the build chain.

## ⚠️ Kotlin Nested-Comment Gotcha (read before pasting any utility file)

**`new-project.sh` runs a preflight scan** for this. If it triggers, the build is
aborted before wasting 5 minutes on a download — fix the source first.

Kotlin's `/* ... */` comments are **nestable** (unlike Java). If a `/**` KDoc block
contains a `/*` substring — extremely common when you describe filesystem paths like
`/proc/*` or `/sys/devices/system/cpu/*` — the inner `/*` opens a nested comment. The
next `*/` only closes that nested level, leaving the outer KDoc open until EOF. The
whole file is then parsed as a giant comment and the build dies with the misleading
error:

```
e: file:///.../Foo.kt:90:1 Syntax error: Unclosed comment.
```

**Fixes** (any one):
1. Rephrase the comment to avoid the path, e.g. write "the cpuinfo pseudo-file"
   instead of "/proc/cpuinfo and /sys/.../*".
2. Escape the slash: write `/proc\u002F` or use the unicode U+002F.
3. Move the path example out of the comment and into a `private const val` instead.

The preflight scan lives in `scripts/new-project.sh` and is an awk state machine
that reads each `*.kt` file in the scaffolded tree. If you bypass `new-project.sh`
and write files by hand, run the same scan yourself:

```bash
awk 'BEGIN{s=0} /\/\*\*/{s=1; next} s==1 && /\/\*/{print FILENAME":"NR": NESTED /*"; exit 1} s==1 && /\*\//{s=0}' app/src/main/java/**/*.kt
```

## Customizing the launcher icon

The base template ships a generic adaptive icon (vector, no PNGs needed) wired
through two drawables. When the user supplies their own icon asset, swap them in
as follows.

The template's icon stack lives at:
- `app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml` — the adaptive-icon
  manifest; references `@drawable/ic_launcher_foreground` and
  `@drawable/ic_launcher_background`
- `app/src/main/res/drawable/ic_launcher_foreground.xml` — the visible vector
- `app/src/main/res/drawable/ic_launcher_background.xml` — solid color or
  pattern behind the foreground
- `app/src/main/res/values/colors.xml` — `ic_launcher_background` color ref

To replace with a user-supplied icon:
1. Save the user's asset as
   `app/src/main/res/drawable/ic_launcher_foreground.xml`. If the asset is
   raster (PNG/JPG), convert it to a vector drawable first (Android Studio's
   *Vector Asset Studio*, or `vd-tool` on the CLI). Confirm the resulting
   XML is a single `<vector>` root, not a `<bitmap>` reference.
2. If the new icon already includes its own background, replace
   `ic_launcher_background.xml` with a solid color (or leave the default).
   Update the `ic_launcher_background` entry in `colors.xml` if needed.
3. Re-run `bash scripts/build.sh --project /workspace/<project-slug>`. The
   adaptive-icon manifest in `mipmap-anydpi-v26/` is the source of truth on
   API 26+ and needs no edits.

Pre-API 26 fallback: minSdk 24 covers Android 7.0/7.1, which fall back to PNG
launchers in `mipmap-{m,h,xh,xxh,xxxh}dpi/`. The template does not ship these —
installs on those devices show a generic Android icon. If you need legacy
support, add a 192×192 `ic_launcher.png` to each `mipmap-*dpi/` directory.

Note: **designing** an icon asset from scratch is out of scope for v1; the
scope line should be read as "we don't draw icons for the user".
**Wiring in a user-supplied asset** is what this section covers.

## Adding more bottom-nav tabs

The template ships with two tabs (`Home`, `Settings`). To add a third
(e.g. `Stats`) and wire it into the bottom navigation, touch these four files
in order. After every edit, run
`bash scripts/build.sh --project /workspace/<project-slug>` to confirm the
project still compiles before moving on.

1. **Create the screen Composable** at
   `app/src/main/java/<package-path>/ui/stats/StatsScreen.kt`. Mirror the
   structure of `HomeScreen.kt` — a `@Composable` that observes its ViewModel
   via `collectAsStateWithLifecycle()` and emits Material 3 widgets.
2. **Create the ViewModel** at
   `app/src/main/java/<package-path>/ui/stats/StatsViewModel.kt`. Extend
   `ViewModel`, expose state as `StateFlow<StatsUiState>`. Keep it empty for
   now (return a default state); features go in as TODOs the same way
   `HomeViewModel` does.
3. **Register the route** in
   `app/src/main/java/<package-path>/ui/NavGraph.kt`. Add a
   `composable("stats") { ... }` entry alongside the existing `home` and
   `settings` routes.
4. **Add the bottom-nav item** in
   `app/src/main/java/<package-path>/ui/MainScreen.kt` (or wherever the
   `NavigationBar` is declared). Add a new `NavigationBarItem` keyed off a
   `Screen.Stats` sealed-class entry — keep the icon, label, and route
   string in lockstep with step 3.

If the new tab needs persistence-backed state, mirror the `DataStore` pattern
from `SettingsViewModel`. If it needs a database, see the Room escalation note
in Scope Boundaries — Room is out of scope for v1.

If you find yourself adding 5+ tabs, the template's bottom-bar layout is the
wrong primitive — consider `NavigationRail` (tablet) or a side drawer
instead, and tell the user the template's MVP assumption no longer holds.

## Output Contract

Always run `scripts/deliver.sh` last. It stages three files (under
`<project>/deliverables/`) and prints a copy-paste-ready `<deliver-assets>` block.

Why two extensions of the same APK:
- `.apk` — for direct adb / sideload: `adb install -r <slug>-app-debug.apk`.
- `.apk.zip` — for environments that block `.apk` downloads (corporate proxies,
  some chat tools, certain email gateways, browsers with download warnings).
  The bytes are identical (verified by `sha256sum` inside `deliver.sh`).
  The user renames it back to `.apk` to install.

Always include **both** in the `<deliver-assets>` block, plus the source zip:

```
<deliver-assets>
<media type="file" src="<slug>-app-debug.apk.zip" caption="Signed debug APK (.apk.zip for friendly downloads)" />
<media type="file" src="<slug>-app-debug.apk"     caption="Same APK as .apk (for direct adb install)" />
<media type="file" src="<slug>-source.zip"        caption="Full Android Studio project source" />
</deliver-assets>
```

Print a one-line summary in chat: APK size, package, minSdk, targetSdk, install
command.

## Monitoring a Long Build

The first `assembleDebug` on a fresh sandbox can take 5-10 minutes — most of it is
downloading the Gradle distribution + ~1 GB of Maven dependencies. `build.sh` does
three things to make that bearable:

1. **Streams to a log file** under `/workspace/.android-build-logs/build-<timestamp>.log`
   so progress is visible in real time. Tail it in another shell:
   ```bash
   tail -f /workspace/.android-build-logs/build-*.log
   ```
2. **Pre-build cleanup** — kills stale Gradle / Kotlin compile daemons from
   prior failed runs. The single most common cause of "build hangs forever" is a
   zombie `KotlinCompileDaemon` (pid 16xxx in `ps`) holding file handles.
3. **Prints a tail + summary on exit** — last 20 lines of the log, plus a hint about
   which phase dominated the wall clock (download-heavy vs compile-heavy).

If a build appears stuck, the right diagnostic is to look at what the JVM is doing:

```bash
# Threads + what they're blocked on
jstack <pid> | head -100

# How much CPU has it actually used?
ps -o pid,pcpu,pmem,etime,cmd -p <pid>

# Is the Kotlin daemon still alive?
pgrep -af "KotlinCompileDaemon"
```

## Failure Handling

- **`env-setup.sh` fails on apt**: sandbox apt mirror is dead. The script
  auto-switches to `mirrors.tuna.tsinghua.edu.cn` and re-tries. If that mirror is
  also blocked, set `APT_MIRROR=https://your-mirror/debian` and patch
  `ensure_apt_sources` in the script.
- **`env-setup.sh` fails on Gradle download**: set `GRADLE_MIRROR=https://your-mirror`
  to override the auto-pick.
- **`assembleDebug` fails on first run**: Gradle is still downloading dependencies.
  Re-run `bash scripts/build.sh --project ...` — the second run uses the cache.
  Watch the log to see if it's network or compile.
- **`assembleDebug` fails on every run** with "Unclosed comment" or "Unresolved
  reference" that doesn't match the source you wrote: see the **Kotlin
  Nested-Comment Gotcha** section above. The preflight check should have caught
  it; if it didn't, run the awk one-liner manually.
- **`assembleDebug` produces the wrong APK** (e.g. x86 included despite
  `abiFilters`): run `aapt dump badging app-debug.apk | grep native-code`. It
  should be `'arm64-v8a'` only.
- **APK won't install on user's device**: see `references/troubleshooting.md` →
  "APK Won't Install on Device".
- **APK won't download** (browser warning, blocked by corporate proxy, etc.):
  use the `.apk.zip` variant from `deliver.sh`. The bytes are identical.
- **NAS / NFS lock files (.nfs*) on `/workspace`**: kill stale Gradle daemons
  (`pkill -9 -f "GradleDaemon|KotlinCompileDaemon"`), then re-run. `build.sh` does
  this automatically. The script already forces `GRADLE_USER_HOME=/root/.gradle`
  to keep caches off NFS — but a daemon from a prior session can still hold nfs
  locks on `.gradle/` inside the project dir.

## Scope Boundaries (MVP)

The base template supports **local-only** apps out of the box:
- Local UI, navigation, state
- `DataStore` for key/value preferences
- Material 3 theming

**Out of scope for v1** (escalate to the user before adding):
- Network / REST / GraphQL → add Retrofit + OkHttp
- Local DB → add Room
- Camera / microphone / location → add permissions + a feature module
- Push notifications → needs FCM + Google Services JSON
- App icon design from scratch (we don't draw icons for the user; wiring a
  user-supplied asset is in-scope — see **Customizing the launcher icon**)
- Release signing with a real keystore (debug signing is automatic; release needs
  the user to provide a `.jks` and passwords)

When a request hits an out-of-scope feature, say so explicitly and ask whether to
extend the skill or treat the current run as MVP.

## Memory / Logs

Build logs land in `/workspace/.android-build-logs/`. Don't delete them mid-session —
they're how you debug build failures. The most recent build's log is
`build-<timestamp>.log`; older logs are kept for diagnosis. Surface the relevant log
path in any error message you hand back to the user.

Deliverable files for the most recent build live under
`<project>/deliverables/`. Re-running `deliver.sh` overwrites them in place.
