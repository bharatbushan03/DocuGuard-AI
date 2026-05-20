import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.ingestion_service import extract_pages_from_file, process_document_background
from app.models.document import Document

def test_extract_text_txt():
    test_file = "test_extract.txt"
    with open(test_file, "w") as f:
        f.write("Hello Text Extraction")
    
    try:
        pages = extract_pages_from_file(test_file, "text/plain")
        assert len(pages) == 1
        assert pages[0]["text"] == "Hello Text Extraction"
        assert pages[0]["page_number"] == 1
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

@patch("fitz.open")
def test_extract_text_pdf(mock_fitz_open):
    # Mock PDF document
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "PDF Content"
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc
    
    pages = extract_pages_from_file("fake.pdf", "application/pdf")
    assert len(pages) == 1
    assert pages[0]["text"] == "PDF Content"
    mock_doc.close.assert_called_once()

@patch("app.services.ingestion_service.extract_pages_from_file")
@patch("app.services.ingestion_service.embed_batch")
@patch("app.services.ingestion_service.store_vectors")
def test_process_document_background(mock_store, mock_embed, mock_extract, db):
    # Create a document in DB
    doc = Document(
        title="bg_test.txt",
        filename="bg_test.txt",
        file_type="text/plain",
        status="uploaded",
        uploaded_by=1
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    mock_extract.return_value = [{"text": "Chunkable text content", "page_number": 1}]
    mock_embed.return_value = [[0.1] * 1536]
    mock_store.return_value = ["point-123"]
    
    process_document_background(doc.id, "fake_path")
    
    db.refresh(doc)
    assert doc.status == "indexed"
    assert len(doc.chunks) > 0
    assert doc.chunks[0].qdrant_point_id == "point-123"
