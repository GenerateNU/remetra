import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from database import SessionLocal
from repositories.chunk_repository import ChunkRepository
from services.ingest import ingest_pdf


def main():
    dbSession = SessionLocal()
    try:
        chunkRepo = ChunkRepository()
        chunkRepo.clear_chunks(dbSession)

        parser = argparse.ArgumentParser()
        parser.add_argument("--strategy", type=str, default="fixed")
        args = parser.parse_args()
        strat = args.strategy

        for pdf_path in Path("backend/data/raw/").glob("*.pdf"):
            source = pdf_path.name
            with open(pdf_path, "rb") as file:
                chunks = ingest_pdf(file, source, strat, model_type="all-MiniLM-L6-v2")
                chunkRepo.create_chunks(dbSession, source, chunks)
    finally:
        dbSession.close()


if __name__ == "__main__":
    main()
