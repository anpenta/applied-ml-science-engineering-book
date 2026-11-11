#!/usr/bin/env python3
"""Verify that HTML and EPUB show the book mark above the title."""

from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
TITLE = "The Science and Engineering of Applied Machine Learning"


def validate_html() -> None:
    page = (DIST / "index.html").read_text(encoding="utf-8")
    image = re.search(
        r'<img\b[^>]*src="assets/applied-ml-mark\.svg"[^>]*>', page
    )
    title = page.find(TITLE)
    if image is None or title < 0 or image.start() > title:
        raise AssertionError("HTML landing page must show the SVG before the title")
    if not (DIST / "assets" / "applied-ml-mark.svg").is_file():
        raise AssertionError("HTML book mark asset is missing")


def validate_epub() -> None:
    epub = DIST / "science-and-engineering-of-applied-machine-learning.epub"
    with ZipFile(epub) as archive:
        title_page = archive.read("EPUB/text/title_page.xhtml").decode("utf-8")
        image = re.search(r'<img\b[^>]*src="([^"]+)"', title_page)
        title = title_page.find(TITLE)
        if image is None or title < 0 or image.start() > title:
            raise AssertionError("EPUB title page must show the mark before the title")
        if not image.group(1).endswith(".png"):
            raise AssertionError("EPUB title page must use the PNG mark")
        media_path = "EPUB/" + image.group(1).removeprefix("../")
        if media_path not in archive.namelist():
            raise AssertionError(f"EPUB title page image is not embedded: {media_path}")
        if title_page.count('class="title"') != 1:
            raise AssertionError("EPUB must have exactly one title on its title page")


if __name__ == "__main__":
    validate_html()
    validate_epub()
    print("HTML and EPUB title marks verified")
