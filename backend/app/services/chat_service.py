import time
import json
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.models.user import User
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ChatSessionCreate, ChatMessageCreate
from app.schemas.log import QueryLogCreate
from app.crud.crud_chat import create_chat_session, create_chat_message
from app.crud.crud_log import create_query_log
from app.services.embedding import embed_text
from app.services.vector_db import search_similar_chunks

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE,
)

def process_chat_query(db: Session, request: ChatQueryRequest, current_user: User) -> ChatQueryResponse:
    start_time = time.time()
    
    # 2. Embed the user question
    try:
        question_embedding = embed_text(request.question)
    except Exception as e:
        logger.error(f"Failed to embed question: {e}")
        raise e
        
    # 3 & 4. Retrieve top relevant chunks from Qdrant and filter by role
    try:
        chunks = search_similar_chunks(
            query_vector=question_embedding,
            user_role=current_user.role,
            user_id=current_user.id,
            top_k=5
        )
    except Exception as e:
        logger.error(f"Failed to retrieve chunks: {e}")
        chunks = []

    # 5. Build context block
    context_text = ""
    for i, chunk in enumerate(chunks):
        context_text += f"\n--- Chunk {i+1} ---\n"
        context_text += f"Document: {chunk.get('filename')} (Page {chunk.get('page_number')})\n"
        context_text += f"Content: {chunk.get('content')}\n"
        
    # 6, 7 & 8. Ask LLM using only provided context
    SYSTEM_PROMPT = """You are an enterprise AI assistant for DocuGuard AI.
1. Answer only using the provided context.
2. Never invent policy, legal, financial, or security details.
3. Always cite the document name and chunk/page when making a claim.
4. Say "I could not find enough information in the provided documents" when context is insufficient.
5. Mark high-risk answers as requiring human review.
6. Be concise but complete.
7. Avoid giving final legal, medical, financial, or security approval.
8. Output your answer in the exact JSON format specified by the user."""

    USER_PROMPT = f"""Please answer the following question using the provided context.
Return the answer in this JSON format:
{{
  "answer": "...",
  "citations": [
    {{
      "document": "...",
      "page": "...",
      "chunk_id": "...",
      "supporting_text": "..."
    }}
  ],
  "confidence_reasoning": "...",
  "requires_human_review": true or false
}}

Context:
{context_text}

User Question: {request.question}
"""
    
    answer = "I could not find enough information in the provided documents"
    citations = []
    risk_level = "low"
    is_supported = False
    confidence_reasoning = ""
    
    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        content = response.choices[0].message.content
        if content:
            parsed = json.loads(content)
            answer = parsed.get("answer", "I could not find enough information in the provided documents")
            citations = parsed.get("citations", [])
            requires_human_review = parsed.get("requires_human_review", False)
            risk_level = "high" if requires_human_review else "low"
            confidence_reasoning = parsed.get("confidence_reasoning", "")
            is_supported = "I could not find enough information" not in answer
    except Exception as e:
        logger.error(f"Failed to generate LLM response: {e}")
        
    # 9. Calculate confidence score
    if answer.strip().lower().startswith("i could not find enough information") or not is_supported:
        confidence_score = 0.0
    else:
        avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks) if chunks else 0.0
        citation_bonus = min(len(citations) * 0.1, 0.2)
        confidence_score = min(avg_score + citation_bonus, 0.99)
        
    # 11. Store question and answer in ChatMessage and QueryLog
    session_id = request.session_id
    if not session_id:
        new_session = create_chat_session(db, ChatSessionCreate(
            title=request.question[:50], 
            user_id=current_user.id
        ))
        session_id = new_session.id
        
    # Store user message
    create_chat_message(db, ChatMessageCreate(
        session_id=session_id,
        role="user",
        content=request.question
    ))
    
    # Store assistant message
    create_chat_message(db, ChatMessageCreate(
        session_id=session_id,
        role="assistant",
        content=answer,
        citations=citations,
        confidence_score=confidence_score,
        risk_level=risk_level
    ))
    
    latency_ms = (time.time() - start_time) * 1000
    
    create_query_log(db, QueryLogCreate(
        user_id=current_user.id,
        query=request.question,
        answer=answer,
        retrieved_chunks=chunks,
        confidence_score=confidence_score,
        risk_level=risk_level,
        latency_ms=latency_ms
    ))
    
    # 12. Return
    return ChatQueryResponse(
        answer=answer,
        citations=citations,
        confidence_score=confidence_score,
        risk_level=risk_level,
        retrieved_chunks=chunks,
        session_id=session_id
    )
