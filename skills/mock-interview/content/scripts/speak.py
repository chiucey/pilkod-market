#!/usr/bin/env python3
"""Speak interview questions aloud using MiniMax text-to-speech.

Usage:
    python scripts/speak.py "Tell me about a time you failed."
    python scripts/speak.py --voice female-shaonv "Why this company?"
    echo "Walk me through your resume." | python scripts/speak.py

Requires MINIMAX_API_KEY (and MINIMAX_GROUP_ID for the domestic endpoint) in a
.env file at the project root, or exported in your shell. Copy .env.example.

Audio is written to a temp .mp3 and played with the system player. If playback
isn't available, the file path is printed so you can open it yourself.

API details can change; if a call starts failing, check:
https://platform.minimaxi.com/document/T2A%20V2
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency. Run: pip install requests")

DOMESTIC_URL = "https://api.minimaxi.com/v1/t2a_v2"
GLOBAL_URL = "https://api.minimax.io/v1/t2a_v2"
DEFAULT_MODEL = "speech-02-hd"
DEFAULT_VOICE = "male-qn-jingying"


def load_dotenv(path: Path) -> None:
    """Minimal .env loader so the script has no dependency on python-dotenv."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Don't clobber anything already exported in the shell.
        os.environ.setdefault(key, value)


def play(path: Path) -> None:
    """Play an audio file with whatever the platform provides."""
    players = {
        "darwin": ["afplay", str(path)],
        "linux": ["mpg123", "-q", str(path)],
        "win32": ["powershell", "-c", f"(New-Object Media.SoundPlayer '{path}').PlaySync()"],
    }
    cmd = players.get(sys.platform)
    if not cmd:
        print(f"No known player for {sys.platform}. Audio saved to: {path}")
        return
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"Couldn't play audio automatically. File saved to: {path}")


def synthesize(text: str, voice: str, model: str, region: str) -> bytes:
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MINIMAX_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    url = GLOBAL_URL if region == "global" else DOMESTIC_URL
    group_id = os.environ.get("MINIMAX_GROUP_ID")
    if group_id:
        url = f"{url}?GroupId={group_id}"

    payload = {
        "model": model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice,
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
        },
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()

    audio_hex = body.get("data", {}).get("audio")
    if not audio_hex:
        status = body.get("base_resp", {})
        raise RuntimeError(f"No audio returned. API said: {status}")

    return bytes.fromhex(audio_hex)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("text", nargs="?", help="Text to speak. Reads stdin if omitted.")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Voice id (default: {DEFAULT_VOICE})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"TTS model (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--region",
        choices=["domestic", "global"],
        default=os.environ.get("MINIMAX_REGION", "domestic"),
        help="Which MiniMax endpoint to use",
    )
    parser.add_argument("--save", help="Write the mp3 here instead of a temp file")
    parser.add_argument("--no-play", action="store_true", help="Synthesize but don't play")
    args = parser.parse_args()

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    text = args.text if args.text else sys.stdin.read().strip()
    if not text:
        parser.error("No text given.")

    try:
        audio = synthesize(text, args.voice, args.model, args.region)
    except Exception as exc:
        # The interview matters more than the audio. Fail loudly but cheaply so
        # the caller can fall back to text and keep going.
        print(f"TTS failed: {exc}", file=sys.stderr)
        return 1

    if args.save:
        out = Path(args.save)
    else:
        out = Path(tempfile.gettempdir()) / "mock_interview_question.mp3"
    out.write_bytes(audio)

    if not args.no_play:
        play(out)
    else:
        print(out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
