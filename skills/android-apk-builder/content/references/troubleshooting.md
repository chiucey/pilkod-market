# Troubleshooting

## Build Errors

### `Unsupported class file major version 65`
JDK too new. AGP 8.5.x requires JDK 17. Run:
```bash
export JAVA_HOME=/opt/openjdk-17
export PATH=$JAVA_HOME/bin:$PATH
java -version   # should be 17.x
```

### `SDK location not found`
`local.properties` is missing or points to a bad path. Re-run `env-setup.sh` then:
```bash
echo "sdk.dir=/opt/android-sdk" > local.properties
```

### `Failed to install the following Android SDK packages as some licences have not been accepted`
```bash
yes | sdkmanager --licenses
```

### `OutOfMemoryError` / `Java heap space`
Add to `gradle.properties`:
```
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=1024m
```
Or pass at build time: `GRADLE_ARGS="-Xmx4g" bash build.sh --project ...`

### First build is very slow
First run downloads ~1GB of Gradle + Maven dependencies. Subsequent builds use the
local cache (`~/.gradle/caches/`) and finish in 30-90s for a no-change rebuild.

### `e: file:///.../Foo.kt:NN:1 Syntax error: Unclosed comment.`
**This is the Kotlin nested-comment trap** — see the SKILL.md warning section. The
most common cause is a `/** KDoc` block that mentions a filesystem path like
`/proc/cpuinfo` or `/sys/devices/system/cpu/*`. The `/*` inside the KDoc opens a
nested comment that the next `*/` only closes at the wrong level, so the rest of
the file becomes one big comment.

**Diagnose:**
```bash
grep -n '/\*' app/src/main/java/**/*.kt
```
Look for lines inside a `/** ... */` block that contain a literal `/*` (e.g. a
path that ends in `/*`).

**Fix** (any one):
- Rephrase the comment to avoid the path
- Escape the slash: `/proc\u002Fcpuinfo`
- Move the path example to a `private const val` outside the comment

The scaffold script (`new-project.sh`) runs a preflight scan and aborts with a
clear error before wasting 5 min on the build, so this should only bite you if
you pasted the file in *after* scaffolding. The same awk one-liner in the SKILL.md
catches it.

### Build "Unresolved reference X" on freshly-pasted file
Usually a downstream effect of the Unclosed-comment bug above (the file was
parsed as a comment, so nothing inside it was registered). Fix the comment first
and these cascade away.

### "Build succeeded but no APK"
Look at the bottom of `/workspace/.android-build-logs/build-<timestamp>.log`.
`build.sh` prints a tail on exit; if you ran gradle by hand, check there. The
usual cause is a non-fatal "build cache invalidated" warning that the user
mistook for failure — scroll up for the actual `:app:assembleDebug` line.

## Build Appears Stuck

The first `assembleDebug` on a fresh sandbox legitimately takes 5-10 minutes
(Gradle dist + Maven deps). After that, no-change rebuilds finish in <90s. If a
build has been "running" for more than 15 min with no progress, it's actually
stuck. Diagnostic steps, in order:

1. **Tail the log** in another shell:
   ```bash
   tail -f /workspace/.android-build-logs/build-*.log
   ```
   If you see "Downloading" lines for the last several minutes, you're on the
   network edge — likely a flaky `dl.google.com` or `repo1.maven.org`. Set a
   mirror or `https_proxy` and re-run.

2. **Check what the JVM is actually doing**:
   ```bash
   ps -ef | grep -E "java|gradle" | grep -v grep
   jstack <pid> | head -100
   ```
   Threads stuck in `socketRead` = network. Stuck in `CompileDaemon` JIT = OK,
   gradle daemon is busy compiling. Stuck on a file lock = `.nfs*` from NAS;
   `pkill -9 -f KotlinCompileDaemon` and re-run.

3. **Most common culprit: a zombie `KotlinCompileDaemon`**. It outlives the
   parent Gradle process and holds file handles on the project's `.gradle/`
   and `app/build/` dirs. The pre-build cleanup in `build.sh` kills it
   automatically; if you ran gradle by hand:
   ```bash
   pkill -9 -f "KotlinCompileDaemon\|GradleDaemon"
   rm -rf /workspace/<project>/.gradle
   ```

4. **NAS lock files (.nfs*)** — see the section further down.

## Sandbox / Environment

### `Permission denied` when running gradle
Sandbox runs as root. If a project was generated as non-root, fix ownership:
```bash
chown -R $(whoami) /workspace/<project>
```

### `No space left on device`
Android SDK + Gradle caches need ~3GB. Clean caches if needed:
```bash
rm -rf /root/.gradle/caches/transforms-*    # safe to delete
rm -rf /root/.gradle/caches/jars-*          # safe; will re-download
```

### `dl.google.com` is unreachable
Test:
```bash
curl -sI --max-time 10 https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
```
If blocked, set `GRADLE_MAVEN_MIRROR` or use a proxy:
```bash
export https_proxy=http://your-proxy:port
```

### `Cannot delete file: .../test-counter/.gradle/.../buildOutputCleanup/.nfs...`
NAS-mounted workspace + stale Gradle daemon. The daemon holds `.nfs*` lock files
that survive `rm -rf`. Fix:
```bash
pkill -9 -f "GradleDaemon\|KotlinCompileDaemon"   # kill stale daemons
sleep 2
rm -rf /workspace/<project>  # now succeeds
bash scripts/new-project.sh --out /workspace/<project> --force
bash scripts/build.sh --project /workspace/<project>
```
The build script already pins `GRADLE_USER_HOME=/root/.gradle` so caches live on
local overlay, not NFS — but a daemon started before that env was set will still
trip this.

## Reset

To wipe everything and re-install:
```bash
rm -rf /opt/openjdk-17 /opt/android-sdk /opt/gradle-8.9
rm -f /etc/profile.d/android-build-env.sh
rm -rf /workspace/.android-build-logs
bash /workspace/.skills/android-apk-builder/scripts/env-setup.sh
```

## APK Won't Install on Device

1. **"App not installed"** — usually a signature mismatch. Uninstall any old version
   of the same `applicationId` first, or change the package name.
2. **"This app isn't compatible with your device"** — `minSdk` is higher than the
   device's Android version. Lower it with `--min 21`. Or the device isn't
   `arm64-v8a` and the APK was filtered to that ABI (intentional for some users);
   rebuild without `ndk.abiFilters` or rebuild for the target ABI.
3. **"Parse error"** — APK corrupted during transfer. Re-check the SHA256.
4. **"There was a problem parsing the package"** after renaming
   `app-debug.apk.zip` → `app-debug.apk`: make sure the rename preserved all
   bytes (some file managers re-encode or skip bytes on cross-device transfer).
   Re-download and re-rename with `mv`, not a GUI tool.

## APK Won't Download

Browsers, corporate proxies, some chat tools, and many email gateways block or
warn-strip `.apk` attachments. `scripts/deliver.sh` solves this by shipping the
APK as `<slug>-app-debug.apk.zip` — same bytes (verified by sha256), friendlier
extension. The user renames it back to `.apk` to install:

```bash
mv app-debug.apk.zip app-debug.apk
adb install -r app-debug.apk
```

If even `.apk.zip` is blocked, deploy the file with `website_deploy` (a static
HTTPS URL) or send it through any file-transfer service.

## Verify the APK Before Delivering

```bash
# ABI filter actually applied?
/opt/android-sdk/build-tools/34.0.0/aapt dump badging app-debug.apk \
  | grep -E "native-code|sdkVersion|targetSdk|package:"
# should show: native-code: 'arm64-v8a'  (or whatever you asked for)

# Signature valid?
/opt/android-sdk/build-tools/34.0.0/apksigner verify --verbose app-debug.apk
# should print: Verifies  /  Verified using v2 scheme (APK Signature Scheme v2): true
```

## Kotlin / Compose Errors

### `Unresolved reference 'remember'` / `Unresolved reference 'getValue'`
Missing `import androidx.compose.runtime.remember` or `import androidx.compose.runtime.getValue`.
Add the import — Compose property delegation needs `getValue` to be in scope.

### `Type 'State<T?>' has no method 'getValue', so it cannot serve as a delegate`
Same root cause as above. `import androidx.compose.runtime.getValue` must be present
in any file that uses `val x by state.collectAsState()`.

### `Function 'component1()' is ambiguous` inside a `forEach { (k, v) -> ... }`
Either you're destructuring a Pair in a context where multiple `component1()`
extensions are in scope (rare), or — more likely — the surrounding type isn't
what you think it is. Print the type: `items.forEach { println(it::class) }`.
If you see the cascade "Unresolved reference 'X'" everywhere, check for the
**Unclosed-comment** bug above; once that's fixed these go away.
