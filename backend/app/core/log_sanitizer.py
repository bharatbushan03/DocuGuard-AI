"""Redact sensitive fields before persistence or API responses."""

from typing import Any, Dict, List, Optional

CONTENT_PREVIEW_LENGTH = 120


def redact_chunk_for_api(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Return chunk metadata safe for client responses (no full document text)."""
    content = chunk.get("content") or ""
    preview = content[:CONTENT_PREVIEW_LENGTH]
    if len(content) > CONTENT_PREVIEW_LENGTH:
        preview += "…"
    return {
        "score": chunk.get("score"),
        "document_id": chunk.get("document_id"),
        "chunk_id": chunk.get("chunk_id"),
        "filename": chunk.get("filename"),
        "page_number": chunk.get("page_number"),
        "access_level": chunk.get("access_level", "private"),
        "content_preview": preview if preview else None,
    }


def redact_chunks_for_api(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [redact_chunk_for_api(c) for c in chunks]


def redact_chunks_for_storage(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Store audit metadata without full chunk bodies."""
    return [
        {
            "document_id": c.get("document_id"),
            "chunk_id": c.get("chunk_id"),
            "filename": c.get("filename"),
            "page_number": c.get("page_number"),
            "score": c.get("score"),
            "access_level": c.get("access_level", "private"),
        }
        for c in chunks
    ]
