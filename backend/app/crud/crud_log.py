from sqlalchemy.orm import Session
from app.models.log import QueryLog
from app.schemas.log import QueryLogCreate

def create_query_log(db: Session, log: QueryLogCreate):
    db_log = QueryLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
