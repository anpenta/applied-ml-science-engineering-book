"""Shared book definitions and configuration."""

import json
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[2]
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

class BookSection(NamedTuple):
    kind: str
    heading: str
    body: str
    chapter_number: int | None

