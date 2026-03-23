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


def chunk_text(text: str, strategy: str, size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []
    if strategy == "fixed":
        step = size - overlap
        for i in range(0, len(words), step):
            chunk = " ".join(words[i : i + size])
            if chunk:
                chunks.append(chunk)
    return chunks
