#!/usr/bin/env python3
"""Install the newest bundled MiniMax H3 extension and verify the disk copy."""

from __future__ import annotations

import argparse
import collections
import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile


Archive = collections.namedtuple("Archive", "path version mtime")
_ARCHIVE_RE = re.compile(r"^minimax_h3-[0-9]+(?:\.[0-9]+){2}\.zip$")
_VERSION_RE = re.compile(r'^version\s*=\s*"([0-9]+(?:\.[0-9]+){2})"', re.MULTILINE)
_LEGACY_FALLBACK = "未安装该插件时按下面的步骤执行"
_INTERNAL_BUNDLE = "com.minimax.agent.cn.internal"
_DIRECT_VIDEO = "preview_video.mp4"
_PLUGIN_TRIGGER = "Blender 白模渲染"


def _version_tuple(text):
    return tuple(int(part) for part in text.split("."))


def inspect_archive(path):
    try:
        with zipfile.ZipFile(path) as archive:
            manifest = archive.read("blender_manifest.toml").decode("utf-8")
            handoff = archive.read("services/handoff_inbox.py").decode("utf-8")
            region = archive.read("region.py").decode("utf-8")
    except (OSError, KeyError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
        raise ValueError("invalid Blender extension archive: {0}".format(exc)) from exc
    match = _VERSION_RE.search(manifest)
    if not match:
        raise ValueError("extension version is missing")
    if _LEGACY_FALLBACK in handoff:
        raise ValueError("legacy fallback prompt found in extension")
    if _DIRECT_VIDEO not in handoff:
        raise ValueError("direct preview video handoff is missing")
    if _PLUGIN_TRIGGER not in handoff:
        raise ValueError("current Plugin trigger name is missing")
    if _INTERNAL_BUNDLE not in region:
        raise ValueError("Internal Pilkod bundle support is missing")
    return _version_tuple(match.group(1))


def _archives_under(roots):
    seen = set()
    for root in roots:
        root = os.path.abspath(os.path.expanduser(root))
        if not os.path.isdir(root):
            continue
        for folder, _dirs, files in os.walk(root, followlinks=True):
            if "blender-h3-dcc" not in folder.replace("\\", "/"):
                continue
            for name in files:
                if not _ARCHIVE_RE.match(name):
                    continue
                path = os.path.realpath(os.path.join(folder, name))
                if path in seen:
                    continue
                seen.add(path)
                try:
                    version = inspect_archive(path)
                    mtime = os.path.getmtime(path)
                except (OSError, ValueError):
                    # Keep invalid candidates out unless there is nothing valid;
                    # the final error below then explains the missing safe build.
                    continue
                yield Archive(path, version, mtime)


def select_archive(roots):
    candidates = sorted(
        _archives_under(roots), key=lambda item: (item.version, item.mtime),
        reverse=True,
    )
    if candidates:
        return candidates[0]

    # Surface a precise safety error when a matching archive exists but is bad.
    for root in roots:
        for folder, _dirs, files in os.walk(os.path.expanduser(root), followlinks=True):
            if "blender-h3-dcc" not in folder.replace("\\", "/"):
                continue
            for name in files:
                if _ARCHIVE_RE.match(name):
                    inspect_archive(os.path.join(folder, name))
    raise FileNotFoundError("no safe bundled minimax_h3 extension archive found")


def find_blender(explicit=""):
    if explicit:
        path = os.path.abspath(os.path.expanduser(explicit))
        if os.path.isfile(path):
            return path
        raise FileNotFoundError("Blender executable not found: {0}".format(path))
    candidates = []
    if sys.platform == "darwin":
        candidates += glob.glob(
            "/Applications/Blender*.app/Contents/MacOS/Blender"
        )
    elif os.name == "nt":
        for base in (os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")):
            if base:
                candidates += glob.glob(os.path.join(
                    base, "Blender Foundation", "Blender*", "blender.exe"
                ))
    else:
        resolved = shutil.which("blender")
        if resolved:
            candidates.append(resolved)
    candidates = sorted(set(candidates), reverse=True)
    if not candidates:
        raise FileNotFoundError("Blender 4.2 or newer was not found")
    return candidates[0]


def _installed_extension_dirs():
    home = os.path.expanduser("~")
    patterns = [
        os.path.join(home, "Library", "Application Support", "Blender", "*",
                     "extensions", "user_default", "minimax_h3"),
        os.path.join(os.environ.get("APPDATA", ""), "Blender Foundation", "Blender",
                     "*", "extensions", "user_default", "minimax_h3"),
        os.path.join(home, ".config", "blender", "*", "extensions", "user_default",
                     "minimax_h3"),
    ]
    return [path for pattern in patterns if pattern for path in glob.glob(pattern)]


def verify_installed(expected_version):
    for folder in _installed_extension_dirs():
        try:
            manifest = open(os.path.join(folder, "blender_manifest.toml"),
                            encoding="utf-8").read()
            handoff = open(os.path.join(folder, "services", "handoff_inbox.py"),
                           encoding="utf-8").read()
            region = open(os.path.join(folder, "region.py"), encoding="utf-8").read()
        except OSError:
            continue
        match = _VERSION_RE.search(manifest)
        if (match and _version_tuple(match.group(1)) == expected_version
                and _LEGACY_FALLBACK not in handoff
                and _DIRECT_VIDEO in handoff
                and _PLUGIN_TRIGGER in handoff
                and _INTERNAL_BUNDLE in region):
            return folder
    raise RuntimeError("the installed extension did not match the bundled safe version")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", help="use this bundled extension ZIP")
    parser.add_argument("--blender", help="path to the Blender executable")
    parser.add_argument("--root", action="append", default=[],
                        help="Pilkod data root to search; may be repeated")
    args = parser.parse_args(argv)

    if args.archive:
        path = os.path.abspath(os.path.expanduser(args.archive))
        selected = Archive(path, inspect_archive(path), os.path.getmtime(path))
    else:
        roots = args.root or [os.path.expanduser("~/.minimax"),
                              os.path.expanduser("~/.minimax")]
        selected = select_archive(roots)
    blender = find_blender(args.blender or "")
    result = subprocess.run(
        [blender, "--command", "extension", "install-file", "-r", "user_default",
         "--enable", selected.path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        return result.returncode
    installed = verify_installed(selected.version)
    print("Installed MiniMax H3 {0} from {1}".format(
        ".".join(str(part) for part in selected.version), selected.path))
    print("Verified {0}".format(installed))
    print("Restart Blender before using Open Pilkod.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
