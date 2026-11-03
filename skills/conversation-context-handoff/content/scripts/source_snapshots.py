#!/usr/bin/env python3
"""Embed or verify exact source snapshots in a Markdown context-handoff file.

Usage:
  python source_snapshots.py append HANDOFF.md PROJECT_ROOT --rev REV --heading "..." file1 file2
  python source_snapshots.py verify HANDOFF.md PROJECT_ROOT --rev REV file1 file2

Use REV=WORKTREE for current files, or any Git revision such as HEAD, a tag,
or a commit hash. The script writes a machine-readable HTML marker before
each fenced source block, then verifies the embedded text byte-for-byte.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

MARKER = '<!-- source-snapshot:rev={rev};path={path} -->'
LANGS = {
    '.js': 'javascript',
    '.jsx': 'jsx',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.json': 'json',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.py': 'python',
    '.sh': 'bash',
    '.md': 'markdown',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.toml': 'toml',
    '.gitignore': 'text',
}


def fail(message: str) -> None:
    raise SystemExit(f'error: {message}')


def read_source(project_root: Path, revision: str, relative_path: str) -> str:
    if revision.upper() == 'WORKTREE':
        path = project_root / relative_path
        if not path.is_file():
            fail(f'worktree file not found: {path}')
        return path.read_text(encoding='utf-8')
    try:
        raw = subprocess.check_output(
            ['git', 'show', f'{revision}:{relative_path}'],
            cwd=project_root,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.output.decode('utf-8', 'replace').strip()
        fail(f'cannot read {revision}:{relative_path}: {detail}')
    return raw.decode('utf-8')


def fence_language(relative_path: str) -> str:
    name = Path(relative_path).name
    if name in LANGS:
        return LANGS[name]
    return LANGS.get(Path(relative_path).suffix.lower(), 'text')


def append_snapshots(args: argparse.Namespace) -> int:
    handoff = Path(args.handoff)
    root = Path(args.project_root)
    revision = args.rev
    if not handoff.is_file():
        fail(f'handoff file not found: {handoff}')

    chunks: list[str] = []
    if args.heading:
        chunks.append(f'\n\n{args.heading}\n')
    for relative_path in args.files:
        code = read_source(root, revision, relative_path).rstrip()
        if '```' in code:
            fail(f'{relative_path} contains a Markdown fence; embed it with a different tool')
        marker = MARKER.format(rev=revision, path=relative_path)
        chunks.extend([
            '\n\n',
            marker,
            '\n\n',
            f'{"#" * args.heading_level} `{relative_path}`',
            '\n\n',
            f'```{fence_language(relative_path)}',
            '\n',
            code,
            '\n```\n',
        ])

    with handoff.open('a', encoding='utf-8') as handle:
        handle.write(''.join(chunks))
    return len(args.files)


def extract_snapshot(document: str, revision: str, relative_path: str) -> str:
    marker = MARKER.format(rev=revision, path=relative_path)
    start = document.find(marker)
    if start < 0:
        fail(f'marker not found: {marker}')
    fence_start = document.find('```', start + len(marker))
    if fence_start < 0:
        fail(f'opening fence not found after marker: {relative_path}')
    newline = document.find('\n', fence_start)
    if newline < 0:
        fail(f'opening fence is not closed by a newline: {relative_path}')
    fence_end = document.find('\n```', newline + 1)
    if fence_end < 0:
        fail(f'closing fence not found: {relative_path}')
    return document[newline + 1:fence_end]


def verify_snapshots(args: argparse.Namespace) -> int:
    handoff = Path(args.handoff)
    root = Path(args.project_root)
    revision = args.rev
    if not handoff.is_file():
        fail(f'handoff file not found: {handoff}')
    document = handoff.read_text(encoding='utf-8')
    for relative_path in args.files:
        expected = read_source(root, revision, relative_path).rstrip()
        actual = extract_snapshot(document, revision, relative_path)
        if actual != expected:
            fail(f'snapshot mismatch for {revision}:{relative_path}')
    return len(args.files)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)

    for command in ('append', 'verify'):
        child = subparsers.add_parser(command)
        child.add_argument('handoff', help='Markdown context-handoff file')
        child.add_argument('project_root', help='Project root or Git repository')
        child.add_argument('files', nargs='+', help='Repository-relative source files')
        child.add_argument('--rev', default='WORKTREE', help='Git revision, or WORKTREE for current files')
        child.set_defaults(handler=append_snapshots if command == 'append' else verify_snapshots)
        if command == 'append':
            child.add_argument('--heading', default='', help='Optional Markdown heading inserted before snapshots')
            child.add_argument('--heading-level', type=int, default=3, choices=(2, 3, 4, 5, 6))
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    count = args.handler(args)
    action = 'appended' if args.command == 'append' else 'verified'
    print(f'{action} {count} source snapshot(s) from {args.rev}')


if __name__ == '__main__':
    main()
