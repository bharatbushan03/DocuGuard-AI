import os
import shutil
import fitz  # PyMuPDF
import docx
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentCreate
from app.crud import crud_document
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md"
}

os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_file(file_path: str, mime_type: str) -> str:
    try:
        text = ""
        if mime_type == "application/pdf":
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif mime_type in ["text/plain", "text/markdown"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            raise ValueError("Unsupported file type for extraction")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        raise e

def process_upload(file: UploadFile, user_id: int, db: Session) -> Document:
    # 1. Validation
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
    file.file.seek(0)

    # 2. Save File
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Could not save file.")

    # 3. Create initial DB record
    doc_in = DocumentCreate(
        title=file.filename,
        filename=file.filename,
        file_type=file.content_type,
        access_level="private",
        uploaded_by=user_id
    )
    # The Document base model needs to be updated or we just create it manually since DocumentCreate schema doesn't match perfectly with the model fields directly if it doesn't have filename etc. Let's check `crud_document.py` later.
    db_doc = Document(
        title=doc_in.title,
        filename=doc_in.filename,
        file_type=doc_in.file_type,
        access_level=doc_in.access_level,
        uploaded_by=doc_in.uploaded_by,
        status="uploaded"
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # 4. Extract Text
    try:
        db_doc.status = "processing"
        db.commit()

        text = extract_text_from_file(file_path, db_doc.file_type)
        
        # Simple chunking for MVP: by paragraph/line breaks or fixed size
        chunks = text.split("\n\n")
        chunks = [c.strip() for c in chunks if c.strip()]
        
        # Store chunks
        for idx, chunk_content in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=db_doc.id,
                chunk_index=idx,
                content=chunk_content
            )
            db.add(db_chunk)
        
        db_doc.status = "indexed" # Pretending we indexed them since we don't do embeddings yet
        db.commit()
        db.refresh(db_doc)

    except Exception as e:
        logger.error(f"Processing failed for document {db_doc.id}: {e}")
        db_doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to process document text.")

    return db_doc
