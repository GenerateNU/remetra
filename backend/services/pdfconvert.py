import re

from pypdf import PdfReader


def convert(data) -> str:
    """Extract and concatenate text from all pages of a PDF."""
    reader = PdfReader(data)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    return "\n".join(pages_text)


def chunk_text(text: str, strategy: str = "fixed", size: int = 512, overlap: int = 50, sentence_group: int = 3) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []

    if strategy == "fixed":
        step = size - overlap
        for i in range(0, len(words), step):
            chunk = " ".join(words[i : i + size])
            if chunk:
                chunks.append(chunk)

    elif strategy == "semantic":
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks.extend(paragraphs)

    elif strategy == "sentence":  # pragma: no cover
        sentences = re.split(r"(?<=[.!?]) +", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        for i in range(0, len(sentences), sentence_group):
            chunk = " ".join(sentences[i : i + sentence_group])
            chunks.append(chunk)

    return chunks
