"""Server-side file type validation using magic bytes (not client Content-Type)."""

from typing import Dict, List, Optional, Tuple

# MIME -> list of magic byte prefixes
MAGIC_SIGNATURES: Dict[str, List[bytes]] = {
    "application/pdf": [b"%PDF"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        b"PK\x03\x04"
    ],
    "text/plain": [],  # no magic; validated as decodable UTF-8 text
    "text/markdown": [],
}

ALLOWED_MIME_TO_EXT = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}


def detect_mime_from_content(header: bytes, sample_text: Optional[str] = None) -> Optional[str]:
    """Detect MIME type from file header bytes."""
    for mime, signatures in MAGIC_SIGNATURES.items():
        if not signatures:
            continue
        for sig in signatures:
            if header.startswith(sig):
                return mime
    if sample_text is not None:
        return "text/plain"
    return None


def validate_upload_content(
    content: bytes,
    declared_mime: Optional[str],
) -> Tuple[str, str]:
    """
    Validate upload bytes against allowed types.
    Returns (verified_mime, extension).
    Raises ValueError on failure.
    """
    if not content:
        raise ValueError("Empty file.")

    if declared_mime not in ALLOWED_MIME_TO_EXT:
        raise ValueError("Unsupported file type.")

    header = content[:8192]
    sample_text: Optional[str] = None

    if declared_mime in ("text/plain", "text/markdown"):
        try:
            sample_text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Text file must be valid UTF-8.") from exc
        # Reject embedded null bytes (binary masquerading as text)
        if b"\x00" in content[:4096]:
            raise ValueError("Invalid text file content.")

    detected = detect_mime_from_content(header, sample_text=sample_text)

    if declared_mime in ("text/plain", "text/markdown"):
        if detected and detected not in ("text/plain", "text/markdown"):
            raise ValueError("File content does not match declared text type.")
        return declared_mime, ALLOWED_MIME_TO_EXT[declared_mime]

    if detected != declared_mime:
        raise ValueError(
            "File content does not match declared type. "
            "Upload rejected to prevent type spoofing."
        )

    return declared_mime, ALLOWED_MIME_TO_EXT[declared_mime]
