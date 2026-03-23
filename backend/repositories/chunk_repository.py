import logging
<<<<<<< HEAD
from typing import Any
=======
from typing import Any, List
>>>>>>> 936ac18 (feat: created script to run different strategies and edited existing files to check strategy string. Added create_chunks and clear_chunks to chunk repository. Haven't tested yet)

from sqlalchemy.orm import Session

from models.knowledge_chunk import KnowledgeChunk

logger = logging.getLogger(__name__)


class ChunkRepository:
    """Repository for database interactions related to knowledge chunks."""

    def get_top_chunks(self, db: Session, query: list[float], n: int) -> list[KnowledgeChunk]:
        """Retrieve the top-n closest chunks by cosine similarity."""
        logger.info("Retrieving top %d chunks by cosine similarity", n)
        distance = KnowledgeChunk.embedding.cosine_distance(query)
        return db.query(KnowledgeChunk).order_by(distance).limit(n).all()

<<<<<<< HEAD
    def create_chunks(self, db: Session, chunks: list[dict[str, Any]]) -> list[KnowledgeChunk]:
        """Persist a batch of chunk dicts. Each must have: content, embedding, source."""
        logger.info("Inserting %d knowledge chunks", len(chunks))
        try:
            db_chunks = [
                KnowledgeChunk(
                    content=chunk["content"],
                    embedding=chunk["embedding"],
                    source=chunk["source"],
                )
                for chunk in chunks
            ]
            db.add_all(db_chunks)
            db.commit()
            for chunk in db_chunks:
                db.refresh(chunk)
            logger.info("Successfully inserted %d chunks", len(db_chunks))
            return db_chunks
        except Exception as e:
            db.rollback()
            logger.error("Failed to insert chunks: %s", e)
            raise

    def clear_chunks(self, db: Session, source: str) -> int:
        """Delete all chunks for a given source. Returns number of rows deleted."""
        logger.info("Clearing chunks for source='%s'", source)
        try:
            deleted = db.query(KnowledgeChunk).filter(KnowledgeChunk.source == source).delete(synchronize_session=False)
            db.commit()
            logger.info("Deleted %d chunks for source='%s'", deleted, source)
            return deleted
        except Exception as e:
            db.rollback()
            logger.error("Failed to clear chunks for source='%s': %s", source, e)
            raise
=======
    def create_chunks(self, db: Session, source: str, chunks: list[dict[str, Any]]) -> KnowledgeChunk:
        doc = KnowledgeChunk(source=source)
        db.add(doc)
        db.flush()  # get doc.id before inserting chunks

        for chunk in chunks:
            db.add(
                KnowledgeChunk(
                    document_id=doc.id,
                    content=chunk["content"],
                    chunk_index=chunk["chunk_index"],
                    embedding=chunk["embedding"],
                    source=source,
                )
            )

        db.commit()
        db.refresh(doc)
        return doc

    def clear_chunks(self, db: Session):
        db.query(KnowledgeChunk).delete()
        db.commit()
        logging.info("Cleared all knowledge chunks")
>>>>>>> 936ac18 (feat: created script to run different strategies and edited existing files to check strategy string. Added create_chunks and clear_chunks to chunk repository. Haven't tested yet)
