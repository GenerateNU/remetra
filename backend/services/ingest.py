from typing import Any

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from models.knowledge_chunk import KnowledgeChunk
from repositories.chunk_repository import ChunkRepository
from services.pdfconvert import chunk_text, convert

# Heavy model — loaded once at module level intentionally to avoid per-request cost
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings using all-MiniLM-L6-v2."""
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def ingest_pdf(file, source: str) -> list[dict[str, Any]]:
    """Parse, chunk, and embed a PDF. Returns chunk dicts ready to persist."""
    full_text = convert(file)
    chunks = chunk_text(full_text)
    vectors = embed(chunks)

    return [
        {
            "content": text,
            "embedding": vector,
            "source": source,
        }
        for text, vector in zip(chunks, vectors)
    ]


def similarity_search(input: str, db: Session, n: int = 5) -> list[KnowledgeChunk]:
    """Return the top-n most similar chunks for a given query string."""
    chunk_repo = ChunkRepository()
    embed_query = embed([input])[0]
    return chunk_repo.get_top_chunks(db, embed_query, n)
