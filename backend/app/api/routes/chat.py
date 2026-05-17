from fastapi import APIRouter

router = APIRouter()

@router.get("/sessions")
def get_chat_sessions():
    return {"message": "List of chat sessions"}

@router.post("/message")
def send_message():
    return {"message": "Send a message endpoint"}
