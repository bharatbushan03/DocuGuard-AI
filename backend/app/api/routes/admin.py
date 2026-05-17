from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_all_users():
    return {"message": "List of users for admin"}
