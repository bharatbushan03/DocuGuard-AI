from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_documents():
    return {"message": "List of documents"}

@router.post("/upload")
def upload_document():
    return {"message": "Upload document endpoint"}
