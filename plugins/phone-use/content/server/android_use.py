#!/usr/bin/env python3
"""Dependency-free local MCP stdio entrypoint for the Android half of Phone Use.

Transport is adb plus the Mobilerun Portal accessibility service on the phone. The
model drives the phone directly through these tools; there is no in-plugin LLM and
no API key. Analytics are not collected by this server.
"""
import argparse
import base64
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
from android_adb import (KEYCODES, PACKAGE_RE, PORTAL_LICENSE, PORTAL_PACKAGE, PORTAL_SHA256, PORTAL_SIZE, PORTAL_SOURCE,
                         PORTAL_URL, PORTAL_VERSION, SELECTOR_FIELDS, SERIAL_RE, Adb, AndroidError, Portal,
                         accessibility_enabled, adb_candidates, compact, enable_accessibility, flatten, installed_version,
                         launcher_component, lock_state, resolve, tap_point, tree_view, matches)
import wda_image
from wda_screen import ScreenHub

VERSION = "0.5.2"
SERVER_NAME = "phone-use-android"
PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
SETTLE_SECONDS = 0.6
SHOT_KEEP = 12


def state_directory(explicit=None):
    configured = explicit or os.environ.get("PHONE_USE_ANDROID_STATE_DIR")
    if configured and configured.strip():
        return Path(configured).expanduser().resolve()
    return Path.home() / ".local/share/phone-use/android"


# ---------------------------------------------------------------- schemas

def obj(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}


def string(description="", max_length=1000, enum=None):
    result = {"type": "string", "minLength": 1, "maxLength": max_length}
    if description:
        result["description"] = description
    if enum:
        result["enum"] = enum
    return result


def num(low, high, kind="number", description=""):
    result = {"type": kind, "minimum": low, "maximum": high}
    if description:
        result["description"] = description
    return result


BOOL = {"type": "boolean"}
OBSERVE = string("Post-action output for the next decision; default none.", enum=["none", "tree", "screenshot", "both"])
SELECTOR = obj({
    "text": string("Exact visible text copied from fresh nodes."),
    "text_contains": string("Substring of the visible text; case-sensitive."),
    "desc": string("Exact content description (accessibility label of icons)."),
    "desc_contains": string("Substring of the content description."),
    "label": string("Exact text, content description or hint; whichever the node has."),
    "label_contains": string("Substring of text, content description or hint."),
    "id": string("Resource id as nodes show it (short name), or the full pkg:id/name."),
    "resource_id": string("Alias of id."),
    "type": string("Short class name as nodes show it, e.g. Button, EditText, TextView."),
    "enabled": BOOL, "clickable": BOOL, "editable": BOOL, "scrollable": BOOL, "checked": BOOL,
    "index": num(0, 199, "integer", "0-based position among matches, from find or an ambiguous_target error."),
})
SELECTOR["minProperties"] = 1
SELECTOR["description"] = "Fields copied from fresh nodes. Only visible nodes match. Several separate matches return candidates with tap points and an index."
REGION = obj({"x": num(0, 20000), "y": num(0, 20000), "width": num(1, 20000), "height": num(1, 20000)}, ("x", "y", "width", "height"))
REGION["description"] = "Area in device pixels. Omit for the central part of the screen."

SCHEMAS = {
    "doctor": obj({}),
    "setup": obj({
        "action": string("status reads state. install_portal downloads the pinned Portal APK and installs it; requires accept_license=true after the user agreed. enable_portal turns its accessibility service on again. select chooses the device by serial.",
                         enum=["status", "install_portal", "enable_portal", "select"]),
        "serial": string("adb serial from status/doctor.", 128),
        "accept_license": {"type": "boolean", "description": "true only after the user explicitly accepted downloading the AGPL-3.0 Mobilerun Portal APK from GitHub."},
        "apk_path": string("Optional absolute path of an already downloaded Portal APK; it must match the pinned SHA-256.", 4096),
        "wait_seconds": num(0, 60, description="install_portal: bounded wait for the download; default 45. Call again while state=downloading."),
        "mirror": string("install_portal/status: download source chosen by the user, saved for later. An https prefix put before the GitHub URL "
                         "(e.g. https://proxy.example/) or the full https URL of the APK; \"github\" restores GitHub. Every source must match the pinned SHA-256.", 2048),
    }, ("action",)),
    "ready": obj({"screenshot": {"type": "boolean", "description": "Also attach a screenshot; default true."}}),
    "observe": obj({
        "mode": string("tree (default), screenshot or both.", enum=["tree", "screenshot", "both"]),
        "max_nodes": num(1, 500, "integer"),
        "include_invisible": BOOL,
    }),
    "find": obj({"selector": SELECTOR, "limit": num(1, 30, "integer")}, ("selector",)),
    "tap": obj({
        "selector": SELECTOR, "x": num(0, 20000), "y": num(0, 20000),
        "duration_ms": num(0, 5000, "integer", "Hold time; 500 or more is a long press. Default 0 is a tap."),
        "observe": OBSERVE,
    }),
    "swipe": obj({
        "direction": string("Finger movement; up reveals later rows. Default up.", enum=["up", "down", "left", "right"]),
        "region": REGION,
        "distance": num(0.1, 1, description="Fraction of the region to travel; default 0.6."),
        "x": num(0, 20000), "y": num(0, 20000), "to_x": num(0, 20000), "to_y": num(0, 20000),
        "duration_ms": num(50, 5000, "integer"),
        "observe": OBSERVE,
    }),
    "type_text": obj({
        "text": string("Full Unicode text to enter.", 5000),
        "selector": SELECTOR,
        "replace": {"type": "boolean", "description": "Clear the field first; default false appends."},
        "submit": {"type": "boolean", "description": "Press Enter afterwards; default false."},
        "allow_newlines": BOOL,
        "verify": {"type": "boolean", "description": "Read the focused field back after typing."},
        "observe": OBSERVE,
    }, ("text",)),
    "press_key": obj({"key": string("Key to press.", enum=sorted(KEYCODES)), "long_press": BOOL, "observe": OBSERVE}, ("key",)),
    "launch_app": obj({"package": string("Android package name, e.g. com.android.settings. Resolve unknown names with android_apps.", 256), "observe": OBSERVE}, ("package",)),
    "apps": obj({"query": string("Name or package substring; omit to list.", 100), "include_system": BOOL, "limit": num(1, 100, "integer")}),
    "install_apk": obj({"apk_path": string("Absolute path of a local .apk built or downloaded by the user.", 4096)}, ("apk_path",)),
    "wait": obj({"selector": SELECTOR, "timeout_seconds": num(0, 20), "gone": {"type": "boolean", "description": "Wait until no element matches instead."}}, ("selector",)),
    "screen": obj({"action": string("Pause or resume the Phone Use Mini App preview. Pause before password/biometric takeover; resume after the user confirms.", enum=["pause", "resume"])}, ("action",)),
}

DESCRIPTIONS = {
    "doctor": "Read-only check of adb, connected Android devices, USB debugging authorization, Mobilerun Portal and its accessibility service. Start here for Android setup.",
    "setup": "Android setup: status, select a device, install the pinned Mobilerun Portal (AGPL-3.0, downloaded only after the user accepts; accept_license=true), or re-enable its accessibility service.",
    "ready": "READY for Android: device online, screen awake and unlocked, Portal answering. Returns the current app, viewport in device pixels and an observation; only ready=true permits phone tasks.",
    "observe": "Fresh Android accessibility nodes and/or screenshot. Node rect=[x,y,width,height] in device pixels; screenshot pixels x image.pixel_scale = device pixels.",
    "find": "Query visible nodes by selector without the whole tree; returns matches with rect and tap_point.",
    "tap": "Tap the element a selector resolves to, or device-pixel x/y. duration_ms>=500 long-presses. Executes once; request observe when the next decision needs the new page.",
    "swipe": "One swipe by direction (finger movement) inside an optional region, or explicit x/y to to_x/to_y in device pixels.",
    "type_text": "Type full Unicode text through the Portal keyboard into the focused field; optional selector taps the field first. replace clears it, submit presses Enter. Never replay uncertain input.",
    "press_key": "Press an Android key: back, home, recent, enter, delete, tab, escape, volume and more.",
    "launch_app": "Start an installed app by package name and report the foreground package afterwards.",
    "apps": "List or search installed apps (label, package, version) through the Portal; third-party apps by default.",
    "install_apk": "Install a local APK the user provided (adb install -r -t) for testing their own app.",
    "wait": "Poll until a selector matches (or is gone with gone=true), up to timeout_seconds.",
    "screen": "Pause or resume the live Android preview in the Phone Use Mini App. No phone action.",
}

TOOLS = []
for _name, _schema in SCHEMAS.items():
    _readonly = _name in ("doctor", "ready", "observe", "find", "apps", "wait")
    TOOLS.append({"name": "android_" + _name, "description": DESCRIPTIONS[_name], "inputSchema": _schema,
                  "annotations": {"readOnlyHint": _readonly, "destructiveHint": _name in ("install_apk", "setup"),
                                  "idempotentHint": _readonly, "openWorldHint": _name == "setup"}})


def validate(value, schema, path="arguments"):
    kind = schema.get("type")
    valid = {"object": lambda: isinstance(value, dict), "array": lambda: isinstance(value, list),
             "string": lambda: isinstance(value, str), "boolean": lambda: isinstance(value, bool),
             "number": lambda: not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value),
             "integer": lambda: not isinstance(value, bool) and isinstance(value, int)}
    if kind and not valid[kind]():
        raise AndroidError("invalid_argument", f"{path} must be {kind}.", details={"action_executed": False})
    if "enum" in schema and value not in schema["enum"]:
        raise AndroidError("invalid_argument", f"Invalid {path} option; allowed: {', '.join(schema['enum'])}.", details={"action_executed": False})
    if kind == "object":
        props = schema.get("properties", {})
        unknown = sorted(set(value) - set(props))
        if schema.get("additionalProperties") is False and unknown:
            raise AndroidError("invalid_argument", f"Unknown fields in {path}: {', '.join(unknown)}.",
                               details={"action_executed": False, "allowed_fields": sorted(props)})
        if set(schema.get("required", [])) - set(value):
            raise AndroidError("invalid_argument", f"Missing required fields in {path}.", details={"action_executed": False})
        if len(value) < schema.get("minProperties", 0):
            raise AndroidError("invalid_argument", f"{path} cannot be empty.", details={"action_executed": False})
        for key, item in value.items():
            if key in props:
                validate(item, props[key], f"{path}.{key}")
    if kind in ("number", "integer") and not schema.get("minimum", -math.inf) <= value <= schema.get("maximum", math.inf):
        raise AndroidError("invalid_argument", f"{path} is out of range.", details={"action_executed": False})
    if kind == "string" and not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 100000):
        raise AndroidError("invalid_argument", f"{path} has invalid length.", details={"action_executed": False})


def validate_semantics(name, args):
    if name == "tap":
        coords = "x" in args or "y" in args
        if ("selector" in args) == coords or (coords and not ("x" in args and "y" in args)):
            raise AndroidError("invalid_argument", "tap requires either selector or both x and y.", details={"action_executed": False})
    if name == "swipe":
        explicit = [key for key in ("x", "y", "to_x", "to_y") if key in args]
        if explicit and (len(explicit) != 4 or "direction" in args or "region" in args or "distance" in args):
            raise AndroidError("invalid_argument", "Use either direction/region/distance or all of x, y, to_x, to_y.", details={"action_executed": False})
    if name == "type_text":
        text = args["text"]
        if any((ord(c) < 32 and c not in "\n\r") or ord(c) == 127 for c in text):
            raise AndroidError("invalid_argument", "Control characters are not allowed in text.", details={"action_executed": False})
        if ("\n" in text or "\r" in text) and not args.get("allow_newlines", False):
            raise AndroidError("newline_requires_intent", "Line breaks require allow_newlines=true.", details={"action_executed": False})
    if name == "launch_app" and not PACKAGE_RE.match(args["package"]):
        raise AndroidError("invalid_argument", "Use the app's package name, e.g. com.android.settings.", details={"action_executed": False})
    if name == "setup":
        if args["action"] == "select" and "serial" not in args:
            raise AndroidError("invalid_argument", "select needs serial.", details={"action_executed": False})
        if "serial" in args and not SERIAL_RE.match(args["serial"]):
            raise AndroidError("invalid_argument", "Invalid adb serial.", details={"action_executed": False})
    if name == "install_apk":
        path = Path(args["apk_path"])
        if not path.is_absolute() or path.suffix.lower() != ".apk":
            raise AndroidError("invalid_argument", "apk_path must be an absolute path ending in .apk.", details={"action_executed": False})


def copy_png(directory, data):
    """Put a PNG on the macOS clipboard; the temporary file exists only during the copy."""
    fd, name = tempfile.mkstemp(prefix=".clipboard-", suffix=".png", dir=directory)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        done = subprocess.run(["/usr/bin/osascript", "-e", "on run argv", "-e",
                               "set the clipboard to (read (POSIX file (item 1 of argv)) as «class PNGf»)", "-e", "end run", name],
                              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8, check=False)
        if done.returncode != 0:
            raise AndroidError("clipboard_unavailable", "The screenshot was captured but macOS did not accept it on the clipboard.")
    except (OSError, subprocess.SubprocessError) as exc:
        raise AndroidError("clipboard_unavailable", "The screenshot could not be copied to the clipboard.") from exc
    finally:
        try:
            os.unlink(name)
        except OSError:
            pass


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


SLOW_BYTES_PER_SECOND = 300 * 1024
SLOW_AFTER_SECONDS = 15


def portal_source(mirror):
    """The download URL for a mirror setting: empty/"github" = GitHub, a prefix ending in / or a full .apk URL."""
    mirror = (mirror or "").strip()
    if not mirror or mirror.lower() == "github":
        return PORTAL_URL
    parsed = urllib.parse.urlsplit(mirror)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise AndroidError("invalid_argument", "mirror must be an https URL: a prefix such as https://example.com/ or the full URL of the Portal APK.",
                           details={"action_executed": False})
    if parsed.path.lower().endswith(".apk"):
        return mirror
    return mirror.rstrip("/") + "/" + PORTAL_URL


class PortalDownload:
    """One background download of the pinned Portal APK, verified before use. Any source must deliver the pinned SHA-256."""

    def __init__(self, cache_dir):
        self.cache_dir = Path(cache_dir)
        self.target = self.cache_dir / f"com.mobilerun.portal-{PORTAL_VERSION}.apk"
        self.partial = self.target.with_suffix(".part")
        self.thread = None
        self.lock = threading.Lock()
        self.received = 0
        self.resumed_from = 0
        self.started = None
        self.url = None
        self.error = None

    def ready(self):
        if self.target.is_file() and self.target.stat().st_size == PORTAL_SIZE and sha256_file(self.target) == PORTAL_SHA256:
            return True
        if self.target.exists():
            self.target.unlink()
        return False

    def running(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, url):
        with self.lock:
            if self.running():
                return False
            self.error, self.url, self.started = None, url, time.monotonic()
            self.thread = threading.Thread(target=self._run, args=(url,), name="portal-download", daemon=True)
            self.thread.start()
            return True

    def _run(self, url):
        self.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        digest = hashlib.sha256()
        keep_partial = False
        try:
            offset = self.partial.stat().st_size if self.partial.is_file() else 0
            if offset >= PORTAL_SIZE:
                offset = 0
            headers = {"User-Agent": f"phone-use/{VERSION}"}
            if offset:
                headers["Range"] = f"bytes={offset}-"
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                if offset and response.status == 206:
                    with open(self.partial, "rb") as previous:
                        for block in iter(lambda: previous.read(1024 * 1024), b""):
                            digest.update(block)
                    mode = "ab"
                else:
                    offset, mode = 0, "wb"
                self.received = self.resumed_from = offset
                fd = os.open(self.partial, os.O_CREAT | os.O_WRONLY | (os.O_APPEND if mode == "ab" else os.O_TRUNC), 0o600)
                with os.fdopen(fd, mode) as stream:
                    keep_partial = True
                    while True:
                        block = response.read(256 * 1024)
                        if not block:
                            break
                        if self.received + len(block) > PORTAL_SIZE:
                            keep_partial = False
                            raise AndroidError("checksum_mismatch", "The source sent more data than the pinned Portal release; it was discarded.")
                        self.received += len(block)
                        digest.update(block)
                        stream.write(block)
            if self.received != PORTAL_SIZE:
                raise AndroidError("download_failed", "The download ended early; call install_portal again to resume it.")
            keep_partial = False
            if digest.hexdigest() != PORTAL_SHA256:
                raise AndroidError("checksum_mismatch", "The downloaded APK does not match the pinned SHA-256; it was discarded. Use GitHub or another source.")
            os.replace(self.partial, self.target)
        except AndroidError as exc:
            self.error = exc.as_dict()
        except Exception as exc:  # network errors of every kind end the attempt; the partial file resumes next time
            host = urllib.parse.urlsplit(url).hostname
            self.error = {"code": "download_failed", "uncertain": False,
                          "message": f"Portal download from {host} failed ({type(exc).__name__}). Retry to resume, set a mirror, or download the APK yourself and pass apk_path."}
        finally:
            if not keep_partial and self.partial.exists():
                self.partial.unlink()

    def status(self):
        state = "ready" if self.target.is_file() else "downloading" if self.running() else "failed" if self.error else "absent"
        result = {"state": state, "received_bytes": self.received, "total_bytes": PORTAL_SIZE}
        if self.url:
            result["source"] = urllib.parse.urlsplit(self.url).hostname
        if state == "downloading" and self.started:
            elapsed = max(time.monotonic() - self.started, 0.001)
            speed = (self.received - self.resumed_from) / elapsed
            result["bytes_per_second"] = int(speed)
            if speed > 0:
                result["eta_seconds"] = int((PORTAL_SIZE - self.received) / speed)
            if elapsed >= SLOW_AFTER_SECONDS and speed < SLOW_BYTES_PER_SECOND:
                result["slow"] = True
                result["hint"] = ("The download is slow. Tell the user the speed and ask whether to keep waiting or switch to a download mirror they trust "
                                  "(android_setup mirror=...); every source is checked against the pinned SHA-256.")
        if self.error and not self.running():
            result["error"] = self.error
        return result


class Runtime:
    def __init__(self, state_dir=None):
        self.state_dir = state_directory(state_dir)
        self.state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.state_dir.chmod(0o700)
        self.config_path = self.state_dir / "config.json"
        self.adb = Adb()
        self.screen = ScreenHub(self.state_dir)
        self.download = PortalDownload(self.state_dir / "cache")
        self.settle = SETTLE_SECONDS
        try:
            value = float(os.environ.get("PHONE_USE_ANDROID_SETTLE_SECONDS", ""))
            if 0 <= value <= 3:
                self.settle = value
        except ValueError:
            pass
        self._viewport = None
        self._touched = 0

    # ---------------------------------------------------------------- state

    def config(self):
        try:
            value = json.loads(self.config_path.read_text())
            return value if isinstance(value, dict) else {}
        except (OSError, ValueError):
            return {}

    def save_config(self, **changes):
        value = {**self.config(), **changes, "adb": self.adb.path, "last_used_at": int(time.time() * 1000)}
        fd, temporary = tempfile.mkstemp(prefix=".config-", dir=self.state_dir)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w") as stream:
                json.dump(value, stream, ensure_ascii=False)
            os.replace(temporary, self.config_path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        self._touched = time.monotonic()

    def touch(self):
        """Mark Android as the most recently used phone so the Mini App shows it."""
        if time.monotonic() - self._touched > 5 and self.config().get("serial"):
            self.save_config()

    @contextlib.contextmanager
    def operation(self, blocking=True):
        path = self.state_dir / "operation.lock"
        with path.open("a") as lock:
            path.chmod(0o600)
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
            except BlockingIOError:
                raise AndroidError("device_busy", "The phone is in the middle of another operation; nothing was sent.", details={"action_executed": False})
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    @contextlib.contextmanager
    def activity(self):
        token = self.screen.begin("android")
        try:
            yield
        finally:
            self.screen.end(token)

    # ---------------------------------------------------------------- device

    def device(self, required=True):
        """The selected online device: ANDROID_SERIAL, the saved choice, or the only one connected."""
        devices = self.adb.devices()
        wanted = os.environ.get("ANDROID_SERIAL", "").strip() or self.config().get("serial")
        public = [{key: item[key] for key in ("serial", "state", "model", "connection") if key in item} for item in devices]
        if wanted:
            row = next((item for item in devices if item["serial"] == wanted), None)
            if row is None:
                raise AndroidError("device_not_found", f"The selected Android device {wanted} is not connected. Reconnect it, or choose another with android_setup(action=select).",
                                   details={"action_executed": False, "devices": public})
        else:
            online = [item for item in devices if item["state"] == "device"]
            if not online:
                unauthorized = [item for item in devices if item["state"] == "unauthorized"]
                if unauthorized:
                    raise AndroidError("device_unauthorized", "Unlock the phone and tap Allow on the USB debugging prompt, then retry.", details={"action_executed": False, "devices": public})
                if not required:
                    return None
                raise AndroidError("no_device", "No Android device is connected over adb. Enable Developer options > USB debugging and connect it, or start an emulator.",
                                   details={"action_executed": False, "devices": public})
            if len(online) > 1:
                raise AndroidError("multiple_devices", "Several Android devices are connected. Ask the user which one to use, then call android_setup(action=select, serial=...).",
                                   details={"action_executed": False, "devices": public})
            row = online[0]
        if row["state"] == "unauthorized":
            raise AndroidError("device_unauthorized", "Unlock the phone and tap Allow on the USB debugging prompt, then retry.", details={"action_executed": False, "devices": public})
        if row["state"] != "device":
            raise AndroidError("device_offline", f"The device is {row['state']}. Reconnect the cable or restart adb, then retry.", details={"action_executed": False, "devices": public})
        if self.config().get("serial") != row["serial"]:
            self._remember(row)
        return row["serial"]

    def _remember(self, row):
        serial = row["serial"]
        try:
            model = self.adb.getprop(serial, "ro.product.model") or row.get("model")
            release = self.adb.getprop(serial, "ro.build.version.release")
        except AndroidError:
            model, release = row.get("model"), None
        self.save_config(serial=serial, model=(model or "Android")[:60], android_version=release)

    def portal(self, serial=None):
        return Portal(self.adb, serial or self.device())

    def viewport(self, state):
        bounds = (state.get("device_context") or {}).get("screen_bounds") or {}
        width, height = bounds.get("width"), bounds.get("height")
        if isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0:
            viewport = {"width": width, "height": height}
            if viewport != self._viewport:
                self._viewport = viewport
                self.screen.set_viewport(viewport)
            return viewport
        return self._viewport

    # ---------------------------------------------------------------- observation

    def screenshot(self, serial):
        data = self.adb.screencap(serial)
        shots = self.state_dir / "shots"
        shots.mkdir(mode=0o700, exist_ok=True)
        path = shots / f"android-{int(time.time() * 1000)}.png"
        fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        for old in sorted(shots.glob("android-*"))[:-2 * SHOT_KEEP]:
            try:
                old.unlink()
            except OSError:
                pass
        native = wda_image.png_size(data[:32])
        image_path, mime, width, height = wda_image.model_image(path)
        image = {"path": str(image_path), "mimeType": mime}
        if width and height and native:
            image.update(width=width, height=height, pixel_scale=[round(native[0] / width, 4), round(native[1] / height, 4)])
            if not self._viewport:
                self._viewport = {"width": native[0], "height": native[1]}
        return image

    def nodes(self, serial):
        state = self.portal(serial).state()
        viewport = self.viewport(state)
        return flatten(state.get("a11y_tree"), viewport), viewport, state

    def observe(self, mode="tree", max_nodes=200, include_invisible=False, serial=None):
        serial = serial or self.device()
        result = {}
        if mode in ("tree", "both"):
            nodes, viewport, state = self.nodes(serial)
            phone = state.get("phone_state") or {}
            package, activity = phone.get("packageName"), phone.get("activityName")
            # Portal can report the previous app's activity right after a switch; keep it only when it belongs to the package.
            if activity and package and not (activity.startswith(package) or activity.startswith(".")):
                activity = None
            result["app"] = {"package": package, "activity": activity, "label": phone.get("currentApp")}
            result["viewport"] = viewport
            if phone.get("keyboardVisible"):
                result["keyboard_visible"] = True
            focused = phone.get("focusedElement") or {}
            if phone.get("isEditable") and focused:
                result["focused"] = {"id": focused.get("resourceId") or None, "text": str(focused.get("text") or "")[:300] or None}
            view, total = tree_view(nodes, max_nodes, include_invisible)
            result["nodes"] = view
            if total > len(view):
                result.update(truncated=True, total_nodes=total)
        if mode in ("screenshot", "both"):
            result["image"] = self.screenshot(serial)
            if "viewport" not in result:
                result["viewport"] = self._viewport
        return result

    def after(self, args, serial, result):
        mode = args.get("observe", "none")
        if mode != "none":
            time.sleep(self.settle)
            result["observation"] = self.observe(mode, serial=serial)
        return result

    # ---------------------------------------------------------------- tools

    def call(self, name, args):
        if not isinstance(args, dict):
            raise AndroidError("invalid_argument", "arguments must be an object.", details={"action_executed": False})
        short = name[len("android_"):] if name.startswith("android_") else None
        if short not in SCHEMAS:
            raise AndroidError("unknown_tool", f"Unknown tool {name}.")
        validate(args, SCHEMAS[short])
        validate_semantics(short, args)
        result = getattr(self, "tool_" + short)(args)
        if short not in ("doctor", "setup", "screen"):
            self.touch()
        return result

    def status(self):
        report = {"platform": "android", "version": VERSION, "adb": {"path": self.adb.path, "searched": None if self.adb.path else adb_candidates()}}
        url = self.portal_url()
        report["portal_release"] = {"version": PORTAL_VERSION, "license": PORTAL_LICENSE, "source": PORTAL_SOURCE, "url": PORTAL_URL, "sha256": PORTAL_SHA256, "size_bytes": PORTAL_SIZE,
                                    "download_from": "github" if url == PORTAL_URL else url}
        report["download"] = self.download.status()
        if not self.adb.path:
            report["next_step"] = "Install Android platform-tools (brew install android-platform-tools) or set PHONE_USE_ADB, then run doctor again."
            return report
        report["adb"]["version"] = self.adb.version()
        devices = self.adb.devices()
        report["devices"] = [{key: item[key] for key in ("serial", "state", "model", "connection") if key in item} for item in devices]
        config = self.config()
        report["selected"] = os.environ.get("ANDROID_SERIAL", "").strip() or config.get("serial")
        try:
            serial = self.device(required=False)
        except AndroidError as exc:
            report["device_error"] = exc.as_dict()
            report["next_step"] = exc.args[0]
            return report
        if not serial:
            report["next_step"] = "Connect an Android phone with USB debugging enabled (or start an emulator), then run doctor again."
            return report
        report["selected"] = serial
        config = self.config()
        report["device"] = {"serial": serial, "model": config.get("model"), "android_version": config.get("android_version")}
        portal = {"package": PORTAL_PACKAGE, "installed_version": installed_version(self.adb, serial)}
        if portal["installed_version"]:
            portal["accessibility_enabled"] = accessibility_enabled(self.adb, serial)[0]
            try:
                portal["responding"] = self.portal(serial).ping()
            except AndroidError as exc:
                portal["responding"] = False
                portal["error"] = exc.code
        report["portal"] = portal
        if not portal["installed_version"]:
            report["next_step"] = ("Portal is missing. Tell the user it is the AGPL-3.0 Mobilerun Portal APK, downloaded from GitHub "
                                   f"({PORTAL_URL}); after they agree call android_setup(action=install_portal, accept_license=true).")
        elif not portal.get("accessibility_enabled") or not portal.get("responding"):
            report["next_step"] = "Portal is installed but its accessibility service is off. Call android_setup(action=enable_portal)."
        else:
            report["next_step"] = "Ready to run android_ready."
        return report

    def tool_doctor(self, args):
        report = self.status()
        report["read_only"] = True
        return report

    def portal_url(self):
        """User choice saved in config, then PHONE_USE_PORTAL_MIRROR / PHONE_USE_PORTAL_URL, then GitHub."""
        saved = self.config().get("portal_mirror")
        env = os.environ.get("PHONE_USE_PORTAL_MIRROR", "").strip() or os.environ.get("PHONE_USE_PORTAL_URL", "").strip()
        try:
            return portal_source(saved or env)
        except AndroidError:
            return PORTAL_URL

    def tool_setup(self, args):
        action = args["action"]
        if "mirror" in args:
            if action not in ("status", "install_portal"):
                raise AndroidError("invalid_argument", "mirror applies to status and install_portal.", details={"action_executed": False})
            url = portal_source(args["mirror"])
            if self.download.running() and self.download.url != url:
                raise AndroidError("download_in_progress", "A Portal download from another source is still running; wait for it or retry after it ends.",
                                   details={"action_executed": False, "download": self.download.status()})
            self.save_config(portal_mirror=None if url == PORTAL_URL else args["mirror"].strip())
        if action == "status":
            return self.status()
        if action == "select":
            row = next((item for item in self.adb.devices() if item["serial"] == args["serial"]), None)
            if row is None:
                raise AndroidError("device_not_found", "No connected device has that serial.", details={"action_executed": False})
            self._remember(row)
            return {"selected": args["serial"], **self.status()}
        serial = args.get("serial") or self.device()
        if action == "enable_portal":
            with self.operation():
                self._enable(serial)
            return self.status()
        if args.get("accept_license") is not True:
            raise AndroidError("license_confirmation_required",
                               "Ask the user first: installing the Mobilerun Portal downloads an AGPL-3.0 APK from GitHub and enables its accessibility service on the phone. Call again with accept_license=true only after they agree.",
                               details={"action_executed": False, "license": PORTAL_LICENSE, "source": PORTAL_SOURCE, "url": PORTAL_URL,
                                        "sha256": PORTAL_SHA256, "size_bytes": PORTAL_SIZE})
        if "apk_path" in args:
            apk = Path(args["apk_path"]).expanduser()
            if not apk.is_absolute() or not apk.is_file() or sha256_file(apk) != PORTAL_SHA256:
                raise AndroidError("checksum_mismatch", f"apk_path must be the pinned Portal {PORTAL_VERSION} APK (SHA-256 {PORTAL_SHA256}).", details={"action_executed": False})
        else:
            apk = self.download.target
            if not self.download.ready():
                self.download.start(self.portal_url())
                deadline = time.monotonic() + args.get("wait_seconds", 45)
                while self.download.running() and time.monotonic() < deadline:
                    time.sleep(0.5)
                if not self.download.ready():
                    status = self.download.status()
                    if status.get("error"):
                        raise AndroidError(status["error"]["code"], status["error"]["message"], details={"action_executed": False, "download": status})
                    return {"state": "downloading", "download": status,
                            "next_step": "Call android_setup(action=install_portal, accept_license=true) again to keep waiting; the download continues in the background."}
        with self.operation(), self.activity():
            done = self.adb.run(["install", "-r", "-g", str(apk)], serial, timeout=110)
            output = (done.stdout + done.stderr).strip()
            if done.returncode != 0 or "Success" not in output:
                lines = output.splitlines()
                raise AndroidError("install_failed", (lines[-1] if lines else "adb install failed")[:300],
                                   details={"hint": "Some phones (MIUI, ColorOS, HarmonyOS) require allowing 'Install via USB' in Developer options."})
            self._enable(serial)
        return {"installed": True, **self.status()}

    def _enable(self, serial):
        enable_accessibility(self.adb, serial)
        portal = self.portal(serial)
        deadline = time.monotonic() + 10
        while True:
            try:
                if portal.ping():
                    break
            except AndroidError as exc:
                if exc.code == "portal_missing" or time.monotonic() > deadline:
                    raise
            if time.monotonic() > deadline:
                raise AndroidError("portal_disabled", "Portal did not start. On the phone open Settings > Accessibility and turn on Mobilerun Portal, then run android_ready.")
            time.sleep(0.5)
        try:
            portal.overlay(False)
        except AndroidError:
            pass

    def tool_ready(self, args):
        serial = self.device()
        state = lock_state(self.adb, serial)
        if state["awake"] is False or state["keyguard"]:
            with self.operation():
                if state["awake"] is False:
                    self.adb.keyevent(serial, KEYCODES["wakeup"])
                    time.sleep(0.5)
                self.adb.shell(serial, ["wm", "dismiss-keyguard"], timeout=10)
                time.sleep(0.8)
            state = lock_state(self.adb, serial)
        if state["awake"] is False or state["keyguard"]:
            self.screen.set_paused(True, reason="device_locked")
            raise AndroidError("phone_locked", "The Android phone is locked. Ask the user to unlock it (PIN, pattern or biometrics), then run android_ready again.",
                               details={"action_executed": False, "lock": state})
        pause_id = self.screen.locked_pause_id()
        if pause_id:
            self.screen.resume_after_unlock(pause_id)
        version = installed_version(self.adb, serial)
        if not version:
            raise AndroidError("portal_missing", "Mobilerun Portal is not installed. Read android-use-setup and ask the user before android_setup(action=install_portal, accept_license=true).",
                               details={"action_executed": False})
        # The observation itself proves the Portal answers; a separate ping would cost another ~1 s on phones.
        observation = self.observe("both" if args.get("screenshot", True) else "tree", serial=serial)
        config = self.config()
        result = {"ready": True, "platform": "android",
                  "device": {"serial": serial, "model": config.get("model"), "android_version": config.get("android_version")},
                  "portal": {"version": version, **({"update_available": PORTAL_VERSION} if version != PORTAL_VERSION else {})},
                  "preview": self.screen.pause_status(), "observation": observation}
        return result

    def tool_observe(self, args):
        return self.observe(args.get("mode", "tree"), args.get("max_nodes", 200), args.get("include_invisible", False))

    def tool_find(self, args):
        serial = self.device()
        nodes, viewport, _ = self.nodes(serial)
        found = [node for node in nodes if matches(node, args["selector"])]
        limit = args.get("limit", 10)
        return {"match_count": len(found),
                "matches": [{"index": i, **compact(node), "tap_point": tap_point(node, viewport)} for i, node in enumerate(found[:limit])],
                "viewport": viewport}

    def tool_tap(self, args):
        serial = self.device()
        target = None
        if "selector" in args:
            nodes, viewport, _ = self.nodes(serial)
            node, _ = resolve(nodes, args["selector"], viewport)
            point = tap_point(node, viewport)
            if point is None:
                raise AndroidError("not_on_screen", "The element is outside the screen; swipe it into view first.", details={"action_executed": False, "rect": node["rect"]})
            target = compact(node)
        else:
            point = {"x": args["x"], "y": args["y"]}
            viewport = self._viewport
            if viewport and (point["x"] >= viewport["width"] or point["y"] >= viewport["height"]):
                raise AndroidError("invalid_argument", "x/y is outside the screen (device pixels).", details={"action_executed": False, "viewport": viewport})
        duration = args.get("duration_ms", 0)
        with self.operation(), self.activity():
            self.adb.tap(serial, point["x"], point["y"], duration)
            if duration:
                self.screen.gesture("drag", from_point=point, to_point=point, duration_ms=min(duration, 5000), viewport=self._viewport)
            else:
                self.screen.gesture("tap", point=point, viewport=self._viewport)
        result = {"tapped": point, "long_press": bool(duration >= 500)}
        if target:
            result["target"] = target
        return self.after(args, serial, result)

    def tool_swipe(self, args):
        serial = self.device()
        if "x" in args:
            start, end = (args["x"], args["y"]), (args["to_x"], args["to_y"])
        else:
            viewport = self._viewport
            if not viewport:
                _, viewport, _ = self.nodes(serial)
            region = args.get("region") or {"x": 0, "y": viewport["height"] * 0.2, "width": viewport["width"], "height": viewport["height"] * 0.6}
            distance = args.get("distance", 0.6)
            cx, cy = region["x"] + region["width"] / 2, region["y"] + region["height"] / 2
            dx, dy = region["width"] * distance / 2, region["height"] * distance / 2
            direction = args.get("direction", "up")
            start, end = {"up": ((cx, cy + dy), (cx, cy - dy)), "down": ((cx, cy - dy), (cx, cy + dy)),
                          "left": ((cx + dx, cy), (cx - dx, cy)), "right": ((cx - dx, cy), (cx + dx, cy))}[direction]
        duration = args.get("duration_ms", 350)
        with self.operation(), self.activity():
            self.adb.swipe(serial, start[0], start[1], end[0], end[1], duration)
            self.screen.gesture("drag", from_point={"x": start[0], "y": start[1]}, to_point={"x": end[0], "y": end[1]},
                                duration_ms=duration, viewport=self._viewport)
        return self.after(args, serial, {"from": [round(start[0]), round(start[1])], "to": [round(end[0]), round(end[1])], "duration_ms": duration})

    def tool_type_text(self, args):
        serial = self.device()
        portal = self.portal(serial)
        result = {}
        with self.operation(), self.activity():
            if "selector" in args:
                nodes, viewport, _ = self.nodes(serial)
                node, _ = resolve(nodes, args["selector"], viewport)
                point = tap_point(node, viewport)
                if point is None:
                    raise AndroidError("not_on_screen", "The field is outside the screen; swipe it into view first.", details={"action_executed": False})
                self.adb.tap(serial, point["x"], point["y"])
                self.screen.gesture("tap", point=point, viewport=self._viewport)
                result["focused_by_tap"] = point
                time.sleep(0.4)
            # Focus may land a moment after the tap that opened the field (e.g. a search page transition).
            deadline = time.monotonic() + 2.5
            phone = portal.phone_state()
            while not phone.get("isEditable") and time.monotonic() < deadline:
                time.sleep(0.3)
                phone = portal.phone_state()
            if not phone.get("isEditable"):
                raise AndroidError("no_focused_field", "No editable field has focus. Tap the field (or pass selector), then type again.",
                                   details={"action_executed": "selector" in args, "text_entered": False})
            try:
                portal.input_text(args["text"], bool(args.get("replace", False)))
            except AndroidError as exc:
                exc.uncertain = True
                exc.details.update(text_entered="unknown", recovery={"next_step": "Observe the field before typing again; never replay uncertain input."})
                raise
            result["text_entered"] = True
            if args.get("verify"):
                time.sleep(0.3)
                current = str((portal.phone_state().get("focusedElement") or {}).get("text") or "")
                result["verified"] = (current == args["text"]) if args.get("replace") else (args["text"] in current)
                result["field_text"] = current[:500]
            if args.get("submit"):
                self.adb.keyevent(serial, KEYCODES["enter"])
                result["submitted"] = True
        return self.after(args, serial, result)

    def tool_press_key(self, args):
        serial = self.device()
        with self.operation(), self.activity():
            self.adb.keyevent(serial, KEYCODES[args["key"]], bool(args.get("long_press")))
        return self.after(args, serial, {"pressed": args["key"]})

    def tool_launch_app(self, args):
        serial = self.device()
        package = args["package"]
        started = False
        with self.operation(), self.activity():
            component = launcher_component(self.adb, serial, package)
            if component:
                output = self.adb.shell(serial, ["am", "start", "-W", "-n", component], timeout=30)
                if "Error" in output and "Status: ok" not in output:
                    raise AndroidError("launch_failed", output.strip().splitlines()[-1][:300])
                started = "Status: ok" in output or "Error" not in output
            else:
                output = self.adb.shell(serial, ["monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"], timeout=30)
                if "No activities found" in output or "monkey aborted" in output:
                    raise AndroidError("app_not_found", f"{package} is not installed or has no launcher activity. Check android_apps.", details={"action_executed": False})
                started = True
        foreground = None
        deadline = time.monotonic() + 2.5
        portal = self.portal(serial)
        while True:
            try:
                foreground = portal.phone_state().get("packageName")
            except AndroidError:
                foreground = None
            if foreground == package or time.monotonic() >= deadline:
                break
            time.sleep(0.3)
        # An app resumed on a screen owned by a helper package (e.g. Settings search) is still launched.
        result = {"package": package, "component": component, "launched": started, "foreground_package": foreground,
                  "foreground_matches": foreground == package}
        return self.after(args, serial, result)

    def tool_apps(self, args):
        serial = self.device()
        include_system = args.get("include_system", False)
        try:
            rows = [{"package": item.get("packageName"), "label": item.get("label"), "version": item.get("versionName"), "system": bool(item.get("isSystemApp"))}
                    for item in self.portal(serial).packages() if isinstance(item, dict) and item.get("packageName")]
            source = "portal"
        except AndroidError:
            listing = self.adb.shell(serial, ["pm", "list", "packages"] + ([] if include_system else ["-3"]), timeout=20)
            rows = [{"package": line.split(":", 1)[1].strip(), "label": None} for line in listing.splitlines() if line.startswith("package:")]
            source = "pm"
        if not include_system:
            rows = [row for row in rows if not row.get("system")]
        query = args.get("query", "").lower()
        if query:
            rows = [row for row in rows if query in (row["package"] or "").lower() or query in (row.get("label") or "").lower()]
        rows.sort(key=lambda row: ((row.get("label") or row["package"]).lower()))
        limit = args.get("limit", 30)
        return {"source": source, "count": len(rows), "apps": rows[:limit], "truncated": len(rows) > limit}

    def tool_install_apk(self, args):
        serial = self.device()
        apk = Path(args["apk_path"])
        if not apk.is_file():
            raise AndroidError("invalid_argument", "apk_path does not exist.", details={"action_executed": False})
        with self.operation(), self.activity():
            done = self.adb.run(["install", "-r", "-t", str(apk)], serial, timeout=110)
        output = (done.stdout + done.stderr).strip()
        if done.returncode != 0 or "Success" not in output:
            lines = output.splitlines()
            raise AndroidError("install_failed", (lines[-1] if lines else "adb install failed")[:300])
        return {"installed": True, "apk": apk.name}

    def tool_wait(self, args):
        serial = self.device()
        deadline = time.monotonic() + args.get("timeout_seconds", 5)
        gone = args.get("gone", False)
        while True:
            nodes, viewport, _ = self.nodes(serial)
            found = [node for node in nodes if matches(node, args["selector"])]
            if bool(found) != gone:
                return {"found": not gone, "gone": gone, "match_count": len(found),
                        "matches": [{"index": i, **compact(node), "tap_point": tap_point(node, viewport)} for i, node in enumerate(found[:5])]}
            if time.monotonic() >= deadline:
                raise AndroidError("wait_timeout", "The selector did not reach the expected state in time.", details={"action_executed": False, "match_count": len(found)})
            time.sleep(0.5)

    def tool_screen(self, args):
        if args["action"] == "pause":
            self.screen.set_paused(True, reason="authentication")
        else:
            pause_id = self.screen.reconnect_pause_id()
            self.screen.resume_after_unlock(pause_id, explicit=True)
        return self.screen.pause_status()

    def screen_action(self, action):
        """Toolbar of the Mini App: the user's own click, outside the model's tool sequence."""
        if action == "refresh":
            serial = None
            try:
                serial = self.device()
                ready = self.portal(serial).ping()
                state = lock_state(self.adb, serial)
                if state["keyguard"] or state["awake"] is False:
                    self.screen.set_paused(True, reason="device_locked")
                else:
                    pause_id = self.screen.reconnect_pause_id()
                    self.screen.resume_after_unlock(pause_id, explicit=True)
            except AndroidError:
                ready = serial is not None
            return {"ok": True, "action": action, "service_ready": ready, **self.screen.pause_status()}
        if self.screen.paused():
            raise AndroidError("preview_paused", "The preview is paused while the user handles the phone. Nothing was sent.", details={"action_executed": False})
        serial = self.device()
        if action == "home":
            with self.operation(blocking=False):
                self.adb.keyevent(serial, KEYCODES["home"])
            return {"ok": True, "action": action}
        data = self.adb.screencap(serial)
        size = wda_image.png_size(data[:32])
        copy_png(self.state_dir, data)
        return {"ok": True, "action": action, "copied": True, "width": size[0] if size else None, "height": size[1] if size else None}


# ---------------------------------------------------------------- MCP

def result_content(data):
    """One compact JSON text block, plus the screenshot when the result carries one."""
    content = [{"type": "text", "text": json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(",", ":"))}]
    image = data.get("image") or (data.get("observation") or {}).get("image")
    if image and Path(image["path"]).is_file():
        content.append({"type": "image", "data": base64.b64encode(Path(image["path"]).read_bytes()).decode(), "mimeType": image.get("mimeType", "image/png")})
    return {"content": content, "isError": "error" in data}


def tool_result(runtime, params):
    name = params.get("name")
    try:
        return result_content(runtime.call(name, params.get("arguments", {})))
    except AndroidError as exc:
        return result_content({"error": exc.as_dict()})
    except Exception as exc:
        print("phone-use android tool failure: " + type(exc).__name__, file=sys.stderr)
        return result_content({"error": {"code": "internal_error", "message": "Local tool failed; run android_doctor or inspect local stderr.", "uncertain": True}})


INSTRUCTIONS = (
    "Android half of Phone Use; tools use the android_ prefix (iPhone tools use pua_). Read android-use-setup before setup and android-use for tasks. "
    "First Android use in a chat: android_doctor (read-only), fix what it names, then android_ready; only ready=true permits phone tasks. "
    "Several devices: ask the user and call android_setup(action=select, serial). Portal missing: tell the user it is the AGPL-3.0 Mobilerun Portal APK downloaded from GitHub and enabled as an accessibility service, and call install_portal with accept_license=true only after they agree. "
    "Coordinates are device pixels. Nodes give type, text, desc, hint, id and rect=[x,y,width,height]; omitted flags are false, omitted enabled/visible are true. Screenshot pixels x image.pixel_scale = device pixels. "
    "Read the image block itself; if the host drops it, open image.path. Prefer selectors copied from fresh nodes; on not_found/ambiguous_target inspect a screenshot before tapping by x/y. "
    "Actions run once with observe=none by default; request observe=tree/both when the next decision needs the new page. Never replay uncertain input. "
    "phone_locked already pauses the preview: ask the user to unlock, then android_ready again. For app passwords call android_screen(action=pause), ask with first option 已完成继续, then android_screen(action=resume). "
    "The live screen is the Phone Use Mini App in the right-side panel; ask the user to open it. Verify final results before reporting completion."
)


def serve(runtime):
    for line in sys.stdin:
        request = None
        try:
            if len(line) > 1024 * 1024:
                raise ValueError("Request exceeds 1 MiB")
            request = json.loads(line)
            if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
                raise ValueError("Invalid request")
            if "id" not in request:
                continue
            ident, method = request["id"], request["method"]
            params = request.get("params", {})
            if not isinstance(params, dict):
                raise ValueError("params must be an object")
            if method == "initialize":
                offered = params.get("protocolVersion")
                result = {"protocolVersion": offered if offered in PROTOCOLS else PROTOCOLS[0], "capabilities": {"tools": {"listChanged": False}},
                          "serverInfo": {"name": SERVER_NAME, "version": VERSION}, "instructions": INSTRUCTIONS}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                result = tool_result(runtime, params)
            else:
                response = {"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": "Method not found"}}
                print(json.dumps(response), flush=True)
                continue
            response = {"jsonrpc": "2.0", "id": ident, "result": result}
        except (ValueError, TypeError, KeyError):
            response = {"jsonrpc": "2.0", "id": request.get("id") if isinstance(request, dict) else None,
                        "error": {"code": -32700 if request is None else -32600, "message": "Parse error" if request is None else "Invalid request"}}
        print(json.dumps(response, ensure_ascii=False, allow_nan=False), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-dir")
    parser.add_argument("--doctor", action="store_true")
    parser.add_argument("--ready", action="store_true")
    parser.add_argument("--screen-action", choices=["refresh", "home", "screenshot"])
    args = parser.parse_args()
    runtime = Runtime(args.state_dir)
    if args.screen_action:
        try:
            data = runtime.screen_action(args.screen_action)
        except AndroidError as exc:
            data = {"ok": False, "error": exc.as_dict()}
        print(json.dumps(data, ensure_ascii=False, allow_nan=False))
        return 0 if data.get("ok") else 1
    if args.doctor or args.ready:
        try:
            data = runtime.call("android_doctor" if args.doctor else "android_ready", {"screenshot": False} if args.ready else {})
        except AndroidError as exc:
            data = {"error": exc.as_dict()}
        print(json.dumps(data, ensure_ascii=False))
        return 1 if "error" in data else 0
    serve(runtime)
    return 0


if __name__ == "__main__":
    sys.exit(main())
