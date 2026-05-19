from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from app.core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)

# Collection Name
COLLECTION_NAME = "docuguard_chunks"

try:
    client = QdrantClient(url=settings.QDRANT_URL)
except Exception as e:
    logger.error(f"Could not connect to Qdrant: {e}")
    client = None

def init_qdrant():
    """Initializes the Qdrant collection if it does not exist."""
    if not client:
        return
        
    try:
        collections = client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if not exists:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qdrant_models.VectorParams(
                    size=1536, # Size for OpenAI text-embedding-3-small
                    distance=qdrant_models.Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant: {e}")

# Call init automatically
init_qdrant()

def store_vectors(chunks_data: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
    """
    Stores embeddings in Qdrant and returns the generated point IDs.
    chunks_data must contain the metadata.
    """
    if not client or not chunks_data or not embeddings:
        return []

    points = []
    point_ids = []
    
    for idx, data in enumerate(chunks_data):
        point_id = str(uuid.uuid4())
        point_ids.append(point_id)
        
        # Build metadata payload
        payload = {
            "document_id": data.get("document_id"),
            "chunk_id": data.get("chunk_id"),
            "filename": data.get("filename"),
            "page_number": data.get("page_number"),
            "access_level": data.get("access_level", "private"),
            "uploaded_by": data.get("uploaded_by"),
            "content": data.get("content")
        }
        
        points.append(qdrant_models.PointStruct(
            id=point_id,
            vector=embeddings[idx],
            payload=payload
        ))
        
    try:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        return point_ids
    except Exception as e:
        logger.error(f"Failed to store vectors in Qdrant: {e}")
        raise e

def search_similar_chunks(query_vector: List[float], user_role: str, user_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Searches for similar chunks and filters based on role/access level.
    """
    if not client:
        return []

    # Build Role-Based Access Control Filter
    # Admins see everything.
    # Non-admins see public docs OR docs they uploaded.
    filter_condition = None
    
    if user_role != "admin":
        filter_condition = qdrant_models.Filter(
            should=[
                qdrant_models.FieldCondition(
                    key="access_level",
                    match=qdrant_models.MatchValue(value="public")
                ),
                qdrant_models.FieldCondition(
                    key="uploaded_by",
                    match=qdrant_models.MatchValue(value=user_id)
                )
            ]
        )

    try:
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=filter_condition,
            limit=top_k
        )
        
        # Format results
        formatted_results = []
        for res in results:
            formatted_results.append({
                "score": res.score,
                "document_id": res.payload.get("document_id"),
                "chunk_id": res.payload.get("chunk_id"),
                "filename": res.payload.get("filename"),
                "page_number": res.payload.get("page_number"),
                "content": res.payload.get("content"),
                "access_level": res.payload.get("access_level", "private")
            })
            
        return formatted_results
    except Exception as e:
        logger.error(f"Failed to search vectors in Qdrant: {e}")
        raise e
