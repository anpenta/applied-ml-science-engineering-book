#!/usr/bin/env python3
"""Build the PDF, EPUB, and HTML editions of the canonical book."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
DIST_DIR = ROOT / "dist"
METADATA = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))

FRONT_MATTER = [
    ("copyright-and-licence.md", "Copyright and license"),
    ("dedication.md", "Dedication"),
    ("acknowledgements.md", "Acknowledgments"),
    ("use-of-ai-tools.md", "Use of AI tools"),
]

BACK_MATTER = [
    ("feedback-and-support.md", "Feedback and support"),
]

def chapter_files() -> list[Path]:
    """Find numbered chapters in order and reject missing or repeated numbers."""
    directory = MANUSCRIPT / "chapters"
    files = sorted(directory.glob("*.md"))
    numbers: list[int] = []
    for path in files:
        match = re.fullmatch(r"(\d{2})-.+\.md", path.name)
        if match is None:
            raise ValueError(f"Chapter filename must start with NN-: {path.name}")
        numbers.append(int(match.group(1)))
    if not files or numbers != list(range(1, len(files) + 1)):
        raise ValueError(
            "Chapter files must be numbered consecutively from 01, without duplicates"
        )
    return files


def read_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        pattern=r"\A---\s*\n.*?\n---\s*\n",
        repl="",
        string=text,
        count=1,
        flags=re.S,
    )
    return text.strip()


def remove_document_title(text: str) -> str:
    return re.sub(pattern=r"\A#\s+.+\n+", repl="", string=text, count=1)


def escape_tex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in value)


def extract_chapter_title(text: str) -> str:
    match = re.search(pattern=r"\A#\s+(.+)", string=text)
    if not match:
        raise ValueError("A chapter is missing its level-one title heading.")
    return match.group(1).strip()


class BookSection(NamedTuple):
    kind: str
    heading: str
    body: str
    chapter_number: int | None


def iter_book_sections() -> Iterator[BookSection]:
    """Yield the complete book in its canonical publication order."""
    for filename, heading in FRONT_MATTER:
        body = remove_document_title(
            read_markdown(MANUSCRIPT / "front-matter" / filename)
        )
        yield BookSection(
            kind="front-matter", heading=heading, body=body, chapter_number=None
        )

    introduction = remove_document_title(
        read_markdown(MANUSCRIPT / "introduction.md")
    )
    yield BookSection(
        kind="introduction",
        heading="Introduction",
        body=introduction,
        chapter_number=None,
    )

    for path in chapter_files():
        chapter_number = int(path.name[:2])
        body = read_markdown(path)
        heading = extract_chapter_title(body)
        yield BookSection(
            kind="chapter",
            heading=heading,
            body=remove_document_title(body),
            chapter_number=chapter_number,
        )

    conclusion = remove_document_title(
        read_markdown(MANUSCRIPT / "conclusion.md")
    )
    yield BookSection(
        kind="conclusion",
        heading="Conclusion",
        body=conclusion,
        chapter_number=None,
    )

    for filename, heading in BACK_MATTER:
        body = remove_document_title(
            read_markdown(MANUSCRIPT / "back-matter" / filename)
        )
        yield BookSection(
            kind="back-matter", heading=heading, body=body, chapter_number=None
        )


def build_pdf_source() -> str:
    sections = [r"\frontmatter", ""]

    for section in iter_book_sections():
        if section.kind == "front-matter":
            escaped_heading = escape_tex(section.heading)
            sections.extend(
                [
                    rf"\chapter*{{{escaped_heading}}}",
                    rf"\addcontentsline{{toc}}{{chapter}}{{{escaped_heading}}}",
                    "",
                    section.body,
                    r"\clearpage",
                    "",
                ]
            )
        elif section.kind == "introduction":
            sections.extend(
                [
                    r"\tableofcontents",
                    "",
                    r"\mainmatter",
                    r"\setcounter{secnumdepth}{0}",
                    r"\chapter*{Introduction}",
                    r"\addtocontents{toc}{\protect\vspace{\baselineskip}}",
                    r"\addcontentsline{toc}{chapter}{Introduction}",
                    r"\markboth{Introduction}{}",
                    "",
                    section.body,
                    "",
                    r"\setcounter{secnumdepth}{3}",
                    "",
                ]
            )
        elif section.kind == "chapter":
            sections.extend(
                [
                    rf"\chapter{{{escape_tex(section.heading)}}}",
                    "",
                    section.body,
                    "",
                ]
            )
        elif section.kind == "conclusion":
            sections.extend(
                [
                    r"\backmatter",
                    r"\chapter*{Conclusion}",
                    r"\addcontentsline{toc}{chapter}{Conclusion}",
                    r"\setcounter{secnumdepth}{0}",
                    "",
                    section.body,
                    "",
                ]
            )
        elif section.kind == "back-matter":
            escaped_heading = escape_tex(section.heading)
            sections.extend(
                [
                    rf"\chapter*{{{escaped_heading}}}",
                    r"\addtocontents{toc}{\protect\vspace{\baselineskip}}",
                    rf"\addcontentsline{{toc}}{{chapter}}{{{escaped_heading}}}",
                    "",
                    section.body,
                    "",
                ]
            )

    return "\n\n".join(sections) + "\n"


def build_markdown_source() -> str:
    """Render the canonical book sections as Markdown for EPUB."""
    sections: list[str] = []
    for section in iter_book_sections():
        if section.kind == "chapter":
            markdown_heading = (
                f"# Chapter {section.chapter_number} — {section.heading}"
            )
        else:
            markdown_heading = f"# {section.heading}"
        sections.extend([markdown_heading, "", section.body, ""])
    return "\n".join(sections)



def build_epub_source() -> str:
    """Provide a native Pandoc title page with a parsed image and plain book text."""
    title = METADATA["title"]
    title_metadata = (
        "---\n"
        f'title: "![](assets/applied-ml-mark.png) {title}"\n'
        "---\n\n"
    )
    return title_metadata + build_markdown_source()


def convert_book_mark_to_pdf() -> None:
    """Convert the SVG book mark for inclusion in the PDF edition."""
    logo_directory = DIST_DIR / "assets"
    logo_directory.mkdir(parents=True, exist_ok=True)
    logo_path = logo_directory / "applied-ml-mark.pdf"

    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise RuntimeError(
            "rsvg-convert is required to prepare the vector book mark for PDF."
        )

    subprocess.run(
        [
            converter,
            "--format=pdf",
            "--output",
            str(logo_path),
            str(ROOT / "assets" / "applied-ml-mark.svg"),
        ],
        cwd=ROOT,
        check=True,
    )


def build_homepage_metadata() -> str:
    """Generate homepage metadata from the publication records."""
    fields = (
        ("citation_title", METADATA["title"]),
        ("citation_author", METADATA["author"]),
        ("citation_publication_date", METADATA["date_released"].replace("-", "/")),
    )
    tags = [
        f'<meta name="{name}" content="{html.escape(value, quote=True)}" />'
        for name, value in fields
    ]
    canonical = html.escape(METADATA["url"], quote=True)
    tags.append(f'<link rel="canonical" href="{canonical}" />')
    return "\n".join(tags) + "\n"


def run_pandoc(source: str, output: Path, *, edition: str, homepage: bool = False) -> None:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise RuntimeError("Pandoc is required. Install Pandoc before building.")

    if edition == "pdf":
        convert_book_mark_to_pdf()

    with tempfile.TemporaryDirectory(prefix="book-") as temporary_directory:
        source_path = Path(temporary_directory) / "book.md"
        source_path.write_text(source, encoding="utf-8")
        if homepage:
            homepage_header = Path(temporary_directory) / "homepage-metadata.html"
            homepage_header.write_text(build_homepage_metadata(), encoding="utf-8")
        subprocess.run(
            [
                pandoc,
                f"--defaults={ROOT / 'defaults' / f'{edition}.yaml'}",
                f"--metadata-file={ROOT / 'metadata.json'}",
                *([f"--include-in-header={homepage_header}"] if homepage else []),
                "--output",
                str(output),
                str(source_path),
            ],
            cwd=ROOT,
            check=True,
        )


def get_html_page_filename(section: BookSection) -> str:
    if section.kind == "chapter":
        return f"chapter-{section.chapter_number:02d}.html"
    if section.kind in ("front-matter", "back-matter"):
        slug = re.sub(r"[^a-z0-9]+", "-", section.heading.lower()).strip("-")
        return f"{slug}.html"
    return f"{section.kind}.html"


def build_html_navigation(
    previous: str | None, following: str | None, *, on_contents: bool = False
) -> str:
    """Render consistent navigation with inaccessible endpoints disabled."""
    def link(label: str, destination: str | None) -> str:
        if destination is None:
            return f'<span class="disabled" aria-disabled="true">{label}</span>'
        return f'<a href="{destination}">{label}</a>'

    controls = [
        link("Previous", previous),
        link("Contents", None if on_contents else "index.html"),
        link("Next", following),
    ]
    return (
        '<nav class="book-navigation" aria-label="Book navigation">'
        + "".join(controls)
        + "</nav>"
    )


def build_html() -> None:
    """Create a navigable HTML site, one document per book section."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(DIST_DIR / "assets", ignore_errors=True)
    shutil.copytree(src=ROOT / "assets", dst=DIST_DIR / "assets")

    sections = list(iter_book_sections())
    pages = [(get_html_page_filename(section), section) for section in sections]
    toc_items = []
    for filename, section in pages:
        label = (
            f"Chapter {section.chapter_number}: {section.heading}"
            if section.kind == "chapter" else section.heading
        )
        toc_items.append(
            f'<li><a href="{filename}">{html.escape(label)}</a></li>'
        )
    contents = '<ul class="book-contents">' + "\n".join(toc_items) + "</ul>"

    landing = (
        '<div class="book-landing-title">\n'
        '<p class="book-cover-mark"><img src="assets/applied-ml-mark.svg" '
        'alt="" width="265"></p>\n'
        f"<h1>{html.escape(METADATA['title'])}</h1>\n"
        f"<p>{html.escape(METADATA['author'])}</p>\n"
        "</div>\n\n"
        "## Contents\n\n"
        + contents + "\n\n"
        + build_html_navigation(None, pages[0][0], on_contents=True) + "\n"
    )
    run_pandoc(source=landing, output=DIST_DIR / "index.html", edition="html", homepage=True)

    for index, (filename, section) in enumerate(pages):
        title = (
            f"Chapter {section.chapter_number}: {section.heading}"
            if section.kind == "chapter" else section.heading
        )
        previous = pages[index - 1][0] if index else "index.html"
        following = pages[index + 1][0] if index + 1 < len(pages) else None
        navigation = build_html_navigation(previous, following)
        source = f"# {title}\n\n{section.body}\n\n{navigation}\n"
        run_pandoc(source=source, output=DIST_DIR / filename, edition="html")

    print(f"HTML edition written to {DIST_DIR} ({len(pages) + 1} pages)")


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
