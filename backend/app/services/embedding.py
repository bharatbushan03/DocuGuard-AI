from typing import List
from openai import OpenAI
from tenacity import retry, wait_exponential, stop_after_attempt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE,
)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def embed_text(text: str) -> List[float]:
    """Generates an embedding for a single string using OpenAI's compatible API."""
    try:
        response = client.embeddings.create(
            input=text,
            model=settings.EMBEDDING_MODEL_NAME
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise e

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def embed_batch(texts: List[str]) -> List[List[float]]:
    """Generates embeddings for a batch of strings."""
    if not texts:
        return []
        
    try:
        response = client.embeddings.create(
            input=texts,
            model=settings.EMBEDDING_MODEL_NAME
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        logger.error(f"Failed to generate batch embeddings: {e}")
        raise e
