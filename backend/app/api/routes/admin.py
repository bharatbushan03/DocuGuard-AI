from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, require_role
from app.core.log_sanitizer import redact_chunks_for_storage
from app.models.user import User
from app.models.document import Document
from app.models.log import QueryLog
from app.schemas.log import QueryLogResponse

router = APIRouter()

# TODO: Implement more robust logging and telemetry for admin actions


def _sanitize_log(log: QueryLog) -> dict:
    data = {
        "id": log.id,
        "user_id": log.user_id,
        "query": log.query,
        "answer": log.answer,
        "confidence_score": log.confidence_score,
        "risk_level": log.risk_level,
        "latency_ms": log.latency_ms,
        "created_at": log.created_at,
        "retrieved_chunks": log.retrieved_chunks,
    }
    if data["retrieved_chunks"]:
        data["retrieved_chunks"] = redact_chunks_for_storage(data["retrieved_chunks"])
    return data


@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    total_docs = db.query(Document).count()
    total_queries = db.query(QueryLog).count()
    avg_conf = db.query(func.avg(QueryLog.confidence_score)).scalar() or 0.0
    high_risk_count = db.query(QueryLog).filter(QueryLog.risk_level == "high").count()
    failed_docs_count = db.query(Document).filter(Document.status == "failed").count()

    frequent_queries = (
        db.query(QueryLog.query, func.count(QueryLog.id).label("cnt"))
        .group_by(QueryLog.query)
        .order_by(func.count(QueryLog.id).desc())
        .limit(5)
        .all()
    )
    freq_list = [{"query": q[0], "count": q[1]} for q in frequent_queries]

    failed_docs = db.query(Document).filter(Document.status == "failed").limit(5).all()
    failed_docs_list = [
        {"id": d.id, "filename": d.title, "created_at": d.created_at}
        for d in failed_docs
    ]

    return {
        "total_documents": total_docs,
        "total_queries": total_queries,
        "avg_confidence": avg_conf,
        "high_risk_queries_count": high_risk_count,
        "failed_documents_count": failed_docs_count,
        "frequent_queries": freq_list,
        "failed_documents": failed_docs_list,
    }


@router.get("/query-logs", response_model=list[QueryLogResponse])
def get_query_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    logs = db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(200).all()
    return [_sanitize_log(log) for log in logs]


@router.get("/high-risk", response_model=list[QueryLogResponse])
def get_high_risk_queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    logs = (
        db.query(QueryLog)
        .filter(QueryLog.risk_level == "high")
        .order_by(QueryLog.created_at.desc())
        .limit(200)
        .all()
    )
    return [_sanitize_log(log) for log in logs]


@router.get("/low-confidence", response_model=list[QueryLogResponse])
def get_low_confidence_queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    logs = (
        db.query(QueryLog)
        .filter(QueryLog.confidence_score < 0.45)
        .order_by(QueryLog.created_at.desc())
        .limit(200)
        .all()
    )
    return [_sanitize_log(log) for log in logs]
