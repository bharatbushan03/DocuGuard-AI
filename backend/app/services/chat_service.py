import time
import json
import logging
from typing import List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.core.access_control import user_owns_chat_session
from app.core.log_sanitizer import redact_chunks_for_api, redact_chunks_for_storage
from app.core.prompt_safety import (
    detect_suspicious_content,
    scan_retrieved_chunks,
    wrap_untrusted_context_block,
    build_rag_system_prompt,
    build_rag_user_prompt,
    merge_detections,
    format_injection_warning,
)
from app.models.user import User
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ChatSessionCreate, ChatMessageCreate
from app.schemas.log import QueryLogCreate
from app.crud.crud_chat import create_chat_session, create_chat_message, get_chat_session
from app.crud.crud_log import create_query_log
from app.services.embedding import embed_text
from app.services.vector_db import search_similar_chunks
from app.services.risk_classifier import classify_risk
from app.services.citation_verifier import verify_and_rewrite_answer
from app.services.confidence_scorer import calculate_confidence

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE,
)


def _resolve_session_id(
    db: Session,
    request: ChatQueryRequest,
    current_user: User,
    safe_question: str,
) -> int:
    """Access control for chat sessions — must run before retrieval / LLM."""
    if request.session_id:
        session = get_chat_session(db, request.session_id)
        if not session or not user_owns_chat_session(current_user, session):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or unauthorized chat session",
            )
        return session.id

    new_session = create_chat_session(
        db,
        ChatSessionCreate(title=safe_question[:50], user_id=current_user.id),
    )
    return new_session.id


def process_chat_query(db: Session, request: ChatQueryRequest, current_user: User) -> ChatQueryResponse:
    start_time = time.time()

    # 1. Input sanitization + detection (user query)
    query_detection = detect_suspicious_content(request.question, source="user_query")
    safe_question = query_detection.sanitized_text

    if query_detection.is_suspicious:
        logger.warning(
            "Prompt injection patterns in user query user_id=%s categories=%s",
            current_user.id,
            query_detection.matched_categories,
        )

    # 2. Access control before any retrieval or LLM call
    session_id = _resolve_session_id(db, request, current_user, safe_question)

    # 3. Embed and retrieve (vector DB enforces document access control)
    try:
        question_embedding = embed_text(safe_question)
    except Exception as e:
        logger.error("Failed to embed question for user_id=%s: %s", current_user.id, e)
        raise

    try:
        chunks = search_similar_chunks(
            query_vector=question_embedding,
            user_role=current_user.role,
            user_id=current_user.id,
            top_k=5,
        )
    except Exception as e:
        logger.error("Failed to retrieve chunks for user_id=%s: %s", current_user.id, e)
        chunks = []

    # 4. Sanitize retrieved document text (untrusted) + detect indirect injection
    chunks, doc_detection = scan_retrieved_chunks(chunks)
    combined_detection = merge_detections(query_detection, doc_detection)

    if doc_detection.is_suspicious:
        logger.warning(
            "Prompt injection patterns in retrieved context user_id=%s categories=%s",
            current_user.id,
            doc_detection.matched_categories,
        )

    context_text = ""
    for i, chunk in enumerate(chunks):
        context_text += f"\n--- Chunk {i+1} ---\n"
        context_text += f"Document: {chunk.get('filename')} (Page {chunk.get('page_number')})\n"
        context_text += f"Content: {chunk.get('content')}\n"

    context_block = wrap_untrusted_context_block(context_text)
    injection_note = format_injection_warning(combined_detection)

    system_prompt = build_rag_system_prompt(
        has_retrieved_context=bool(context_block),
        injection_detected=combined_detection.is_suspicious,
    )
    user_prompt = build_rag_user_prompt(
        context_block=context_block,
        safe_question=safe_question,
        injection_note=injection_note or None,
    )

    answer = "I could not find enough information in the provided documents"
    citations: List[Dict[str, Any]] = []
    risk_level = "low"
    is_supported = False
    confidence_reasoning = ""
    requires_human_review = combined_detection.is_suspicious
    risk_reason = ""
    citation_coverage = 0.0

    if combined_detection.is_suspicious:
        risk_reason = (
            "Suspicious prompt-injection language detected and neutralized. "
            f"Categories: {', '.join(combined_detection.matched_categories)}."
        )

    # 5. LLM call (only after access control + sanitization)
    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        content = response.choices[0].message.content
        if content:
            parsed = json.loads(content)
            answer = parsed.get("answer", answer)
            citations = parsed.get("citations", [])
            llm_requires_review = parsed.get("requires_human_review", False)
            confidence_reasoning = parsed.get("confidence_reasoning", "")
            is_supported = "I could not find enough information" not in answer

            if is_supported:
                answer, citation_coverage = verify_and_rewrite_answer(answer, chunks)
                if not answer or answer.startswith("I could not find enough information"):
                    is_supported = False

            risk_assessment = classify_risk(safe_question, answer, citations)
            risk_level = risk_assessment["risk_level"]
            if risk_reason:
                risk_reason += " " + risk_assessment["reason"]
            else:
                risk_reason = risk_assessment["reason"]
            requires_human_review = (
                requires_human_review
                or risk_assessment["requires_human_review"]
                or llm_requires_review
            )

            if requires_human_review and risk_level != "high":
                risk_level = "high"
                risk_reason += " (Elevated to high by safety or LLM flag)"
    except Exception as e:
        logger.error("Failed to generate LLM response for user_id=%s: %s", current_user.id, e)

    confidence_score = calculate_confidence(chunks, citation_coverage, answer)

    if is_supported and confidence_score < 0.45:
        requires_human_review = True
        risk_reason += " (Low confidence score, human review recommended)"
        if "human review is recommended" not in answer.lower():
            answer += "\n\nNote: Confidence is low. Human review is recommended."

    create_chat_message(
        db,
        ChatMessageCreate(session_id=session_id, role="user", content=safe_question),
    )
    create_chat_message(
        db,
        ChatMessageCreate(
            session_id=session_id,
            role="assistant",
            content=answer,
            citations=citations,
            confidence_score=confidence_score,
            risk_level=risk_level,
        ),
    )

    latency_ms = (time.time() - start_time) * 1000

    create_query_log(
        db,
        QueryLogCreate(
            user_id=current_user.id,
            query=safe_question,
            answer=answer,
            retrieved_chunks=redact_chunks_for_storage(chunks),
            confidence_score=confidence_score,
            risk_level=risk_level,
            latency_ms=latency_ms,
        ),
    )

    return ChatQueryResponse(
        answer=answer,
        citations=citations,
        confidence_score=confidence_score,
        risk_level=risk_level,
        risk_reason=risk_reason or None,
        requires_human_review=requires_human_review,
        injection_detected=combined_detection.is_suspicious,
        injection_categories=combined_detection.matched_categories,
        retrieved_chunks=redact_chunks_for_api(chunks),
        session_id=session_id,
    )
