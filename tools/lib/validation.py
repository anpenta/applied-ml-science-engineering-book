"""Validate generated PDF, EPUB, and HTML editions."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from urllib.parse import unquote, urldefrag
from xml.etree import ElementTree as ET

from pypdf import PdfReader
from playwright.sync_api import sync_playwright

from tools.lib.definitions import DIST_DIR, METADATA
from tools.lib.build import get_html_page_filename, iter_book_sections

BOOK = "science-and-engineering-of-applied-machine-learning"
NS = {
    "c": "urn:oasis:names:tc:opendocument:xmlns:container",
    "o": "http://www.idpf.org/2007/opf",
    "x": "http://www.w3.org/1999/xhtml",
}


def check_requirement(*, condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def get_expected_sections():
    return list(iter_book_sections())


def validate_html(*, sections) -> None:
    pages = [get_html_page_filename(section) for section in sections]
    screenshots = DIST_DIR.parent / "html-screenshots"
    screenshots.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for width, label in [(1280, "desktop"), (390, "mobile")]:
                page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
                page.goto((DIST_DIR / "index.html").as_uri())
                check_requirement(condition=page.locator(".book-landing-title h1").count() == 1, message="HTML: expected one landing title")
                check_requirement(condition=page.locator(".book-landing-title h1").inner_text().strip() == METADATA["title"], message="HTML: incorrect title")
                check_requirement(condition=METADATA["author"] in page.locator(".book-landing-title").inner_text(), message="HTML: author missing")
                logo = page.locator(".book-cover-mark img")
                check_requirement(condition=logo.count() == 1 and logo.evaluate("(img) => img.complete && img.naturalWidth > 0"), message="HTML: logo not loaded")
                hrefs = page.locator(".book-contents a").evaluate_all("(links) => links.map(link => link.getAttribute('href'))")
                check_requirement(condition=hrefs == pages, message="HTML: contents order differs from manuscript")
                page.screenshot(path=str(screenshots / f"home-{label}.png"), full_page=True)
                page.locator(".book-contents").screenshot(path=str(screenshots / f"contents-{label}.png"))
                for index, filename in enumerate(pages):
                    page.goto((DIST_DIR / filename).as_uri())
                    expected = sections[index]
                    heading = f"Chapter {expected.chapter_number}: {expected.heading}" if expected.kind == "chapter" else expected.heading
                    check_requirement(condition=page.get_by_role("heading", name=heading, exact=True).count() == 1, message=f"HTML: wrong heading on {filename}")
                    nav = page.locator("nav.book-navigation")
                    check_requirement(condition=nav.count() == 1, message=f"HTML: missing navigation on {filename}")
                    previous = "index.html" if index == 0 else pages[index - 1]
                    check_requirement(condition=nav.get_by_text("Previous", exact=True).get_attribute("href") == previous, message=f"HTML: wrong Previous on {filename}")
                    next_link = nav.get_by_role("link", name="Next")
                    if index + 1 < len(pages):
                        check_requirement(condition=next_link.get_attribute("href") == pages[index + 1], message=f"HTML: wrong Next on {filename}")
                    else:
                        check_requirement(condition=next_link.count() == 0, message="HTML: final page has an active Next link")
                representative = next((p for p, s in zip(pages, sections) if s.kind == "chapter"), pages[0])
                page.goto((DIST_DIR / representative).as_uri())
                page.screenshot(path=str(screenshots / f"chapter-{label}.png"), full_page=True)
                page.close()
        finally:
            browser.close()


def validate_pdf(*, sections) -> None:
    path = DIST_DIR / f"{BOOK}.pdf"
    pdf = PdfReader(path)
    check_requirement(condition=len(pdf.pages) > 1, message="PDF: empty document")
    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    check_requirement(condition=METADATA["title"] in text, message="PDF: title missing")
    check_requirement(condition=METADATA["author"] in text, message="PDF: author missing")
    check_requirement(condition="Contents" in text, message="PDF: contents missing")
    bookmarks = []

    def collect_bookmarks(*, items):
        for item in items:
            if isinstance(item, list):
                collect_bookmarks(items=item)
            else:
                bookmarks.append(item.title)

    collect_bookmarks(items=pdf.outline)
    expected = [
        section.heading if section.kind != "chapter"
        else f"{section.chapter_number} {section.heading}"
        for section in sections
    ]
    bookmark_index = 0
    for heading in expected:
        while bookmark_index < len(bookmarks) and bookmarks[bookmark_index] != heading:
            bookmark_index += 1
        check_requirement(
            condition=bookmark_index < len(bookmarks),
            message=f"PDF: missing or out-of-order bookmark {heading}",
        )
        bookmark_index += 1
    check_requirement(
        condition=any("/Annots" in page for page in pdf.pages),
        message="PDF: no navigation links",
    )
    # The SVG logo is rendered as vector paths; inspect the title page's
    # drawing commands rather than looking only for raster images.
    contents = pdf.pages[0].get_contents()
    streams = contents if isinstance(contents, list) else [contents] if contents else []
    drawing_commands = b"\n".join(stream.get_object().get_data() for stream in streams)
    check_requirement(
        condition=bool(re.search(rb"(?<!\S)(?:m|l|c|re)(?!\S)", drawing_commands)),
        message="PDF: no title-page vector graphics",
    )


def validate_epub(*, sections) -> None:
    path = DIST_DIR / f"{BOOK}.epub"
    with zipfile.ZipFile(path) as epub:
        names = set(epub.namelist()
        )
        container = ET.fromstring(epub.read("META-INF/container.xml"))
        rootfile = container.find(".//c:rootfile", NS)
        check_requirement(condition=rootfile is not None, message="EPUB: missing package rootfile")
        opf_path = rootfile.attrib["full-path"]
        package = ET.fromstring(epub.read(opf_path))
        base = str(Path(opf_path).parent)
        def resolve_resource_path(*, href: str) -> str:
            return str(Path(base, unquote(urldefrag(href)[0]))) if base != "." else unquote(urldefrag(href)[0])
        titles = [e.text for e in package.findall(".//{http://purl.org/dc/elements/1.1/}title")]
        creators = [e.text for e in package.findall(".//{http://purl.org/dc/elements/1.1/}creator")]
        check_requirement(condition=any(METADATA["title"] in (title or "") for title in titles), message="EPUB: incorrect title metadata")
        check_requirement(condition=METADATA["author"] in creators, message="EPUB: incorrect author metadata")
        manifest = {item.attrib["id"]: item for item in package.findall(".//o:manifest/o:item", NS)}
        spine = [item.attrib["idref"] for item in package.findall(".//o:spine/o:itemref", NS)]
        check_requirement(condition=all(item in manifest for item in spine), message="EPUB: invalid spine reference")
        nav = next((item for item in manifest.values() if "nav" in item.attrib.get("properties", "").split()), None)
        check_requirement(condition=nav is not None, message="EPUB: navigation document missing")
        nav_root = ET.fromstring(epub.read(resolve_resource_path(href=nav.attrib["href"])))
        toc = next((node for node in nav_root.findall(".//x:nav", NS) if node.attrib.get("{http://www.idpf.org/2007/ops}type") == "toc"), None)
        check_requirement(condition=toc is not None, message="EPUB: table of contents missing")
        labels = [" ".join(a.itertext()).strip() for a in toc.findall(".//x:a", NS)]
        chapter_labels = [label for label in labels if "Chapter " in label]
        expected = [f"Chapter {s.chapter_number}" for s in sections if s.kind == "chapter"]
        check_requirement(condition=len(chapter_labels) == len(expected), message="EPUB: wrong chapter count in contents")
        for label, prefix in zip(chapter_labels, expected):
            check_requirement(condition=label.startswith(prefix), message=f"EPUB: wrong contents entry: {label}")
            check_requirement(condition=not re.match(r"^\\d+[.\\s]+Chapter ", label), message=f"EPUB: unwanted numbering: {label}")
        for anchor in toc.findall(".//x:a", NS):
            target = resolve_resource_path(href=anchor.attrib.get("href", ""))
            check_requirement(condition=target in names, message=f"EPUB: broken contents target {target}")
        xhtml = [resolve_resource_path(href=item.attrib["href"]) for item in manifest.values() if item.attrib.get("media-type") == "application/xhtml+xml"]
        logo_files = {resolve_resource_path(href=item.attrib["href"]) for item in manifest.values() if "applied-ml-mark" in item.attrib.get("href", "")}
        check_requirement(condition=logo_files and logo_files <= names, message="EPUB: logo resource missing")
        check_requirement(condition=any("applied-ml-mark" in epub.read(name).decode("utf-8") for name in xhtml if name in names), message="EPUB: logo not referenced by content")


