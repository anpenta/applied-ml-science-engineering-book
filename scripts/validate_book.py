#!/usr/bin/env python3
"""Check book-specific requirements in generated HTML, PDF, and EPUB editions."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urldefrag
from xml.etree import ElementTree as ET

import fitz
from playwright.sync_api import sync_playwright

from build_book import DIST_DIR, METADATA, get_html_page_filename, iter_book_sections

BOOK = "science-and-engineering-of-applied-machine-learning"
NS = {
    "c": "urn:oasis:names:tc:opendocument:xmlns:container",
    "o": "http://www.idpf.org/2007/opf",
    "x": "http://www.w3.org/1999/xhtml",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expected_sections():
    return list(iter_book_sections())


def validate_html(sections) -> None:
    pages = [get_html_page_filename(section) for section in sections]
    screenshots = DIST_DIR.parent / "html-screenshots"
    screenshots.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for width, label in [(1280, "desktop"), (390, "mobile")]:
                page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
                page.goto((DIST_DIR / "index.html").as_uri())
                require(page.locator(".book-landing-title h1").count() == 1, "HTML: expected one landing title")
                require(page.locator(".book-landing-title h1").inner_text().strip() == METADATA["title"], "HTML: incorrect title")
                require(METADATA["author"] in page.locator(".book-landing-title").inner_text(), "HTML: author missing")
                logo = page.locator(".book-cover-mark img")
                require(logo.count() == 1 and logo.evaluate("(img) => img.complete && img.naturalWidth > 0"), "HTML: logo not loaded")
                hrefs = page.locator(".book-contents a").evaluate_all("(links) => links.map(link => link.getAttribute('href'))")
                require(hrefs == pages, "HTML: contents order differs from manuscript")
                page.screenshot(path=str(screenshots / f"home-{label}.png"), full_page=True)
                page.locator(".book-contents").screenshot(path=str(screenshots / f"contents-{label}.png"))
                for index, filename in enumerate(pages):
                    page.goto((DIST_DIR / filename).as_uri())
                    expected = sections[index]
                    heading = f"Chapter {expected.chapter_number}: {expected.heading}" if expected.kind == "chapter" else expected.heading
                    require(page.locator("h1").first.inner_text().strip() == heading, f"HTML: wrong heading on {filename}")
                    nav = page.locator("nav.book-navigation")
                    require(nav.count() == 1, f"HTML: missing navigation on {filename}")
                    previous = "index.html" if index == 0 else pages[index - 1]
                    require(nav.get_by_role("link", name="Previous").get_attribute("href") == previous, f"HTML: wrong Previous on {filename}")
                    next_link = nav.get_by_role("link", name="Next")
                    if index + 1 < len(pages):
                        require(next_link.get_attribute("href") == pages[index + 1], f"HTML: wrong Next on {filename}")
                    else:
                        require(next_link.count() == 0, "HTML: final page has a Next link")
                representative = next((p for p, s in zip(pages, sections) if s.kind == "chapter"), pages[0])
                page.goto((DIST_DIR / representative).as_uri())
                page.screenshot(path=str(screenshots / f"chapter-{label}.png"), full_page=True)
                page.close()
        finally:
            browser.close()


def validate_pdf(sections) -> None:
    path = DIST_DIR / f"{BOOK}.pdf"
    with fitz.open(path) as pdf:
        require(len(pdf) > 1, "PDF: empty document")
        text = "\n".join(page.get_text() for page in pdf)
        require(METADATA["title"] in text, "PDF: title missing")
        require(METADATA["author"] in text, "PDF: author missing")
        require("Contents" in text, "PDF: contents missing")
        positions = []
        for section in sections:
            heading = section.heading
            if section.kind == "chapter":
                heading = f"Chapter {section.chapter_number}"
            position = text.find(heading)
            require(position >= 0, f"PDF: missing section {heading}")
            positions.append(position)
        require(positions == sorted(positions), "PDF: sections out of order")
        require(any(page.get_links() for page in pdf), "PDF: no navigation links")
        # The SVG logo is converted to vector paths, not necessarily a raster image.
        require(bool(pdf[0].get_drawings()) or bool(pdf[0].get_images()), "PDF: no title-page logo graphics")


def validate_epub(sections) -> None:
    path = DIST_DIR / f"{BOOK}.epub"
    with zipfile.ZipFile(path) as epub:
        names = set(epub.namelist()
        )
        container = ET.fromstring(epub.read("META-INF/container.xml"))
        rootfile = container.find(".//c:rootfile", NS)
        require(rootfile is not None, "EPUB: missing package rootfile")
        opf_path = rootfile.attrib["full-path"]
        package = ET.fromstring(epub.read(opf_path))
        base = str(Path(opf_path).parent)
        def resource(href):
            return str(Path(base, unquote(urldefrag(href)[0]))) if base != "." else unquote(urldefrag(href)[0])
        titles = [e.text for e in package.findall(".//{http://purl.org/dc/elements/1.1/}title")]
        creators = [e.text for e in package.findall(".//{http://purl.org/dc/elements/1.1/}creator")]
        require(METADATA["title"] in titles, "EPUB: incorrect title metadata")
        require(METADATA["author"] in creators, "EPUB: incorrect author metadata")
        manifest = {item.attrib["id"]: item for item in package.findall(".//o:manifest/o:item", NS)}
        spine = [item.attrib["idref"] for item in package.findall(".//o:spine/o:itemref", NS)]
        require(all(item in manifest for item in spine), "EPUB: invalid spine reference")
        nav = next((item for item in manifest.values() if "nav" in item.attrib.get("properties", "").split()), None)
        require(nav is not None, "EPUB: navigation document missing")
        nav_root = ET.fromstring(epub.read(resource(nav.attrib["href"])))
        toc = next((node for node in nav_root.findall(".//x:nav", NS) if node.attrib.get("{http://www.idpf.org/2007/ops}type") == "toc"), None)
        require(toc is not None, "EPUB: table of contents missing")
        labels = [" ".join(a.itertext()).strip() for a in toc.findall(".//x:a", NS)]
        chapter_labels = [label for label in labels if "Chapter " in label]
        expected = [f"Chapter {s.chapter_number}" for s in sections if s.kind == "chapter"]
        require(len(chapter_labels) == len(expected), "EPUB: wrong chapter count in contents")
        for label, prefix in zip(chapter_labels, expected):
            require(label.startswith(prefix), f"EPUB: wrong contents entry: {label}")
            require(not re.match(r"^\\d+[.\\s]+Chapter ", label), f"EPUB: unwanted numbering: {label}")
        for anchor in toc.findall(".//x:a", NS):
            target = resource(anchor.attrib.get("href", ""))
            require(target in names, f"EPUB: broken contents target {target}")
        xhtml = [resource(item.attrib["href"]) for item in manifest.values() if item.attrib.get("media-type") == "application/xhtml+xml"]
        logo_files = {resource(item.attrib["href"]) for item in manifest.values() if "applied-ml-mark" in item.attrib.get("href", "")}
        require(logo_files and logo_files <= names, "EPUB: logo resource missing")
        require(any("applied-ml-mark" in epub.read(name).decode("utf-8") for name in xhtml if name in names), "EPUB: logo not referenced by content")


def main() -> int:
    sections = expected_sections()
    failures = []
    for name, validate in [("HTML", validate_html), ("PDF", validate_pdf), ("EPUB", validate_epub)]:
        try:
            validate(sections)
            print(f"{name}: PASS")
        except Exception as error:
            failures.append(f"{name}: {error}")
            print(f"{name}: FAIL — {error}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
