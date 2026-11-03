#!/usr/bin/env python3
"""Call the fixed WeRead gateway while keeping authorization out of tool logs."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

from weread_key import load_key


GATEWAY = "https://i.weread.qq.com/api/agent/gateway"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--request",
        help="Non-secret JSON request. If omitted, read the request from stdin.",
    )
    args = parser.parse_args()

    raw = args.request if args.request is not None else sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid request JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit("Request JSON must be an object")
    if not payload.get("api_name"):
        raise SystemExit("Request JSON must contain api_name")
    if not payload.get("skill_version"):
        raise SystemExit("Request JSON must contain skill_version")

    key = load_key()
    if not key:
        raise SystemExit("WEREAD_KEY_MISSING")

    request = urllib.request.Request(
        GATEWAY,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read()
        sys.stdout.buffer.write(body)
        raise SystemExit(1) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"WEREAD_NETWORK_ERROR: {exc.reason}") from exc
    finally:
        key = None

    sys.stdout.buffer.write(body)


if __name__ == "__main__":
    main()
