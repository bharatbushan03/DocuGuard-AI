import re
from typing import List, Dict, Any, Tuple

def extract_claims(text: str) -> List[str]:
    """
    Extracts claims from text by splitting into sentences.
    MVP implementation using simple regex.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 3]

def get_significant_words(text: str) -> set:
    """
    Tokenizes text and removes basic stopwords for MVP keyword overlap.
    """
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
        "of", "with", "by", "is", "are", "was", "were", "be", "been", "it", 
        "this", "that", "these", "those", "i", "you", "he", "she", "we", "they"
    }
    return set(words) - stopwords

def verify_claim(claim: str, chunks: List[Dict[str, Any]], overlap_threshold: float = 0.3) -> bool:
    """
    Verifies if a claim is supported by any chunk using simple keyword overlap.
    """
    claim_words = get_significant_words(claim)
    if not claim_words:
        return True # Empty or no significant words -> trivial
        
    for chunk in chunks:
        chunk_content = chunk.get("content", "")
        chunk_words = get_significant_words(chunk_content)
        
        # Calculate overlap (words in claim that appear in chunk)
        overlap = claim_words.intersection(chunk_words)
        overlap_ratio = len(overlap) / len(claim_words)
        
        if overlap_ratio >= overlap_threshold:
            return True
            
    return False

def verify_and_rewrite_answer(answer: str, chunks: List[Dict[str, Any]]) -> Tuple[str, float]:
    """
    Verifies claims in the answer against retrieved chunks.
    Drops unsupported claims and returns rewritten answer and coverage score.
    """
    claims = extract_claims(answer)
    if not claims:
        return answer, 1.0
        
    supported_claims = []
    
    for claim in claims:
        if verify_claim(claim, chunks):
            supported_claims.append(claim)
            
    # Calculate coverage
    coverage = len(supported_claims) / len(claims) if claims else 1.0
    
    # Rebuild answer
    if not supported_claims:
        return "I could not find enough information in the provided documents.", 0.0
        
    rewritten_answer = " ".join(supported_claims)
    return rewritten_answer, coverage
