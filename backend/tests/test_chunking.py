import pytest
from app.services.chunking import chunk_text

def test_chunk_text_basic():
    text = "This is sentence one. This is sentence two. This is sentence three."
    chunks = chunk_text(
        text=text,
        document_id=1,
        filename="test.txt",
        chunk_size=30,
        chunk_overlap=5
    )
    
    assert len(chunks) > 0
    assert chunks[0]["document_id"] == 1
    assert chunks[0]["filename"] == "test.txt"
    assert chunks[0]["page_number"] is None
    
def test_chunk_text_avoids_cutting_sentences():
    text = "First long sentence that should fit in the first chunk perfectly. Second sentence that will overflow."
    chunks = chunk_text(
        text=text,
        document_id=1,
        filename="test.txt",
        chunk_size=70,  # "First long sentence..." is ~65 chars
        chunk_overlap=10
    )
    
    assert len(chunks) == 2
    assert chunks[0]["content"] == "First long sentence that should fit in the first chunk perfectly."
    assert "Second sentence" in chunks[1]["content"]

def test_chunk_text_metadata():
    text = "Some text."
    chunks = chunk_text(
        text=text,
        document_id=99,
        filename="meta.pdf",
        page_number=5,
        section_title="Intro"
    )
    
    assert len(chunks) == 1
    assert chunks[0]["document_id"] == 99
    assert chunks[0]["page_number"] == 5
    assert chunks[0]["section_title"] == "Intro"
