import re
from typing import List, Dict, Any

def chunk_text(
    text: str,
    document_id: int,
    filename: str,
    page_number: int = None,
    section_title: str = None,
    chunk_size: int = 3000,
    chunk_overlap: int = 500,
    start_chunk_index: int = 0
) -> List[Dict[str, Any]]:
    """
    Chunks text avoiding cutting sentences in the middle.
    Returns a list of chunk dictionaries with preserved metadata.
    """
    # Split text into sentences (naively by punctuation + space)
    sentences = re.split(r'(?<=[.!?]) +|\n+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    chunk_index = start_chunk_index
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            # Store the current chunk
            chunks.append({
                "document_id": document_id,
                "filename": filename,
                "page_number": page_number,
                "chunk_index": chunk_index,
                "section_title": section_title,
                "content": current_chunk.strip()
            })
            chunk_index += 1
            
            # Start new chunk with overlap
            if len(current_chunk) > chunk_overlap:
                overlap_text = current_chunk[-chunk_overlap:]
                # Snap to next sentence to avoid cutting in the middle
                overlap_sentences = re.split(r'(?<=[.!?]) +', overlap_text)
                if len(overlap_sentences) > 1:
                    current_chunk = " ".join(overlap_sentences[1:]) + " " + sentence + " "
                else:
                    current_chunk = overlap_text + " " + sentence + " "
            else:
                current_chunk = current_chunk + " " + sentence + " "
        else:
            current_chunk += sentence + " "
            
    # Add any remaining text as the last chunk
    if current_chunk.strip():
        chunks.append({
            "document_id": document_id,
            "filename": filename,
            "page_number": page_number,
            "chunk_index": chunk_index,
            "section_title": section_title,
            "content": current_chunk.strip()
        })
        
    return chunks
