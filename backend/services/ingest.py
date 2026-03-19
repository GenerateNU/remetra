from typing import Any

from services.pdfconvert import chunk_text, convert
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from models.knowledge_chunk import KnowledgeChunk
from repositories.chunk_repository import ChunkRepository

# all-MiniLM-L6-v2 as the embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chunkRepo = ChunkRepository()


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings using all-MiniLM-L6-v2."""
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def ingest_pdf(db: Session, file, source: str) -> list[dict[str, Any]]:
    # 1. Parse
    full_text = convert(file)

    # 2. Chunk
    chunks = chunk_text(full_text)

    # 3. Embed (batch for efficiency)
    vectors = embed(chunks)

    # 4. Pair each chunk with its embedding and source
    return [
        {
            "content": text,
            "chunk_index": idx,
            "embedding": vector,
            "source": source,
        }
        for idx, (text, vector) in enumerate(zip(chunks, vectors))
    ]

    # Got to add below to a different file as it edits the DB
    """
    # 4. Persist
    doc = KnowledgeChunk(source=source)
    db.add(doc)
    db.flush()   # get doc.id before inserting chunks

    for idx, (text, vector) in enumerate(zip(chunks, vectors)):
        db.add(KnowledgeChunk(
            document_id = doc.id,
            content     = text,
            chunk_index = idx,
            embedding   = vector,
            source      = source,
        ))

    db.commit()
    db.refresh(doc)
    return doc
    """


def similarity_search(input: str, db: Session, n: int = 5) -> list[KnowledgeChunk]:
    embedQuery = embed([input])[0]
    return chunkRepo.get_top_chunks(db, embedQuery, n)
