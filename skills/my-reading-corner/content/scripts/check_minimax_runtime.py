#!/usr/bin/env python3
"""Collect the first layer of evidence for a MiniMax Agent runtime."""

from __future__ import annotations

import os
from collections.abc import Mapping


RUNTIME_MARKERS = (
    "__MAVIS_RUNTIME_PORT",
    "__MAVIS_RUNTIME_DATA_DIR",
    "__MAVIS_PARENT_DATA_DIR",
    "MAVIS_BUILD_ENV",
    "MAVIS_REGION",
    "MINIMAX_DATA_DIR",
)


def is_minimax_runtime(environment: Mapping[str, str]) -> bool:
    return any(environment.get(name, "").strip() for name in RUNTIME_MARKERS)


def main() -> None:
    if is_minimax_runtime(os.environ):
        print("MINIMAX")
        return

    # MiniMax Code intentionally removes its private runtime values before a
    # shell command starts. In that case the command tool still reports the
    # removed variable names in its structured `envSanitized` metadata. The
    # Skill instructions perform that second-layer check without exposing any
    # value to the user.
    print("CHECK_TOOL_METADATA")


if __name__ == "__main__":
    main()
