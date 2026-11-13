#!/usr/bin/env python3
"""Build the PDF, EPUB, and HTML editions of the book."""

import argparse
from tools.lib.build import build_epub_source, build_html, build_pdf_source, run_pandoc
from tools.lib.definitions import DIST_DIR

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=("pdf", "epub", "html", "all"),
        default="all",
        help="Which publication format to build.",
    )
    args = parser.parse_args()

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    if args.format in ("pdf", "all"):
        pdf_path = (
            DIST_DIR / "science-and-engineering-of-applied-machine-learning.pdf"
        )
        run_pandoc(
            source=build_pdf_source(), output=pdf_path, edition="pdf"
        )

    if args.format in ("epub", "all"):
        epub_path = (
            DIST_DIR / "science-and-engineering-of-applied-machine-learning.epub"
        )
        run_pandoc(
            source=build_epub_source(), output=epub_path, edition="epub"
        )

    if args.format in ("html", "all"):
        build_html()

    print(f"Publication files written to {DIST_DIR}")

if __name__ == "__main__":
    main()
