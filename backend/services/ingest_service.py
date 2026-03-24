import logging
from pathlib import Path

from sqlalchemy.orm import Session

from repositories.chunk_repository import ChunkRepository
from services.ingest import ingest_pdf

logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


class IngestService:

    def ingest_pdf_file(self, db: Session, file, source: str) -> dict:
        """Parse, embed, and persist a single PDF file."""
        logger.info("Ingesting PDF: %s", source)
        chunk_dicts = ingest_pdf(file, source=source)
        chunk_repo = ChunkRepository()
        created = chunk_repo.create_chunks(db, chunk_dicts)
        logger.info("Ingested %d chunks from '%s'", len(created), source)
        return {"source": source, "chunks_created": len(created)}

    def ingest_folder(self, db: Session) -> dict:
        """Ingest all PDFs from the raw data directory. Idempotent."""
        logger.info("Ingesting all PDFs from %s", RAW_DATA_DIR)
        chunk_repo = ChunkRepository()
        results = []

        pdf_files = sorted(RAW_DATA_DIR.glob("*.pdf"))
        for pdf_path in pdf_files:
            source = pdf_path.name
            logger.info("Ingesting seed PDF: %s", source)
            try:
                with pdf_path.open("rb") as f:
                    chunk_dicts = ingest_pdf(f, source=source)
                cleared = chunk_repo.clear_chunks(db, source=source)
                created = chunk_repo.create_chunks(db, chunk_dicts)
                results.append({
                    "source": source,
                    "chunks_cleared": cleared,
                    "chunks_created": len(created),
                })
            except Exception as e:
                logger.error("Failed to ingest '%s': %s", source, e)
                results.append({"source": source, "error": str(e)})

        return {"sources_ingested": results}