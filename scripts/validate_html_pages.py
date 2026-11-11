#!/usr/bin/env python3
"""Check generated HTML page structure and local navigation."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

DIST = Path(__file__).resolve().parents[1] / "dist"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.headings: list[tuple[str, str]] = []
        self.links: list[str] = []
        self.navigation_count = 0
        self._heading: str | None = None
        self._heading_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in ("h1", "h2", "h3"):
            self._heading = tag
            self._heading_text = []
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "nav" and attributes.get("aria-label") == "Book navigation":
            self.navigation_count += 1

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._heading_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading:
            self.headings.append((tag, "".join(self._heading_text).strip()))
            self._heading = None


def validate_html_pages() -> None:
    pages = sorted(DIST.glob("*.html"))
    if len(pages) != 19:
        raise ValueError(f"Expected 19 HTML pages, found {len(pages)}")

    for path in pages:
        source = path.read_text(encoding="utf-8")
        if r"\n" in source:
            raise ValueError(f"{path.name} contains a literal backslash-n")
        parser = PageParser()
        parser.feed(source)
        if not parser.headings:
            raise ValueError(f"{path.name} has no headings")
        if path.name == "index.html":
            expected = {p.name for p in pages if p != path}
            linked = {urlsplit(link).path for link in parser.links}
            if not expected.issubset(linked):
                raise ValueError(f"Contents missing links: {sorted(expected - linked)}")
        else:
            if parser.navigation_count != 1:
                raise ValueError(f"{path.name} must have one book navigation")
            if not any(urlsplit(link).path == "index.html" for link in parser.links):
                raise ValueError(f"{path.name} has no contents link")
        for link in parser.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (DIST / unquote(parsed.path)).resolve()
            if not target.is_relative_to(DIST.resolve()) or not target.exists():
                raise ValueError(f"{path.name}: broken local link {link}")
    print(f"Validated structure and local links for {len(pages)} HTML pages")


if __name__ == "__main__":
    validate_html_pages()
