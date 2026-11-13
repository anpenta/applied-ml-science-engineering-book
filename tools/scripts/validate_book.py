#!/usr/bin/env python3
"""Validate generated book editions."""

import sys
from tools.lib.validation import get_expected_sections, validate_html, validate_pdf, validate_epub

def main() -> int:
    sections = get_expected_sections()
    failures = []
    for name, validate in [("HTML", validate_html), ("PDF", validate_pdf), ("EPUB", validate_epub)]:
        try:
            validate(sections=sections)
            print(f"{name}: PASS")
        except Exception as error:
            failures.append(f"{name}: {error}")
            print(f"{name}: FAIL — {error}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
