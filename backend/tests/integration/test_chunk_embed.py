from pathlib import Path
from database import SessionLocal
from repositories.chunk_repository import ChunkRepository
from services.pdfconvert import convert, chunk_text
from services.ingest import embed, ingest_pdf

RAW_PDF_DIR = Path("backend/data/raw/")
CHUNKING_STRATEGIES = ["fixed", "semantic", "sentence"]
EMBEDDING_MODELS = ["all-MiniLM-L6-v2", "text-embedding-ada-002", "text-embedding-3-large"]

def seed_experiments(dbSession: Session):
    chunkRepo = ChunkRepository()

    for strategy in CHUNKING_STRATEGIES:
        for model_type in EMBEDDING_MODELS:
            print(f"\nSeeding chunks for strategy='{strategy}', model='{model_type}'")

            # Clear previous chunks for this new combination
            chunkRepo.clear_chunks(dbSession, source=f"{strategy}_{model_type}")

            for pdf_path in RAW_PDF_DIR.glob("*.pdf"):
                source = pdf_path.stem
                with open(pdf_path, "rb") as file:
                    chunks_to_store = ingest_pdf(
                        file,
                        source=source,
                        strategy=strategy,
                        model_type=model_type
                    )
                    chunkRepo.create_chunks(dbSession, chunks_to_store)