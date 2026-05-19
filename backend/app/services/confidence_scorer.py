from typing import List, Dict, Any

def calculate_confidence(retrieved_chunks: List[Dict[str, Any]], citation_coverage: float, answer: str) -> float:
    """
    Calculate confidence score for RAG answers.
    Score is between 0 and 1.
    """
    if "i could not find enough information" in answer.lower():
        return 0.0
        
    if not retrieved_chunks:
        return 0.0

    # 1. Average similarity score of retrieved chunks
    avg_sim = sum(c.get("score", 0.0) for c in retrieved_chunks) / len(retrieved_chunks)
    
    # 2. Number of relevant chunks found (cap at 5 for max factor)
    chunk_factor = min(len(retrieved_chunks) / 5.0, 1.0)
    
    # 3. Citation coverage is already provided (0 to 1)
    
    # 5. Trusted access levels (private docs might be more authoritative than public)
    trusted_levels = {"private", "internal", "confidential", "restricted"}
    trusted_chunks = sum(1 for c in retrieved_chunks if c.get("access_level", "private").lower() in trusted_levels)
    trusted_ratio = trusted_chunks / len(retrieved_chunks)
    
    # Combine signals
    score = (avg_sim * 0.35) + (citation_coverage * 0.35) + (chunk_factor * 0.15) + (trusted_ratio * 0.15)
    
    return min(max(score, 0.0), 1.0)
