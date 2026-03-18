from pypdf import PdfReader


def convert(data):
    reader = PdfReader(data)
    page = reader.pages[0]
    text = page.extract_text()

    return text


def chunk_text(text: str, size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []
    step = size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + size])
        if chunk:
            chunks.append(chunk)
    return chunks
