#!/usr/bin/env python3
"""Record a spoken interview answer to a .wav file.

Usage:
    python scripts/record.py --output answer.wav          # Enter to stop
    python scripts/record.py --output answer.wav --seconds 120

Why record instead of just typing: pacing, filler words and the length of your
pauses are invisible in text, and they're usually the things people are most
surprised by in a debrief.

Backends, tried in order: sounddevice (pip install sounddevice), then ffmpeg.
If neither is available the script says so and exits — fall back to your device's
built-in dictation, which needs no setup at all.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import threading
import wave
from pathlib import Path

SAMPLE_RATE = 16000  # plenty for speech, and small files
CHANNELS = 1


def record_sounddevice(out: Path, seconds: int | None) -> bool:
    try:
        import numpy as np
        import sounddevice as sd
    except ImportError:
        return False

    frames = []
    stop = threading.Event()

    def callback(indata, _frames, _time, status):
        if status:
            print(status, file=sys.stderr)
        frames.append(indata.copy())

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16", callback=callback
        ):
            if seconds:
                print(f"Recording for {seconds}s… speak now.")
                sd.sleep(seconds * 1000)
            else:
                print("Recording… press Enter when you're done.")
                threading.Thread(target=lambda: (input(), stop.set()), daemon=True).start()
                while not stop.is_set():
                    sd.sleep(120)
    except Exception as exc:
        print(f"Recording failed: {exc}", file=sys.stderr)
        return False

    if not frames:
        print("Nothing was recorded — is the microphone permitted?", file=sys.stderr)
        return False

    audio = np.concatenate(frames, axis=0)
    with wave.open(str(out), "wb") as wav:
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(2)  # int16
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(audio.tobytes())
    return True


def record_ffmpeg(out: Path, seconds: int | None) -> bool:
    if not shutil.which("ffmpeg"):
        return False

    inputs = {
        "darwin": ["-f", "avfoundation", "-i", ":0"],
        "linux": ["-f", "alsa", "-i", "default"],
        "win32": ["-f", "dshow", "-i", "audio=default"],
    }
    args = inputs.get(sys.platform)
    if not args:
        return False

    cmd = ["ffmpeg", "-y", "-loglevel", "error", *args,
           "-ar", str(SAMPLE_RATE), "-ac", str(CHANNELS)]
    if seconds:
        cmd += ["-t", str(seconds)]
    cmd.append(str(out))

    if seconds:
        print(f"Recording for {seconds}s… speak now.")
        subprocess.run(cmd, check=False)
    else:
        print("Recording… press Enter when you're done.")
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        input()
        proc.communicate(input=b"q", timeout=10)

    return out.exists() and out.stat().st_size > 1024


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--output", default="answer.wav", help="Where to write the .wav")
    parser.add_argument("--seconds", type=int, help="Fixed duration; omit to stop with Enter")
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    for backend in (record_sounddevice, record_ffmpeg):
        if backend(out, args.seconds):
            size_kb = out.stat().st_size / 1024
            print(f"Saved {out} ({size_kb:.0f} KB)")
            return 0

    print(
        "No working audio backend.\n"
        "  Fix:  pip install sounddevice numpy    (or install ffmpeg)\n"
        "  Or skip it: use your device's dictation instead — press the mic key on\n"
        "  macOS or the keyboard mic on your phone, and speak your answer into chat.\n"
        "  Dictation captures your words fine; only the pacing analysis needs audio.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
