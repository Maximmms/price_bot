from fastapi import APIRouter

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/me")
async def get_current_user():
    return {
            "username": "test",
            "email": "test@test.com"
            }