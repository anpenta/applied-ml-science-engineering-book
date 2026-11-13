#!/usr/bin/env python3
"""Validate generated book editions."""

import sys

from tools.lib.build import iter_book_sections
from tools.lib.validation import validate_epub, validate_html, validate_pdf


def main() -> int:
    sections = list(iter_book_sections())
    failed = False
    for name, validate in [("HTML", validate_html), ("PDF", validate_pdf), ("EPUB", validate_epub)]:
        try:
            validate(sections=sections)
            print(f"{name}: PASS")
        except Exception as error:
            failed = True
            print(f"{name}: FAIL — {error}", file=sys.stderr)
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
