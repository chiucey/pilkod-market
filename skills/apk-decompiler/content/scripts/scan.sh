#!/usr/bin/env bash
# scan.sh — Scan a decompiled APK output for sensitive strings, dangerous
# permissions, and embedded SDKs. Writes SCAN_REPORT.md and SCAN_REPORT.json
# into the decompile output directory.
#
# Usage:
#   scan.sh --in DIR
#   scan.sh --in DIR --json-only
set -uo pipefail

IN=""
JSON_ONLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --in)        IN="$2"; shift 2;;
    --json-only) JSON_ONLY=1; shift;;
    -h|--help)   sed -n '2,8p' "$0"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

[ -n "$IN" ] || { echo "--in is required" >&2; exit 2; }
[ -d "$IN" ] || { echo "Not a directory: $IN" >&2; exit 2; }

REPORT="$IN/SCAN_REPORT.md"
JSON="$IN/SCAN_REPORT.json"

# Read APK metadata if available.
APK_NAME=$(grep -oE 'APK\*\*: .*' "$IN/DECOMPILE_REPORT.md" 2>/dev/null | head -1 | sed 's/.*: //')
PKG=$(grep -oE 'Package\*\*: .*' "$IN/DECOMPILE_REPORT.md" 2>/dev/null | head -1 | sed 's/.*: //')
VER=$(grep -oE 'Version\*\*: .*' "$IN/DECOMPILE_REPORT.md" 2>/dev/null | head -1 | sed 's/.*: //')

# Pick best source dir: jadx (most readable) > smali > apktool smali.
SOURCES_DIR=""
if [ -d "$IN/jadx/sources" ]; then
  SOURCES_DIR="$IN/jadx/sources"
elif [ -d "$IN/jadx" ]; then
  SOURCES_DIR="$IN/jadx"
elif [ -d "$IN/smali/classes" ]; then
  SOURCES_DIR="$IN/smali/classes"
elif [ -d "$IN/smali" ]; then
  SOURCES_DIR="$IN/smali"
elif [ -d "$IN/apktool/smali" ]; then
  SOURCES_DIR="$IN/apktool/smali"
fi
[ -z "$SOURCES_DIR" ] && { echo "No source dir under $IN" >&2; exit 1; }

FILE_COUNT=$(find "$SOURCES_DIR" -type f 2>/dev/null | wc -l)
echo "[scan] scanning $FILE_COUNT files in $SOURCES_DIR"
echo

# Helper: grep -r with literal -F support; bounded to source dir.
# Disable filename prefix (-h) and only show first 200 hits.
rgrep() {
  local pattern="$1"; shift
  grep -rhE --binary-files=without-match "$pattern" "$@" "$SOURCES_DIR" 2>/dev/null
}
rgrep_files() {
  local pattern="$1"; shift
  grep -rlE --binary-files=without-match "$pattern" "$@" "$SOURCES_DIR" 2>/dev/null
}

# Use a temp work area on local fs (avoid NFS lock issues).
WORK=$(mktemp -d -p /opt/decompile-work)
trap "rm -rf $WORK" EXIT

# Per-step timeout (seconds). On NFS, large source trees can make grep hang.
SCAN_TIMEOUT="${SCAN_TIMEOUT:-60}"

# Each step:
# 1. Mirror $SOURCES_DIR to $WORK/mirror/ on local fs (real copy, not symlink —
#    symlinks across NFS trigger slow per-file stat calls under --dereference).
# 2. grep there.
# 3. Cleanup mirror.
mirror_scan() {
  local label="$1"; local pattern="$2"
  local mirror="$WORK/mirror-$label"
  echo "      [copy $label]" >&2
  rm -rf "$mirror"; mkdir -p "$mirror"
  (cd "$SOURCES_DIR" && find . -type f -print0 | head -z -n 10000 \
    | tar --null -cf - -T - | tar -xf - -C "$mirror")
  grep -rhE --binary-files=without-match "$pattern" "$mirror" 2>/dev/null
  rm -rf "$mirror"
}

mirror_scan_files() {
  local label="$1"; local pattern="$2"
  local mirror="$WORK/mirror-$label"
  echo "      [copy $label]" >&2
  rm -rf "$mirror"; mkdir -p "$mirror"
  (cd "$SOURCES_DIR" && find . -type f -print0 | head -z -n 10000 \
    | tar --null -cf - -T - | tar -xf - -C "$mirror")
  grep -rlE --binary-files=without-match "$pattern" "$mirror" 2>/dev/null
  rm -rf "$mirror"
}

# -------- 1. URLs --------
echo "[1/6] URLs ..."
mirror_scan urls 'https?://[A-Za-z0-9._~:/?#@!$'"'"'&*+,;=%-]+' \
  | grep -vE '://(schemas\.android\.com|www\.w3\.org|java\.sun\.com|xmlns\.jcp\.org)' \
  | sort -u > "$WORK/urls.txt"
URL_COUNT=$(wc -l < "$WORK/urls.txt" | tr -d ' ')

# -------- 2. API keys / secrets --------
echo "[2/6] API keys / secrets ..."
mirror_scan aws 'AKIA[0-9A-Z]{16}' | sort -u > "$WORK/aws.txt"
mirror_scan google 'AIza[0-9A-Za-z_-]{35}' | sort -u > "$WORK/google.txt"
mirror_scan_files pk 'BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY' > "$WORK/pk_files.txt"
mirror_scan jwt 'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+' | sort -u > "$WORK/jwt.txt"
mirror_scan generic-i '(secret|api[_-]?key|access[_-]?key|app[_-]?key|token|password|passwd|pwd)[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_\-]{16,}' \
  | head -50 > "$WORK/generic.txt"
AWS_COUNT=$(wc -l < "$WORK/aws.txt" | tr -d ' ')
GOOGLE_COUNT=$(wc -l < "$WORK/google.txt" | tr -d ' ')
PK_COUNT=$(wc -l < "$WORK/pk_files.txt" | tr -d ' ')
JWT_COUNT=$(wc -l < "$WORK/jwt.txt" | tr -d ' ')

# -------- 3. Dangerous permissions --------
echo "[3/6] Permissions ..."
PERMS_RAW="$WORK/perms.txt"
if [ -f "$IN/apktool/AndroidManifest.xml" ]; then
  grep -oE 'android\.permission\.[A-Z_]+' "$IN/apktool/AndroidManifest.xml" 2>/dev/null | sort -u > "$PERMS_RAW"
else
  mirror_scan perms 'android\.permission\.[A-Z_]+' | grep -oE 'android\.permission\.[A-Z_]+' | sort -u | head -50 > "$PERMS_RAW"
fi

DANGEROUS_PERMS=(
  "android.permission.READ_SMS"
  "android.permission.SEND_SMS"
  "android.permission.RECEIVE_SMS"
  "android.permission.READ_CONTACTS"
  "android.permission.WRITE_CONTACTS"
  "android.permission.RECORD_AUDIO"
  "android.permission.CAMERA"
  "android.permission.ACCESS_FINE_LOCATION"
  "android.permission.ACCESS_COARSE_LOCATION"
  "android.permission.READ_EXTERNAL_STORAGE"
  "android.permission.WRITE_EXTERNAL_STORAGE"
  "android.permission.READ_PHONE_STATE"
  "android.permission.READ_CALL_LOG"
  "android.permission.WRITE_CALL_LOG"
  "android.permission.SYSTEM_ALERT_WINDOW"
  "android.permission.REQUEST_INSTALL_PACKAGES"
  "android.permission.BIND_ACCESSIBILITY_SERVICE"
  "android.permission.BIND_DEVICE_ADMIN"
)
DANGEROUS_FOUND="$WORK/dangerous_perms.txt"
> "$DANGEROUS_FOUND"
for p in "${DANGEROUS_PERMS[@]}"; do
  if grep -qx "$p" "$PERMS_RAW" 2>/dev/null; then
    echo "$p" >> "$DANGEROUS_FOUND"
  fi
done
DANGEROUS_COUNT=$(wc -l < "$DANGEROUS_FOUND" | tr -d ' ')

# -------- 4. SDK fingerprints --------
echo "[4/6] Third-party SDK fingerprints ..."
SDK_PATTERNS=(
  "com.tencent"             "Tencent (QQ/WeChat/IMSdk)"
  "com.alibaba"             "Alibaba"
  "com.baidu"               "Baidu"
  "com.alipay"              "Alipay"
  "com.bytedance"           "ByteDance"
  "com.qq"                  "QQ"
  "weixin"                  "WeChat"
  "com.xiaomi"              "Xiaomi"
  "com.huawei"              "Huawei"
  "com.oppo"                "Oppo"
  "com.vivo"                "Vivo"
  "com.samsung"             "Samsung"
  "com.umeng"               "Umeng"
  "com.igexin"              "Getui"
  "com.jpush"               "JPush"
  "com.bugly"               "Bugly"
  "com.flurry"              "Flurry"
  "com.appsflyer"           "AppsFlyer"
  "com.adjust"              "Adjust"
  "com.kochava"             "Kochava"
  "io.branch"               "Branch.io"
  "io.firebase"             "Firebase"
  "com.google.android.gms"  "Google Play Services"
  "com.google.ads"          "Google Ads"
  "com.facebook"            "Facebook"
  "com.twitter"             "Twitter"
  "io.reactivex"            "RxJava"
  "retrofit2"               "Retrofit"
  "okhttp3"                 "OkHttp"
  "com.squareup"            "Square"
  "io.flutter"              "Flutter"
  "com.facebook.react"      "React Native"
  "com.swmansion"           "RN Reanimated"
)
SDK_HITS="$WORK/sdk_hits.txt"
> "$SDK_HITS"
# Build a single mirror for all SDK pattern checks.
SDKMIRROR="$WORK/mirror-sdks"
rm -rf "$SDKMIRROR"; mkdir -p "$SDKMIRROR"
(cd "$SOURCES_DIR" && find . -type f -print0 | head -z -n 10000 \
  | tar --null -cf - -T - | tar -xf - -C "$SDKMIRROR")
i=0
while [ $i -lt ${#SDK_PATTERNS[@]} ]; do
  pattern="${SDK_PATTERNS[$i]}"
  label="${SDK_PATTERNS[$((i+1))]}"
  count=$(grep -rlE "$pattern" "$SDKMIRROR" 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    echo "| $label | \`$pattern\` | $count |" >> "$SDK_HITS"
  fi
  i=$((i+2))
done
rm -rf "$SDKMIRROR"

# -------- 5. Crypto / WebView --------
echo "[5/6] WebView & crypto ..."
mirror_scan_files webview 'setJavaScriptEnabled|addJavascriptInterface' > "$WORK/webview.txt"
mirror_scan weak 'Cipher\.getInstance\("(DES|RC4|MD5|SHA1)"' \
  | grep -oE 'Cipher\.getInstance\("[^"]+"' | sort -u > "$WORK/weak_crypto.txt"
WEBVIEW_COUNT=$(wc -l < "$WORK/webview.txt" | tr -d ' ')
WEAK_COUNT=$(wc -l < "$WORK/weak_crypto.txt" | tr -d ' ')

# -------- 6. Network security --------
echo "[6/6] Network security ..."
mirror_scan_files cleartext 'usesCleartextTraffic|cleartextTrafficPermitted' > "$WORK/cleartext.txt"
CLEARTEXT_COUNT=$(wc -l < "$WORK/cleartext.txt" | tr -d ' ')

# -------- Severity --------
HIGH=0
[ "$AWS_COUNT" -gt 0 ] && HIGH=1
[ "$GOOGLE_COUNT" -gt 0 ] && HIGH=1
[ "$PK_COUNT" -gt 0 ] && HIGH=1
[ "$JWT_COUNT" -gt 0 ] && HIGH=1
[ "$WEAK_COUNT" -gt 0 ] && HIGH=1
[ "$DANGEROUS_COUNT" -ge 5 ] && HIGH=1
if [ "$HIGH" = 1 ]; then
  SEV="🔴 HIGH"
elif [ "$DANGEROUS_COUNT" -gt 0 ] || [ "$WEBVIEW_COUNT" -gt 0 ] || [ "$URL_COUNT" -gt 20 ]; then
  SEV="🟡 MED"
else
  SEV="🟢 LOW"
fi

# -------- Write report --------
echo "[scan] writing $REPORT ..."

{
echo "# Security Scan Report"
echo
echo "- **APK**: $APK_NAME"
echo "- **Package**: $PKG"
echo "- **Version**: $VER"
echo "- **Scanned at**: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "- **Source root**: $SOURCES_DIR"
echo "- **Severity**: $SEV"
echo
echo "## 1. URLs (top 50 of $URL_COUNT)"
echo
head -50 "$WORK/urls.txt" | sed 's/^/- /'
echo
echo "## 2. Credentials & Secrets"
echo
echo "| Type | Count |"
echo "|------|------:|"
echo "| AWS Access Key (\`AKIA[16]\`) | $AWS_COUNT |"
echo "| Google API Key (\`AIza[35]\`) | $GOOGLE_COUNT |"
echo "| Private Key blocks | $PK_COUNT |"
echo "| JWT tokens | $JWT_COUNT |"
echo
echo "### AWS hits"
echo '```'
cat "$WORK/aws.txt" | head -10
echo '```'
echo
echo "### Google hits"
echo '```'
cat "$WORK/google.txt" | head -10
echo '```'
echo
echo "### JWT hits"
echo '```'
cat "$WORK/jwt.txt" | head -10
echo '```'
echo
echo "### Generic suspicious assignments (first 20)"
echo '```'
head -20 "$WORK/generic.txt"
echo '```'
echo
echo "## 3. Dangerous Android Permissions"
echo
if [ -s "$DANGEROUS_FOUND" ]; then
  echo "| Permission | Status |"
  echo "|------------|:------:|"
  while IFS= read -r p; do
    echo "| \`$p\` | ⚠ requested |"
  done < "$DANGEROUS_FOUND"
else
  echo "_None of the high-risk permissions found._"
fi
echo
echo "## 4. Third-Party SDK Fingerprints"
echo
if [ -s "$SDK_HITS" ]; then
  echo "| SDK | Pattern | Files |"
  echo "|-----|---------|------:|"
  cat "$SDK_HITS"
else
  echo "_No third-party SDKs detected._"
fi
echo
echo "## 5. WebView & Crypto"
echo
echo "- **WebView with JavaScript / addJavascriptInterface**: $WEBVIEW_COUNT"
head -5 "$WORK/webview.txt" | sed 's|^|  - |'
echo "- **Weak crypto (DES/RC4/MD5/SHA1)**: $WEAK_COUNT"
cat "$WORK/weak_crypto.txt" | head -5 | sed 's|^|  - |'
echo
echo "## 6. Network Security"
echo
echo "- **cleartextTrafficPermitted / usesCleartextTraffic**: $CLEARTEXT_COUNT"
head -5 "$WORK/cleartext.txt" | sed 's|^|  - |'
echo
echo "---"
echo
echo "## Next steps"
echo
echo "- Review high-severity hits and rotate any leaked keys."
echo "- For packed DEX, run \`scripts/unpack-helper/dump-dex.js\` on a real device first."
echo "- Re-run after fixes: \`bash scripts/scan.sh --in $IN\`"
} > "$REPORT"

# JSON
python3 - "$JSON" "$WORK" "$APK_NAME" "$PKG" "$VER" "$SOURCES_DIR" \
  "$URL_COUNT" "$AWS_COUNT" "$GOOGLE_COUNT" "$PK_COUNT" "$JWT_COUNT" \
  "$DANGEROUS_COUNT" "$WEBVIEW_COUNT" "$WEAK_COUNT" "$CLEARTEXT_COUNT" "$SEV" <<'PY'
import json, sys, os
(out, work, apk, pkg, ver, src, urls, aws, g, pk, jwt, dperm, wv, wc, ct, sev) = sys.argv[1:]
def read_lines(p):
    if not os.path.exists(p): return []
    with open(p) as f: return [l.rstrip("\n") for l in f if l.strip()]
def read_files(p):
    if not os.path.exists(p): return []
    with open(p) as f: return [l.rstrip("\n") for l in f if l.strip()]
data = {
    "apk": apk, "package": pkg, "version": ver, "sources": src,
    "scanned_at": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "severity": sev,
    "counts": {
        "urls": int(urls), "aws_keys": int(aws), "google_keys": int(g),
        "private_key_files": int(pk), "jwt_tokens": int(jwt),
        "dangerous_permissions": int(dperm), "webview_js_files": int(wv),
        "weak_crypto": int(wc), "cleartext_files": int(ct),
    },
    "urls": read_lines(os.path.join(work, "urls.txt"))[:200],
    "secrets": {
        "aws_keys": read_lines(os.path.join(work, "aws.txt")),
        "google_keys": read_lines(os.path.join(work, "google.txt")),
        "jwt_tokens": read_lines(os.path.join(work, "jwt.txt")),
        "private_key_files": read_files(os.path.join(work, "pk_files.txt")),
    },
    "dangerous_permissions": read_lines(os.path.join(work, "dangerous_perms.txt")),
    "webview_js_files": read_files(os.path.join(work, "webview.txt")),
    "weak_crypto": read_lines(os.path.join(work, "weak_crypto.txt")),
    "cleartext_files": read_files(os.path.join(work, "cleartext.txt")),
    "suspicious_assignments_sample": read_lines(os.path.join(work, "generic.txt"))[:20],
}
with open(out, "w") as f: json.dump(data, f, indent=2, ensure_ascii=False)
PY

echo
echo "═══════════════════════════════════════════════"
echo "  Scan complete — severity: $SEV"
echo "═══════════════════════════════════════════════"
echo "  URLs:               $URL_COUNT"
echo "  AWS keys:           $AWS_COUNT"
echo "  Google keys:        $GOOGLE_COUNT"
echo "  Private key files:  $PK_COUNT"
echo "  JWT tokens:         $JWT_COUNT"
echo "  Dangerous perms:    $DANGEROUS_COUNT"
echo "  WebView JS:         $WEBVIEW_COUNT"
echo "  Weak crypto:        $WEAK_COUNT"
echo "  Report (md):        $REPORT"
echo "  Report (json):      $JSON"
