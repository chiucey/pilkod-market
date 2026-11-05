#!/usr/bin/env python3
"""Configure and retrieve the WeRead API key without exposing it to the agent."""

from __future__ import annotations

import argparse
import ctypes
import getpass
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional


SERVICE = "my-reading-corner.weread-api"
ACCOUNT = getpass.getuser()
WINDOWS_STORE = (
    Path(os.environ.get("LOCALAPPDATA", Path.home()))
    / "my-reading-corner"
    / "weread-key.bin"
)


def _valid_key(value: str) -> bool:
    return value.startswith("wrk-") and len(value) >= 12


def _mac_prompt() -> Optional[str]:
    raise RuntimeError("LOCAL_PROMPT_DISABLED")
    script = r'''
try
    set resultDialog to display dialog "请粘贴微信读书 Key" default answer "" with hidden answer buttons {"取消", "保存"} default button "保存" cancel button "取消" with title "我的阅读角"
    return text returned of resultDialog
on error number -128
    return "__CANCELLED__"
end try
'''
    result = subprocess.run(
        ["/usr/bin/osascript", "-e", script],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("无法打开本地输入框")
    value = result.stdout.rstrip("\r\n")
    return None if value == "__CANCELLED__" else value


def _mac_store(value: str) -> None:
    # `-w` is deliberately last and receives the secret through stdin, so the
    # value never appears in the process arguments or agent-visible command.
    result = subprocess.run(
        [
            "/usr/bin/security",
            "add-generic-password",
            "-a",
            ACCOUNT,
            "-s",
            SERVICE,
            "-U",
            "-w",
        ],
        input=value + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("无法保存到 macOS 钥匙串")


def _mac_load() -> Optional[str]:
    result = subprocess.run(
        [
            "/usr/bin/security",
            "find-generic-password",
            "-a",
            ACCOUNT,
            "-s",
            SERVICE,
            "-w",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.rstrip("\r\n")
    return value if _valid_key(value) else None


def _windows_prompt() -> Optional[str]:
    raise RuntimeError("LOCAL_PROMPT_DISABLED")
    powershell = r'''
Add-Type -AssemblyName System.Windows.Forms
$form = New-Object System.Windows.Forms.Form
$form.Text = "我的阅读角"
$form.Width = 440
$form.Height = 170
$form.StartPosition = "CenterScreen"

$label = New-Object System.Windows.Forms.Label
$label.Text = "请粘贴微信读书 Key"
$label.Left = 20
$label.Top = 20
$label.Width = 380
$form.Controls.Add($label)

$box = New-Object System.Windows.Forms.TextBox
$box.Left = 20
$box.Top = 48
$box.Width = 380
$box.UseSystemPasswordChar = $true
$form.Controls.Add($box)

$save = New-Object System.Windows.Forms.Button
$save.Text = "保存"
$save.Left = 230
$save.Top = 82
$save.DialogResult = [System.Windows.Forms.DialogResult]::OK
$form.AcceptButton = $save
$form.Controls.Add($save)

$cancel = New-Object System.Windows.Forms.Button
$cancel.Text = "取消"
$cancel.Left = 320
$cancel.Top = 82
$cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$form.CancelButton = $cancel
$form.Controls.Add($cancel)

$form.Add_Shown({$box.Select()})
$result = $form.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
    [Console]::Out.Write($box.Text)
} else {
    [Console]::Out.Write("__CANCELLED__")
}
'''
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            powershell,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("无法打开本地输入框")
    value = result.stdout.rstrip("\r\n")
    return None if value == "__CANCELLED__" else value


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.c_uint32),
        ("pbData", ctypes.POINTER(ctypes.c_ubyte)),
    ]


def _blob_from_bytes(data: bytes):
    buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    blob = _DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    return blob, buffer


def _windows_protect(data: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    source, source_buffer = _blob_from_bytes(data)
    output = _DataBlob()
    ok = crypt32.CryptProtectData(
        ctypes.byref(source),
        "my-reading-corner",
        None,
        None,
        None,
        0,
        ctypes.byref(output),
    )
    del source_buffer
    if not ok:
        raise RuntimeError("Windows 无法加密 Key")
    try:
        return ctypes.string_at(output.pbData, output.cbData)
    finally:
        kernel32.LocalFree(output.pbData)


def _windows_unprotect(data: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    source, source_buffer = _blob_from_bytes(data)
    output = _DataBlob()
    ok = crypt32.CryptUnprotectData(
        ctypes.byref(source),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(output),
    )
    del source_buffer
    if not ok:
        raise RuntimeError("Windows 无法解密 Key")
    try:
        return ctypes.string_at(output.pbData, output.cbData)
    finally:
        kernel32.LocalFree(output.pbData)


def _windows_store(value: str) -> None:
    WINDOWS_STORE.parent.mkdir(parents=True, exist_ok=True)
    WINDOWS_STORE.write_bytes(_windows_protect(value.encode("utf-8")))


def _windows_load() -> Optional[str]:
    if not WINDOWS_STORE.exists():
        return None
    try:
        value = _windows_unprotect(WINDOWS_STORE.read_bytes()).decode("utf-8")
    except (OSError, UnicodeDecodeError, RuntimeError):
        return None
    return value if _valid_key(value) else None


def load_key() -> Optional[str]:
    existing = os.environ.get("WEREAD_API_KEY", "")
    if _valid_key(existing):
        return existing
    return None


def setup_key() -> str:
    return "DISABLED"
    system = platform.system()
    if system == "Darwin":
        value = _mac_prompt()
    elif system == "Windows":
        value = _windows_prompt()
    else:
        return "UNSUPPORTED"

    if value is None:
        return "CANCELLED"
    if not _valid_key(value):
        return "INVALID"

    if system == "Darwin":
        _mac_store(value)
    else:
        _windows_store(value)
    return "READY"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "setup"))
    args = parser.parse_args()

    try:
        if args.action == "status":
            print("READY" if load_key() else "MISSING")
        else:
            print(setup_key())
    except RuntimeError:
        print("ERROR")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
