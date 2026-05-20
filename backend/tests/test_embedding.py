import pytest
from app.services.embedding import embed_text, embed_batch
from unittest.mock import MagicMock

def test_embed_text(mock_openai):
    embedding = embed_text("test string")
    assert len(embedding) == 1536
    assert embedding[0] == 0.1
    mock_openai.embeddings.create.assert_called_once()

def test_embed_batch(mock_openai):
    mock_openai.embeddings.create.reset_mock()
    # Mock for batch
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1] * 1536),
        MagicMock(embedding=[0.2] * 1536)
    ]
    mock_openai.embeddings.create.return_value = mock_response
    
    embeddings = embed_batch(["text 1", "text 2"])
    assert len(embeddings) == 2
    assert embeddings[0][0] == 0.1
    assert embeddings[1][0] == 0.2
    mock_openai.embeddings.create.assert_called_once()
