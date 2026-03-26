"""
Integration tests for the full RAG ingest pipeline:
  pdfconvert.py → services/ingest.py → repositories/chunk_repository.py → services/ingest_service.py

PDF fixtures:
  pdf_with_text  — fpdf2-generated PDF with extractable text (covers pdfconvert lines 10-11)
  blank_pdf      — pypdf PdfWriter blank page (no extractable text, covers the False branch of line 10)
"""

import io

import pytest
from pypdf import PdfWriter

from models.knowledge_chunk import KnowledgeChunk
from repositories.chunk_repository import ChunkRepository
from services.ingest import embed, ingest_pdf
from services.ingest_service import IngestService
from services.pdfconvert import chunk_text, convert

# ---------------------------------------------------------------------------
# Shared PDF fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pdf_with_text():
    """Return a BytesIO containing a real PDF with extractable text."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    # Write enough words to guarantee multiple chunks at default size=512
    long_text = " ".join([f"word{i}" for i in range(600)])
    pdf.multi_cell(0, 10, txt=long_text)
    return io.BytesIO(pdf.output())


@pytest.fixture
def blank_pdf():
    """Return a BytesIO containing a PDF with a blank page (no extractable text)."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# pdfconvert.py
# ---------------------------------------------------------------------------

class TestPdfConvert:
    """Tests for convert() and chunk_text() in services/pdfconvert.py."""

    def test_convert_extracts_text(self, pdf_with_text):
        """convert() on a PDF with content returns a non-empty string."""
        result = convert(pdf_with_text)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_convert_blank_pdf_returns_empty_string(self, blank_pdf):
        """convert() on a blank page returns an empty string (no text appended)."""
        result = convert(blank_pdf)

        assert isinstance(result, str)
        assert result == ""

    def test_chunk_text_splits_into_multiple_chunks(self):
        """Text with more than `size` words is split into multiple chunks."""
        text = " ".join([f"word{i}" for i in range(600)])

        chunks = chunk_text(text, size=512, overlap=50)

        assert len(chunks) > 1

    def test_chunk_text_each_chunk_respects_size(self):
        """Each chunk contains at most `size` words."""
        text = " ".join([f"word{i}" for i in range(600)])

        chunks = chunk_text(text, size=100, overlap=10)

        for chunk in chunks:
            assert len(chunk.split()) <= 100

    def test_chunk_text_has_overlap(self):
        """The last `overlap` words of chunk[n] equal the first `overlap` words of chunk[n+1]."""
        words = [f"w{i}" for i in range(200)]
        text = " ".join(words)

        chunks = chunk_text(text, size=50, overlap=10)

        assert len(chunks) >= 2
        end_of_first = chunks[0].split()[-10:]
        start_of_second = chunks[1].split()[:10]
        assert end_of_first == start_of_second

    def test_chunk_text_empty_string_returns_empty_list(self):
        """chunk_text('') returns an empty list."""
        result = chunk_text("")

        assert result == []

    def test_chunk_text_short_text_returns_single_chunk(self):
        """Text shorter than `size` words produces exactly one chunk."""
        text = "just a few words here"

        result = chunk_text(text)

        assert len(result) == 1
        assert result[0] == text


# ---------------------------------------------------------------------------
# services/ingest.py  (ingest_pdf)
# ---------------------------------------------------------------------------

class TestIngestPdf:
    """Tests for the ingest_pdf() pure function in services/ingest.py."""

    def test_ingest_pdf_returns_list_of_dicts(self, pdf_with_text):
        """ingest_pdf() returns a non-empty list of chunk dicts."""
        result = ingest_pdf(pdf_with_text, source="test.pdf")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_ingest_pdf_dict_has_required_keys(self, pdf_with_text):
        """Each chunk dict contains content, embedding, and source keys."""
        result = ingest_pdf(pdf_with_text, source="test.pdf")

        for chunk in result:
            assert "content" in chunk
            assert "embedding" in chunk
            assert "source" in chunk

    def test_ingest_pdf_embedding_is_384_floats(self, pdf_with_text):
        """Each embedding is a list of 384 floats (all-MiniLM-L6-v2 output dim)."""
        result = ingest_pdf(pdf_with_text, source="test.pdf")

        for chunk in result:
            assert isinstance(chunk["embedding"], list)
            assert len(chunk["embedding"]) == 384
            assert all(isinstance(v, float) for v in chunk["embedding"])

    def test_ingest_pdf_source_propagated(self, pdf_with_text):
        """The source string is set on every chunk dict."""
        result = ingest_pdf(pdf_with_text, source="my_doc.pdf")

        assert all(chunk["source"] == "my_doc.pdf" for chunk in result)

    def test_ingest_pdf_blank_returns_empty_list(self, blank_pdf):
        """A PDF with no extractable text produces an empty chunk list."""
        result = ingest_pdf(blank_pdf, source="blank.pdf")

        assert result == []


# ---------------------------------------------------------------------------
# repositories/chunk_repository.py
# ---------------------------------------------------------------------------

class TestChunkRepository:
    """Integration tests for ChunkRepository against the real test database."""

    def _make_chunks(self, texts: list[str], source: str = "test_source") -> list[dict]:
        """Helper: embed a list of strings into chunk dicts."""
        embeddings = embed(texts)
        return [
            {"content": t, "embedding": e, "source": source}
            for t, e in zip(texts, embeddings)
        ]

    def test_create_chunks(self, db_session):
        """create_chunks persists rows and returns KnowledgeChunk objects with IDs."""
        repo = ChunkRepository()
        chunks = self._make_chunks(["alpha text", "beta text"])

        result = repo.create_chunks(db_session, chunks)

        assert len(result) == 2
        assert all(isinstance(c, KnowledgeChunk) for c in result)
        assert all(c.id is not None for c in result)
        assert all(c.source == "test_source" for c in result)

    def test_create_chunks_empty_list(self, db_session):
        """create_chunks with an empty list is a no-op and returns []."""
        repo = ChunkRepository()

        result = repo.create_chunks(db_session, [])

        assert result == []

    def test_get_top_chunks_returns_n_results(self, db_session):
        """get_top_chunks returns exactly n results when n <= total rows."""
        repo = ChunkRepository()
        chunks = self._make_chunks(["text one", "text two", "text three"])
        repo.create_chunks(db_session, chunks)

        query_embedding = embed(["text"])[0]
        results = repo.get_top_chunks(db_session, query_embedding, n=2)

        assert len(results) == 2
        assert all(isinstance(r, KnowledgeChunk) for r in results)

    def test_get_top_chunks_returns_all_when_n_exceeds_count(self, db_session):
        """get_top_chunks returns all rows when n is larger than the total."""
        repo = ChunkRepository()
        chunks = self._make_chunks(["only chunk"])
        repo.create_chunks(db_session, chunks)

        query_embedding = embed(["chunk"])[0]
        results = repo.get_top_chunks(db_session, query_embedding, n=10)

        assert len(results) == 1

    def test_clear_chunks_deletes_by_source_and_returns_count(self, db_session):
        """clear_chunks removes only rows matching the given source."""
        repo = ChunkRepository()
        repo.create_chunks(db_session, self._make_chunks(["source A"], source="source_a"))
        repo.create_chunks(db_session, self._make_chunks(["source B"], source="source_b"))

        cleared = repo.clear_chunks(db_session, source="source_a")

        assert cleared == 1
        remaining = db_session.query(KnowledgeChunk).filter(
            KnowledgeChunk.source == "source_b"
        ).all()
        assert len(remaining) == 1

    def test_clear_chunks_nonexistent_source_returns_zero(self, db_session):
        """clear_chunks returns 0 when no rows match the given source."""
        repo = ChunkRepository()

        cleared = repo.clear_chunks(db_session, source="nonexistent_source")

        assert cleared == 0


# ---------------------------------------------------------------------------
# services/ingest_service.py
# ---------------------------------------------------------------------------

class TestIngestService:
    """Integration tests for IngestService — RAW_DATA_DIR is monkeypatched to tmp_path."""

    def test_ingest_pdf_file(self, db_session, pdf_with_text):
        """ingest_pdf_file embeds and persists chunks, returning source + chunk count."""
        service = IngestService()

        result = service.ingest_pdf_file(db_session, pdf_with_text, source="test.pdf")

        assert result["source"] == "test.pdf"
        assert result["chunks_created"] > 0
        stored = db_session.query(KnowledgeChunk).filter(
            KnowledgeChunk.source == "test.pdf"
        ).all()
        assert len(stored) == result["chunks_created"]

    def test_ingest_pdf_file_blank_pdf_creates_zero_chunks(self, db_session, blank_pdf):
        """ingest_pdf_file on a blank PDF creates 0 chunks (no extractable text)."""
        service = IngestService()

        result = service.ingest_pdf_file(db_session, blank_pdf, source="blank.pdf")

        assert result["chunks_created"] == 0

    def test_ingest_folder(self, db_session, tmp_path, monkeypatch, pdf_with_text):
        """ingest_folder processes every PDF in RAW_DATA_DIR and returns a result per file."""
        pdf_path = tmp_path / "doc.pdf"
        pdf_path.write_bytes(pdf_with_text.read())

        monkeypatch.setattr("services.ingest_service.RAW_DATA_DIR", tmp_path)

        service = IngestService()
        result = service.ingest_folder(db_session)

        sources = result["sources_ingested"]
        assert len(sources) == 1
        assert sources[0]["source"] == "doc.pdf"
        assert sources[0]["chunks_created"] > 0
        assert "error" not in sources[0]

    def test_ingest_folder_idempotent(self, db_session, tmp_path, monkeypatch, pdf_with_text):
        """Calling ingest_folder twice clears old chunks before re-inserting."""
        pdf_path = tmp_path / "doc.pdf"
        pdf_path.write_bytes(pdf_with_text.read())

        monkeypatch.setattr("services.ingest_service.RAW_DATA_DIR", tmp_path)

        service = IngestService()
        first = service.ingest_folder(db_session)
        chunks_first = first["sources_ingested"][0]["chunks_created"]

        second = service.ingest_folder(db_session)

        assert second["sources_ingested"][0]["chunks_cleared"] == chunks_first
        assert second["sources_ingested"][0]["chunks_created"] == chunks_first

    def test_ingest_folder_no_pdfs_returns_empty_list(self, db_session, tmp_path, monkeypatch):
        """ingest_folder with an empty directory returns sources_ingested: []."""
        monkeypatch.setattr("services.ingest_service.RAW_DATA_DIR", tmp_path)

        service = IngestService()
        result = service.ingest_folder(db_session)

        assert result == {"sources_ingested": []}

    def test_ingest_folder_logs_error_on_corrupt_pdf(self, db_session, tmp_path, monkeypatch):
        """A corrupt file logs an error entry without raising — other files are unaffected."""
        (tmp_path / "bad.pdf").write_bytes(b"this is not a valid pdf")

        monkeypatch.setattr("services.ingest_service.RAW_DATA_DIR", tmp_path)

        service = IngestService()
        result = service.ingest_folder(db_session)

        sources = result["sources_ingested"]
        assert len(sources) == 1
        assert sources[0]["source"] == "bad.pdf"
        assert "error" in sources[0]
