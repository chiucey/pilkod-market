"""adb and Mobilerun Portal transport for the Android half of Phone Use. Standard library only.

The protocol (content provider URIs, accessibility service component, keyboard input
binds) follows the MIT-licensed mobilerun-core-local client; see PROVENANCE.md.
The Portal APK itself is AGPL-3.0 and is never shipped: setup downloads one pinned
release from upstream after the user accepts its license.
"""
import base64
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess

PORTAL_PACKAGE = "com.mobilerun.portal"
PORTAL_SERVICE = "com.mobilerun.portal/com.mobilerun.portal.service.MobilerunAccessibilityService"
PORTAL_VERSION = "0.7.25"
PORTAL_URL = f"https://github.com/droidrun/mobilerun-portal/releases/download/v{PORTAL_VERSION}/com.mobilerun.portal-{PORTAL_VERSION}.apk"
PORTAL_SHA256 = "6dc9e8327fcaecf3ba0ad5054f19357d832fc923763fb6c9d1ab09f79e3d3297"
PORTAL_SIZE = 53610015
PORTAL_LICENSE = "AGPL-3.0"
PORTAL_SOURCE = "https://github.com/droidrun/mobilerun-portal"

SERIAL_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+$")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

KEYCODES = {
    "back": 4, "home": 3, "recent": 187, "enter": 66, "delete": 67, "forward_delete": 112,
    "tab": 61, "escape": 111, "menu": 82, "search": 84, "volume_up": 24, "volume_down": 25,
    "wakeup": 224, "dpad_up": 19, "dpad_down": 20, "dpad_left": 21, "dpad_right": 22,
}


class AndroidError(Exception):
    def __init__(self, code, message, uncertain=False, details=None):
        super().__init__(message)
        self.code, self.uncertain, self.details = code, uncertain, details or {}

    def as_dict(self):
        return {"code": self.code, "message": str(self), "uncertain": self.uncertain, **self.details}


def adb_candidates():
    """Where adb usually lives. GUI hosts start MCP servers with a short PATH."""
    found = []
    configured = os.environ.get("PHONE_USE_ADB", "").strip()
    if configured:
        found.append(configured)
    which = shutil.which("adb")
    if which:
        found.append(which)
    for variable in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        root = os.environ.get(variable, "").strip()
        if root:
            found.append(str(Path(root) / "platform-tools" / "adb"))
    found += [str(Path.home() / "Library/Android/sdk/platform-tools/adb"), "/opt/homebrew/bin/adb",
              "/usr/local/bin/adb", str(Path.home() / "Android/Sdk/platform-tools/adb")]
    unique = []
    for item in found:
        if item not in unique:
            unique.append(item)
    return unique


def find_adb():
    for candidate in adb_candidates():
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def parse_devices(output):
    """`adb devices -l` rows: serial, state and the descriptive key:value fields."""
    devices = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices") or line.startswith("*"):
            continue
        parts = line.split()
        if len(parts) < 2 or not SERIAL_RE.match(parts[0]):
            continue
        row = {"serial": parts[0], "state": parts[1]}
        for field in parts[2:]:
            if ":" in field:
                key, value = field.split(":", 1)
                if key in ("model", "product", "device", "transport_id") and value:
                    row[key] = value[:80]
            elif field.startswith("usb"):
                row["connection"] = "usb"
        if "connection" not in row:
            row["connection"] = "emulator" if parts[0].startswith("emulator-") else ("network" if ":" in parts[0] else "usb")
        devices.append(row)
    return devices


def parse_content(output):
    """Decode `content query` output: `Row: 0 result={"status":...,"result":...}`."""
    text = output.strip()
    if "Could not find provider" in text or "Unknown URI" in text or "Unknown authority" in text:
        raise AndroidError("portal_missing", "Mobilerun Portal is not installed on this device. Run android_setup(action=install_portal).",
                           details={"action_executed": False})
    payload = None
    for line in text.splitlines():
        index = line.find("result=")
        if index >= 0:
            try:
                payload = json.loads(line[index + 7:])
                break
            except ValueError:
                continue
    if payload is None:
        if "No result found" in text:
            raise AndroidError("portal_unavailable", "Portal returned no result.", details={"action_executed": False})
        raise AndroidError("portal_unavailable", "Portal returned an unreadable answer.", details={"action_executed": False})
    if isinstance(payload, dict) and "status" in payload:
        if payload.get("status") != "success":
            message = str(payload.get("error") or payload.get("message") or "Portal reported an error.")[:300]
            if "Accessibility service not available" in message:
                raise AndroidError("portal_disabled", "Portal accessibility service is not enabled. Run android_setup(action=enable_portal).",
                                   details={"action_executed": False})
            raise AndroidError("portal_error", message, details={"action_executed": False})
        payload = payload.get("result", payload.get("data"))
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except ValueError:
            return payload
    return payload


class Adb:
    def __init__(self, path=None):
        self.path = path or find_adb()

    def require(self):
        if not self.path:
            raise AndroidError("adb_missing", "adb was not found. Install Android platform-tools (for example `brew install android-platform-tools`) or set PHONE_USE_ADB.",
                               details={"action_executed": False, "searched": adb_candidates()})
        return self.path

    def run(self, args, serial=None, timeout=20, binary=False):
        command = [self.require()] + (["-s", serial] if serial else []) + list(args)
        try:
            done = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            raise AndroidError("adb_timeout", f"adb did not answer within {timeout} seconds.", uncertain=True) from exc
        except OSError as exc:
            raise AndroidError("adb_missing", "adb could not be started.", details={"action_executed": False}) from exc
        if binary:
            return done
        done.stdout = done.stdout.decode("utf-8", "replace")
        done.stderr = done.stderr.decode("utf-8", "replace")
        return done

    def check(self, args, serial=None, timeout=20):
        done = self.run(args, serial, timeout)
        if done.returncode != 0:
            message = (done.stderr or done.stdout).strip().splitlines()
            detail = message[-1][:300] if message else f"adb exited with {done.returncode}"
            if "unauthorized" in detail:
                raise AndroidError("device_unauthorized", "Allow USB debugging on the phone (tap Allow on the RSA prompt), then retry.", details={"action_executed": False})
            if "not found" in detail and "device" in detail or "offline" in detail:
                raise AndroidError("device_not_found", "The selected Android device is not connected.", details={"action_executed": False})
            raise AndroidError("adb_failed", detail)
        return done.stdout

    def shell(self, serial, words, timeout=20):
        """Run one device shell command; every word is quoted for the device shell."""
        return self.check(["shell", " ".join(shlex.quote(str(word)) for word in words)], serial, timeout)

    def version(self):
        done = self.run(["version"], timeout=10)
        first = done.stdout.strip().splitlines()
        return first[0][:120] if first else None

    def devices(self):
        return parse_devices(self.check(["devices", "-l"], timeout=10))

    def screencap(self, serial, timeout=15):
        done = self.run(["exec-out", "screencap", "-p"], serial, timeout, binary=True)
        data = done.stdout
        if done.returncode != 0 or not data.startswith(PNG_SIGNATURE):
            raise AndroidError("screenshot_failed", "The device did not return a PNG screenshot (secure screens such as password fields can block capture).")
        return data

    def keyevent(self, serial, code, long_press=False):
        words = ["input", "keyevent"] + (["--longpress"] if long_press else []) + [str(code)]
        self.shell(serial, words, timeout=10)

    def tap(self, serial, x, y, duration_ms=0):
        x, y = int(round(x)), int(round(y))
        if duration_ms:
            self.shell(serial, ["input", "swipe", x, y, x, y, int(duration_ms)], timeout=15)
        else:
            self.shell(serial, ["input", "tap", x, y], timeout=10)

    def swipe(self, serial, x, y, to_x, to_y, duration_ms=300):
        self.shell(serial, ["input", "swipe", int(round(x)), int(round(y)), int(round(to_x)), int(round(to_y)), int(duration_ms)], timeout=15)

    def getprop(self, serial, name):
        return self.shell(serial, ["getprop", name], timeout=10).strip()


class Portal:
    def __init__(self, adb, serial):
        self.adb, self.serial = adb, serial

    def query(self, path, timeout=15):
        return parse_content(self.adb.shell(self.serial, ["content", "query", "--uri", f"content://{PORTAL_PACKAGE}/{path}"], timeout))

    def insert(self, path, binds, timeout=15):
        words = ["content", "insert", "--uri", f"content://{PORTAL_PACKAGE}/{path}"]
        for name, kind, value in binds:
            words += ["--bind", f"{name}:{kind}:{value}"]
        output = self.adb.shell(self.serial, words, timeout)
        if "Could not find provider" in output:
            parse_content(output)
        return output

    def ping(self):
        return self.query("ping", timeout=8) == "pong"

    def version(self):
        value = self.query("version", timeout=8)
        return value if isinstance(value, str) else None

    def state(self):
        value = self.query("state_full", timeout=20)
        if not isinstance(value, dict) or "a11y_tree" not in value:
            raise AndroidError("portal_unavailable", "Portal did not return the accessibility tree.")
        return value

    def phone_state(self):
        value = self.query("phone_state", timeout=10)
        return value if isinstance(value, dict) else {}

    def packages(self):
        value = self.query("packages", timeout=20)
        return value if isinstance(value, list) else []

    def input_text(self, text, clear):
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        self.insert("keyboard/input", [("base64_text", "s", encoded), ("clear", "b", "true" if clear else "false")], timeout=30)

    def overlay(self, visible):
        self.insert("overlay_visible", [("visible", "b", "true" if visible else "false")], timeout=10)


def installed_version(adb, serial):
    """versionName of the installed Portal, or None when the package is absent."""
    output = adb.shell(serial, ["dumpsys", "package", PORTAL_PACKAGE], timeout=20)
    match = re.search(r"versionName=([^\s]+)", output)
    return match.group(1) if match else None


def accessibility_enabled(adb, serial):
    value = adb.shell(serial, ["settings", "get", "secure", "enabled_accessibility_services"], timeout=10).strip()
    return PORTAL_SERVICE in value.split(":"), value


def enable_accessibility(adb, serial):
    """Add the Portal service to the enabled list without dropping the user's other services."""
    enabled, current = accessibility_enabled(adb, serial)
    if not enabled:
        services = [item for item in current.split(":") if item and item != "null"]
        services.append(PORTAL_SERVICE)
        adb.shell(serial, ["settings", "put", "secure", "enabled_accessibility_services", ":".join(services)], timeout=10)
    adb.shell(serial, ["settings", "put", "secure", "accessibility_enabled", "1"], timeout=10)


def lock_state(adb, serial):
    """Screen power and keyguard state. Unknown fields stay None rather than guessing."""
    power = adb.shell(serial, ["dumpsys", "power"], timeout=15)
    match = re.search(r"mWakefulness=(\w+)", power)
    wakefulness = match.group(1) if match else None
    keyguard = None
    policy = adb.shell(serial, ["dumpsys", "window", "policy"], timeout=15)
    for pattern in (r"isKeyguardShowing=(true|false)", r"mShowingLockscreen=(true|false)", r"KeyguardServiceDelegate[\s\S]{0,400}?showing=(true|false)", r"^\s*showing=(true|false)"):
        found = re.search(pattern, policy, re.M)
        if found:
            keyguard = found.group(1) == "true"
            break
    if keyguard is None:
        window = adb.shell(serial, ["dumpsys", "window"], timeout=20)
        found = re.search(r"isKeyguardShowing=(true|false)", window) or re.search(r"mDreamingLockscreen=(true|false)", window)
        if found:
            keyguard = found.group(1) == "true"
    return {"awake": None if wakefulness is None else wakefulness == "Awake", "wakefulness": wakefulness, "keyguard": keyguard}


def launcher_component(adb, serial, package):
    output = adb.shell(serial, ["cmd", "package", "resolve-activity", "--brief", "-c", "android.intent.category.LAUNCHER", package], timeout=15)
    for line in reversed(output.strip().splitlines()):
        line = line.strip()
        if "/" in line and line.split("/", 1)[0] == package:
            return line
    return None


# ---------------------------------------------------------------- accessibility tree

FLAG_FIELDS = (("isClickable", "clickable"), ("isLongClickable", "long_clickable"), ("isEditable", "editable"),
               ("isScrollable", "scrollable"), ("isCheckable", "checkable"), ("isChecked", "checked"),
               ("isSelected", "selected"), ("isFocused", "focused"), ("isPassword", "password"))
TEXT_LIMIT = 300


def short_type(class_name):
    return (class_name or "View").rsplit(".", 1)[-1] or "View"


def short_id(resource_id):
    if not resource_id:
        return ""
    return resource_id.split(":id/", 1)[1] if ":id/" in resource_id else resource_id


def _rect(node):
    bounds = node.get("boundsInScreen") or {}
    try:
        left, top, right, bottom = (int(bounds.get(key, 0)) for key in ("left", "top", "right", "bottom"))
    except (TypeError, ValueError):
        return None
    if right <= left or bottom <= top:
        return None
    return [left, top, right - left, bottom - top]


def flatten(root, viewport=None):
    """Every node with a usable rectangle, in tree order, with its depth and parent index."""
    nodes = []

    def walk(node, depth, parent):
        if not isinstance(node, dict):
            return
        rect = _rect(node)
        index = parent
        if rect is not None:
            text = str(node.get("text") or "")[:TEXT_LIMIT]
            entry = {"type": short_type(node.get("className")), "text": text,
                     "desc": str(node.get("contentDescription") or "")[:TEXT_LIMIT],
                     "hint": str(node.get("hint") or "")[:TEXT_LIMIT],
                     "resource_id": str(node.get("resourceId") or ""),
                     "package": str(node.get("packageName") or ""),
                     "rect": rect, "enabled": node.get("isEnabled", True) is not False,
                     "visible": node.get("isVisibleToUser", True) is not False,
                     "depth": depth, "parent": parent}
            if node.get("isShowingHintText"):
                entry["text"] = ""
            for source, name in FLAG_FIELDS:
                entry[name] = node.get(source) is True
            if viewport:
                x, y, w, h = rect
                entry["in_viewport"] = x < viewport["width"] and y < viewport["height"] and x + w > 0 and y + h > 0
            nodes.append(entry)
            index = len(nodes) - 1
        for child in node.get("children") or []:
            walk(child, depth + 1, index)

    if isinstance(root, list):
        for item in root:
            walk(item, 0, None)
    else:
        walk(root, 0, None)
    return nodes


def meaningful(node):
    return bool(node["text"] or node["desc"] or node["hint"] or short_id(node["resource_id"])
                or node["clickable"] or node["editable"] or node["scrollable"] or node["checkable"])


def compact(node):
    """Model-facing node: defaults omitted, rect=[x,y,width,height] in device pixels."""
    item = {"type": node["type"]}
    for key in ("text", "desc", "hint"):
        # Launcher icons and many buttons repeat their text as the description.
        if node[key] and not (key != "text" and node[key] == node["text"]):
            item[key] = node[key]
    rid = short_id(node["resource_id"])
    if rid:
        item["id"] = rid
    item["rect"] = node["rect"]
    for _, name in FLAG_FIELDS:
        if node[name]:
            item[name] = True
    if not node["enabled"]:
        item["enabled"] = False
    if not node["visible"]:
        item["visible"] = False
    if node.get("in_viewport") is False:
        item["in_viewport"] = False
    return item


def tree_view(nodes, max_nodes=200, include_invisible=False):
    kept = [node for node in nodes if meaningful(node) and (include_invisible or node["visible"])]
    return [compact(node) for node in kept[:max_nodes]], len(kept)


SELECTOR_FIELDS = ("text", "text_contains", "desc", "desc_contains", "label", "label_contains", "id", "resource_id",
                   "type", "enabled", "clickable", "editable", "scrollable", "checked", "index")


def matches(node, selector):
    if not node["visible"]:
        return False
    if "text" in selector and node["text"] != selector["text"]:
        return False
    if "text_contains" in selector and selector["text_contains"] not in node["text"]:
        return False
    if "desc" in selector and node["desc"] != selector["desc"]:
        return False
    if "desc_contains" in selector and selector["desc_contains"] not in node["desc"]:
        return False
    if "label" in selector and selector["label"] not in (node["text"], node["desc"], node["hint"]):
        return False
    if "label_contains" in selector and not any(selector["label_contains"] in node[key] for key in ("text", "desc", "hint")):
        return False
    for key in ("id", "resource_id"):
        if key in selector and selector[key] not in (node["resource_id"], short_id(node["resource_id"])):
            return False
    if "type" in selector and selector["type"] not in (node["type"],):
        return False
    if "enabled" in selector and node["enabled"] != selector["enabled"]:
        return False
    for flag in ("clickable", "editable", "scrollable", "checked"):
        if flag in selector and node[flag] != selector[flag]:
            return False
    return True


def contains(outer, inner):
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    return ox <= ix and oy <= iy and ix + iw <= ox + ow and iy + ih <= oy + oh


def tap_point(node, viewport=None):
    x, y, w, h = node["rect"]
    if viewport:
        # Clip to the screen so a partially visible row is tapped on its visible part.
        left, top = max(0, x), max(0, y)
        right, bottom = min(viewport["width"], x + w), min(viewport["height"], y + h)
        if right <= left or bottom <= top:
            return None
        return {"x": (left + right) // 2, "y": (top + bottom) // 2}
    return {"x": x + w // 2, "y": y + h // 2}


def resolve(nodes, selector, viewport=None):
    """One target for the selector: an explicit index, a single match, or one nested group."""
    found = [node for node in nodes if matches(node, selector)]
    if "index" in selector:
        if selector["index"] >= len(found):
            raise AndroidError("not_found", f"Only {len(found)} elements match; index {selector['index']} does not exist.",
                               details={"action_executed": False, "match_count": len(found)})
        return found[selector["index"]], found
    if not found:
        raise AndroidError("not_found", "No visible element matches the selector.", details={"action_executed": False, "match_count": 0})
    if len(found) > 1:
        # A label repeated by a container and its own text child resolves to the innermost.
        if all(contains(found[0]["rect"], node["rect"]) for node in found[1:]):
            return found[-1], found
        candidates = [{"index": i, **compact(node), "tap_point": tap_point(node, viewport)} for i, node in enumerate(found[:10])]
        raise AndroidError("ambiguous_target", f"{len(found)} separate elements match. Pass selector.index, or tap by x/y.",
                           details={"action_executed": False, "match_count": len(found), "candidates": candidates})
    return found[0], found
