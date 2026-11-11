#!/usr/bin/env python3
"""Build the PDF, EPUB, and HTML editions of the canonical book."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
DIST_DIR = ROOT / "dist"

FRONT_MATTER = [
    ("copyright-and-licence.md", "Copyright and license"),
    ("dedication.md", "Dedication"),
    ("acknowledgements.md", "Acknowledgments"),
    ("use-of-ai-tools.md", "Use of AI tools"),
]

CHAPTER_FILES = [
    "01-before-machine-learning.md",
    "02-causal-effects.md",
    "03-understanding-data.md",
    "04-designing-experiments.md",
    "05-using-model-scores.md",
    "06-choosing-model-complexity.md",
    "07-interpreting-model-explanations.md",
    "08-from-experiment-to-system.md",
    "09-engineering-rigor-and-risk.md",
    "10-testing-operational-feasibility.md",
    "11-diagnosing-change-in-production.md",
    "12-technical-judgment-in-teams.md",
]

def validate_chapter_coverage() -> None:
    chapter_directory = MANUSCRIPT / "chapters"
    listed_chapters = CHAPTER_FILES
    available_chapters = {path.name for path in chapter_directory.glob("*.md")}

    duplicates = sorted(
        filename
        for filename, count in Counter(listed_chapters).items()
        if count > 1
    )
    missing = sorted(available_chapters - set(listed_chapters))
    unavailable = sorted(set(listed_chapters) - available_chapters)

    problems = []
    if duplicates:
        problems.append(f"listed more than once: {', '.join(duplicates)}")
    chapter_numbers = [
        int(filename[:2])
        for filename in listed_chapters
        if filename[:2].isdigit()
    ]
    if len(chapter_numbers) != len(listed_chapters):
        problems.append("chapter filenames must begin with a two-digit number")
    elif chapter_numbers != list(range(1, len(listed_chapters) + 1)):
        problems.append("chapters must be listed once in consecutive numeric order")
    if missing:
        problems.append(f"not included in the book: {', '.join(missing)}")
    if unavailable:
        problems.append(f"files do not exist: {', '.join(unavailable)}")
    if not available_chapters:
        problems.append(f"no chapter files found in {chapter_directory}")
    if problems:
        raise ValueError("Chapter list is inconsistent: " + "; ".join(problems))


def read_markdown(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Required manuscript file is missing: {path}")
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

    for filename in CHAPTER_FILES:
        chapter_number = int(filename[:2])
        body = read_markdown(MANUSCRIPT / "chapters" / filename)
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

    return "\n\n".join(sections) + "\n"


def build_markdown_source() -> str:
    """Render the canonical book sections as Markdown for EPUB and HTML."""
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


def run_pandoc(source: str, output: Path, *, edition: str) -> None:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise RuntimeError("Pandoc is required. Install Pandoc before building.")

    if edition == "pdf":
        convert_book_mark_to_pdf()

    with tempfile.TemporaryDirectory(prefix="book-") as temporary_directory:
        source_path = Path(temporary_directory) / "book.md"
        source_path.write_text(source, encoding="utf-8")
        subprocess.run(
            [
                pandoc,
                f"--defaults={ROOT / 'defaults' / f'{edition}.yaml'}",
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
    return f"{section.kind}.html" if section.kind != "front-matter" else (
        re.sub(r"[^a-z0-9]+", "-", section.heading.lower()).strip("-") + ".html"
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
    contents = "<ol>" + "\n".join(toc_items) + "</ol>"

    landing = (
        "# The Science and Engineering of Applied Machine Learning\n\n"
        "Andreas Pentaliotis\n\n"
        "## Contents\n\n"
        + contents + "\n"
    )
    run_pandoc(source=landing, output=DIST_DIR / "index.html", edition="html")

    for index, (filename, section) in enumerate(pages):
        title = (
            f"Chapter {section.chapter_number}: {section.heading}"
            if section.kind == "chapter" else section.heading
        )
        previous = pages[index - 1][0] if index else "index.html"
        navigation_links = [
            f'<a href="{previous}">Previous</a>',
            '<a href="index.html">Contents</a>',
        ]
        if index + 1 < len(pages):
            following = pages[index + 1][0]
            navigation_links.append(f'<a href="{following}">Next</a>')
        navigation = (
            '<nav class="book-navigation" aria-label="Book navigation">'
            + "".join(navigation_links)
            + "</nav>"
        )
        source = f"# {title}\n\n{section.body}\n\n{navigation}\n"
        run_pandoc(source=source, output=DIST_DIR / filename, edition="html")

    for filename in ["index.html", *(name for name, _ in pages)]:
        output_file = DIST_DIR / filename
        if not output_file.is_file() or output_file.stat().st_size == 0:
            raise RuntimeError(f"Missing or empty HTML page: {filename}")
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

    validate_chapter_coverage()
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
            source=build_markdown_source(), output=epub_path, edition="epub"
        )

    if args.format in ("html", "all"):
        build_html()

    print(f"Publication files written to {DIST_DIR}")


if __name__ == "__main__":
    main()
