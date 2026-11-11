#!/usr/bin/env python3
"""Check Python code fences in the book chapters for syntax errors."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "manuscript" / "chapters"
PYTHON_FENCE = re.compile(
    r"^[ \t]*```python(?:[ \t]+[^\r\n`]*)?\r?\n(.*?)^[ \t]*```[ \t]*$",
    flags=re.MULTILINE | re.DOTALL,
)


def main() -> int:
    chapter_files = sorted(CHAPTERS.glob("*.md"))
    if not chapter_files:
        print(f"No chapter files found in {CHAPTERS}", file=sys.stderr)
        return 1

    checked = 0
    failures = []
    for path in chapter_files:
        source = path.read_text(encoding="utf-8")
        for index, match in enumerate(PYTHON_FENCE.finditer(source), start=1):
            checked += 1
            try:
                ast.parse(match.group(1), filename=str(path))
            except SyntaxError as error:
                failures.append(
                    f"{path.relative_to(ROOT)} block {index}: "
                    f"{error.lineno}:{error.offset} {error.msg}"
                )

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Checked {checked} Python blocks in {len(chapter_files)} chapters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
