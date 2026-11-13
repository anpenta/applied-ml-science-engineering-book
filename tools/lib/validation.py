"""Validate generated PDF, EPUB, and HTML editions."""

import posixpath
import zipfile
from pathlib import Path
from urllib.parse import unquote, urldefrag
from xml.etree import ElementTree as ET

from playwright.sync_api import Page, sync_playwright
from pypdf import PdfReader

from tools.lib.build import get_html_page_filename
from tools.lib.definitions import BOOK, DIST_DIR, METADATA, ROOT, BookSection

NS = {
    "c": "urn:oasis:names:tc:opendocument:xmlns:container",
    "dc": "http://purl.org/dc/elements/1.1/",
    "o": "http://www.idpf.org/2007/opf",
    "x": "http://www.w3.org/1999/xhtml",
}
EPUB_TYPE = "{http://www.idpf.org/2007/ops}type"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_html_layout(page: Page, path: Path, width: int) -> None:
    page.goto(path.as_uri())
    has_no_overflow = page.evaluate(
        "document.documentElement.scrollWidth <= window.innerWidth"
    )
    require(has_no_overflow, f"Horizontal overflow on {path.name} at {width}px")


def check_html_home(page: Page, filenames: list[str], headings: list[str]) -> None:
    landing = page.locator(".book-landing-title")
    title = landing.get_by_role("heading", level=1)
    require(title.count() == 1 and title.inner_text() == METADATA["title"],
            "Incorrect landing title")
    require(METADATA["author"] in landing.inner_text(), "Landing author missing")
    logo = landing.locator(".book-cover-mark img")
    require(logo.count() == 1 and logo.evaluate("(img) => img.naturalWidth > 0"),
            "Landing logo did not load")
    require(page.get_by_role("heading", name="Contents", exact=True).count() == 1,
            "Contents heading missing")
    links = page.locator(".book-contents a")
    require(links.all_inner_texts() == headings, "Incorrect contents labels or order")
    hrefs = links.evaluate_all("(links) => links.map(link => link.getAttribute('href'))")
    require(hrefs == filenames, "Incorrect contents destinations or order")


def check_html_navigation(page: Page, filenames: list[str], headings: list[str],
                          chapter: str, screenshot: Path) -> None:
    home = (DIST_DIR / "index.html").as_uri()
    toc_link = page.locator(".book-contents a").nth(filenames.index(chapter))
    toc_link.click()
    page.wait_for_url((DIST_DIR / chapter).as_uri())
    page.screenshot(path=screenshot, full_page=True)

    nav = page.get_by_role("navigation", name="Book navigation")
    nav.get_by_role("link", name="Contents", exact=True).click()
    page.wait_for_url(home)
    for filename, heading in zip(filenames, headings, strict=True):
        nav.get_by_role("link", name="Next", exact=True).click()
        page.wait_for_url((DIST_DIR / filename).as_uri())
        require(page.get_by_role("heading", name=heading, level=2, exact=True).count() == 1,
                f"Incorrect heading on {filename}")
    require(nav.get_by_role("link", name="Next", exact=True).count() == 0,
            "Final page has an active Next link")

    for filename in reversed(["index.html", *filenames[:-1]]):
        nav.get_by_role("link", name="Previous", exact=True).click()
        page.wait_for_url((DIST_DIR / filename).as_uri())
    require(nav.get_by_role("link", name="Previous", exact=True).count() == 0,
            "Homepage has an active Previous link")


def validate_html(*, sections: list[BookSection]) -> None:
    filenames = [get_html_page_filename(section) for section in sections]
    headings = [
        f"Chapter {section.chapter_number}: {section.heading}"
        if section.kind == "chapter" else section.heading
        for section in sections
    ]
    expected = {"index.html", *filenames}
    actual = {path.name for path in DIST_DIR.glob("*.html")}
    require(actual == expected,
            f"Missing pages: {sorted(expected - actual)}; unexpected pages: {sorted(actual - expected)}")

    chapter = next(get_html_page_filename(section) for section in sections
                   if section.kind == "chapter")
    screenshots = ROOT / "html-screenshots"
    screenshots.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for width, label in [(1280, "desktop"), (390, "mobile")]:
                page = browser.new_page(viewport={"width": width, "height": 900})
                page.set_default_timeout(5000)
                for filename in filenames:
                    check_html_layout(page, DIST_DIR / filename, width)
                check_html_layout(page, DIST_DIR / "index.html", width)
                check_html_home(page, filenames, headings)
                page.screenshot(path=screenshots / f"home-{label}.png", full_page=True)
                page.locator(".book-contents").screenshot(
                    path=screenshots / f"contents-{label}.png"
                )
                check_html_navigation(page, filenames, headings, chapter,
                                      screenshots / f"chapter-{label}.png")
                page.close()
        finally:
            browser.close()


def check_pdf_outline(pdf: PdfReader, sections: list[BookSection]) -> None:
    headings = ["Contents", *(
        f"{section.chapter_number} {section.heading}"
        if section.kind == "chapter" else section.heading
        for section in sections
    )]
    bookmarks = iter(item for item in pdf.outline if not isinstance(item, list))
    for heading in headings:
        bookmark = next((item for item in bookmarks if item.title == heading), None)
        require(bookmark is not None, f"Missing or out-of-order bookmark: {heading}")
        page_number = pdf.get_destination_page_number(bookmark)
        require(page_number is not None and 0 <= page_number < len(pdf.pages),
                f"Invalid bookmark destination: {heading}")


def validate_pdf(*, sections: list[BookSection]) -> None:
    pdf = PdfReader(DIST_DIR / f"{BOOK}.pdf")
    require(len(pdf.pages) > 1, "Empty document")
    require(pdf.metadata.title == METADATA["title"], "Incorrect title metadata")
    require(pdf.metadata.author == METADATA["author"], "Incorrect author metadata")
    cover = pdf.pages[0]
    text = " ".join((cover.extract_text() or "").split())
    for value in (METADATA["title"], METADATA["author"]):
        require(value in text, f"Missing from title page: {value}")
    resources = cover["/Resources"].get("/XObject")
    require(resources and any(
        obj.get_object().get("/Subtype") in {"/Form", "/Image"}
        for obj in resources.get_object().values()
    ), "Title-page logo graphic missing")

    check_pdf_outline(pdf, sections)
    links = [
        ref.get_object()
        for page in pdf.pages
        for ref in page.get("/Annots", [])
        if ref.get_object().get("/Subtype") == "/Link"
    ]
    require(any("/Dest" in link or link.get("/A", {}).get("/S") == "/GoTo"
                for link in links), "Internal navigation links missing")
    require(any(link.get("/A", {}).get("/S") == "/URI" for link in links),
            "External links missing")


def epub_resource(document: str, href: str) -> str:
    path = unquote(urldefrag(href)[0])
    return posixpath.normpath(posixpath.join(posixpath.dirname(document), path))


def check_epub_navigation(epub: zipfile.ZipFile, nav_path: str,
                          sections: list[BookSection]) -> list[str]:
    document = ET.fromstring(epub.read(nav_path))
    toc = next((node for node in document.findall(".//x:nav", NS)
                if node.get(EPUB_TYPE) == "toc"), None)
    require(toc is not None, "Contents navigation missing")
    require(toc.findtext("x:h1", namespaces=NS) == "Contents",
            "Contents heading missing")
    entries = toc.findall("x:ol/x:li/x:a", NS)
    expected = [
        f"Chapter {section.chapter_number} — {section.heading}"
        if section.kind == "chapter" else section.heading
        for section in sections
    ]
    actual = [" ".join("".join(entry.itertext()).split()) for entry in entries]
    require(actual == expected, f"Incorrect contents labels or order: {actual!r}")
    return [epub_resource(nav_path, entry.attrib["href"]) for entry in entries]


def validate_epub(*, sections: list[BookSection]) -> None:
    with zipfile.ZipFile(DIST_DIR / f"{BOOK}.epub") as epub:
        container = ET.fromstring(epub.read("META-INF/container.xml"))
        rootfile = container.find(".//c:rootfile", NS)
        require(rootfile is not None, "Package rootfile missing")
        opf_path = rootfile.attrib["full-path"]
        package = ET.fromstring(epub.read(opf_path))
        for tag, key in (("title", "title"), ("creator", "author"), ("language", "lang")):
            value = package.findtext(f"o:metadata/dc:{tag}", default="", namespaces=NS)
            require(value.strip() == METADATA[key], f"Incorrect {tag} metadata: {value!r}")

        items = package.findall("o:manifest/o:item", NS)
        paths = {item.attrib["id"]: epub_resource(opf_path, item.attrib["href"])
                 for item in items}
        nav = next((item for item in items if "nav" in item.get("properties", "").split()),
                   None)
        require(nav is not None, "Navigation document missing")
        nav_path = paths[nav.attrib["id"]]
        toc_paths = check_epub_navigation(epub, nav_path, sections)
        spine = [paths[item.attrib["idref"]] for item in package.findall("o:spine/o:itemref", NS)]
        require(spine[1:] == [nav_path, *toc_paths],
                "Reading order must be title page, contents, then manuscript sections")

        cover = ET.fromstring(epub.read(spine[0]))
        title_page = cover.find(f".//x:section[@{EPUB_TYPE}='titlepage']", NS)
        require(title_page is not None, "Title page missing from start of reading order")
        logo = title_page.find(".//x:img", NS)
        require(logo is not None, "Title-page logo missing")
        logo_path = epub_resource(spine[0], logo.attrib["src"])
        require(epub.read(logo_path) == (ROOT / "assets/applied-ml-mark.png").read_bytes(),
                f"Incorrect title-page logo: {logo_path}")
