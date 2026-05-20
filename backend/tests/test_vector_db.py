import pytest
from app.services.vector_db import search_similar_chunks, store_vectors
from unittest.mock import MagicMock

def test_search_similar_chunks(mock_qdrant):
    mock_qdrant.search.reset_mock()
    
    results = search_similar_chunks(
        query_vector=[0.1] * 1536,
        user_role="employee",
        user_id=1,
        top_k=5
    )
    
    assert len(results) == 5
    assert results[0]["filename"] == "test.pdf"
    assert results[0]["score"] == 0.95
    mock_qdrant.search.assert_called_once()
    
    # Check that filter was applied for non-admin
    args, kwargs = mock_qdrant.search.call_args
    assert kwargs["query_filter"] is not None

def test_search_similar_chunks_admin(mock_qdrant):
    mock_qdrant.search.reset_mock()
    
    search_similar_chunks(
        query_vector=[0.1] * 1536,
        user_role="admin",
        user_id=1,
        top_k=5
    )
    
    args, kwargs = mock_qdrant.search.call_args
    assert kwargs["query_filter"] is None

def test_store_vectors(mock_qdrant):
    mock_qdrant.upsert.reset_mock()
    
    chunks_data = [{
        "document_id": 1,
        "chunk_id": 1,
        "filename": "test.txt",
        "content": "Hello"
    }]
    embeddings = [[0.1] * 1536]
    
    ids = store_vectors(chunks_data, embeddings)
    assert len(ids) == 1
    mock_qdrant.upsert.assert_called_once()
