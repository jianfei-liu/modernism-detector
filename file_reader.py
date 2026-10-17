"""Read supported text files and remove Project Gutenberg boilerplate."""

import re
from io import BytesIO
from pathlib import Path


def read_uploaded_file(name: str, data: bytes) -> str:
    """Read an uploaded plain-text or PDF file."""
    extension = Path(name).suffix.lower()
    if extension == ".txt":
        return data.decode("utf-8", errors="replace")
    if extension == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError("Please upload a .txt or .pdf file.")


def strip_gutenberg_boilerplate(text: str) -> str:
    """Keep the text between Gutenberg's start and end markers, when present."""
    start = re.search(r"\*\*\* ?START OF.*?\*\*\*", text)
    end = re.search(r"\*\*\* ?END OF", text)
    if start and end and start.end() <= end.start():
        return text[start.end() : end.start()]
    return text
