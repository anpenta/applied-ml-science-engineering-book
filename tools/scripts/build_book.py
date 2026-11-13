#!/usr/bin/env python3
"""Build the PDF, EPUB, and HTML editions of the book."""

import argparse

from tools.lib.build import build_epub_source, build_html, build_pdf_source, run_pandoc
from tools.lib.definitions import BOOK, DIST_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=("pdf", "epub", "html", "all"),
        default="all",
        help="Which publication format to build.",
    )
    args = parser.parse_args()

    if args.format in ("pdf", "all"):
        run_pandoc(build_pdf_source(), DIST_DIR / f"{BOOK}.pdf", edition="pdf")

    if args.format in ("epub", "all"):
        run_pandoc(build_epub_source(), DIST_DIR / f"{BOOK}.epub", edition="epub")

    if args.format in ("html", "all"):
        build_html()

    print(f"Publication files written to {DIST_DIR}")

if __name__ == "__main__":
    main()
